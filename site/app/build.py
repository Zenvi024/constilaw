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
cid = set(ids)

rev = '\n'.join(open(f).read() for f in sorted(glob.glob(os.path.join(DATA, 'reviewer', '*.html'))))
for m in re.findall(r'data-c="([^"]+)"', rev):
    assert m in cid, 'reviewer cites unknown case ' + m

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
    'e20f-8': 'Nasino and mootness', 'e24f-1': 'RA 12077 student loan moratorium', 'e24f-2': 'PhilHealth subsidy options',
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
eid = {e['id'] for e in essays}
for m in re.findall(r'data-e="([^"]+)"', rev):
    assert m in eid, 'reviewer cites unknown essay ' + m

# numbers table from the method section
meth = open(os.path.join(DATA, 'reviewer', '00_method.html')).read()
tbl = meth[meth.find('id="method-numbers"'):]
numbers = [[html.unescape(re.sub('<[^>]+>', '', a)), html.unescape(re.sub('<[^>]+>', '', b))]
           for a, b in re.findall(r'<tr><td>(.*?)</td><td>(.*?)</td></tr>', tbl)]

# day plan (from the prep plan, adjusted to 22-minute answers)
R = lambda *a: list(a)
plan = [
    dict(date='2026-10-08', short='Thu 8', label='Thursday, October 8', focus='Set-up and diagnostic', items=[
        dict(k='Read', t='How to answer his midterm: format, the four question shapes, ALAC, the checklist.', rv=R('method')),
        dict(k='Diagnose', t='Take the 2016 multiple-choice midterm cold to see where you stand.', go='mcq:2016 Midterm', goL='Start 2016 MCQs'),
        dict(k='News', t='Skim the 2026 news watch: these stories are likely exam material.', rv=R('news'))]),
    dict(date='2026-10-09', short='Fri 9', label='Friday, October 9', focus='Block A: judicial review, interpretation, amendment', items=[
        dict(k='Write cold', t='Before studying: 22 minutes each, handwritten, then grade against the rubric.', e=R('e24m-2', 'e24m-3')),
        dict(k='Learn', t='Separation of powers, political questions, actual case, ripeness, mootness, all standing types, earliest opportunity, lis mota. Then interpretation and amendment (Javellana, Lambino, Francisco).', rv=R('jr', 'interp')),
        dict(k='Drill', t='Case → rule for judicial review and interpretation.', go='drill:jr,basics', goL='Drill Block A'),
        dict(k='Evening', t='2015 midterm as quick multiple choice.', go='mcq:2015 Midterm', goL='Start 2015 MCQs')]),
    dict(date='2026-10-10', short='Sat 10', label='Saturday, October 10', focus='Block B: state, people, government', items=[
        dict(k='Review', t='20 minutes of due cards first.', go='due', goL='Review due cards'),
        dict(k='Learn', t='Inherent powers (police power versus taking), immunity from suit, de facto government, citizenship, suffrage, territory.', rv=R('gov', 'cit', 'suff', 'terr')),
        dict(k='Write', t='22 minutes each.', e=R('e23m-2', 'e15f-2')),
        dict(k='Drill', t='Facts → case for Block B.', go='drill:gov,cit,suff,terr', goL='Drill Block B')]),
    dict(date='2026-10-11', short='Sun 11', label='Sunday, October 11', focus='Block C: Congress structure', items=[
        dict(k='Review', t='20 minutes of due cards first.', go='due', goL='Review due cards'),
        dict(k='Learn', t='Party-list (Atong Paglaum to Duterte Youth), qualifications, elections, officers and quorum, discipline, privileges, incompatible offices, electoral tribunals, CA.', rv=R('comp', 'internal', 'priv', 'et')),
        dict(k='Write', t='22 minutes each.', e=R('e23m-1', 'e23m-4', 'e24m-1')),
        dict(k='Drill', t='Case → rule for Congress.', go='drill:house,org,et', goL='Drill Block C')]),
    dict(date='2026-10-12', short='Mon 12', label='Monday, October 12', focus='Block D: powers of Congress', items=[
        dict(k='Review', t='20 minutes of due cards first.', go='due', goL='Review due cards'),
        dict(k='Learn', t='Plenary power and limits, delegation and ABAKADA, title rule, the appropriations line (Demetria to Macalintal 2023), tax (Tolentino, Lung Center, Garcia, John Hay).', rv=R('powers', 'money')),
        dict(k='Write', t='22 minutes each.', e=R('e23m-3', 'e24m-4', 'n26-5')),
        dict(k='Drill', t='Rule → case for powers, appropriations and tax.', go='drill:powers,approp,tax', goL='Drill Block D')]),
    dict(date='2026-10-13', short='Tue 13', label='Tuesday, October 13', focus='Class day: patch weak spots', items=[
        dict(k='Review', t='Due cards; then re-read the rule map where you missed the most.', go='due', goL='Review due cards'),
        dict(k='Write', t='One answer from your weakest block, or this news problem.', e=R('n26-3')),
        dict(k='Spot', t='Two issue-spotter rounds on problems you have not written.')]),
    dict(date='2026-10-14', short='Wed 14', label='Wednesday, October 14', focus='Timed set: four news problems in 90 minutes', items=[
        dict(k='Timed', t='Four 2026 news problems back to back, 22 minutes each, on one sheet. Grade the same day, then rewrite your two weakest.', e=R('n26-1', 'n26-2', 'n26-4', 'n26-7')),
        dict(k='Review', t='Due cards in the evening.', go='due', goL='Review due cards')]),
    dict(date='2026-10-15', short='Thu 15', label='Thursday, October 15', focus='Class day: light review', items=[
        dict(k='Read', t='The checklist and the anchor-case list only. No new material after 9:00 PM.', go='print', goL='Open printables'),
        dict(k='Optional', t='One last timed answer.', e=R('n26-6')),
        dict(k='Review', t='Due cards, then sleep.', go='due', goL='Review due cards')]),
    dict(date='2026-10-16', short='Fri 16', label='Friday, October 16', focus='Midterm (morning)', items=[
        dict(k='Before', t='45 minutes before: the checklist and anchor list. Outline one warm-up problem in your head; do not write it out.', go='print', goL='Open printables'),
        dict(k='In the room', t='90 minutes, about 22 per problem. Answer first, ALAC, half a page each. Read every fact: the stories ‘may have been altered’.', rv=R('method'))]),
]
for d in plan:
    for it in d['items']:
        for e in it.get('e', []): assert e in eid, e

D = dict(examDate='2026-10-16', topics=topics, cases=cases, mcq=mcq, stories=stories, essays=essays, issues=issues, numbers=numbers, plan=plan)
t = open(os.path.join(HERE, 'template.html')).read()
t = t.replace('__CSS__', open(os.path.join(HERE, 'style.css')).read())
t = t.replace('__REVIEWER__', rev)
t = t.replace('__JS__', open(os.path.join(HERE, 'app.js')).read())
t = t.replace('__DATA__', J(D))
assert '__DATA__' not in t and '__JS__' not in t and '__REVIEWER__' not in t
os.makedirs(os.path.dirname(os.path.abspath(A.out)), exist_ok=True)
open(A.out, 'w').write(t)
print(f'wrote {A.out}: {len(t):,} bytes · {len(cases)} cases ({sum(c["a"] for c in cases)} anchors) · {len(mcq)} MCQs · {len(essays)} essays · {len(numbers)} numbers')
