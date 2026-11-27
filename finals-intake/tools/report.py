"""Re-categorize sources and write the coverage checklist (markdown + json)."""
import json, re, collections
rows = json.load(open('../coverage.json'))
for r in rows:
    if r['cite'].startswith('Gudani'):
        r['block'] += ['block_digests/[BLOCK I-B] Consti 1 Digests - Masterfile 2.docx :: GUDANI v. SENGA (2006)', 'other/Consti - Rubi to Mangudadatu.docx :: GUDANI v. SENGA (2006)']
    allsrc = r['own'] + [b.split(' :: ')[0] for b in r['block']]
    r['mine'] = sorted({s for s in r['own'] if s.startswith('my_digests/') and 'ZENS' not in s and '[01]' not in s})
    r['mine_comp'] = sorted({s for s in allsrc if 'ZENS' in s or '[01]' in s})
    r['manual'] = sorted({s for s in allsrc if 'Rubi to Mangudadatu' in s})
    r['blk'] = sorted({s for s in allsrc if s.startswith('block_digests/')})
json.dump(rows, open('../coverage.json', 'w'), ensure_ascii=False, indent=1)
F = [r for r in rows if r['finals']]
def short(c): return re.split(r',\s*(G\.\s?R|A\.M|A\.C|JGR|P\.E\.T|\d+ SCRA|\d+ Phil|Bar Matter|Res\.|Extended)', c)[0].strip()
L = ['# Finals coverage checklist', '',
     'Generated from the syllabus and the uploaded files (`sources/finals/`). Finals coverage starts right after John Hay PAC v. Lim, at V.A.7(c), and runs to the last Constitutional Commissions case.', '',
     'Columns: **Yours** = your own single-case digest files (number = versions); **Comp.** = in your compilations ([01] / 2.0); **Manual** = Rubi-to-Mangudadatu file; **Block** = block digest files; **Full text** = decision PDF gathered; **Deck** = already in the Nov 3/5 Recit Deck; **Mid card** = already has a midterm desk card.', '']
cur = None; n = 0
for r in F:
    sec = ' › '.join(p for p in r['path'] if not p.startswith(('Required', 'CONSTITUTIONAL')))
    sec = re.sub(r'\s+', ' ', sec)
    if sec != cur:
        cur = sec; L += ['', f'### {sec}', '', '| # | Case | Yours | Comp. | Manual | Block | Full text | Deck | Mid card |', '|---|---|---|---|---|---|---|---|---|']
    n += 1
    y = lambda x: str(len(x)) if x else '–'
    L.append(f"| {n} | {short(r['cite'])} | {y(r['mine'])} | {'✓' if r['mine_comp'] else '–'} | {'✓' if r['manual'] else '–'} | {y(r['blk'])} | {'✓' if r['decision'] else '–'} | {'✓' if r['deck'] else '–'} | {'✓' if r['midterm_card'] else '–'} |")
open('../FINALS_COVERAGE.md', 'w').write('\n'.join(L) + '\n')
c = collections.Counter()
for r in F:
    c['entries'] += 1
    if r['mine']: c['own single'] += 1
    elif r['mine_comp']: c['own compilation only'] += 1
    elif r['manual'] or r['blk']: c['block/manual only'] += 1
    else: c['none'] += 1
    if r['decision']: c['full text'] += 1
    if r['deck']: c['in deck'] += 1
    if r['midterm_card']: c['midterm card'] += 1
print(dict(c))
print('BLOCK/MANUAL ONLY:', [short(r['cite']) for r in F if not r['mine'] and not r['mine_comp'] and (r['manual'] or r['blk'])])
print('OWN COMPILATION ONLY:', [short(r['cite']) for r in F if not r['mine'] and r['mine_comp']])
print('MULTI-VERSION OWN:', [(short(r['cite']), len(r['mine'])) for r in F if len(r['mine']) > 1])
