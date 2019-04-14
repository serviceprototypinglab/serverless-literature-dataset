#!/usr/bin/env python3

import json

analysis_filename = "serverless-literature-analysis.json"
biblio_filename = "serverless-literature-bibliography.json"
tech_filename = "serverless-literature-technologies.json"

f = open(biblio_filename)
biblio = json.load(f)

f = open(analysis_filename)
analysis = json.load(f)

f = open(tech_filename)
tech = json.load(f)

techkeys = []
bibliokeys = []
allkeys = []
for ident in analysis:
	if not ident in biblio:
		print("!! work {} in analysis but not present in bibliography".format(ident))
	for key in analysis[ident].keys():
		if not key in allkeys:
			allkeys.append(key)
for ident in biblio:
	for key in biblio[ident].keys():
		if not key in bibliokeys:
			bibliokeys.append(key)
for ident in tech:
	for key in tech[ident].keys():
		if not key in techkeys:
			techkeys.append(key)

print("Check {} entries for keys: {} and {} (and {})".format(len(biblio), bibliokeys, allkeys, techkeys))

for ident in biblio:
	if not ident in analysis:
		print("!! work {} missing in analysis".format(ident))
		print("- {}".format(biblio[ident]["title"]))
		continue
	for key in allkeys:
		if not key in analysis[ident]:
			print("!! work {} misses key {} in analysis".format(ident, key))
	for key in bibliokeys:
		if not key in biblio[ident]:
			pairs = [("journal", "booktitle"), ("retrieved-from-doi", "link")]
			ispaired = False
			for pair in pairs:
				if key == pair[0] and pair[1] in biblio[ident]:
					ispaired = True
				if key == pair[1] and pair[0] in biblio[ident]:
					ispaired = True
			if not ispaired:
				print("!! work {} misses key {} in bibliography".format(ident, key))
	for t in analysis[ident]["technologies"]:
		if not t in tech:
			print("!! technology {} not described with metadata".format(t))
for ident in tech:
	for key in techkeys:
		if not key in tech[ident]:
			print("!! technology {} misses key {}".format(ident, key))
