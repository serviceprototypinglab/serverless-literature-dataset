#!/usr/bin/env python3

import json
import os
import urllib.request
import pybtex.database

analysis_filename = "serverless-literature-analysis.json"
biblio_filename = "serverless-literature-bibliography.json"

f = open(biblio_filename)
biblio = json.load(f)

f = open(analysis_filename)
analysis = json.load(f)

allkeys = []
for ident in analysis:
	if not ident in biblio:
		print("!! work {} in analysis but not present in bibliography".format(ident))
	for key in analysis[ident].keys():
		if not key in allkeys:
			allkeys.append(key)

print("Check {} entries for keys: {}".format(len(biblio), allkeys))

for ident in biblio.keys():
	if not ident in analysis:
		print("!! work {} missing in analysis".format(ident))
		print("- {}".format(biblio[ident]["title"]))
		continue
	for key in allkeys:
		if not key in analysis[ident]:
			print("!! work {} misses key {}".format(ident, key))
