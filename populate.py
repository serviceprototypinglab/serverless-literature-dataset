#!/usr/bin/env python3
#
# Populate the file 'serverless-literature-bibliography.json' based on
# DOI information from 'serverless-literature-base.json'. Includes
# enforced pauses to prevent load spikes on the DOI servers.
# Syntax:
# python3 populate.py          # complement entries
# python3 populate.py --forced # overwrite entries

import json
import os
import urllib.request
import pybtex.database
import sys
import time

base_filename = "serverless-literature-base.json"
biblio_filename = "serverless-literature-bibliography.json"

forced = False
if len(sys.argv) == 2 and sys.argv[1] == "--forced":
	forced = True

def populate_bibliography(base_filename, biblio_filename, forced):
	f = open(base_filename)
	literature = json.load(f)

	if os.path.isfile(biblio_filename):
		f = open(biblio_filename)
		biblio = json.load(f)
	else:
		biblio = {}

	header = {}
	header["Accept"] = "application/x-bibtex"
	header["User-Agent"] = "serverless-literature-database (Python-urllib/3.x)"

	header2 = header.copy()
	header2["Accept"] = "text/bibliography; style=bibtex"

	for ident in sorted(literature):
		if not "doi" in literature[ident]:
			if ident in biblio and "title" in biblio[ident]:
				print("## work {} has no doi but a manual entry".format(ident))
			else:
				print("!! work {} has no doi".format(ident))
			continue
		if not ident in biblio or forced:
			doi = literature[ident]["doi"]
			print("Retrieving {}: {}".format(ident, doi))
			req = urllib.request.Request(doi, headers=header)
			res = urllib.request.urlopen(req)
			bib = res.read().decode("utf-8")
			db = pybtex.database.parse_string(bib, "bibtex")
			req = urllib.request.Request(doi, headers=header2)
			res = urllib.request.urlopen(req)
			bib = res.read().decode("utf-8")
			db2 = pybtex.database.parse_string(bib, "bibtex")
			for entry in db.entries:
				ft = db2.entries[entry].fields["title"]
				fa = db2.entries[entry].fields["author"]
				fy = db2.entries[entry].fields["year"]
				fb = None
				fj = None
				if "journal" in db.entries[entry].fields:
					fj = db2.entries[entry].fields["journal"]
				elif "booktitle" in db.entries[entry].fields:
					fb = db2.entries[entry].fields["journal"]
				biblio[ident] = {}
				biblio[ident]["title"] = ft
				biblio[ident]["author"] = fa
				biblio[ident]["year"] = fy
				if fj:
					biblio[ident]["journal"] = fj
				if fb:
					biblio[ident]["booktitle"] = fb
				biblio[ident]["retrieved-from-doi"] = doi
				print("- Updated '{}'".format(ft))
			time.sleep(5)

	f = open(biblio_filename, "w")
	biblio_sorted = {int(x) : biblio[x] for x in biblio}
	json.dump(biblio_sorted, f, indent=2, ensure_ascii=False, sort_keys=True)
	f.close()

	return biblio

def check_consistency(biblio):
	allkeys = [int(x) for x in biblio]
	allkeys.sort()
	if allkeys[-1] != len(allkeys):
		print("!! Inconsistency: keys={}".format(allkeys))
	dois = {}
	for x in sorted(biblio):
		if "retrieved-from-doi" in biblio[x]:
			if not biblio[x]["retrieved-from-doi"] in dois:
				dois[biblio[x]["retrieved-from-doi"]] = x
			else:
				print("!! Inconsistency: keys={}/{} for doi {}".format(x, dois[biblio[x]["retrieved-from-doi"]], biblio[x]["retrieved-from-doi"]))

biblio = populate_bibliography(base_filename, biblio_filename, forced)
check_consistency(biblio)

print("Statistics:")
print("- {} entries".format(len(biblio)))
print("- {}% manual entries".format(round(100 * len([x for x in biblio if not "retrieved-from-doi" in biblio[x]]) / len(biblio))))
