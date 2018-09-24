#!/usr/bin/env python3

import json
import operator

analysis_filename = "serverless-literature-analysis.json"
biblio_filename = "serverless-literature-bibliography.json"

f = open(biblio_filename)
biblio = json.load(f)

f = open(analysis_filename)
analysis = json.load(f)

years = {}
for ident in biblio:
	y = biblio[ident]["year"]
	years[y] = years.get(y, 0) + 1

countries = {}
for ident in analysis:
	cs = analysis[ident]["countries"]
	for c in cs:
		countries[c] = countries.get(c, 0) + 1

academic = 0
for ident in analysis:
	a = analysis[ident]["academic"]
	if a:
		academic += 1

instmult = []
instuniq = set()
for ident in analysis:
	insts = analysis[ident]["institutions"]
	for inst in insts:
		instmult.append(inst)
		instuniq.add(inst)

allsorted = lambda x, y: sorted(x.items(), key=operator.itemgetter(y), reverse=True)

f = open("stats.txt", "w")
print("Years:", allsorted(years, 0), file=f)
print("Countries:", allsorted(countries, 1), file=f)
print("Ratio academic to industry:", academic, ":", len(analysis) - academic, "=", academic / len(analysis), file=f)
print("Number of institutions:", len(instmult) / len(analysis), "per paper;", len(instuniq), "involved in total", file=f)
f.close()

print("Written stats to stats.txt.")
