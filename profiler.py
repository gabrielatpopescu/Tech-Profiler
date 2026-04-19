import os
import json
import re
from typing import Dict, Any, List, Optional, Callable, Pattern, Union, Set

def load_technologies(tech_dir: str) -> Dict[str, Dict[str, Any]]:
    technologies: Dict[str, Any] = {}
    for file in os.listdir(tech_dir):
        if file.endswith('.json'):
            with open(os.path.join(tech_dir, file), 'r', encoding='utf-8') as f:
                data = json.load(f)
                technologies.update(data)
    
    parsed_technologies: Dict[str, Dict[str, Any]] = {}
    for tech_name, rules in technologies.items():
        parsed_technologies[tech_name] = parse_rules(rules)
    return parsed_technologies
            
def parse_rules(rules: Dict[str, Any]) -> Dict[str, Any]:
    parsed: Dict[str, Any] = {}
    
    def clean_regex(pattern_str: Any) -> str:
        if not isinstance(pattern_str, str):
            return str(pattern_str)
        parts = pattern_str.split('\\;')
        return parts[0]

    def compile_regex(pattern_str: Any) -> Optional[Pattern[str]]:
        if not pattern_str:
            return None
        cleaned = clean_regex(pattern_str)
        try:
            return re.compile(cleaned, re.IGNORECASE)
        except re.error:
            return None

    def compile_pattern_list(raw_rules: Union[str, List[Any], None]) -> List[Pattern[str]]:
        if raw_rules is None:
            return []
        values = raw_rules if isinstance(raw_rules, list) else [raw_rules]
        compiled: List[Pattern[str]] = []
        for value in values:
            regex = compile_regex(value)
            if regex:
                compiled.append(regex)
        return compiled

    def compile_keyed_rules(raw_rules: Dict[str, Any]) -> Dict[str, List[Pattern[str]]]:
        compiled_rules: Dict[str, List[Pattern[str]]] = {}
        for key, value in raw_rules.items():
            compiled_rules[str(key).lower()] = compile_pattern_list(value)
        return compiled_rules

    if 'headers' in rules:
        parsed['headers'] = compile_keyed_rules(rules['headers'])
            
    if 'meta' in rules:
        parsed['meta'] = compile_keyed_rules(rules['meta'])
            
    if 'cookies' in rules:
        parsed['cookies'] = compile_keyed_rules(rules['cookies'])

    if 'html' in rules:
        parsed['html'] = compile_pattern_list(rules['html'])

    if 'scriptSrc' in rules:
        parsed['scriptSrc'] = compile_pattern_list(rules['scriptSrc'])

    if 'url' in rules:
        parsed['url'] = compile_pattern_list(rules['url'])

    if 'xhr' in rules:
        parsed['xhr'] = compile_pattern_list(rules['xhr'])

    if 'text' in rules:
        parsed['text'] = compile_pattern_list(rules['text'])
        
    if 'scripts' in rules:
        parsed['scripts'] = compile_pattern_list(rules['scripts'])
        
    if 'js' in rules:
        parsed['js'] = compile_keyed_rules(rules['js'])
        
    if 'dom' in rules:
        dom_rule = rules['dom']
        parsed_dom: Dict[str, Any] = {}
        if isinstance(dom_rule, str):
            parsed_dom[dom_rule] = {"exists": True}
        elif isinstance(dom_rule, list):
            for s in dom_rule:
                parsed_dom[str(s)] = {"exists": True}
        elif isinstance(dom_rule, dict):
            for selector, s_rules in dom_rule.items():
                parsed_selector: Dict[str, Any] = {}
                if isinstance(s_rules, str):
                    parsed_selector["text"] = compile_pattern_list(s_rules)
                elif isinstance(s_rules, list):
                    parsed_selector["text"] = compile_pattern_list(s_rules)
                elif isinstance(s_rules, dict):
                    if not s_rules:
                        parsed_selector["exists"] = True
                    if "text" in s_rules:
                        parsed_selector["text"] = compile_pattern_list(s_rules["text"])
                    if "attributes" in s_rules:
                        parsed_selector["attributes"] = compile_keyed_rules(s_rules["attributes"])
                    if "properties" in s_rules:
                        parsed_selector["properties"] = compile_keyed_rules(s_rules["properties"])
                parsed_dom[str(selector)] = parsed_selector
        parsed['dom'] = parsed_dom
        
    if 'css' in rules:
        parsed['css'] = compile_pattern_list(rules['css'])
        
    if 'robots' in rules:
        parsed['robots'] = compile_pattern_list(rules['robots'])
        
    if 'dns' in rules:
        parsed['dns'] = compile_keyed_rules(rules['dns'])
        
    if 'certIssuer' in rules:
        parsed['certIssuer'] = compile_pattern_list(rules['certIssuer'])
        
    def clean_dep(dep: Any) -> str:
        return str(dep).split('\\;')[0]
        
    for dep_key in ['implies', 'requires', 'excludes']:
        if dep_key in rules:
            parsed[dep_key] = [clean_dep(r) for r in (rules[dep_key] if isinstance(rules[dep_key], list) else [rules[dep_key]])]

    return parsed

def profile(
    html: str, 
    headers: Dict[str, str], 
    cookies: List[Dict[str, str]], 
    script_srcs: List[str], 
    meta_tags: Dict[str, str], 
    js_values: Dict[str, Any],
    dom_values: Dict[str, Any],
    scripts_contents: List[str],
    parsed_technologies: Dict[str, Dict[str, Any]],
    page_url: str = "",
    xhr_urls: Optional[List[str]] = None,
    css_content: str = "",
    robots_text: str = "",
    dns_records: Optional[Dict[str, List[str]]] = None,
    cert_issuer: str = "",
) -> List[str]:
    if html and len(html) > 500000:
        html = html[:500000]

    detected: Set[str] = set()
    
    headers_lower: Dict[str, str] = {str(k).lower(): str(v) for k, v in headers.items()}
    cookies_lower: Dict[str, str] = {str(c['name']).lower(): str(c.get('value', '')) for c in cookies if 'name' in c}
    meta_lower: Dict[str, str] = {str(k).lower(): str(v) for k, v in meta_tags.items()}
    xhr_values = xhr_urls or []
    dns_values = dns_records or {}
    dns_lower: Dict[str, str] = {str(k).lower(): '\n'.join(v) for k, v in dns_values.items()}

    def keyed_match(source: Dict[str, str], key_patterns: Dict[str, List[Pattern[str]]]) -> bool:
        for key, patterns in key_patterns.items():
            if key not in source:
                continue
            if not patterns:
                return True
            value = source[key]
            if any(pattern.search(value) for pattern in patterns):
                return True
        return False

    def list_match(values: List[str], patterns: List[Pattern[str]]) -> bool:
        if not values or not patterns:
            return False
        for pattern in patterns:
            for value in values:
                if pattern.search(value):
                    return True
        return False

    html_text: Optional[str] = None
    
    for tech_name, rules in parsed_technologies.items():
        found = False
        
        if not found and 'headers' in rules:
            found = keyed_match(headers_lower, rules['headers'])

        if not found and 'cookies' in rules:
            found = keyed_match(cookies_lower, rules['cookies'])

        if not found and 'meta' in rules:
            found = keyed_match(meta_lower, rules['meta'])

        if not found and 'html' in rules:
            for regex in rules['html']:
                if regex.search(html):
                    found = True
                    break

        if not found and 'scriptSrc' in rules:
            found = list_match(script_srcs, rules['scriptSrc'])

        if not found and 'url' in rules and page_url:
            for regex in rules['url']:
                if regex.search(page_url):
                    found = True
                    break

        if not found and 'xhr' in rules:
            found = list_match(xhr_values, rules['xhr'])

        if not found and 'text' in rules:
            if html_text is None:
                html_text = re.sub(r"<[^>]+>", " ", html[:300000] if html else "")
            for regex in rules['text']:
                if regex.search(html_text):
                    found = True
                    break

        if not found and 'scripts' in rules:
            found = list_match(scripts_contents, rules['scripts'])

        if not found and 'js' in rules:
            js_rules: Dict[str, List[Pattern[str]]] = rules['js']
            for prop, patterns in js_rules.items():
                if prop not in js_values or js_values[prop] is None:
                    continue
                val = str(js_values[prop])
                if not patterns:
                    found = True
                    break
                if any(p.search(val) for p in patterns):
                    found = True
                    break

        if not found and 'dom' in rules:
            dom_rules: Dict[str, Dict[str, Any]] = rules['dom']
            for selector, s_rules in dom_rules.items():
                if selector not in dom_values:
                    continue
                extracted: Dict[str, Any] = dom_values[selector]
                
                if s_rules.get("exists") and extracted.get("exists"):
                    found = True
                    break
                
                if "text" in s_rules and "text" in extracted:
                    if list_match(extracted["text"], s_rules["text"]):
                        found = True
                        break
                        
                if "attributes" in s_rules and "attributes" in extracted:
                    for attr_name, attr_patterns in s_rules["attributes"].items():
                        vals = extracted["attributes"].get(attr_name, [])
                        if list_match(vals, attr_patterns):
                            found = True
                            break
                    if found: break
                
                if "properties" in s_rules and "properties" in extracted:
                    for prop_name, prop_patterns in s_rules["properties"].items():
                        vals = extracted["properties"].get(prop_name, [])
                        if list_match(vals, prop_patterns):
                            found = True
                            break
                    if found: break

        if not found and 'css' in rules and css_content:
            for regex in rules['css']:
                if regex.search(css_content):
                    found = True
                    break

        if not found and 'robots' in rules and robots_text:
            for regex in rules['robots']:
                if regex.search(robots_text):
                    found = True
                    break

        if not found and 'dns' in rules:
            if keyed_match(dns_lower, rules['dns']):
                found = True

        if not found and 'certIssuer' in rules and cert_issuer:
            for regex in rules['certIssuer']:
                if regex.search(cert_issuer):
                    found = True
                    break

        if found:
            detected.add(tech_name)
            
    # Resolve requires/implies/excludes
    changed = True
    while changed:
        changed = False
        for tech in list(detected):
            tech_rules = parsed_technologies.get(tech, {})
            # requires logic (remove if required not present)
            if 'requires' in tech_rules:
                has_req = any(str(req) in detected for req in tech_rules['requires'])
                if not has_req:
                    detected.remove(tech)
                    changed = True
                    continue # Removed, don't cascade implies
                    
            if 'implies' in tech_rules:
                for imp in tech_rules['implies']:
                    imp_str = str(imp)
                    if imp_str not in detected:
                        detected.add(imp_str)
                        changed = True

    # Final excludes filtering
    final_detected = set(detected)
    for tech in list(final_detected):
        tech_rules = parsed_technologies.get(tech, {})
        if 'excludes' in tech_rules:
            for exc in tech_rules['excludes']:
                exc_str = str(exc)
                if exc_str in final_detected:
                    final_detected.discard(exc_str)

    return list(final_detected)
