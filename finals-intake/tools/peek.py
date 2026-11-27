import sys, docx, collections
from docx.oxml.ns import qn
for f in sys.argv[1:]:
    d = docx.Document(f)
    body = d.element.body
    nP = len(body.findall(qn('w:p'))); nT = len(body.findall(qn('w:tbl')))
    styles = collections.Counter(p.style.name for p in d.paragraphs if p.text.strip())
    heads = [(p.style.name, p.text.strip()[:90]) for p in d.paragraphs if p.text.strip() and (p.style.name.lower().startswith(('heading', 'title')))]
    print('==', f.split('/')[-1], 'paras', nP, 'tables', nT, 'styles', styles.most_common(6))
    for h in heads[:12]: print('   ', h)
    print('    ... headings total', len(heads))
