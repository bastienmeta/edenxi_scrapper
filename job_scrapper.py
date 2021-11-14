import time
import json
import sys
from bs4 import BeautifulSoup
from selenium import webdriver


char_url=lambda name: "https://edenxi.com/tools/player/"+name

# parse html content to find jobs div content and build dictionnary
def parse_jobs_html(html):
	soup = BeautifulSoup(html, features="lxml")	
	jobs_div = soup.find_all("div", class_="eden_player-jobs")
	jobs_list = [t.text for t in jobs_div[0].findChildren("td", recursive=True)]
	crafts_list = [t.text for t in jobs_div[1].findChildren("td", recursive=True)]

	json = {}
	json["jobs"] = {}
	build_jobs_json(jobs_list, json["jobs"])
	json["crafts"] = {}
	build_jobs_json(crafts_list, json["crafts"])

	return json

# build dictionnary from a performatted list of jobs data
def build_jobs_json(jobs_data, json=dict({})):
	if len(jobs_data) == 0:
		return json
	json[jobs_data[0].replace(":","")] = jobs_data[1]
	data = build_jobs_json(jobs_data[2:], json)
	return data

# build csv character information from preformatted dict data
def format_csv(members_data, first_member, category):
	csv_txt = get_csv_columns(members_data, first_member, category)
	for m_name in members_data:
		csv_txt += get_csv_row(members_data, first_member, m_name, category)
	return csv_txt

# get columns of csv data row
def get_csv_columns(members_data, first_member, category):
	columns = members_data[first_member][category].keys()
	csv_col = "name,"
	for c in columns: csv_col += c+","
	csv_col += "\n"
	return csv_col

# get a full row of jobs data for a specific members fron json data
def get_csv_row(members_data, first_member, m_name, category):
	columns = members_data[first_member][category].keys()	
	member_jobs = members_data[m_name][category]
	csv_txt = m_name+","
	for c in columns:
		csv_txt += member_jobs[c]+","
	csv_txt += "\n"	
	return csv_txt

# usage: python3 job_scrapper.py input.txt output.json output.csv [csv_category]
if __name__ == "__main__":
	members_txt = sys.argv[1]
	output_json = sys.argv[2]
	output_csv = sys.argv[3]
	if len(sys.argv) < 5:
		csv_category = "jobs"
	else:
		csv_category = sys.argv[4]

	with open(members_txt, 'r') as f:
		members_list = f.read().split(",")

	member_data = {}

	for i,m_name in enumerate(members_list):
		options = webdriver.ChromeOptions()
		options.add_argument('headless')

		driver = webdriver.Chrome(options=options)
		driver.get(char_url(m_name))
		time.sleep(1)

		member_data[m_name] = parse_jobs_html(driver.page_source)

		if i == 0 :
			print(get_csv_columns(member_data, members_list[0], csv_category).replace(",", "\t"))
		print(get_csv_row(member_data, m_name, members_list[0], csv_category).replace(",", "\t"))

		# on reecrit tout, osef cest bon laaaa
		with open(output_json, "w") as f:
			json.dump(member_data, f, indent=4)

		with open(output_csv, "w") as f:
			f.write(format_csv(member_data, members_list[0], category=csv_category))

		driver.close()
	driver.quit()




