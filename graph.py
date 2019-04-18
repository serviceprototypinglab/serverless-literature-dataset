#!/usr/bin/env python3

import json
import random
import os

analysis_filename = "serverless-literature-analysis.json"
biblio_filename = "serverless-literature-bibliography.json"
tech_filename = "serverless-literature-technologies.json"

f = open(biblio_filename)
biblio = json.load(f)

f = open(analysis_filename)
analysis = json.load(f)

f = open(tech_filename)
tech = json.load(f)

debug = False

authorworks = {}
for ident in sorted(biblio):
	authors = biblio[ident]["author"].replace("\xa0", " ")
	cc = authors.count(",")
	ac = authors.count("and ")
	noswap = False
	nosplit = False
	anom = False
	if not (cc == ac + 1 and ac > 0) and not cc == ac:
		anom = True
		if ac == 0:
			noswap = True
		elif cc == 0:
			nosplit = True
		elif debug:
			print("ANOM:", ident, authors, cc, ac)
	if noswap:
		authors = authors.split(", ")
	else:
		authors = authors.split(" and ")
	for idx, author in enumerate(authors):
		if "," in author:
			n = author.split(", ")
			authors[idx] = n[1] + " " + n[0]
		if not ident in authorworks:
			authorworks[ident] = []
		authorworks[ident].append(authors[idx])
	if anom and debug and not noswap and not nosplit:
		print(anom, authorworks[ident])

def xid(s, xids):
	while not s in xids:
		rid = "_S" + str(random.randrange(10000, 100000))
		if not rid in xids:
			xids[rid] = s
			xids[s] = rid
			return rid
	return xids[s]

filename = "/tmp/sldgraph.dot"
f = open(filename, "w")
	
xids = {}
print("digraph sldgraph {", file=f)
print("overlap=false;", file=f)
for ident in sorted(analysis):
	for t in analysis[ident]["technologies"]:
		for author in authorworks[ident]:
			print("{} -> {};".format(xid(author, xids), xid(t, xids)), file=f)
for rid in xids:
	if rid.startswith("_"):
		shape = ""
		if xids[rid] in tech:
			color = "e0e0ff"
			if tech[xids[rid]]["open-source"]:
				color = "ffe0e0"
			shape=",shape=box,style=filled,fillcolor=\"#{}\"".format(color)
		print("{} [label=\"{}\"{}];".format(rid, xids[rid], shape), file=f)
print("}", file=f)
f.close()

# engines: twopi, sfdp, ...
engine = "sfdp"
cmd = "{} -Tpdf {} > {}".format(engine, filename, filename + ".pdf")
os.system(cmd)
print("Graph: {}".format(filename + ".pdf"))
