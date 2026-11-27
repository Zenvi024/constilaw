"""Syllabus (pdftotext -layout) -> ordered list of headings and case entries."""
import re, json, sys
src = open(sys.argv[1], encoding='utf-8').read().split('\n')
HEAD = re.compile(r'^\s*((?:[IVX]+\.)|(?:[A-Z]\.)|(?:\d{1,2}\.)|(?:[a-q]\.)|(?:\d\.\s))\s+\S')
CASE = re.compile(r"(^\s*In the Matter of| v\.? |\bvs\.? |^\s*\.?\s*(In [Rr]e\b|n re\b|Re:|IN RE\b)|^\s*Marcos v\.)")
READ = re.compile(r'^\s*(\d\s+DANTE|Dante|DANTE|GATMAYTAN|See |Republic Act|Executive Order|Declaration of State|Philippine Maritime|Philippine Archipelagic|Lower courts|\d Dante)')
END = re.compile(r'(\d{4}\)?\.?|issues?\)|Leonen\)|Leonen, J\., dissenting\)|\(2026\)|2018-11-15|[0-9]\)\.?|SCRA \d+|Phil\. \d+(\s*\(\d{4}\))?|available at.*|\.pdf\.?)\s*$')
out = []; path = {}; i = 0
def lvl(tok, indent=0):
    if re.match(r'\d{1,2}\.$', tok) and indent >= 17: return 4
    if re.match(r'[IVX]+\.$', tok): return 0
    if re.match(r'[A-Z]\.$', tok): return 1
    if re.match(r'\d{1,2}\.$', tok): return 2
    if re.match(r'[a-q]\.$', tok): return 3
    return 4
while i < len(src):
    raw = src[i]; s = raw.strip(); i += 1
    if not s or re.fullmatch(r'\d{1,2}', s) or s == 'Θάνατος': continue
    m = HEAD.match(raw)
    indent = len(raw) - len(raw.lstrip())
    if m and (not CASE.search(s) or (re.match(r'\d', m.group(1)) and indent >= 17)):
        tok = m.group(1).strip(); L = lvl(tok, indent)
        # 'Constitutional Commissions' etc. appear without a marker; handled below
        path = {k: v for k, v in path.items() if k < L}; path[L] = s
        out.append({'type': 'head', 'level': L, 'text': s}); continue
    if s in ('Constitutional Commissions', 'Lower courts', 'Prematurity:', 'Mootness:') or s.endswith(':') and not CASE.search(s):
        L = 1 if s == 'Constitutional Commissions' else 4
        path = {k: v for k, v in path.items() if k < L}; path[L] = s
        out.append({'type': 'head', 'level': L, 'text': s}); continue
    kind = 'case' if CASE.search(s) and not READ.match(s) else 'reading'
    s = re.sub(r'^\.\s*', '', s)
    # join wrapped lines
    while not END.search(s) and i < len(src) and src[i].strip() and not HEAD.match(src[i]) and not (CASE.search(src[i]) and not src[i].strip()[0].islower() and re.match(r'\s*[A-Z]', src[i]) and END.search(s[-3:]) ):
        nxt = src[i].strip()
        if re.fullmatch(r'\d{1,2}', nxt): i += 1; continue
        if CASE.search(nxt) and re.match(r'[A-Z]', nxt) and len(s) > 40 and re.search(r'\d{4}', nxt) and not re.match(r'(\d|[a-z])', nxt) and ' v.' in nxt[:60] and ',' in nxt: break
        s = s + ' ' + nxt; i += 1
    out.append({'type': kind, 'text': re.sub(r'\s+', ' ', s), 'path': [path[k] for k in sorted(path)]})
json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1)
print(sum(1 for o in out if o['type'] == 'case'), 'case lines;', sum(1 for o in out if o['type'] == 'reading'), 'reading lines;', sum(1 for o in out if o['type'] == 'head'), 'headings')
