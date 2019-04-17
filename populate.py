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
import re

def generateheaders():
	header = {}
	header["User-Agent"] = "serverless-literature-database (Python-urllib/3.x)"
	return header

def parseusenix(usenixurl):
	req = urllib.request.Request(usenixurl, headers=generateheaders())
	f = urllib.request.urlopen(req)
	html = f.read().decode()

	biblink = None
	lines = html.split("\n")
	for line in lines:
		if "export/bibtex" in line:
			m = re.search("href=\"([^\"]*)\"", line)
			biblink = "https://www.usenix.org/" + m.groups()[0]

	if not biblink:
		return None
	print("(Redirect: {})".format(biblink))
	return parseusenixbib(biblink)

def parseusenixbib(usenixbiburl):
	req = urllib.request.Request(usenixbiburl, headers=generateheaders())
	f = urllib.request.urlopen(req)
	bib = f.read().decode()
	db = pybtex.database.parse_string(bib, "bibtex")

	for entry in db.entries:
		ft = db.entries[entry].fields["title"].replace("{", "").replace("}", "")
		fa = db.entries[entry].fields["author"]
		fy = db.entries[entry].fields["year"]
		fb = db.entries[entry].fields["booktitle"].replace("{", "").replace("}", "")

		return ft, fy, fa, fb

def parsearxiv(arxivid):
	arxivid = arxivid.split("/")[-1]
	url = "http://export.arxiv.org/api/query?id_list=" + arxivid
	req = urllib.request.Request(url, headers=generateheaders())
	res = urllib.request.urlopen(req)
	arxivmeta = res.read().decode("utf-8")
	
	doc = xml.dom.minidom.parseString(arxivmeta)
	feed = doc.documentElement
	entries = feed.getElementsByTagName("entry")
	if len(entries) == 1:
		title = entries[0].getElementsByTagName("title")[0].childNodes[0].nodeValue.replace("\n", "").replace("  ", " ")
		date = entries[0].getElementsByTagName("published")[0].childNodes[0].nodeValue
		year = date[:4]
		authors = entries[0].getElementsByTagName("author")
		names = [author.getElementsByTagName("name")[0].childNodes[0].nodeValue for author in authors]
		return title, year, ", ".join(names)

def parsedoi(doi):
	header = generateheaders()
	header["Accept"] = "application/x-bibtex"

	header2 = header.copy()
	header2["Accept"] = "text/bibliography; style=bibtex"

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

		return ft, fy, fa, fb, fj

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

	for ident in sorted(literature):
		if not "doi" in literature[ident] and not "arxiv" in literature[ident] and not "usenix" in literature[ident]:
			if ident in biblio and "title" in biblio[ident]:
				if "link" in literature[ident]:
					print("## work {} has no DOI/arXiv/USENIX but a manual entry and link".format(ident))
				else:
					print("!! work {} has no DOI/arXiv/USENIX and incomplete manual entry, link missing".format(ident))
			else:
				print("!! work {} has no DOI/arXiv/USENIX".format(ident))
			continue
		if not ident in biblio or forced:
			fj = None
			fb = None
			r = None
			if "doi" in literature[ident]:
				doi = literature[ident]["doi"]
				print("Retrieving {}: DOI {}".format(ident, doi))
				ft, fy, fa, fb, fj = parsedoi(doi)
				r = ("retrieved-from-doi", doi)
			elif "arxiv" in literature[ident]:
				arxivid = literature[ident]["arxiv"]
				print("Retrieving {}: arXiv {}".format(ident, arxivid))
				ft, fy, fa = parsearxiv(arxivid)
				biblio[ident] = {}
				fj = "arXiv/CoRR"
				r = ("retrieved-from-arxiv", arxivid)
			elif "usenix" in literature[ident]:
				usenixurl = literature[ident]["usenix"]
				print("Retrieving {}: USENIX {}".format(ident, usenixurl))
				res = parseusenix(usenixurl)
				if not res:
					print("!! ERROR no bibliographic information found")
					time.sleep(5)
					continue
				ft, fy, fa, fb = res
				r = ("retrieved-from-usenix", usenixurl)

			biblio[ident] = {}
			biblio[ident]["title"] = ft
			biblio[ident]["author"] = fa
			biblio[ident]["year"] = fy
			if fj:
				biblio[ident]["journal"] = fj
			if fb:
				biblio[ident]["booktitle"] = fb
			biblio[ident][r[0]] = r[1]
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
		mkeys = [x for x in range(1, len(allkeys)) if not x in allkeys]
		print("!! Inconsistency: keys={} some are missing: {}".format(allkeys, mkeys))
	dois = {}
	for x in sorted(biblio):
		for source in ("doi", "arxiv", "usenix"):
			rsource = "retrieved-from-" + source
			if rsource in biblio[x]:
				if not biblio[x][rsource] in dois:
					dois[biblio[x][rsource]] = x
				else:
					print("!! Inconsistency: keys={}/{} duplicate for DOI {}".format(x, dois[biblio[x][rsource]], biblio[x][rsource]))

def check_correlations(base_filename):
	f = open(base_filename)
	literature = json.load(f)

	corr = []
	for ident in sorted(literature):
		if "correlation" in literature[ident]:
			c = literature[ident]["correlation"]
			if not (c in literature and "correlation" in literature[c] and literature[c]["correlation"] == ident):
				print("!! Inconsistency: correlation {}/{}".format(ident, c))
			else:
				if not (c, ident) in corr:
					corr.append((ident, c))
	return corr

biblio = populate_bibliography(base_filename, biblio_filename, forced)
check_consistency(biblio)
corr = check_correlations(base_filename)

filterlist_doi = [x for x in biblio if "retrieved-from-doi" in biblio[x]]
percent_doi = round(100 * len(filterlist_doi) / len(biblio))
filterlist_arxiv = [x for x in biblio if "retrieved-from-arxiv" in biblio[x]]
percent_arxiv = round(100 * len(filterlist_arxiv) / len(biblio))
filterlist_usenix = [x for x in biblio if "retrieved-from-usenix" in biblio[x]]
percent_usenix = round(100 * len(filterlist_usenix) / len(biblio))

print("Serverless literature statistics:")
print("- {} entries in total".format(len(biblio)))
print("- {:2d}% DOI entries".format(percent_doi))
print("- {:2d}% arXiv entries".format(percent_arxiv))
print("- {:2d}% USENIX entries".format(percent_usenix))
print("- {:2d}% manual/other entries".format(100 - percent_arxiv - percent_doi - percent_usenix))
print("Correlations ({}):".format(len(corr)), ",".join(["{}⇋{}".format(c[0], c[1]) for c in corr]))
