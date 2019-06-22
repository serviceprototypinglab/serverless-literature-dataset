#!/usr/bin/env python3

import json
import collections
import glob
import os

prefix = "serverless"
basefiles = glob.glob("*-literature-base.json")
if len(basefiles) == 1:
	prefix = os.path.basename(basefiles[0]).split("-")[0]

biblio_filename = "{}-literature-bibliography.json".format(prefix)

f = open(biblio_filename)
biblio = json.load(f)

journals = []
jratio = 0
for ident in biblio:
	if "journal" in biblio[ident]:
		journals.append(biblio[ident]["journal"])
		jratio += 1
	elif "booktitle" in biblio[ident]:
		journals.append(biblio[ident]["booktitle"])

consjournals = []
for journal in journals:
	if "arXiv" in journal or "ArXiv" in journal:
		consjournals.append("arXiv")
	elif "USENIX" in journal or "HotCloud" in journal or "HotOS" in journal or ";login:" in journal:
		consjournals.append("USENIX")
	elif "ACM" in journal or "ESEC/FSE" in journal or "ICPP" in journal or "WoSC ’17" in journal or "SIGMOD" in journal:
		consjournals.append("ACM")
	elif "IEEE" in journal or "UCC" in journal or "PDP" in journal:
		consjournals.append("IEEE")
	elif "Lecture Notes in Computer Science" in journal:
		consjournals.append("Springer")
	elif "Future Generation Computer Systems" in journal:
		consjournals.append("Elsevier")
	elif "CEUR-WS" in journal:
		consjournals.append("CEUR-WS")
	else:
		print("!! unknown journal/conference {}".format(journal))
		consjournals.append("unknown")

print(collections.Counter(consjournals))
print("Ratio of journals: {}%".format(round(100 * jratio / len(biblio))))
