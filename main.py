import json
import pandas as pd
from playwright.sync_api import sync_playwright
import requests
import os
from profiler import load_technologies, profile
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from playwright_stealth import Stealth
from tqdm import tqdm
from urllib.parse import urlparse
import dns.resolver

requests.packages.urllib3.disable_warnings()

thread_local = threading.local()
MAX_TASKS_PER_BROWSER = 25

def get_browser():
	needs_refresh = False
	if not hasattr(thread_local, "playwright"):
		needs_refresh = True
	elif not getattr(thread_local, "browser").is_connected():
		needs_refresh = True
	elif getattr(thread_local, "tasks_on_browser", 0) >= MAX_TASKS_PER_BROWSER:
		needs_refresh = True

	if needs_refresh and hasattr(thread_local, "browser"):
		try:
			thread_local.browser.close()
		except Exception:
			pass
		try:
			thread_local.playwright.stop()
		except Exception:
			pass

	if needs_refresh:
		thread_local.playwright = sync_playwright().start()
		thread_local.browser = thread_local.playwright.chromium.launch()
		thread_local.tasks_on_browser = 0

	thread_local.tasks_on_browser = getattr(thread_local, "tasks_on_browser", 0) + 1
	return getattr(thread_local, "browser")

def profile_domain(domain: str, parsed_technologies: Dict[str, Any], global_js_props: List[str], global_dom_selectors: Dict[str, Any]):
	candidate_urls = [f"https://{domain}", f"http://{domain}"]
	page_url = candidate_urls[0]
	
	html = ""
	headers = {}
	cookies = []
	script_srcs = []
	xhr_urls = []
	meta_tags = {}
	
	css_content = ""
	robots_text = ""
	cert_issuer = ""
	dns_records = {"TXT": [], "SOA": [], "NS": []}
	
	try:
		resolver = dns.resolver.Resolver()
		resolver.timeout = 3
		resolver.lifetime = 3
		for rtype in ["TXT", "SOA", "NS"]:
			try:
				answers = resolver.resolve(domain, rtype)
				dns_records[rtype] = [rdata.to_text().strip('"') for rdata in answers]
			except: pass
	except: pass

	try:
		rob_resp = requests.get(f"https://{domain}/robots.txt", headers={"User-Agent": user_agent}, timeout=5, verify=False)
		if rob_resp.status_code == 200:
			robots_text = rob_resp.text
	except: pass
	
	detected = []
	user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

	try:
		browser = get_browser()
		context = browser.new_context(user_agent=user_agent, ignore_https_errors=True)
		try:
			page = context.new_page()
			Stealth().apply_stealth_sync(page)

			def handle_response(response):
				nonlocal headers, cert_issuer
				response_host = (urlparse(response.url).hostname or "").lower()
				root_domain = domain.lower()
				if response_host == root_domain or response_host.endswith(f".{root_domain}"):
					headers.update(response.headers)
					if not cert_issuer:
						try:
							sec = response.security_details() or {}
							if "issuer" in sec:
								cert_issuer = sec["issuer"]
						except: pass
				if response.request.resource_type in {"xhr", "fetch"}:
					xhr_urls.append(response.url)
					
			page.on("response", handle_response)
			
			page_loaded = False
			try:
				for url in candidate_urls:
					try:
						page.goto(url, timeout=30000, wait_until="domcontentloaded")
						page_url = page.url
						page_loaded = True
						break
					except Exception:
						continue

				if not page_loaded:
					raise RuntimeError("Playwright navigation failed")

				html = page.content()
				cookies = context.cookies()
				
				meta_elements = page.query_selector_all('meta')
				for m in meta_elements:
					name = m.get_attribute('name') or m.get_attribute('property')
					content = m.get_attribute('content')
					if name and content:
						meta_tags[name.lower()] = content

				script_elements = page.query_selector_all('script')
				for s in script_elements:
					src = s.get_attribute('src')
					if src:
						script_srcs.append(src)
			except Exception:
				for url in candidate_urls:
					try:
						resp = requests.get(
							url,
							headers={"User-Agent": user_agent},
							timeout=(5, 12),
							verify=False,
							allow_redirects=True,
						)
						page_url = resp.url
						html = resp.text
						headers.update(dict(resp.headers))
						for cookie_name, cookie_val in resp.cookies.get_dict().items():
							cookies.append({"name": cookie_name, "value": cookie_val})
						break
					except Exception:
						continue

			js_values = {}
			dom_values = {}
			scripts_contents = []

			try:
				for s in page.query_selector_all('script:not([src])'):
					txt = s.inner_text()
					if txt: scripts_contents.append(txt[:10000])
			except: pass
			try:
				js_code = """([props, domReqs]) => {
					let jsVals = {};
					for(let p of props) {
						try {
							let parts = p.split('.');
							let val = window;
							for(let part of parts) val = val[part];
							if (typeof val !== 'undefined' && val !== null) {
								jsVals[p] = String(val);
							} else {
								jsVals[p] = null;
							}
						} catch(e) { jsVals[p] = null; }
					}
					
					let domVals = {};
					for (let sel of Object.keys(domReqs)) {
						try {
							let els = document.querySelectorAll(sel);
							if (els.length === 0) continue;
							let req = domReqs[sel];
							let ex = { text: [], attributes: {}, properties: {} };
							for(let el of els) {
								if (req.text) {
									let t = el.innerText || el.textContent;
									if(t) ex.text.push(t);
								}
								if (req.attributes) {
									for(let attr of req.attributes) {
										let v = el.getAttribute(attr);
										if (v) {
											if (!ex.attributes[attr]) ex.attributes[attr] = [];
											ex.attributes[attr].push(v);
										}
									}
								}
								if (req.properties) {
									for(let prop of req.properties) {
										let v = el[prop];
										if (v !== undefined && v !== null) {
											if (!ex.properties[prop]) ex.properties[prop] = [];
											ex.properties[prop].push(String(v));
										}
									}
								}
								if (req.exists) ex.exists = true;
							}
							if (ex.text.length > 0 || Object.keys(ex.attributes).length > 0 || Object.keys(ex.properties).length > 0 || ex.exists) {
								domVals[sel] = ex;
							}
						} catch(e) {}
					}
					let cssVals = [];
					for (let sheet of document.styleSheets) {
						try {
							for (let rule of sheet.cssRules) {
								if (rule.cssText) cssVals.push(rule.cssText);
							}
						} catch(e) {}
					}
					return {jsVals, domVals, cssVals: cssVals.join('\\n')};
				}"""
				res = page.evaluate(js_code, [global_js_props, global_dom_selectors])
				if res:
					js_values = res.get("jsVals", {})
					dom_values = res.get("domVals", {})
					css_content = res.get("cssVals", "")
			except Exception:
				pass
				
			detected = profile(
				html,
				headers,
				cookies,
				script_srcs,
				meta_tags,
				js_values,
				dom_values,
				scripts_contents,
				parsed_technologies,
				page_url=page_url,
				xhr_urls=xhr_urls,
				css_content=css_content,
				robots_text=robots_text,
				dns_records=dns_records,
				cert_issuer=cert_issuer,
			)
			
			return domain, detected
		finally:
			context.close()

	except Exception:
		return domain, detected
		

def main():
	parquet_file = "part-00000-66e0628d-2c7f-425a-8f5b-738bcd6bf198-c000.snappy.parquet"
	if not os.path.exists(parquet_file):
		print(f"Error: Parquet file {parquet_file} not found.")
		return

	print("Loading Technologies...")
	parsed_technologies = load_technologies("technologies")

	global_js_props_set = set()
	global_dom_selectors: dict = {}
	for tech_name, rules in parsed_technologies.items():
		if 'js' in rules:
			global_js_props_set.update(rules['js'].keys())
		if 'dom' in rules:
			for selector, s_rules in rules['dom'].items():
				if selector not in global_dom_selectors:
					global_dom_selectors[selector] = {}
				if "attributes" in s_rules:
					global_dom_selectors[selector].setdefault("attributes", []).extend(s_rules["attributes"].keys())
				if "properties" in s_rules:
					global_dom_selectors[selector].setdefault("properties", []).extend(s_rules["properties"].keys())
				if "text" in s_rules:
					global_dom_selectors[selector]["text"] = True
				if "exists" in s_rules:
					global_dom_selectors[selector]["exists"] = True

	global_js_props = list(global_js_props_set)
	for sel in global_dom_selectors:
		if "attributes" in global_dom_selectors[sel]:
			global_dom_selectors[sel]["attributes"] = list(set(global_dom_selectors[sel]["attributes"]))
		if "properties" in global_dom_selectors[sel]:
			global_dom_selectors[sel]["properties"] = list(set(global_dom_selectors[sel]["properties"]))

	print(f"Reading Parquet file: {parquet_file}")
	df = pd.read_parquet(parquet_file)
	all_domains = df['root_domain'].tolist()
	
	results = {}
	if os.path.exists("output.json"):
		try:
			with open("output.json", "r", encoding="utf-8") as f:
				results = json.load(f)
		except:
			pass

	domains = [d for d in all_domains if d not in results]
	total_domains = len(domains)
	print(f"Domains to process: {total_domains} (remaining of {len(all_domains)})")
	if total_domains == 0:
		print("Nothing to process. output.json already has all domains.")
		return

	max_workers = 6
	print(f"Starting ThreadPoolExecutor with {max_workers} workers...")
	
	completed = 0
	
	with ThreadPoolExecutor(max_workers=max_workers) as executor:
		futures = {executor.submit(profile_domain, domain, parsed_technologies, global_js_props, global_dom_selectors): domain for domain in domains}
		for future in tqdm(as_completed(futures), total=total_domains, desc="Profiling"):
			domain, detected = future.result()
			results[domain] = detected
			completed += 1
			# Incremental save
			if completed % 5 == 0:
				with open("output.json", "w", encoding="utf-8") as f:
					json.dump(results, f, indent=4)
				
	with open("output.json", "w", encoding="utf-8") as f:
		json.dump(results, f, indent=4)

	print("\n\nProfiling complete. Results saved to output.json")

if __name__ == "__main__":
	main()
