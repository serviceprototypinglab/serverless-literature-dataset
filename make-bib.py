#!/usr/bin/env python3

import json
import datetime

biblio_filename = "serverless-literature-bibliography.json"

f = open(biblio_filename)
biblio = json.load(f)

print("# Serverless Literature Dataset - BibTeX export - {}".format(str(datetime.datetime.now())))
print("# https://zenodo.org/record/1175424")
print()

for bibkey, bib in biblio.items():
	print("@article{{SLR_{},".format(bibkey))
	print(" title   = {{{{{}}}}},".format(bib["title"]))
	print(" author  = {{{}}},".format(bib["author"]))
	print(" journal = {{{}}},".format(bib["journal"]))
	print(" year    = {{{}}},".format(bib["year"]))
	print("}")
