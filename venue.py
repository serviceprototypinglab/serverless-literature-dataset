#!/usr/bin/env python3

import json
import collections

biblio_filename = "serverless-literature-bibliography.json"

f = open(biblio_filename)
biblio = json.load(f)

journals = []
for ident in biblio:
	journals.append(biblio[ident]["journal"])

consjournals = []
for journal in journals:
	if "arXiv" in journal or "ArXiv" in journal:
		consjournals.append("arXiv")
	elif "USENIX" in journal or "HotCloud" in journal or "HotOS" in journal:
		consjournals.append("USENIX")
	elif "ACM" in journal or "ESEC/FSE" in journal or "ICPP" in journal:
		consjournals.append("ACM")
	elif "IEEE" in journal or "UCC" in journal or "PDP" in journal:
		consjournals.append("IEEE")
	elif "Lecture Notes in Computer Science" in journal:
		consjournals.append("Springer")
	elif "Future Generation Computer Systems" in journal:
		consjournals.append("Elsevier")
	else:
		print("!! unknown journal/conference {}".format(journal))
		consjournals.append("unknown")

print(collections.Counter(consjournals))
