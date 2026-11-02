"""Lossless digest parser: .docx -> case dict.

Every paragraph and table cell is kept, in document order, with run formatting
(highlight, shading, colour, bold, italic, underline, line breaks) and list
numbering.  Blocks are then grouped into recit sections (headnote, header WRITE,
facts, issues, decision, opinions, 5x8 card).  Anything not recognised is kept
as a generic section, so no text can be dropped.

usage: python3 -I parse.py <digest-dir> <out.json>
"""
import sys, os, re, glob, json, html
import docx
from docx.oxml.ns import qn

HL = {'yellow': 'hl-y'}
SHD = {'F8B6CF': 'hl-p', 'FFBE6B': 'hl-o'}
FG = {'1B7F4B': 'fg-g', 'C62828': 'fg-r', '1F4E9E': 'fg-b', '999999': 'fg-k'}
UNKNOWN = set()


def on(rpr, tag):
    e = rpr.find(qn(tag)) if rpr is not None else None
    if e is None: return False
    v = e.get(qn('w:val'))
    return v not in ('false', '0', 'none')


class Numbering:
    def __init__(self, d):
        self.fmt = {}
        try:
            root = d.part.numbering_part.element
        except Exception:
            return
        absn = {}
        for a in root.findall(qn('w:abstractNum')):
            lv = {}
            for l in a.findall(qn('w:lvl')):
                f = l.find(qn('w:numFmt')); t = l.find(qn('w:lvlText')); s = l.find(qn('w:start'))
                lv[int(l.get(qn('w:ilvl')))] = (f.get(qn('w:val')) if f is not None else 'bullet', t.get(qn('w:val')) if t is not None else '•', int(s.get(qn('w:val'))) if s is not None else 1)
            absn[a.get(qn('w:abstractNumId'))] = lv
        for n in root.findall(qn('w:num')):
            self.fmt[n.get(qn('w:numId'))] = absn.get(n.find(qn('w:abstractNumId')).get(qn('w:val')), {})
        self.count = {}

    def label(self, numId, ilvl):
        lv = self.fmt.get(numId, {}).get(ilvl)
        if not lv: return ('ul', '•')
        f, t, s = lv
        if f == 'bullet': return ('ul', t if t and t.strip() else '•')
        k = (numId, ilvl)
        self.count[k] = self.count.get(k, s - 1) + 1
        for (n2, l2) in list(self.count):
            if n2 == numId and l2 > ilvl: del self.count[(n2, l2)]
        n = self.count[k]
        val = {'decimal': str(n), 'lowerLetter': chr(96 + n), 'upperLetter': chr(64 + n), 'lowerRoman': roman(n).lower(), 'upperRoman': roman(n)}.get(f, str(n))
        return ('ol', re.sub(r'%\d', val, t or '%1.'))


def roman(n):
    r = ''
    for v, s in ((10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')):
        while n >= v: r += s; n -= v
    return r


def runs_of(el):
    for ch in el:
        t = ch.tag.split('}')[1]
        if t == 'r': yield ch
        elif t in ('hyperlink', 'ins', 'smartTag', 'fldSimple', 'sdt', 'sdtContent', 'customXml'): yield from runs_of(ch)


def para(p, num):
    """-> dict(html, text, list=(kind,label,level)|None)"""
    out, text = [], []
    for r in runs_of(p):
        rpr = r.find(qn('w:rPr'))
        cls = []
        if rpr is not None:
            h = rpr.find(qn('w:highlight')); s = rpr.find(qn('w:shd')); c = rpr.find(qn('w:color'))
            if h is not None:
                v = h.get(qn('w:val'))
                if v in HL: cls.append(HL[v])
                elif v not in ('none',): UNKNOWN.add(('hl', v))
            if s is not None:
                v = (s.get(qn('w:fill')) or '').upper()
                if v in SHD: cls.append(SHD[v])
                elif v not in ('', 'AUTO', 'FFFFFF'): UNKNOWN.add(('shd', v))
            if c is not None:
                v = (c.get(qn('w:val')) or '').upper()
                if v in FG: cls.append(FG[v])
                elif v not in ('1A1A1A', '000000', 'AUTO', ''): UNKNOWN.add(('fg', v))
        piece = ''
        for ch in r:
            t = ch.tag.split('}')[1]
            if t == 't': piece += html.escape(ch.text or '', quote=False); text.append(ch.text or '')
            elif t == 'tab': piece += ' '; text.append(' ')
            elif t in ('br', 'cr'): piece += '<br>'; text.append('\n')
            elif t == 'noBreakHyphen': piece += '‑'; text.append('-')
            elif t == 'sym': piece += '•'; text.append('•')
        if not piece: continue
        if on(rpr, 'w:b'): piece = f'<b>{piece}</b>'
        if on(rpr, 'w:i'): piece = f'<i>{piece}</i>'
        if on(rpr, 'w:u'): piece = f'<u>{piece}</u>'
        if on(rpr, 'w:strike'): piece = f'<s>{piece}</s>'
        if cls: piece = f'<span class="{" ".join(cls)}">{piece}</span>'
        out.append(piece)
    lst = None
    ppr = p.find(qn('w:pPr'))
    if ppr is not None and ppr.find(qn('w:numPr')) is not None:
        np_ = ppr.find(qn('w:numPr'))
        nid = np_.find(qn('w:numId')); il = np_.find(qn('w:ilvl'))
        nid = nid.get(qn('w:val')) if nid is not None else '0'; il = int(il.get(qn('w:val'))) if il is not None else 0
        if nid != '0':
            k, lab = num.label(nid, il)
            lst = [k, lab, il]
    return {'html': ''.join(out), 'text': ''.join(text), 'list': lst}


def cell_paras(tc, num):
    res = []
    for ch in tc:
        t = ch.tag.split('}')[1]
        if t == 'p':
            x = para(ch, num)
            if x['text'].strip(): res.append(x)
        elif t == 'tbl':  # nested table: flatten rows as paragraphs (keeps every word)
            for row in ch.findall(qn('w:tr')):
                for c in row.findall(qn('w:tc')):
                    res += cell_paras(c, num)
    return res


def table(tbl, num):
    rows = []
    for tr in tbl.findall(qn('w:tr')):
        row = [cell_paras(tc, num) for tc in tr.findall(qn('w:tc'))]
        rows.append(row)
    return rows


def plain(ps): return ' '.join(p['text'] for p in ps).strip()


def parse(path):
    d = docx.Document(path); num = Numbering(d)
    blocks = []
    for ch in d.element.body.iterchildren():
        t = ch.tag.split('}')[1]
        if t == 'p':
            x = para(ch, num)
            if x['text'].strip(): blocks.append(('p', x))
        elif t == 'tbl':
            blocks.append(('t', table(ch, num)))
    case = {'file': os.path.basename(path), 'title': '', 'headnote': [], 'sections': [], 'front': [], 'back': []}
    i = 0
    assert blocks[0][0] == 'p'; case['title'] = blocks[0][1]['text'].strip(); case['titleHtml'] = blocks[0][1]['html']; i = 1
    case['subtitle'] = []  # note paragraphs between the title and the headnote table
    while blocks[i][0] == 'p': case['subtitle'].append(blocks[i][1]); i += 1
    # headnote: the 3x4 table -> pairs (label, paras)
    t = blocks[i][1]; assert blocks[i][0] == 't' and plain(t[0][0]).startswith('Topic'), path
    for row in t:
        for k in range(0, len(row), 2):
            case['headnote'].append({'label': plain(row[k]), 'paras': row[k + 1] if k + 1 < len(row) else []})
    i += 1
    cur = None  # current section dict

    def new(kind, **kw):
        nonlocal cur
        cur = {'kind': kind, 'parts': [], 'write': [], **kw}
        case['sections'].append(cur); return cur

    new('headwrite', label='Headnote')
    mode = 'body'
    while i < len(blocks):
        typ, b = blocks[i]; i += 1
        if typ == 'p':
            tx = b['text'].strip()
            if tx == 'FRONT': mode = 'front'; continue
            if tx == 'BACK': mode = 'back'; continue
            if mode in ('front', 'back'): case[mode].append(b); continue
            m = re.match(r'^ISSUE\s+(\d+)\b', tx)
            if m: new('issue', num=int(m.group(1)), label=tx, kindLabel='', question=[], answer=[], subs=[]); continue
            if re.match(r'^SEPARATE OPINION', tx): new('opinions', label=tx); continue
            new('group', label=tx, labelHtml=b['html']); continue
        if mode in ('front', 'back'):  # a table inside the card area: keep its text as lines
            for row in b:
                for c in row: case[mode] += c
            continue
        rows = b; c0 = plain(rows[0][0])
        ncols = max(len(r) for r in rows)
        if c0.startswith('WRITE'):
            if re.sub(r'[\sWRITE▸:]', '', c0):  # a labelled box, e.g. "WRITE ▸ (#1.1) ▸": keep the label
                cur['write'] += [dict(p, wl=True) for p in rows[0][0]]
            elif cur['write']:  # a second WRITE box in the same section: keep it visibly separate
                cur['write'] += [dict(p, wl=True) for p in rows[0][0]]
            cur['write'] += rows[0][1] if len(rows[0]) > 1 else []
            for r in rows[1:]:
                for c in r: cur['write'] += c
            continue
        if c0 == 'FACTS' and len(rows) >= 2:
            s = new('facts', label='Facts'); s['parts'].append({'h': '', 'paras': [p for r in rows[1:] for c in r for p in c]}); continue
        if cur['kind'] == 'issue' and ncols == 3 and not cur['question']:
            r = rows[0]; cur['kindLabel'] = plain(r[0]); cur['question'] = r[1]; cur['answer'] = r[2]
            for r in rows[1:]: cur['subs'].append({'q': r[0] if r else [], 'a': [p for c in r[1:] for p in c]})
            continue
        if cur['kind'] == 'issue' and ncols == 2 and re.match(r'^\d+\.\d+', c0):
            for r in rows: cur['subs'].append({'q': r[0], 'a': [p for c in r[1:] for p in c]})
            continue
        if c0.startswith('FINAL DECISION'):
            s = new('decision', label='Final decision'); s['parts'].append({'h': '', 'paras': [p for r in rows for c in r[1:] for p in c] + [p for r in rows[1:] for p in r[0]]}); continue
        if re.match(r'^SEPARATE OPINION', c0):
            s = new('opinions', label=c0.rstrip(':')); s['parts'].append({'h': '', 'paras': [p for r in rows[1:] for c in r for p in c] + [p for c in rows[0][1:] for p in c]}); continue
        # a headed block (arguments, ruling, legal bases, framed issues, opinion of one justice …)
        if len(rows) >= 2 and ncols == 1:
            head = c0.rstrip(':'); body = [p for r in rows[1:] for c in r for p in c]
        else:
            head = c0.rstrip(':') if ncols > 1 else ''; body = [p for r in rows for c in (r[1:] if ncols > 1 else r) for p in c]
            if ncols > 1: body = [p for r in rows[1:] for p in r[0]] + body
        if cur['kind'] in ('issue', 'opinions', 'decision', 'group', 'pre') or (cur['kind'] == 'facts' and not cur['write']):
            cur['parts'].append({'h': head, 'paras': body})
        else:
            s = new('pre', label=head); s['parts'].append({'h': '', 'paras': body})
    return case


def all_text_docx(path):
    """Every text run in the document, for the completeness check."""
    d = docx.Document(path)
    out = []
    for p in d.element.body.iter(qn('w:p')):
        out.append(''.join((t.text or '') if t.tag == qn('w:t') else ' ' for t in p.iter(qn('w:t'), qn('w:br'), qn('w:tab'))))
    return ' \n '.join(out)


if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]
    res = []
    for f in sorted(glob.glob(os.path.join(src, '*.docx'))):
        res.append(parse(f))
    json.dump(res, open(out, 'w'), ensure_ascii=False)
    print('parsed', len(res), 'unknown formats:', sorted(UNKNOWN))
