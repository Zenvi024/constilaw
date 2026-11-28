#!/usr/bin/env python3
"""python3 site/app/pdf_post.py file.pdf outline.json
Adds the PDF's bookmarks and a running header (map or topic name, in the part's colour) to every page from the
first heading that sets one. outline.json: [{lvl, t, page, hd?, c?}] from make_pdfs.js. Needs PyMuPDF."""
import json, sys, os
import pymupdf
pdf, oj = sys.argv[1], sys.argv[2]
items = json.load(open(oj))
doc = pymupdf.open(pdf)
# bookmarks: levels may not jump by more than one
toc, prev = [], 0
for o in items:
    lv = max(1, min(o['lvl'], prev + 1)); prev = lv
    toc.append([lv, o['t'].strip()[:120], int(o['page'])])
doc.set_toc(toc)
# running header: the last item at or before the page that carries one
heads = sorted([(o['page'], o['hd'], o.get('c') or '#555555') for o in items if o.get('hd') is not None], key=lambda x: x[0])
def rgb(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
for pno in range(doc.page_count):
    cur = None
    for pg, hd, c in heads:
        if pg <= pno + 1: cur = (hd, c)
        else: break
    if not cur or not cur[0]: continue
    page = doc[pno]; w = page.rect.width; x = 18 * 72 / 25.4; y = 9.5 * 72 / 25.4
    page.draw_rect(pymupdf.Rect(x, y - 6.2, x + 3.2, y + 0.8), color=None, fill=rgb(cur[1]))
    page.insert_text((x + 6, y), cur[0], fontsize=7, fontname='helv', color=rgb(cur[1]))
    page.draw_line((x, y + 3), (w - x, y + 3), color=(0.82, 0.83, 0.87), width=0.4)
tmp = pdf + '.tmp'
doc.save(tmp, garbage=3, deflate=True); doc.close(); os.replace(tmp, pdf)
