import sys, json, os, re, collections
sys.path.insert(0, sys.argv[3]); from parse import all_text_docx
r = json.load(open(sys.argv[2])); W = lambda s: collections.Counter(re.findall(r"\w+", s.lower()))
bad = 0
for f, txt in r.items():
    miss = W(all_text_docx(os.path.join(sys.argv[1], f))) - W(txt)
    miss = {k: v for k, v in miss.items() if True}
    if miss: bad += 1; print(f[:40], 'MISSING', dict(list(miss.items())[:15]))
print('rendered cases missing words:', bad, 'of', len(r))
