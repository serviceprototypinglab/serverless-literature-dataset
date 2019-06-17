import dblplocal as dblp
import time
import json
import glob
import os

prefix = "serverless"
basefiles = glob.glob("../*-literature-base.json")
if len(basefiles) == 1:
	prefix = os.path.basename(basefiles[0]).split("-")[0]

base_filename = "../{}-literature-base.json".format(prefix)
neg_filename = "negative.json"

# Authors,Title,(Type),Where,Year

searchterms = json.load(open("searchterms.json"))

try:
	f = open(base_filename)
	literature = json.load(f)
except:
	print("Warning: no base {} found.".format(base_filename))
	literature = {}

try:
	f = open(neg_filename)
	negs = json.load(f)
except:
	print("Warning: no negatives {} found.".format(neg_filename))
	negs = []

neglinks = []
for neg in negs:
	if "doi" in neg:
		neglinks.append(neg["doi"])
	elif "usenix" in neg:
		neglinks.append(neg["usenix"])
	elif "arxiv" in neg:
		neglinks.append(neg["arxiv"])
	elif "link" in neg:
		neglinks.append(neg["link"])

if len(literature) > 0:
	nextnum = sorted([int(x) for x in literature])[-1] + 1
else:
	nextnum = 1
courtesy = False

for searchterm in searchterms:
	if courtesy:
		print("courtesy delay (5s)...")
		time.sleep(5)
	courtesy = True

	print("Search:", searchterm, "...")
	results = dblp.search([searchterm])

	doiactions = {}
	f_doi = results["Link"].str.contains("doi.org")
	f_arxiv = results["Link"].str.contains("arxiv.org")
	f_usenix = results["Link"].str.contains("usenix.org")
	for idx, r in results[f_doi | f_arxiv | f_usenix].iterrows():
		doi = r["Link"]
		title = r["Title"]
		skip = False
		skipped = ""
		if doi in neglinks:
			skip = True
			skipped = "(negative)"
		for ident in literature:
			if "doi" in literature[ident] and literature[ident]["doi"] == doi:
				skip = True
				skipped = "(present)"
			elif "arxiv" in literature[ident] and literature[ident]["arxiv"] == doi:
				skip = True
				skipped = "(present)"
			elif "usenix" in literature[ident] and literature[ident]["usenix"] == doi:
				skip = True
				skipped = "(present)"
			elif "link" in literature[ident] and literature[ident]["link"] == doi:
				skip = True
				skipped = "(present)"
		if not skip:
			a = input("Insert '{}' (y/n)? ".format(title))
			if a == "y":
				skipped = str(nextnum)
				if "doi.org" in doi:
					literature[skipped] = {"doi": doi}
				elif "arxiv.org" in doi:
					literature[skipped] = {"arxiv": doi}
				elif "usenix.org" in doi:
					literature[skipped] = {"usenix": doi}
				else:
					literature[skipped] = {"link": doi}
				nextnum += 1
			else:
				neglinks.append(doi)
				skipped = "(excluded)"
		doiactions[doi] = skipped

	for doi in sorted([x for x in doiactions if "doi.org" in x]):
		print("* {:10s} <= DOI: {}".format(doiactions[doi], doi))
	for doi in sorted([x for x in doiactions if "arxiv.org" in x]):
		print("* {:10s} <= arXiv: {}".format(doiactions[doi], doi))
	for doi in sorted([x for x in doiactions if "usenix.org" in x]):
		print("* {:10s} <= USENIX: {}".format(doiactions[doi], doi))

	for nondoi in results["Link"][~f_doi & ~f_arxiv & ~f_usenix]:
		print("* {:10s} <= non-DOI/arXiv/USENIX: {}".format("(unknown)", nondoi))

	f = open(base_filename, "w")
	base_sorted = {int(x) : literature[x] for x in literature}
	json.dump(base_sorted, f, indent=2, ensure_ascii=False, sort_keys=True)
	f.close()

	negs = []
	for doi in neglinks:
		if "doi.org" in doi:
			negs.append({"doi": doi})
		elif "arxiv.org" in doi:
			negs.append({"arxiv": doi})
		elif "usenix.org" in doi:
			negs.append({"usenix": doi})
		else:
			negs.append({"link": doi})

	f = open(neg_filename, "w")
	json.dump(negs, f, indent=2, ensure_ascii=False, sort_keys=True)
	f.close()
