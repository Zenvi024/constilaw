"""Index every digest: individual .docx files (title = first paragraph) and compilations (Heading 1 / Title per case)."""
import sys, os, re, json, docx
from docx.oxml.ns import qn
base = sys.argv[1]; out = []
COMPIL = re.compile(r"(Masterfile|ZENS CONSTI|\[01\]|Rubi to Mangudadatu|^\d{4} Consti)", re.I)
SKIP = re.compile(r'^(TITLE \(DATE\)|SEPARATE OPINION|Hi Kim|CONTENTS|TABLE OF CONTENTS)', re.I)
for dp, _, fs in os.walk(base):
    for f in sorted(fs):
        if not f.endswith('.docx'): continue
        p = os.path.join(dp, f); rel = os.path.relpath(p, base)
        d = docx.Document(p)
        paras = [x for x in d.paragraphs if x.text.strip()]
        if COMPIL.search(f):
            # case titles = paragraph right before a headnote table ("Topic | Subtopic"), plus Heading 1 / Title paragraphs
            body = list(d.element.body.iterchildren()); lastp = None; tabtitles = set()
            for ch in body:
                tag = ch.tag.split('}')[1]
                if tag == 'p':
                    t = ''.join(x.text or '' for x in ch.iter(qn('w:t'))).strip()
                    if t: lastp = t
                elif tag == 'tbl':
                    first = ''.join(x.text or '' for x in ch.iter(qn('w:t')))[:40]
                    if first.lstrip().startswith('Topic') and lastp:
                        tabtitles.add(lastp)
            heads = set()
            prev = None
            for x in paras:
                st = x.style.name.lower()
                if st in ('heading 1', 'title'):
                    t = x.text.strip()
                    if SKIP.match(t): prev = None; continue
                    if prev is not None and not re.search(r'\(\d{4}\)|\d{4}', out[-1]['title']) and prev == 'h':
                        out[-1]['title'] += ' ' + t; continue   # heading split over lines
                    out.append({'file': rel, 'kind': 'compilation', 'title': t}); heads.add(t); prev = 'h'
                else: prev = None
            for t in sorted(tabtitles - heads):
                if not SKIP.match(t) and not any(t in h or h in t for h in heads):
                    out.append({'file': rel, 'kind': 'compilation', 'title': t, 'via': 'headnote-table'})
        else:
            t = paras[0].text.strip() if paras else ''
            out.append({'file': rel, 'kind': 'single', 'title': t})
json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
import collections
print(len(out), 'digest entries', collections.Counter((o['kind'], o['file'].split('/')[0] if o['kind']=='single' else os.path.basename(o['file'])) for o in out))
