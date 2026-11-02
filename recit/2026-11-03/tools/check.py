import sys, json, glob, os, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse import all_text_docx
cases = json.load(open(sys.argv[2]))
def ext(c):
    T=[c['title']] + [p['text'] for p in c.get('subtitle', [])]
    for h in c['headnote']: T.append(h['label']); T += [p['text'] for p in h['paras']]
    for s in c['sections']:
        T.append(s.get('label','')); T.append(s.get('kindLabel',''))
        for k in ('question','answer','write'): T += [p['text'] for p in s.get(k,[])]
        for sb in s.get('subs',[]): T += [p['text'] for p in sb['q']+sb['a']]
        for pt in s['parts']: T.append(pt['h']); T += [p['text'] for p in pt['paras']]
    T += [p['text'] for p in c['front']+c['back']]
    return ' '.join(T)
W = lambda s: collections.Counter(re.findall(r"\w+", s))
bad=0
for c in cases:
    a = W(all_text_docx(os.path.join(sys.argv[1], c['file']))); b = W(ext(c))
    miss = a - b; extra = b - a
    miss = {k:v for k,v in miss.items() if k not in ('WRITE','FRONT','BACK','FACTS','FINAL','DECISION','ISSUE')}
    if miss or extra: bad+=1; print(c['file'][:40], 'MISSING', dict(list(miss.items())[:12]), 'EXTRA', dict(list(extra.items())[:8]))
print('cases with differences:', bad, 'of', len(cases))
