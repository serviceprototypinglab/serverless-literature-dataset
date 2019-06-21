import difflib
import json
import glob
import os

prefix = "serverless"
basefiles = glob.glob("*-literature-base.json")
if len(basefiles) == 1:
	prefix = os.path.basename(basefiles[0]).split("-")[0]

base_filename = "{}-literature-base.json".format(prefix)
biblio_filename = "{}-literature-bibliography.json".format(prefix)

f = open(biblio_filename)
biblio = json.load(f)

f = open(base_filename)
base = json.load(f)

print("Performing combinatorial comparisons... (this might take some time)")
found = []
founddata = []
founddata_corr = []
for ident1 in biblio:
	for ident2 in biblio:
		if ident1 == ident2:
			continue
		if (ident2, ident1) in found:
			continue
		t1 = biblio[ident1]["title"]
		t2 = biblio[ident2]["title"]
		r = difflib.SequenceMatcher(isjunk=None, a=t1, b=t2).ratio()
		if r > 0.7:
			found.append((ident1, ident2))
			corr = False
			if "correlation" in base[ident1] and base[ident1]["correlation"] == ident2:
				founddata_corr.append((ident1, ident2, t1, t2, round(100 * r)))
			else:
				founddata.append((ident1, ident2, t1, t2, round(100 * r)))

for ident1, ident2, t1, t2, r in founddata_corr:
	print("[{:3d}%] Already correlated works {} and {}.".format(r, ident1, ident2))
for ident1, ident2, t1, t2, r in founddata:
	print("[{:3d}%] Check works {} and {}.".format(r, ident1, ident2))
	print("       {}".format(t1))
	print("   vs. {}".format(t2))
