#!/usr/bin/env python3

import json
import datetime

biblio_filename = "serverless-literature-bibliography.json"

f = open(biblio_filename)
biblio = json.load(f)
biblio_sorted = {int(x) : biblio[x] for x in biblio}

print("# Serverless Literature Dataset - BibTeX export - {}".format(str(datetime.datetime.now())))
print("# Master source: https://doi.org/10.5281/zenodo.1175423 (https://zenodo.org/record/1436432 or later)")
print()

for bibkey, bib in biblio_sorted.items():
	entrytype = "article"
	if "booktitle" in bib:
		entrytype = "inproceedings"
	print("@{}{{SLD_{},".format(entrytype, bibkey))
	print(" title   = {{{{{}}}}},".format(bib["title"]))
	print(" author  = {{{}}},".format(bib["author"]))
	if "journal" in bib:
		print(" journal = {{{}}},".format(bib["journal"]))
	else:
		print(" booktitle = {{{}}},".format(bib["booktitle"]))
	print(" year    = {{{}}},".format(bib["year"]))
	print("}")
