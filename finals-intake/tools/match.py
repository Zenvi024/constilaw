"""Match syllabus case entries to digests, full-text decisions, midterm desk cards and Recit Deck digests."""
import json, re, os, sys, glob, unicodedata
ROOT = '/home/user/constilaw'
syl = json.load(open('../syllabus.json')); dig = json.load(open('../digest_index.json'))
STOP = set('the of and et al inc jr sr ii iii iv hon chief justice mr mrs ms ma s in re matter petition for writ a an on to by philippines co corp'.split())
ALIAS = {'coa': 'commission audit', 'csc': 'civil service commission', 'comelec': 'commission elections', 'hor': 'house representatives', 'hr': 'house representatives',
         'jbc': 'judicial bar council', 'op': 'office president', 'ca': 'court appeals', 'cir': 'commissioner internal revenue', 'denr': 'environment natural resources',
         'sbma': 'subic bay metropolitan authority', 'ptc': 'philippine truth commission', 'meco': 'manila economic cultural office', 'leb': 'legal education board',
         'pet': 'presidential electoral tribunal', 'mwss': 'manila waterworks sewerage system', 'oca': 'office court administrator', 'tidcorp': 'trade investment development corporation',
         'dbp': 'development bank', 'nea': 'national electrification administration', 'eiib': 'eiib', 'ibp': 'integrated bar', 'tricomm': 'tricomm', 'grp': 'government', 'meralco': 'manila electric'}
def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\bvs?\.?\b', ' v ', s); s = re.sub(r'[^a-z0-9 ]+', ' ', s)
    return [ALIAS.get(w, w) for w in s.split()]
def sides(title):
    t = re.sub(r'\(.*?\)|,?\s*(g\.?\s*r\.?|a\.?\s*m\.?|a\.?\s*c\.?|b\.?\s*m\.?|udk|jgr|p\.?e\.?t\.?)\b.*$', ' ', title, flags=re.I)
    t = re.sub(r',?\s*\d+\s+(scra|phil|u\.s\.)\b.*$', ' ', t, flags=re.I)
    w = ' '.join(norm(t)).split()
    if 'v' in w:
        i = w.index('v'); L, R = w[:i], w[i+1:]
    else: L, R = w, []
    sig = lambda ws: [x for x in ws if x not in STOP and not x.isdigit() and len(x) > 1]
    return sig(L), sig(R)
def years(t):
    ys = [int(y) for y in re.findall(r'(?<![\d-])(1[89]\d\d|20[0-2]\d)(?![\d-])', t)]
    return ys
def score(a, b):
    (aL, aR), (bL, bR) = a, b
    if not aL or not bL: return 0
    l = any(x[:5] == y[:5] for x in aL[:2] for y in bL[:2])
    if not l: return 0
    if not aR or not bR: return 1
    r = len(set(x[:5] for x in aR) & set(y[:5] for y in bR))
    return 2 if r else 0.5
def yr_ok(sy, ty):
    return not sy or not ty or any(abs(a - b) <= 1 for a in sy for b in ty)
# other sources
decs = [p for p in glob.glob(ROOT + '/sources/finals/sources_zip/D_decisions/**/*.pdf', recursive=True)]
dec_items = [(os.path.relpath(p, ROOT + '/sources/finals/sources_zip/D_decisions'), sides(os.path.basename(os.path.dirname(p)) if '_REQUIRED' in p else os.path.basename(p)), years(os.path.basename(os.path.dirname(p)) + os.path.basename(p))) for p in decs]
mid = []
for f in sorted(glob.glob(ROOT + '/site/data/cases/*.json')):
    for c in json.load(open(f)): mid.append((f'{c["n"]} ({c["y"]})', sides(c['n']), [int(c['y'])] if str(c['y']).isdigit() else []))
deck = []
for f in glob.glob(ROOT + '/recit/2026-11-03/data/*.json'):
    for c in json.load(open(f)): deck.append((c['title'], sides(c['title']), years(c['title'])))
import docx
from docx.oxml.ns import qn
def nums(t):
    t = t.replace('–', '-')
    a = set(re.findall(r'(?<![\d-])(?:L-)?(\d{5,6})(?![\d])', t))
    a |= set(re.findall(r'(?<![\d])(\d{2}-\d{1,2}-\d{2}-[A-Z0-9]+|RTJ-\d{2}-\d{4}|SB-\d{2}-\d{2}-J)', t))
    return a
NUMIDX = {}
for d in dig:
    if d['kind'] != 'single': continue
    fp = ROOT + '/sources/finals/digests_zip/' + d['file']
    doc = docx.Document(fp); txt = ' '.join(x.text or '' for x in doc.element.body.iter(qn('w:t')))[:6000]
    d['nums'] = sorted(nums(txt))
rows = []; seen_finals = False
for o in syl:
    if o['type'] != 'case': continue
    t = o['text']
    if t.startswith('Fabian v. Desierto'): seen_finals = True
    s = sides(t); ys = years(t)
    excluded = any(p.startswith('IV.') for p in o['path']) and any(('A. Territory' in p) or ('1. Citizenship' in p) for p in o['path'])
    def best(items):
        hits = []
        for name, sd, ty in items:
            sc = score(s, sd)
            if sc >= 1 and yr_ok(ys, ty): hits.append((sc, name))
        mx = max([h[0] for h in hits], default=0)
        return [n for sc, n in hits if sc == mx]
    dhits = []
    for d in dig:
        sd = sides(d['title']); sc = score(s, sd)
        if sc >= 1 and yr_ok(ys, years(d['title'])): dhits.append((sc, d))
    mx = max([h[0] for h in dhits], default=0); dhits = [d for sc, d in dhits if sc == mx]
    sn = nums(t)
    if sn:
        byn = [d for d in dig if d.get('nums') and sn & set(d['nums'])]
        for d in byn:
            if d not in dhits: dhits.append(d)
    rows.append({'cite': t, 'path': o['path'], 'finals': seen_finals, 'excluded': excluded,
                 'own': sorted({d['file'] for d in dhits if d['file'].startswith(('my_digests', 'other')) and 'Masterfile' not in d['file']}),
                 'block': sorted({d['file'] + ' :: ' + d['title'] for d in dhits if 'block_digests' in d['file'] or 'Rubi' in d['file']}),
                 'decision': best(dec_items), 'midterm_card': best(mid), 'deck': best(deck)})
json.dump(rows, open('../coverage.json', 'w'), ensure_ascii=False, indent=1)
F = [r for r in rows if r['finals']]
print('finals entries', len(F), 'own', sum(1 for r in F if r['own']), 'block', sum(1 for r in F if r['block']), 'none', sum(1 for r in F if not r['own'] and not r['block']), 'fulltext', sum(1 for r in F if r['decision']))
M = [r for r in rows if not r['finals']]
print('midterm entries', len(M), 'excluded', sum(r['excluded'] for r in M), 'with card', sum(1 for r in M if r['midterm_card']))
for r in F:
    if not r['own'] and not r['block']: print('  NO DIGEST:', r['cite'][:100])

# ---- manual corrections after review (number matching picked up cross-cited cases; syllabus typos) ----
FIX = {  # cite prefix -> (remove substrings, add files)
    'Gutierrez v. The House': (['In_re_Production'], []),
    'Pormento v. Estrada': (['Risos-Vidal'], []),
    'Republic v. Sandiganbayan, G.R. No. 152154': (['Marcos_Jr_v_Republic', "[01] Zen"], []),
    'De Leon v. Duterte': (['De_Lima'], []),
    'De Lima v. Duterte': (['De_Leon'], []),
    'Re: COA Opinion': (['Special_Audit'], []),
    'The Special Audit Team': (['Re_COA_Opinion'], []),
    'In Re: Production of Court Records': (['OCA_v_Fuentes'], []),
    'Dulay v. Judicial': (['Adaza'], []),
    'Republic v. Sereno, G.R. No. 237428, May 11, 2018': (['Resolution'], []),
    'Zaldivar v. Gonzales': ([], ['my_digests/Zaldivar_v_Sandiganbayan_Digest.docx']),
    'In re: IBP Elections': ([], ['my_digests/In_re_1989_IBP_Elections_Digest.docx']),
}
rows = json.load(open('../coverage.json'))
for r in rows:
    for k, (rem, add) in FIX.items():
        if r['cite'].startswith(k):
            r['own'] = [o for o in r['own'] if not any(x in o for x in rem)] + [a for a in add if a not in r['own']]
            r['block'] = [b for b in r['block'] if not any(x in b for x in rem)]
            r['fixed'] = True
json.dump(rows, open('../coverage.json', 'w'), ensure_ascii=False, indent=1)
F = [r for r in rows if r['finals']]
print('AFTER FIX: finals', len(F), 'with own', sum(1 for r in F if r['own']), 'block only', sum(1 for r in F if not r['own'] and r['block']), 'none', sum(1 for r in F if not r['own'] and not r['block']))
