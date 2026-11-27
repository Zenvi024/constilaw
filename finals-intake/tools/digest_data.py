"""Build the desk's digest library from the original .docx files.

Writes site/data/finals/syllabus.json (whole-course syllabus with digest and card links)
and site/data/finals/digests.json.gz (id -> lossless parsed digest), and checks every
digest word for word against its source.

Run: python3 -I digest_data.py
"""
import sys, os, re, json, gzip, csv, glob, collections, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import docx
from docx.oxml.ns import qn
import parse
from parse import all_text_docx, para, Numbering

ROOT = '/home/user/constilaw'
SRC = ROOT + '/sources/finals/digests_zip'
OUT = ROOT + '/site/data/finals'
os.makedirs(OUT, exist_ok=True)
cov = json.load(open(ROOT + '/finals-intake/coverage.json'))
syl = json.load(open(ROOT + '/finals-intake/syllabus.json'))
W = lambda s: collections.Counter(re.findall(r"\w+", s.lower()))
LABELS = {'write', 'front', 'back', 'facts', 'final', 'decision', 'issue', 'headnote'}

# ---------- 1. Zen's single digests: drop byte-identical and text-identical copies ----------
man = {r['filename']: r for r in csv.DictReader(open(SRC + '/MANIFEST.csv', encoding='utf-8'))}
parsed = {d['file']: d for d in json.load(open(ROOT + '/finals-intake/parsed/my_digests.json'))}
def text_of(path):
    return all_text_docx(path)
keep, alias = {}, {}     # filename -> kept filename
by_hash, by_text = {}, {}
for fn in sorted(parsed, key=lambda f: (re.search(r'\(\d\)', f) is not None, f)):
    h = man[fn]['SHA-256 hash']
    if h in by_hash: alias[fn] = by_hash[h]; continue
    t = ' '.join(re.findall(r'\w+', text_of(f'{SRC}/my_digests/{fn}').lower()))
    if t in by_text:
        # same words, different formatting: keep the larger file
        other = by_text[t]
        if int(man[fn]['file size in bytes']) > int(man[other]['file size in bytes']):
            del keep[other]; alias[other] = fn; keep[fn] = True; by_text[t] = fn
        else: alias[fn] = other
        by_hash[h] = by_text[t]; continue
    by_hash[h] = fn; by_text[t] = fn; keep[fn] = True
resolve = lambda fn: alias.get(fn, fn) if alias.get(fn, fn) in keep else resolve(alias[fn])
print('single digests:', len(parsed), '→ kept', len(keep), '(dropped', len(parsed) - len(keep), 'copies)')

LIB = {}       # id -> {kind, src, label, data}
SRCWORDS = {}  # id -> Counter of source words
def did(prefix, s): return prefix + ':' + re.sub(r'[^A-Za-z0-9]+', '_', s).strip('_')
for fn in keep:
    i = did('z', fn.replace('_Digest', '').replace('.docx', ''))
    LIB[i] = {'kind': 'case', 'src': 'my_digests/' + fn, 'label': "Zen's digest", 'data': parsed[fn]}
    SRCWORDS[i] = W(text_of(f'{SRC}/my_digests/{fn}'))

# ---------- 2. compilation chunks (one per case) ----------
def is_topic_tbl(el):
    return el.tag.endswith('}tbl') and ''.join(x.text or '' for x in el.iter(qn('w:t'))).lstrip().startswith('Topic')
def ptext(el): return ''.join(x.text or '' for x in el.iter(qn('w:t'))).strip()
def pstyle(el):
    s = el.find(qn('w:pPr'))
    s = s.find(qn('w:pStyle')) if s is not None else None
    return (s.get(qn('w:val')) or '') if s is not None else ''
CHUNKS = {}
def template_chunks(path):
    if path in CHUNKS: return CHUNKS[path]
    d = docx.Document(path); num = Numbering(d); els = list(d.element.body.iterchildren())
    starts = []
    for t, el in enumerate(els):
        if not is_topic_tbl(el): continue
        j = t - 1
        while j >= 0 and not (els[j].tag.endswith('}p') and ptext(els[j])): j -= 1
        # a note paragraph may sit between the title and the table: step back to a heading if one is right above
        k = j - 1
        while k >= 0 and not (els[k].tag.endswith('}p') and ptext(els[k])): k -= 1
        if k >= 0 and k > (starts[-1] if starts else -1) and pstyle(els[k]).lower().startswith(('heading1', 'title')) and not pstyle(els[j]).lower().startswith(('heading1', 'title')):
            j = k
        starts.append(j)
    out = []
    for n, s in enumerate(starts):
        e = starts[n + 1] if n + 1 < len(starts) else len(els)
        out.append((ptext(els[s]), els[s:e]))
    CHUNKS[path] = (out, num)
    return CHUNKS[path]
def raw_chunks(path):
    """Non-template compilation (ZENS 2.0): split at Heading 1; keep every paragraph with formatting."""
    d = docx.Document(path); num = Numbering(d); els = list(d.element.body.iterchildren()); out = []; cur = None
    for el in els:
        if el.tag.endswith('}p') and pstyle(el).lower().startswith('heading1') and ptext(el):
            cur = [ptext(el), []]; out.append(cur)
        if cur is not None: cur[1].append(el)
    return out, num
def chunk_words(els): return W(' \n '.join(ptext(p) if p.tag.endswith('}p') else ' \n '.join(ptext(x) for x in p.iter(qn('w:p'))) for p in els))
import unicodedata
def norm_t(s): return re.sub(r'[^a-z0-9]+', ' ', unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()).strip()
def find_chunk(path, title, raw=False):
    chunks, num = (raw_chunks if raw else template_chunks)(path)
    hits = [(t, e) for t, e in chunks if norm_t(t) == norm_t(title)] or [(t, e) for t, e in chunks if norm_t(title) in norm_t(t) or norm_t(t) in norm_t(title)]
    assert len(hits) >= 1, (path, title)
    return hits[0][0], hits[0][1], num
def raw_parse(title, els, num):
    paras = []
    for el in els:
        if el.tag.endswith('}p'):
            x = para(el, num)
            if x['text'].strip(): paras.append({**x, 'st': pstyle(el)})
        elif el.tag.endswith('}tbl'):
            for p in el.iter(qn('w:p')):
                x = para(p, num)
                if x['text'].strip(): paras.append({**x, 'st': 'cell'})
    return {'raw': True, 'title': title, 'paras': paras}

def add_chunk(prefix, rel, title, label, raw=False):
    path = f'{SRC}/{rel}'
    t, els, num = find_chunk(path, title, raw)
    i = did(prefix, os.path.basename(rel)[:18] + '_' + t[:60])
    if i in LIB: return i
    data = raw_parse(t, els, num) if raw else parse.parse(path, els, num, name=f'{os.path.basename(rel)} :: {t}')
    LIB[i] = {'kind': 'raw' if raw else 'case', 'src': f'{rel} :: {t}', 'label': label, 'data': data}
    SRCWORDS[i] = chunk_words(els)
    return i

# ---------- 3. syllabus entries -> digest ids ----------
cards = {}
for f in glob.glob(ROOT + '/site/data/cases/*.json'):
    for c in json.load(open(f)): cards[f'{c["n"]} ({c["y"]})'] = c['id']
NOT_SAME = {'Republic v. Sandiganbayan, G.R. No. 152154': 'repsandiganbayan'}
entries = []
k = 0
for o in syl:
    if o['type'] == 'head':
        entries.append({'h': o['text'], 'lv': o['level']}); continue
    if o['type'] != 'case': continue
    r = cov[k]; k += 1
    assert r['cite'] == o['text'], (r['cite'], o['text'])
    ids = []
    for fn in r.get('mine', []):
        if not fn.startswith('my_digests/'): continue
        kept = resolve(os.path.basename(fn))
        i = did('z', kept.replace('_Digest', '').replace('.docx', ''))
        if i not in ids: ids.append(i)
    if not ids and r['finals']:
        # no single digest of Zen's: Zen's compilation, then the manual file, then the block
        for m in r.get('mine_comp', []):
            if 'ZENS' in m:
                for b in r['block']:
                    pass
                ids.append(add_chunk('c', m, 'Tanada v. Tuvera' if 'Tanada' in r['cite'] else r['cite'].split(',')[0], "Zen's Digests 2.0", raw=True))
        seen_text = {}
        for b in sorted(r['block'], key=lambda b: (0 if 'Rubi' in b else 1, b)):
            rel, title = b.split(' :: ', 1)
            if not rel.endswith('.docx') or not os.path.exists(f'{SRC}/{rel}'): continue
            if not ('Masterfile' in rel or 'Rubi' in rel): continue   # dated midterm-week block files are unfinished templates
            if os.path.basename(rel)[:2].isdigit() and not rel.split('/')[-1].startswith(('08', '09')):
                pass
            try:
                i = add_chunk('b', rel, title, 'Manual digest (Rubi–Mangudadatu file)' if 'Rubi' in rel else 'Block I-B digest')
            except AssertionError:
                continue
            key = ' '.join(sorted(SRCWORDS[i].elements()))
            if key in seen_text: LIB.pop(i, None); SRCWORDS.pop(i, None); continue
            seen_text[key] = i; ids.append(i)
    card = None
    for nm in r.get('midterm_card', []):
        cidv = cards.get(nm)
        if cidv and not any(r['cite'].startswith(p) and cidv == v for p, v in NOT_SAME.items()): card = cidv; break
    cite = r['cite']
    short = re.split(r',?\s+(?:G\.\s?R|A\.M|A\.C|JGR|P\.E\.T|\d+\s?SCRA|\d+ Phil|Bar Matter|Res\.|Extended|UDK|\d+ U\.S\.)|,\s*(?=\d)', cite)[0].strip().rstrip(',')
    short = re.sub(r'\s+et al\.?$', '', short)
    TYPO = {'Gudani v. Sena': 'Gudani v. Senga', 'General v. Urra': 'General v. Urro', 'Demaisip v. Bacal': 'Demaisip v. Bacal (Cuevas v. Bacal)',
            'Beltran v. Macasiar': 'Beltran v. Macasiar (Soliven v. Makasiar)', 'Zaldivar v. Gonzales': 'Zaldivar v. Gonzales (Zaldivar v. Sandiganbayan)'}
    short = TYPO.get(short, short)
    if short.startswith('Re: In the Matter of Clarification of Exemption'): short = 'Re: Cooperatives’ Exemption from Court Fees (PHCCI)'
    if short.startswith('In Re: Production of Court Records'): short = 'In re: Production of Court Records (2012)'
    entries.append({'c': cite, 's': short, 'f': r['finals'], 'x': r['excluded'], 'card': card, 'd': ids})

# order each entry's digests: the fuller version first when two of Zen's digests differ
for e in entries:
    if 'd' in e and len(e['d']) > 1 and all(x.startswith('z:') for x in e['d']):
        pass  # keep syllabus-meaningful order (decision before resolution)
# the Ramas-Dimaano case (G.R. 104768) has no digest in the files; the 2003 'Republic v. Sandiganbayan' digest is G.R. 152154
for e in entries:
    if e.get('c', '').startswith('Republic v. Sandiganbayan, G.R. No. 104768'): e['d'] = []
DUPS = [('z:Bengzon_v_Senate_Blue_Ribbon_1991', 'z:Bengzon_v_Senate_Blue_Ribbon_1991_1'), ('z:Padilla_v_Congress_2017_1', 'z:Padilla_v_Congress_2017'),
        ('z:Neri_v_Senate', 'z:Neri_v_Senate_Committees_2008'), ('z:Agcaoili_v_Farinas', 'z:Agcaoili_v_Farinas_2018'), ('z:Funa_v_Villar', 'z:Funa_v_Villar_1')]
for pair in DUPS:
    for p in pair: assert p in LIB, p
# Zen's rule (Nov. 27, 2026): one digest per case. Order: Zen's single digest > Zen's compilation > manual file > block.
# Two of Zen's digests of the same ruling: keep the fuller. Two of Zen's digests of different rulings (a decision and its
# resolution) stay together and are read as one continuous digest.
fuller = lambda i: sum(SRCWORDS[i].values())
DROP = set()
for a, b in DUPS:
    lose = b if fuller(a) >= fuller(b) else a
    DROP.add(lose)
for e in entries:
    ds = e.get('d') or []
    if not ds: continue
    if ds[0].startswith('z:'):
        keep_ids = sorted((i for i in ds if i.startswith('z:') and i not in DROP), key=lambda i: bool(re.search(r'Resolution|_MR', i)))   # decision first
    else:
        keep_ids = ds[:1]
    DROP.update(i for i in ds if i not in keep_ids)
    e['d'] = keep_ids
DROP -= {i for e in entries for i in e.get('d', [])}
for i in DROP: LIB.pop(i, None)
print('dropped as duplicates or lower in the source order:', len(DROP))

# digests not reached from any syllabus entry are still kept, listed at the end
used = {i for e in entries for i in e.get('d', [])}
extra = sorted(i for i in LIB if i not in used)
entries.append({'h': 'Other digests (not matched to a syllabus line)', 'lv': 0})
for i in extra:
    entries.append({'c': LIB[i]['data'].get('title', i), 's': LIB[i]['data'].get('title', i), 'f': False, 'x': False, 'card': None, 'd': [i], 'other': True})

# ---------- 4. word check: every source word must be in the parsed digest ----------
def parsed_words(d):
    if d.get('raw'): return W(' '.join(p['text'] for p in d['paras']) + ' ' + d['title'])
    T = [d['title']] + [p['text'] for p in d.get('subtitle', [])]
    for h in d['headnote']: T.append(h['label']); T += [p['text'] for p in h['paras']]
    for s in d['sections']:
        T.append(s.get('label', '')); T.append(s.get('kindLabel', ''))
        for kk in ('question', 'answer', 'write'): T += [p['text'] for p in s.get(kk, [])]
        for sb in s.get('subs', []): T += [p['text'] for p in sb['q'] + sb['a']]
        for pt in s['parts']: T.append(pt['h']); T += [p['text'] for p in pt['paras']]
    T += [p['text'] for p in d['front'] + d['back']]
    return W(' '.join(T))
bad = 0
for i, v in LIB.items():
    miss = {w: n for w, n in (SRCWORDS[i] - parsed_words(v['data'])).items() if w not in LABELS}
    if miss: bad += 1; print('  MISSING in', i, dict(list(miss.items())[:10]))
print('digests:', len(LIB), '· with missing words:', bad)
assert bad == 0

json.dump({'entries': entries}, open(OUT + '/syllabus.json', 'w'), ensure_ascii=False, separators=(',', ':'))
blob = json.dumps({i: {'kind': v['kind'], 'data': v['data']} for i, v in LIB.items()}, ensure_ascii=False, separators=(',', ':')).encode()   # no source labels on the page
json.dump({i: v['src'] for i, v in LIB.items()}, open(ROOT + '/finals-intake/parsed/digest_sources.json', 'w'), ensure_ascii=False, indent=1)
open(OUT + '/digests.json.gz', 'wb').write(gzip.compress(blob, 9, mtime=0))
def hidden_words(d):
    if d.get('raw'): return collections.Counter()
    T = [p['text'] for s in d['sections'] for p in s.get('write', [])] + [p['text'] for p in d.get('front', []) + d.get('back', [])]
    return W(' '.join(T))
json.dump({i: dict(SRCWORDS[i] - hidden_words(v['data'])) for i, v in LIB.items()}, open(ROOT + '/finals-intake/parsed/source_words.json', 'w'), ensure_ascii=False)
F = [e for e in entries if e.get('f')]
print(f'entries: {sum(1 for e in entries if "c" in e)} ({len(F)} finals; finals without a digest: {sum(1 for e in F if not e["d"])}); extra digests listed: {len(extra)}')
print(f'digests.json.gz: {len(blob)//1024} KB raw → {os.path.getsize(OUT + "/digests.json.gz")//1024} KB gzip')
