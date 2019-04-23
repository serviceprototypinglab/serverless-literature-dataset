for g in sldgraph-*.pdf; do convert -scale 1024 -quality 50 $g $g.jpg; done; rename -f 's/.dot.pdf.jpg$/.jpg/' *.jpg
