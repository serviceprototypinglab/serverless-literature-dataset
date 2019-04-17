import dblplocal as dblp
import time
import json

base_filename = "../serverless-literature-base.json"
biblio_filename = "../serverless-literature-bibliography.json"

# Authors,Title,(Type),Where,Year

searchterms = [
	"serverless computing"
]

f = open(base_filename)
literature = json.load(f)

f = open(biblio_filename)
biblio = json.load(f)

nextnum = sorted([int(x) for x in literature])[-1] + 1
courtesy = False

for searchterm in searchterms:
	if courtesy:
		print("courtesy delay (5s)...")
		time.sleep(5)
	courtesy = True

	print("Search:", searchterm, "...")
	results = dblp.search([searchterm])

	doiactions = {}
	for idx, r in results[(results["Link"].str.contains("doi.org")) | (results["Link"].str.contains("arxiv.org"))].iterrows():
		doi = r["Link"]
		title = r["Title"]
		skip = False
		skipped = ""
		for ident in literature:
			if "doi" in literature[ident] and literature[ident]["doi"] == doi:
				skip = True
				skipped = "(present)"
			if "arxiv" in literature[ident] and literature[ident]["arxiv"] == doi:
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
				nextnum += 1
			else:
				skipped = "(excluded)"
		doiactions[doi] = skipped

	for doi in sorted([x for x in doiactions if "doi.org" in x]):
		print("* {:10s} <= DOI: {}".format(doiactions[doi], doi))
	for doi in sorted([x for x in doiactions if "arxiv.org" in x]):
		print("* {:10s} <= arXiv: {}".format(doiactions[doi], doi))

	for nondoi in results["Link"][(~results["Link"].str.contains("doi.org")) & (~results["Link"].str.contains("arxiv.org"))]:
		print("* {:10s} <= non-DOI/arXiv: {}".format("(unknown)", nondoi))

	f = open(base_filename, "w")
	base_sorted = {int(x) : literature[x] for x in literature}
	json.dump(base_sorted, f, indent=2, ensure_ascii=False, sort_keys=True)
	f.close()
