#!/usr/bin/env python3

import json
import random
import os

base_filename = "serverless-literature-base.json"
analysis_filename = "serverless-literature-analysis.json"
biblio_filename = "serverless-literature-bibliography.json"
tech_filename = "serverless-literature-technologies.json"

f = open(base_filename)
base = json.load(f)

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

filename_tech = "/tmp/sldgraph-tech.dot"
f = open(filename_tech, "w")

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
			shape = ",shape=box,style=filled,fillcolor=\"#{}\"".format(color)
		print("{} [label=\"{}\"{}];".format(rid, xids[rid], shape), file=f)
print("}", file=f)
f.close()

filename_bib = "/tmp/sldgraph-bib.dot"
f = open(filename_bib, "w")
print("digraph sldgraph {", file=f)
print("overlap=false;", file=f)
for ident in sorted(authorworks):
	for author in authorworks[ident]:
		print("{} -> {};".format(xid(author, xids), xid(ident, xids)), file=f)
for rid in xids:
	if rid.startswith("_") and not xids[rid] in tech:
		shape = ""
		if xids[rid] in biblio:
			color = "a0ffa0"
			shape = ",shape=box,style=filled,fillcolor=\"#{}\"".format(color)
			if "correlation" in base[xids[rid]]:
				color = "d00000"
				print("{} -> {} [style=dotted,color=\"#{}\"];".format(rid, xids[base[xids[rid]]["correlation"]], color), file=f)
		print("{} [label=\"{}\"{}];".format(rid, xids[rid], shape), file=f)
print("}", file=f)
f.close()

xids = {}
filename_country = "/tmp/sldgraph-country.dot"
f = open(filename_country, "w")
print("digraph sldgraph {", file=f)
print("overlap=false;", file=f)
for ident in analysis:
	for country in analysis[ident]["countries"]:
		print("{} -> {};".format(xid(ident, xids), xid(country, xids)), file=f)
for rid in xids:
	if rid.startswith("_"):
		shape = ""
		if not xids[rid] in analysis:
			color = "80d0e0"
			shape = ",shape=box,style=filled,fillcolor=\"#{}\"".format(color)
		print("{} [label=\"{}\"{}];".format(rid, xids[rid], shape), file=f)
print("}", file=f)
f.close()

# TODO: "pos" attributes (https://www.graphviz.org/doc/info/attrs.html#d:pos) to prepare worldmap...
xids = {}
filename_inst = "/tmp/sldgraph-inst.dot"
f = open(filename_inst, "w")
print("digraph sldgraph {", file=f)
print("overlap=false;", file=f)
for ident in analysis:
	for inst in analysis[ident]["institutions"]:
		print("{} -> {};".format(xid(ident, xids), xid(inst, xids)), file=f)
for rid in xids:
	if rid.startswith("_"):
		shape = ""
		if not xids[rid] in analysis:
			color = "d0e080"
			shape = ",shape=box,style=filled,fillcolor=\"#{}\"".format(color)
		print("{} [label=\"{}\"{}];".format(rid, xids[rid], shape), file=f)
print("}", file=f)
f.close()

xids = {}
filename_fields = "/tmp/sldgraph-fields.dot"
f = open(filename_fields, "w")
print("digraph sldgraph {", file=f)
print("overlap=false;", file=f)
for ident in analysis:
	if "fields" in analysis[ident]:
		for field in analysis[ident]["fields"]:
			print("{} -> {};".format(xid(ident, xids), xid(field, xids)), file=f)
for rid in xids:
	if rid.startswith("_"):
		shape = ""
		if not xids[rid] in analysis:
			color = "60b0ff"
			shape = ",shape=box,style=filled,fillcolor=\"#{}\"".format(color)
		print("{} [label=\"{}\"{}];".format(rid, xids[rid], shape), file=f)
print("}", file=f)
f.close()

for filename in (filename_tech, filename_bib, filename_country, filename_inst, filename_fields):
	# engines: twopi, sfdp, ...
	engine = "sfdp"
	cmd = "{} -Tpdf {} > {}".format(engine, filename, filename + ".pdf")
	os.system(cmd)
	print("Graph: {}".format(filename + ".pdf"))
	print("(Scale: pdfposter -p2x2a4 {}.pdf {}.print.pdf)".format(filename, filename))
