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
import xml.dom.minidom

def parsearxiv(arxivid):
	header = {}
	header["User-Agent"] = "serverless-literature-database (Python-urllib/3.x)"

	arxivid = arxivid.split("/")[-1]
	req = urllib.request.Request("http://export.arxiv.org/api/query?id_list=" + arxivid, headers=header)
	res = urllib.request.urlopen(req)
	arxivmeta = res.read().decode("utf-8")
	
	doc = xml.dom.minidom.parseString(arxivmeta)
	feed = doc.documentElement
	entries = feed.getElementsByTagName("entry")
	if len(entries) == 1:
		title = entries[0].getElementsByTagName("title")[0].childNodes[0].nodeValue.replace("\n", "").replace("  ", " ")
		date = entries[0].getElementsByTagName("published")[0].childNodes[0].nodeValue
		year = date[:4]
		author = entries[0].getElementsByTagName("author")[0]
		names = [x.childNodes[0].nodeValue for x in author.getElementsByTagName("name")]
		return title, year, ", ".join(names)

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
		if not "doi" in literature[ident] and not "arxiv" in literature[ident]:
			if ident in biblio and "title" in biblio[ident]:
				print("## work {} has no DOI/arXiv but a manual entry".format(ident))
			else:
				print("!! work {} has no DOI/arXiv".format(ident))
			continue
		if not ident in biblio or forced:
			if "doi" in literature[ident]:
				doi = literature[ident]["doi"]
				print("Retrieving {}: DOI {}".format(ident, doi))
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
			elif "arxiv" in literature[ident]:
				arxivid = literature[ident]["arxiv"]
				print("Retrieving {}: arXiv {}".format(ident, arxivid))
				ft, fy, fa = parsearxiv(arxivid)
				biblio[ident] = {}
				biblio[ident]["title"] = ft
				biblio[ident]["author"] = fa
				biblio[ident]["year"] = fy
				biblio[ident]["journal"] = "arXiv/CoRR"
				biblio[ident]["retrieved-from-arxiv"] = arxivid
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
				print("!! Inconsistency: keys={}/{} for DOI {}".format(x, dois[biblio[x]["retrieved-from-doi"]], biblio[x]["retrieved-from-doi"]))

biblio = populate_bibliography(base_filename, biblio_filename, forced)
check_consistency(biblio)

filterlist_doi = [x for x in biblio if "retrieved-from-doi" in biblio[x]]
percent_doi = round(100 * len(filterlist_doi) / len(biblio))
filterlist_arxiv = [x for x in biblio if "retrieved-from-arxiv" in biblio[x]]
percent_arxiv = round(100 * len(filterlist_arxiv) / len(biblio))

print("Statistics:")
print("- {} entries in total".format(len(biblio)))
print("- {}% DOI entries".format(percent_doi))
print("- {}% arXiv entries".format( percent_arxiv))
print("- {}% manual entries".format(100 - percent_arxiv - percent_doi))
