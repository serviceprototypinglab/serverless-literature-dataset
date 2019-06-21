#!/usr/bin/env python3

import json
import operator
import glob
import os

prefix = "serverless"
basefiles = glob.glob("*-literature-base.json")
if len(basefiles) == 1:
	prefix = os.path.basename(basefiles[0]).split("-")[0]

analysis_filename = "{}-literature-analysis.json".format(prefix)
biblio_filename = "{}-literature-bibliography.json".format(prefix)
tech_filename = "{}-literature-technologies.json".format(prefix)

f = open(biblio_filename)
biblio = json.load(f)

f = open(analysis_filename)
analysis = json.load(f)

f = open(tech_filename)
tech = json.load(f)

years = {}
for ident in biblio:
	y = biblio[ident]["year"]
	years[y] = years.get(y, 0) + 1

countries = {}
technologies = {}
dtechnologies = {}
for ident in analysis:
	cs = analysis[ident]["countries"]
	for c in cs:
		countries[c] = countries.get(c, 0) + 1
	ts = analysis[ident]["technologies"]
	for t in ts:
		technologies[t] = technologies.get(t, 0) + 1
		if not analysis[ident]["independent"]:
			dtechnologies[t] = dtechnologies.get(t, 0) + 1

academic = 0
industry = 0
both = 0
for ident in analysis:
	a = analysis[ident]["academic"]
	i = analysis[ident]["industry"]
	if a and i:
		both += 1
	elif a:
		academic += 1
	elif i:
		industry += 1
r_academic = academic / len(analysis)
r_industry = industry / len(analysis)
r_both = both / len(analysis)

instmult = []
instuniq = set()
for ident in analysis:
	insts = analysis[ident]["institutions"]
	for inst in insts:
		instmult.append(inst)
		instuniq.add(inst)

def searchkeys(dl, keys_list):
	if isinstance(dl, dict):
		keys_list += dl.keys()
		list(map(lambda x: searchkeys(x, keys_list), list(dl.values())))
	elif isinstance(dl, list):
		list(map(lambda x: searchkeys(x, keys_list), dl))

numkeys = 0
jsonfiles = glob.glob("*.json")
for jsonfile in jsonfiles:
	f = open(jsonfile)
	entries = json.load(f)
	keys = []
	searchkeys(entries, keys)
	numkeys += len(keys)

allsorted = lambda x, *y: sorted(x.items(), key=operator.itemgetter(*y), reverse=True)

f = open("stats.txt", "w")
print("Years:", allsorted(years, 0), file=f)
print("Number of countries:", len(countries), file=f)
print("Countries:", allsorted(countries, 1, 0), file=f)
print("Ratio academic to industry to both:", academic, ":", industry, ":", both, "=", r_academic, r_industry, r_both, file=f)
print("Number of institutions:", len(instmult) / len(analysis), "per paper;", len(instuniq), "involved in total", file=f)
print("Number of technologies:", len(tech), "; open source:", len([x for x in tech if tech[x]["open-source"]]), file=f)
print("Technologies:", allsorted(technologies, 1, 0), file=f)
print("Technology by authors:", allsorted(dtechnologies, 1, 0), file=f)
print("JSON keys: {}".format(numkeys), file=f)
f.close()

print("Written stats to stats.txt.")
