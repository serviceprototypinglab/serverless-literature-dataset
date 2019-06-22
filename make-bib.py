#!/usr/bin/env python3

import json
import datetime
import glob
import os

prefix = "serverless"
basefiles = glob.glob("*-literature-base.json")
if len(basefiles) == 1:
	prefix = os.path.basename(basefiles[0]).split("-")[0]

biblio_filename = "{}-literature-bibliography.json".format(prefix)

f = open(biblio_filename)
biblio = json.load(f)
biblio_sorted = {int(x) : biblio[x] for x in biblio}

print("# Structured '{}' Literature Dataset - BibTeX export - {}".format(prefix, str(datetime.datetime.now())))
print("# Master source: https://doi.org/10.5281/zenodo.1175423 (https://zenodo.org/record/1436432 or later)")
print()

char = prefix[0].upper()

for bibkey, bib in biblio_sorted.items():
	entrytype = "article"
	if "booktitle" in bib:
		entrytype = "inproceedings"
	print("@{}{{{}LD_{},".format(entrytype, char, bibkey))
	print(" title   = {{{{{}}}}},".format(bib["title"]))
	print(" author  = {{{}}},".format(bib["author"]))
	if "journal" in bib:
		print(" journal = {{{}}},".format(bib["journal"]))
	else:
		print(" booktitle = {{{}}},".format(bib["booktitle"]))
	print(" year    = {{{}}},".format(bib["year"]))
	print("}")
