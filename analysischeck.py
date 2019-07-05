#!/usr/bin/env python3

import json
import glob
import os
import sys

prefix = "serverless"
basefiles = glob.glob("*-literature-base.json")
if len(basefiles) == 1:
	prefix = os.path.basename(basefiles[0]).split("-")[0]

analysis_filename = "{}-literature-analysis.json".format(prefix)
biblio_filename = "{}-literature-bibliography.json".format(prefix)
tech_filename = "{}-literature-technologies.json".format(prefix)

f = open(biblio_filename)
biblio = json.load(f)

try:
	f = open(analysis_filename)
	analysis = json.load(f)
except:
	print("Warning: analysis file {} not found, generated".format(analysis_filename), file=sys.stderr)
	analysis = {}

	for ident in biblio:
		analysis[ident] = {}
		for lk in ("technologies", "institutions", "countries", "nature", "fields"):
			analysis[ident][lk] = []
		for bk in ("academic", "industry", "independent"):
			analysis[ident][bk] = False
		analysis[ident]["format"] = ""
		analysis[ident]["citations"] = 0

	f = open(analysis_filename, "a")
	analysis_sorted = {int(x) : analysis[x] for x in analysis}
	json.dump(analysis_sorted, f, indent=2, ensure_ascii=False, sort_keys=True)
	f.close()

try:
	f = open(tech_filename)
	tech = json.load(f)
except:
	print("Warning: tech file {} not found, generated".format(tech_filename), file=sys.stderr)
	tech = {}

	for ident in biblio:
		tech[ident] = {}
		tech[ident]["open-source"] = False
		tech[ident]["link"] = ""
		tech[ident]["actively-maintained"] = ""
		tech[ident]["supported-languages"] = []

	f = open(tech_filename, "a")
	tech_sorted = {int(x) : tech[x] for x in tech}
	json.dump(tech_sorted, f, indent=2, ensure_ascii=False, sort_keys=True)
	f.close()

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

biblio_sorted = {int(x) : biblio[x] for x in biblio}
for ident in biblio_sorted:
	ident = str(ident)
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
			pairs = [("journal", "booktitle"), ("retrieved-from-doi", "retrieved-from-arxiv", "retrieved-from-usenix", "link")]
			ispaired = False
			for pair in pairs:
				for x in range(len(pair)):
					if key == pair[x]:
						for y in range(len(pair)):
							if pair[y] in biblio[ident]:
								ispaired = True
						if not ispaired:
							pairedkeys += pair
							key = pair
			if not ispaired:
				print("!! work {} misses key {} in bibliography".format(ident, key))
	if "technologies" in analysis[ident]:
		for t in analysis[ident]["technologies"]:
			if not t in tech:
				print("!! technology {} not described with metadata".format(t))
for ident in tech:
	for key in techkeys:
		if not key in tech[ident]:
			if key == "link" and not tech[ident]["open-source"]:
				continue
			print("!! technology {} misses key {}".format(ident, key))
