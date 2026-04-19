import json
from collections import Counter

def main():
	try:
		with open("output.json", "r", encoding="utf-8") as f:
			data = json.load(f)
	except FileNotFoundError:
		print("Error: output.json not found.")
		return
		
	tech_counter = Counter()
	total_domains = len(data)
	domains_with_tech = 0
	total_detections = 0
	
	for domain, techs in data.items():
		if techs:
			domains_with_tech += 1
			for tech in techs:
				tech_counter[tech] += 1
				total_detections += 1
				
	print(f"{"="*40}")
	print(f"		Technology Profiler Analytics")
	print(f"{"="*40}")
	print(f"Total Domains Profiled : {total_domains}")
	print(f"Domains w/ Detections  : {domains_with_tech} ({(domains_with_tech/total_domains)*100 if total_domains else 0:.1f}%)")
	print(f"Total Individual Hits  : {total_detections}")
	print(f"Unique Technologies    : {len(tech_counter)}")
	print(f"{"="*40}")

if __name__ == "__main__":
	main()
