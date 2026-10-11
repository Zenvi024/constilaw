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
# the block's 2026 class reviewer, case by case (shown collapsed in each case card)
CASEBY = {c['id']: c for c in cases}
for k, v in load('dg_reviewer.json').items():
    assert k in cid, 'class-reviewer text for unknown case ' + k
    CASEBY[k]['dg'] = v

rev = '\n'.join(open(f).read() for f in sorted(glob.glob(os.path.join(DATA, 'reviewer', '*.html'))))
for m in re.findall(r'data-c="([^"]+)"', rev):
    assert m in cid, 'reviewer cites unknown case ' + m

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

# day plan: the week of Oct 11 (mirrors the study blocks on Zen's Google Calendar)
R = lambda *a: list(a)
P = lambda k, t, **kw: dict(k=k, t=t, **kw)
plan = [
    dict(date='2026-10-11', short='Sun 11', label='Sunday, October 11', focus='Tue class prep, then judicial review', items=[
        P('4:30 PM', 'Tue class prep 1/5: read and digest cases 1–5 (facts, issue, ruling, one-line doctrine). Star the hard ones.'),
        P('7:00 PM', 'Tue class prep 2/5: cases 6–12. Five-minute break after case 9.'),
        P('10:30 PM', 'Exam method: format, the four question shapes, ALAC, the checklist.', rv=R('method')),
        P('10:50 PM', 'Judicial review, part 1: requisites and every type of standing. Then list the standing types from memory.', rv=R('jr')),
        P('11:35 PM', 'Drill Case → rule, Judicial review (one round of 20). Sleep at 12.', go='drill:cr:jr', goL='Start the drill')]),
    dict(date='2026-10-12', short='Mon 12', label='Monday, October 12', focus='Judicial review, interpretation, government, suffrage', items=[
        P('8:00 AM', 'Commute (phone): due cards, then Facts → case for Judicial review.', go='drill:fc:jr', goL='Facts → case drill'),
        P('11:30 AM', 'Tue class prep 3–4/5: digest cases 13–20, clean up every digest, write a likely recit question per starred case.'),
        P('3:30 PM', 'Commute home (phone): the 2015 multiple-choice midterm; retake the misses.', go='mcq:2015 Midterm', goL='Start 2015 MCQs'),
        P('4:30 PM', 'Judicial review, part 2: political questions, mootness exceptions, effects, forum.', rv=R('jr-pq', 'jr-effects', 'jr-forum')),
        P('5:15 PM', 'Write and grade (22 min + 15).', e=R('e20f-8')),
        P('7:00 PM', 'Interpreting and amending the Constitution, including the Kapatiran 2026 box.', rv=R('interp')),
        P('8:15 PM', 'Government, immunity and inherent powers: police power versus taking.', rv=R('gov')),
        P('9:30 PM', 'Suffrage: qualifications versus registration.', rv=R('suff')),
        P('10:00 PM', 'Write and grade two answers.', e=R('e23m-2', 'e15f-2')),
        P('11:20 PM', 'Drill Case → rule for these topics, then all due cards.', go='drill:cr:basics,gov,suff', goL='Start the drill')]),
    dict(date='2026-10-13', short='Tue 13', label='Tuesday, October 13', focus='Consti class day; Congress structure', items=[
        P('9:00 AM', 'Commute (phone): due cards, then the issue spotter.', go='due', goL='Review due cards', sp=R('n26-1', 'e15f-3')),
        P('12:00 PM', 'Tue class prep 5/5: recite each starred case out loud in under 60 seconds.'),
        P('3:00 PM', 'Commute home (phone): the 2016 multiple-choice midterm.', go='mcq:2016 Midterm', goL='Start 2016 MCQs'),
        P('4:00 PM', 'Thu class prep 1/6: digest cases 1–5.'),
        P('7:00 PM', 'Thu class prep 2/6: digest cases 6–10.'),
        P('9:10 PM', 'Congress: composition, party-list, qualifications and elections.', rv=R('comp')),
        P('10:30 PM', 'Congress: officers, quorum, discipline, the Journal. Read the Teves box twice.', rv=R('internal')),
        P('11:15 PM', 'Write and grade.', e=R('e23m-1'))]),
    dict(date='2026-10-14', short='Wed 14', label='Wednesday, October 14', focus='Thu class prep; powers, appropriations, tax', items=[
        P('8:00 AM', 'Commute (phone): due cards, then Case → rule for Congress.', go='drill:cr:house,org,et', goL='Start the drill'),
        P('11:30 AM', 'Thu class prep 3–4/6: digest cases 11–20 (break at 1:15 PM).'),
        P('5:00 PM', 'Commute home (phone): read the privileges rule map.', rv=R('priv')),
        P('7:00 PM', 'Thu class prep 5/6: finish and clean up every digest.'),
        P('8:30 PM', 'Electoral tribunals and the CA.', rv=R('et')),
        P('9:00 PM', 'Powers of Congress: limits, ABAKADA, delegation and IRRs, the title rule. Highest-yield block of the week.', rv=R('powers')),
        P('10:15 PM', 'Appropriation and tax laws.', rv=R('money')),
        P('11:15 PM', 'Write and grade.', e=R('e23m-3'))]),
    dict(date='2026-10-15', short='Thu 15', label='Thursday, October 15', focus='Consti class day; timed set; printables', items=[
        P('9:00 AM', 'Commute (phone): the 2013 multiple-choice midterm.', go='mcq:2013 Midterm', goL='Start 2013 MCQs'),
        P('12:00 PM', 'Thu class prep 6/6: recit rehearsal.'),
        P('3:00 PM', 'Commute home (phone): Rule → case for powers, appropriations and tax.', go='drill:rc:powers,approp,tax', goL='Start the drill'),
        P('4:00 PM', 'Write and grade three answers, 40 minutes each.', e=R('e24m-1', 'e24m-4', 'e24m-3')),
        P('7:00 PM', 'Timed set under exam conditions: four news problems in 90 minutes on one sheet. Grade them from 8:30 PM.', e=R('n26-2', 'n26-3', 'n26-4', 'n26-5')),
        P('9:15 PM', 'The 2026 news watch, then re-read your weakest rule map. No new material after this.', rv=R('news')),
        P('10:15 PM', 'Printables twice, then an anchors-only Rule → case drill.', go='print', goL='Open printables'),
        P('11:30 PM', 'Due cards; pack yellow paper, pens, ID. Sleep by 12.', go='due', goL='Review due cards')]),
    dict(date='2026-10-16', short='Fri 16', label='Friday, October 16', focus='Midterm, 10:00–11:30 AM', items=[
        P('6:00 AM', 'Due cards, then an anchors-only Case → rule drill.', go='drill:cr:anchors', goL='Anchors drill'),
        P('7:00 AM', 'Issue checklist and numbers. Outline two problems in the margin without writing them out, then check the model answers.', go='print', goL='Open printables', sp=R('e23m-4', 'n26-7')),
        P('8:00 AM', 'Anchor-case list and the last-minute checklist of each rule map.', rv=R('method')),
        P('9:00 AM', 'Commute: the two printables only.'),
        P('10:00 AM', 'Midterm: 90 minutes, about 22 per problem. Answer first, ALAC, half a page each. Read every fact.')]),
]
for d in plan:
    for it in d['items']:
        for e in it.get('e', []) + it.get('sp', []): assert e in eid, e
        for r in it.get('rv', []): assert ('id="%s"' % r) in rev, r

D = dict(examDate='2026-10-16', topics=topics, cases=cases, lists=lists, mcq=mcq, stories=stories, essays=essays, issues=issues, numbers=numbers, plan=plan)
t = open(os.path.join(HERE, 'template.html')).read()
t = t.replace('__CSS__', open(os.path.join(HERE, 'style.css')).read())
t = t.replace('__REVIEWER__', rev)
t = t.replace('__JS__', open(os.path.join(HERE, 'app.js')).read())
t = t.replace('__DATA__', J(D))
assert '__DATA__' not in t and '__JS__' not in t and '__REVIEWER__' not in t
os.makedirs(os.path.dirname(os.path.abspath(A.out)), exist_ok=True)
open(A.out, 'w').write(t)
print(f'wrote {A.out}: {len(t):,} bytes · {len(cases)} cases ({sum(c["a"] for c in cases)} anchors, {sum(1 for c in cases if c.get("dg"))} with class-reviewer text) · {len(lists)} lists · {len(mcq)} MCQs · {len(essays)} essays · {len(numbers)} numbers')
