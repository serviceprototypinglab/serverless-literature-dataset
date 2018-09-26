import json
import numpy as np
from matplotlib import pyplot as plt
from matplotlib_venn import venn3, venn3_circles, venn2, venn2_circles

biblio_filename = "serverless-literature-bibliography.json"

f = open(biblio_filename)
biblio = json.load(f)

terms = ("serverless application", "serverless computing", "serverless", "function-as-a-service", "lambda", "cloud function", "faas")
chosenterms=(terms[1], terms[2], terms[6])

allmterms = []
for ident in biblio:
	title = biblio[ident]["title"].lower()
	mterms = []
	for term in terms:
		if term in title:
			mterms.append(term)
	print("keywords for {:3d}: {}".format(int(ident), mterms))
	allmterms.append(mterms)

pairs = {}
for mterms in allmterms:
	if len(mterms) > 1:
		pairs[str(mterms)] = pairs.setdefault(str(mterms), 0) + 1
for pair in pairs:
	print("venn-able pairing: {:3d} {}".format(pairs[pair], pair))

def getsubsets(allmterms, t1, t2, t3):
	# Syntax: Abc, aBc, ABc, abC, AbC, aBC, ABC (where a = not A)
	subsets = [0, 0, 0, 0, 0, 0, 0]
	for mterms in allmterms:
		if t1 in mterms and not t2 in mterms and not t3 in mterms:
			subsets[0] += 1
		elif not t1 in mterms and t2 in mterms and not t3 in mterms:
			subsets[1] += 1
		elif t1 in mterms and t2 in mterms and not t3 in mterms:
			subsets[2] += 1
		elif not t1 in mterms and not t2 in mterms and t3 in mterms:
			subsets[3] += 1
		elif t1 in mterms and not t2 in mterms and t3 in mterms:
			subsets[4] += 1
		elif not t1 in mterms and t2 in mterms and t3 in mterms:
			subsets[5] += 1
		elif t1 in mterms and t2 in mterms and t3 in mterms:
			subsets[6] += 1
	return subsets

subsets_sl=getsubsets(allmterms, *chosenterms)
print("weighted venn subsets", subsets_sl)

plt.figure(figsize=(7, 7))
plt.rc("font", size=16)

v = venn3(subsets=subsets_sl, set_labels=chosenterms)
#v.get_patch_by_id('100').set_alpha(1.0)
#v.get_patch_by_id('100').set_color('white')
#v.get_label_by_id('100').set_text('Unknown')
#v.get_label_by_id('A').set_text('Set "A"')

c = venn3_circles(subsets=subsets_sl, linestyle='dashed')
#c[0].set_lw(1.0)
#c[0].set_ls('dotted')

plt.title("Literature keywords relations")
#plt.annotate('Unknown set', xy=v.get_label_by_id('100').get_position() - np.array([0, 0.05]), xytext=(-70,-70),
#             ha='center', textcoords='offset points', bbox=dict(boxstyle='round,pad=0.5', fc='gray', alpha=0.1),
#             arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.5',color='gray'))
plt.show()

v = venn2(subsets=(34, 7, 14), set_labels=("academia", "industry"))
c = venn2_circles(subsets=(34, 7, 14), linestyle='dashed')
plt.title("Literature institution relations")

plt.show()
