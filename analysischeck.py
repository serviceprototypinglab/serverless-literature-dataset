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
	pairedkeys = []
	for key in bibliokeys:
		if not key in biblio[ident] and not key in pairedkeys:
			pairs = [("journal", "booktitle"), ("retrieved-from-doi", "retrieved-from-arxiv", "link")]
			ispaired = False
			for pair in pairs:
				for x in range(len(pair)):
					for y in range(len(pair)):
						if key == pair[x]:
							if pair[y] in biblio[ident]:
								ispaired = True
							else:
								pairedkeys += pair
								key = pair
			if not ispaired:
				print("!! work {} misses key {} in bibliography".format(ident, key))
	for t in analysis[ident]["technologies"]:
		if not t in tech:
			print("!! technology {} not described with metadata".format(t))
for ident in tech:
	for key in techkeys:
		if not key in tech[ident]:
			print("!! technology {} misses key {}".format(ident, key))
