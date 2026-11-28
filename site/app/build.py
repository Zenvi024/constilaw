#!/usr/bin/env python3
"""Assemble the single-file Consti 1 study site.

Usage: python3 site/app/build.py [--out site/dist/consti1-midterm-desk.html]
Reads site/data/{cases,reviewer,exams}; writes one self-contained HTML file.
"""
import argparse, glob, html, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
ap = argparse.ArgumentParser()
ap.add_argument('--out', default=os.path.join(HERE, '..', 'dist', 'consti1-midterm-desk.html'))
A = ap.parse_args()
J = lambda v: json.dumps(v, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
load = lambda p: json.load(open(os.path.join(DATA, p)))

TOPICS = [  # key, name, syllabus part, rule-map section
    ('basics', 'Interpretation and amendment', 'Parts I–II', 'interp'),
    ('jr', 'Judicial review', 'Part III', 'jr'),
    ('terr', 'Territory', 'IV.A', 'terr'),
    ('cit', 'Citizenship', 'IV.B.1', 'cit'),
    ('suff', 'Suffrage', 'IV.B.2', 'suff'),
    ('gov', 'Government and inherent powers', 'IV.C', 'gov'),
    ('house', 'Congress: composition and party-list', 'V.A.1–2', 'comp'),
    ('org', 'Congress: officers, discipline, privileges', 'V.A.3–4', 'internal'),
    ('et', 'Electoral tribunals and the CA', 'V.A.5–6', 'et'),
    ('powers', 'Powers of Congress and delegation', 'V.A.7–8(a)(1)', 'powers'),
    ('approp', 'Appropriations', 'V.A.8(a)(2)', 'money'),
    ('tax', 'Taxation', 'V.A.8(b)', 'money'),
    # finals (rule-map section ids are added as each batch writes its rule map)
    ('legproc', 'Congress: legislative process and investigations', 'V.A.7(c)–8', 'legproc'),
    ('ocong', 'Congress: other powers and impeachment', 'V.A.9', 'ocong'),
    ('pres', 'The President: office, succession, executive power', 'V.B.1–2(c)', 'pres'),
    ('appt', 'Appointment and clemency', 'V.B.2(d)–(e)', 'appt'),
    ('cinc', 'Commander-in-Chief, other powers, the Vice-President', 'V.B.2(f)–(k), V.B.3', 'cinc'),
    ('court', 'The Supreme Court', 'V.C.1–2(o)', 'court'),
    ('scadmin', 'The SC’s administrative and rule-making powers', 'V.C.2(p)', 'scadmin'),
    ('jbc', 'Lower courts, the JBC, automatic release', 'V.C.3–6', 'jbc'),
    ('concom', 'Constitutional Commissions', 'Constitutional Commissions', 'concom'),
]
topics = [dict(key=k, name=n, part=p, sec=s) for k, n, p, s in TOPICS]
tkeys = {t['key'] for t in topics}

cases = []
for f in sorted(glob.glob(os.path.join(DATA, 'cases', '*.json'))):
    cases += json.load(open(f))
ids = [c['id'] for c in cases]
assert len(ids) == len(set(ids)), 'duplicate case id'
for c in cases:
    assert c['t'] in tkeys, (c['id'], c['t'])
    for k in c.get('also', []): assert k in tkeys and k != c['t'], (c['id'], 'also', k)
cid = set(ids)
# the block's 2026 class reviewer, case by case (shown collapsed in each case card)
CASEBY = {c['id']: c for c in cases}
for k, v in load('dg_reviewer.json').items():
    assert k in cid, 'class-reviewer text for unknown case ' + k
    CASEBY[k]['dg'] = v

# memory hooks: 1 to 3 words per case, colour-coded by outcome (ok upheld, no struck down, sun procedure or twist, acc principle)
HOOKS = json.load(open(os.path.join(DATA, 'case_hooks.json')))
for c in cases:
    h = HOOKS.get(c['id']); assert h, 'no hook for case ' + c['id']
    assert 1 <= len(h['k'].split()) <= 3 and h['c'] in ('ok', 'no', 'sun', 'acc'), ('bad hook', c['id'], h)
    c['hk'], c['hc'] = h['k'], h['c']
assert not set(HOOKS) - {c['id'] for c in cases}, 'hook for unknown case'
# detailed summaries (three-level case cards): id -> {iss: [{q, a, why}], vote?, ops?}; only for cards whose case has a digest
ISS = json.load(open(os.path.join(DATA, 'case_iss.json')))
for k, v in ISS.items():
    assert k in CASEBY, 'detailed summary for unknown case ' + k
    assert v['iss'] and all(set(i) == {'q', 'a', 'why'} and all(i.values()) for i in v['iss']), ('bad detailed summary', k)
    CASEBY[k].update({x: v[x] for x in ('iss', 'vote', 'ops') if v.get(x)})

# rule maps: link every case mention to its card (see caselink.py)
import sys; sys.path.insert(0, HERE)
import caselink, figures
rv_files = sorted(glob.glob(os.path.join(DATA, 'reviewer', '*.html')))
# diagrams (figures.py) go in first, so the case names inside them are linked too
rv_src = {f: figures.insert(open(f).read(), os.path.basename(f)[:2]) for f in rv_files}
print(f'diagrams: {sum(s.count(chr(60) + "figure class=") for s in rv_src.values())}, walk-through fact patterns: {sum(s.count("class=" + chr(34) + "fact" + chr(34)) for s in rv_src.values())}')
link_texts = {}
for f in rv_files:
    for c, t in re.findall(r'<a class="cref" data-c="([^"]+)"[^>]*>(.*?)</a>', rv_src[f]):
        t = html.unescape(re.sub('<[^>]+>', '', t)).strip(); link_texts.setdefault(t, set()).add(c)
link_texts = {t: next(iter(v)) for t, v in link_texts.items() if len(v) == 1 and re.search('[A-Z]', t) and t != 'case card'}
CASEMAP = {c['id']: c for c in cases}
ALIASES = caselink.build_aliases(CASEMAP, link_texts)
linked, parts, leftover = {}, [], []
for f in rv_files:
    src = caselink.link_file(rv_src[f], os.path.basename(f)[:2], ALIASES, CASEMAP, linked)
    leftover += [(os.path.basename(f)[:2], v) for v in caselink.unlinked_vs(src)]
    parts.append(src)
rev = '\n'.join(parts)
print(f'case links added: {sum(linked.values())} mentions of {len(linked)} cases')
for fp, v in leftover: print(f'  note: unlinked mention in rule map {fp}: {v}')
for m in re.findall(r'data-c="([^"]+)"', rev):
    assert m in cid, 'reviewer cites unknown case ' + m
ids_in_rev = set(re.findall(r' id="([^"]+)"', rev))
for m in re.findall(r'class="xref" data-h="([^"]+)"', rev):
    assert m in ids_in_rev, 'diagram link to a missing id ' + m

# lists and requisites (one file per group; validated against topics, cases and rule-map ids)
lists = []
for f in sorted(glob.glob(os.path.join(DATA, 'lists', '*.json'))):
    lists += json.load(open(f))
lid = [l['id'] for l in lists]
assert len(lid) == len(set(lid)), 'duplicate list id'
for l in lists:
    assert l['t'] in tkeys, (l['id'], l['t'])
    assert 2 <= len(l['items']) <= 12 and l['title'] and l['ask'], l['id']
    for c in l.get('cases', []): assert c in cid, (l['id'], c)
    if l.get('rv'): assert ('id="%s"' % l['rv']) in rev, (l['id'], l['rv'])

mcq = load('exams/mcq.json'); stories = load('exams/stories.json'); issues = load('exams/issues.json')['groups']
iid = {i['id'] for g in issues for i in g['items']}
for q in mcq:
    assert 0 <= q['a'] < len(q['c']), q['id']
    assert q['t'] in tkeys, (q['id'], q['t'])
    assert not q.get('story') or q['story'] in stories, q['id']
    for c in q.get('cs', []): assert c in cid, (q['id'], c)

SHORT = {
    'e23m-1': 'Teves expulsion', 'e23m-2': 'Manila cinema free screen time', 'e23m-3': 'Tax Code oversight committee',
    'e23m-4': 'Disqualifying debate no-shows', 'e24m-1': 'Garcia’s party-list proposals', 'e24m-2': 'RA 12006 entrance-exam fee waiver',
    'e24m-3': 'Bulacan Freeport IRR clause', 'e24m-4': 'RA 10530 and Liban v. Gordon', 'e15f-1': 'Ombudsman and absent lawmakers',
    'e15f-2': 'No Bio, No Boto', 'e15f-3': 'October 31 registration deadline', 'e20f-2': 'Senate vs. IRRs',
    'e20f-4': 'Ombudsman case over the PAO rider', 'e20f-6': 'PAO lab MOOE and DBM reorganization', 'e20f-7': 'Rep. Suarez: discipline and immunity',
    'e20f-8': 'Nasino and mootness', 'e20f-1': 'Rodriguez: impeachment only?', 'e20f-3': 'Amparo against red-tagging', 'e20f-5': 'SB 982: designated survivor', 'e20f-9': 'Weaponized search warrants', 'e24f-3': 'OVP vs House subpoena to COA', 'e24f-1': 'RA 12077 student loan moratorium', 'e24f-2': 'PhilHealth subsidy options',
    'e23f-1': 'ICC entry petition in Calbayog', 'n26-1': 'Kapatiran: Congress must ban dynasties', 'n26-2': 'Impeachment: who counts as ‘all the Members’',
    'n26-3': 'Dela Rosa and Senate ‘protective custody’', 'n26-4': 'RA 12326: BSKE moved to 2028', 'n26-5': 'Unprogrammed appropriations',
    'n26-6': 'A 2027 GOCC fund sweep', 'n26-7': 'Challenging a dynasty law',
}
essays = []
for e in load('exams/essays.json'): essays.append({**e, 'news': False})
for e in load('exams/news.json'): essays.append({**e, 'news': True})
for e in essays:
    e['short'] = SHORT[e['id']]
    assert sum(p[1] for p in e['points']) == 10, e['id']
    for i in e['issues']: assert i in iid, (e['id'], i)
    for c in e['cases']: assert c in cid, (e['id'], c)
    for t in e['t']: assert t in tkeys, (e['id'], t)
clear = load('exams/clear.json') if os.path.exists(os.path.join(DATA, 'exams', 'clear.json')) else {}
for e in essays:
    c = clear.get(e['id'])
    if c:
        assert set(c) <= set('CLEAR') and all(c.get(k) for k in 'CLAR'), e['id']
        n = sum(len(v.split()) for v in c.values()); assert n <= 125, (e['id'], n)
        e['clear'] = c
eid = {e['id'] for e in essays}
for m in re.findall(r'data-e="([^"]+)"', rev):
    assert m in eid, 'reviewer cites unknown essay ' + m

# numbers table from the method section
meth = open(os.path.join(DATA, 'reviewer', '00_method.html')).read()
tbl = meth[meth.find('id="method-numbers"'):]
numbers = [[html.unescape(re.sub('<[^>]+>', '', a)), html.unescape(re.sub('<[^>]+>', '', b))]
           for a, b in re.findall(r'<tr><td>(.*?)</td><td>(.*?)</td></tr>', tbl)]

# finals: the whole syllabus with full digests (site/data/finals, built by finals-intake/tools/digest_data.py)
import base64
FIN = load('finals/syllabus.json')['entries']
FDZ = open(os.path.join(DATA, 'finals', 'digests.json.gz'), 'rb').read()
import gzip as _gz
_fd = json.loads(_gz.decompress(FDZ))
# finals cards say which syllabus line(s) they belong to ('sy': citation prefixes); link them so the card opens the digest
for c in cases:
    for pre in c.get('sy', []):
        hits = [e for e in FIN if 'c' in e and e['c'].startswith(pre)]
        assert hits, ('card points to no syllabus line', c['id'], pre)
        for e in hits:
            assert e.get('card') in (None, c['id']), ('syllabus line already linked to another card', pre, e.get('card'), c['id'])
            e['card'] = c['id']
for e in FIN:
    if e.get('card'): assert e['card'] in cid, ('syllabus entry links an unknown card', e['card'])
    for i in e.get('d', []): assert i in _fd, ('syllabus entry links an unknown digest', i)
assert all(e['d'] for e in FIN if e.get('f')), 'a finals case has no digest'
print(f'finals: {sum(1 for e in FIN if e.get("f"))} syllabus cases, {len(_fd)} full digests ({len(FDZ)//1024} KB gzip)')

# the syllabus as written (for the printed reviewer): page numbers, the opening quotes and the closing ornament dropped,
# wrapped lines (URLs, dates) rejoined, whitespace runs collapsed. Each line: [kind, indent level, text].
def syllabus_lines():
    raw = open(os.path.join(HERE, '..', '..', 'sources', 'finals', 'syllabus.txt'), encoding='utf-8').read().split('\n')
    out, blank, skip = [], True, False
    MONTH = r'(January|February|March|April|May|June|July|August|September|October|November|December)\b'
    for ln in raw:
        if '\u201cWithout commitment' in ln: skip = True
        if skip:
            if 'Rocky II' in ln: skip = False
            continue
        if re.fullmatch(r'\s{15,}\d+\s*', ln) or ln.strip() in ('\u0398\u03ac\u03bd\u03b1\u03c4\u03bf\u03c2',):
            continue
        if not ln.strip():
            blank = True; continue
        ind = len(ln) - len(ln.lstrip()); t = re.sub(r'\s{2,}', ' ', ln.strip())
        conn = bool(out) and re.search(r'(\b(AND|THE|OF|IN|ON|TO|FOR|THAN|AN|A|DUTERTE)|\b[A-Z]{2,}:)$', out[-1][2]) and t[:1].isupper() and t.split()[0].isupper()  # an ALL-CAPS title wrapped across a gap
        if out and (conn or (not blank and (t[0].islower() or t.startswith(('http', 'www')) or out[-1][2].endswith(('-', ',', ';', 'G.R.')) or t.startswith('No. ') or re.search(r'\b(AND|THE|OF|IN|ON|TO|FOR|THAN|AN|A)$', out[-1][2]) or (re.match(MONTH, t) and re.search(r'\d$', out[-1][2]))))):
            out[-1][2] += ('' if out[-1][2].endswith('-') else ' ') + t
        else:
            kind = 'h0' if re.match(r'(I|II|III|IV|V|VI|VII|VIII)\.\s', t) else 'h1' if re.match(r'[A-H]\.\s', t) else 'h2' if re.match(r'\d{1,2}\.\s', t) else 'h3' if re.match(r'[a-z]\.\s', t) else 'h4' if re.match(r'\(\d+\)\s', t) else 'p'
            out.append([kind, 0 if ind < 5 else 1 if ind < 11 else 2 if ind < 17 else 3, t])
        blank = False
    return out
syl_lines = syllabus_lines()
assert len(syl_lines) > 300 and not any(re.fullmatch(r'\d+', l[2]) for l in syl_lines)

# downloadable PDFs (site/app/make_pdfs.js writes them and this manifest; they are published next to the page under pdf/)
PDFM = os.path.join(HERE, '..', 'print', 'pdf', 'manifest.json')
pdfs = json.load(open(PDFM)) if os.path.exists(PDFM) else {}
D = dict(examDate='2026-12-16', pdfs=pdfs, syl=syl_lines, fin=FIN, topics=topics, cases=cases, lists=lists, mcq=mcq, stories=stories, essays=essays, issues=issues, numbers=numbers)
t = open(os.path.join(HERE, 'template.html')).read()
t = t.replace('__CSS__', open(os.path.join(HERE, 'style.css')).read())
t = t.replace('__REVIEWER__', rev)
t = t.replace('__JS__', open(os.path.join(HERE, 'app.js')).read())
t = t.replace('__FDZ__', base64.b64encode(FDZ).decode())
t = t.replace('__DATA__', J(D))
assert '__DATA__' not in t and '__JS__' not in t and '__REVIEWER__' not in t and '__FDZ__' not in t
os.makedirs(os.path.dirname(os.path.abspath(A.out)), exist_ok=True)
open(A.out, 'w').write(t)
print(f'wrote {A.out}: {len(t):,} bytes · {len(cases)} cases ({sum(c["a"] for c in cases)} anchors, {sum(1 for c in cases if c.get("dg"))} with class-reviewer text) · {len(lists)} lists · {len(mcq)} MCQs · {len(essays)} essays · {len(numbers)} numbers')
