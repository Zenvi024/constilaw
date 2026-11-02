"""Link every case mention in the rule maps to its case card (build-time).

Text inside existing links, headings (h2/h3), codal boxes and buttons is left alone.
Ambiguous short names are resolved by an explicit year after the name, then by
which rule map the mention sits in; mentions that are really people (‘President
Marcos’, ‘Atty. Macalintal’) are never linked.
"""
import re, html

# short names shared by several cases (or also used for people): rule-map file prefix -> case id
AMBIG = {
    'Belgica': {'*': 'belgica2013'},
    'Macalintal': {'05': 'macalintal2003', '*': 'macalintal2023'},
    'Tolentino': {'01': 'tolentino71', '02': 'tolentino04', '07': 'tolentino04', '11': 'tolentinofinance', '12': 'tolentinofinance', '13': 'tolentinofinance'},
    'Santiago': {'01': 'santiago97', '08': 'santiagoguingona'},
    'Guingona': {'10': 'guingonagonzales', '12': 'guingonacarague'},
    'David': {'02': 'davidgma', '04': 'davidset'},
    'Pangilinan': {'09': 'pangilinan2018', '*': 'pangilinan2021'},
    'Trillanes': {'*': 'trillanespimentel'},
    'PHILCONSA': {'02': 'philconsa2016', '09': 'philconsamathay', '12': 'philconsaenriquez'},
    'Philconsa': {'02': 'philconsa2016', '09': 'philconsamathay', '12': 'philconsaenriquez'},
    'Abayon': {'*': 'abayon'},
    'Reyes': {'10': 'reyescomelec'},
    'Pimentel': {'08': 'pimentelcow', '10': 'pimentelhret', '12': 'pimentelhouse2025', '13': 'pimentelhouse2025'},
    'Gonzales': {'01': 'gonzales67'},
    'Drilon': {'10': 'drilondevenecia'},
    'Laurel': {'06': 'laureldesierto'},
    'Arroyo': {'08': 'arroyodevenecia'},
    'Poe': {'*': 'poe2016'},
}
# names that are also people: link only as a citation, i.e. right after '(' or '; ' and before ')' ';' or ','
CITE_ONLY = {'Marcos': {'05': 'marcos95', '07': 'marcos95'}, 'Aquino': {'05': 'aquino95', '07': 'aquino95'}, 'Garcia': {'12': 'garciaexecsec'}}
# never link these words on their own
STOP = {'People', 'Republic', 'Province', 'City', 'Philippine', 'Philippines', 'Senate', 'House', 'Commission', 'Council', 'Coalition', 'Association',
        'Executive', 'Secretary', 'Social', 'Ang', 'An', 'The', 'Vera', 'Cruz', 'Co', 'Chavez', 'Planas', 'Lambino Group', 'Teves', 'Dimaporo', 'Muhlach', 'Gatmaytan', 'IBP'}
# extra spellings used in the rule maps
EXTRA = {'PASI': 'pasi', 'Iloilo I': 'ileco', 'Iloilo I Electric Coop.': 'ileco', 'GTZ': 'gtz', 'Chavez v. PEA': 'chavezpea', 'In re JDF': 'jdf', 'JDF': 'jdf',
         'Ericta': 'ericta', 'PPI v. COMELEC': 'ppi', 'PPI': 'ppi', 'TELEBAP': 'telebap', 'Manila Memorial': 'manilamemorial', 'Manila Memorial Park v. DSWD': 'manilamemorial', 'Oposa': 'oposa', 'Kida': 'kida',
         'Fertiphil': 'fertiphil', 'SJS v. DDB': 'sjsddb', 'SJS': 'sjsddb', 'Mariano': 'mariano', 'Ang Bagong Bayani': 'angbagongbayani', 'BANAT': 'banat',
         'Labo': 'labo', 'Abayon v. HRET (2010)': 'abayon2010', 'Abayon v. HRET, 2010': 'abayon2010', 'Tolentino v. Sec. of Finance': 'tolentinofinance',
         'Tolentino v. Secretary of Finance': 'tolentinofinance', 'Belgica 2019': 'belgica2019', 'Belgica (2019)': 'belgica2019', 'Belgica 2013': 'belgica2013',
         'Belgica (2013)': 'belgica2013', 'Macalintal 2003': 'macalintal2003', 'Macalintal (2003)': 'macalintal2003', 'Macalintal 2023': 'macalintal2023',
         'Macalintal (2023)': 'macalintal2023', 'PHILCONSA 2016': 'philconsa2016', 'Pimentel v. House': 'pimentelhouse2025', 'Lacson': 'lacsonperez',
         'Kabataan': 'kabataan2015', 'Osmeña': 'osmena', 'Chua': 'chua2016'}

def build_aliases(cases, link_texts):
    al = {}
    def add(name, cid):
        name = name.strip()
        if len(name) < 3 or name in STOP: return
        if name in al and al[name] != cid: al[name] = None  # clash: resolve by AMBIG or skip
        else: al[name] = cid
    for cid, c in cases.items():
        n = re.sub(r'\s*\((?:US|Notice|Ramas-Dimaano)\)', '', c['n']).strip()
        add(n, cid); add(re.sub(r'\s*\(.*?\)', '', n), cid)
        add(n.replace(', Inc.', '').replace(' Jr.', '').replace(', Jr.', ''), cid)
        first = n.split(' v. ')[0].strip()
        if ' v. ' in n and re.fullmatch(r"[A-ZÑ][\w’'\-ñ]+(?: [A-Z][\w’'\-]+)?", first) and first not in STOP: add(first, cid)
    for t, cid in link_texts.items(): add(t, cid)
    for t, cid in EXTRA.items(): al[t] = cid
    for k in list(AMBIG) + list(CITE_ONLY): al[k] = 'AMBIG'
    for k, v in list(al.items()):  # a full name shared by two cards: resolve like its short name
        if v is None and ' v. ' in k and k.split(' v. ')[0] in AMBIG: al[k] = 'AMBIG'
    return {k: v for k, v in al.items() if v}

TOK = re.compile(r'(<[^>]+>)')
SKIP_TAGS = {'a', 'h2', 'h3', 'button', 'script', 'style'}

def link_file(src, prefix, aliases, cases, report):
    keys = sorted(aliases, key=len, reverse=True)
    rx = re.compile(r"(?<![\w’'\-])(" + '|'.join(re.escape(html.escape(k, quote=False)) for k in keys) + r")(?![\w])")
    out, stack = [], []
    for part in TOK.split(src):
        if part.startswith('<'):
            m = re.match(r'<(/?)([a-zA-Z0-9]+)([^>]*?)(/?)>', part)
            if m:
                close, tag, attrs = m.group(1), m.group(2).lower(), m.group(3)
                if close:
                    for k in range(len(stack) - 1, -1, -1):
                        if stack[k][0] == tag: del stack[k:]; break
                elif tag not in ('br', 'img', 'hr', 'input', 'wbr') and not m.group(4):
                    stack.append((tag, attrs))
            out.append(part); continue
        if not part or any(t in SKIP_TAGS or 'codal' in a for t, a in stack):
            out.append(part); continue
        def sub(m):
            name = html.unescape(m.group(1)); cid = aliases.get(name)
            before, after = part[:m.start()], part[m.end():]
            if cid == 'AMBIG':
                if name in CITE_ONLY:
                    if not (re.search(r'(\(|; )$', before) and re.match(r'[);,]', after)): return m.group(0)
                    cid = CITE_ONLY[name].get(prefix)
                else:
                    if re.search(r'(Atty\.|Defensor|President|Senator|Sen\.|Rep\.|Chairman|Justice|Speaker)\s*$', before): return m.group(0)
                    base = name.split(' v. ')[0]; rules = AMBIG.get(name) or AMBIG[base]
                    y = re.match(r'[\s,]*\(?((?:19|20)\d\d)\)?', after)
                    byyear = [i for i, c in cases.items() if y and c['y'] == y.group(1) and c['n'].startswith(base)]
                    cid = byyear[0] if byyear else rules.get(prefix, rules.get('*'))
                if not cid: return m.group(0)
            report[cid] = report.get(cid, 0) + 1
            return f'<a class="cref" data-c="{cid}">{m.group(1)}</a>'
        out.append(rx.sub(sub, part))
    return ''.join(out)

def unlinked_vs(src):
    """'X v. Y' mentions still not inside a link (for the build report)."""
    left = []
    stack = []
    for part in TOK.split(src):
        if part.startswith('<'):
            m = re.match(r'<(/?)([a-zA-Z0-9]+)', part)
            if m:
                if m.group(1):
                    for k in range(len(stack) - 1, -1, -1):
                        if stack[k] == m.group(2).lower(): del stack[k:]; break
                elif m.group(2).lower() not in ('br', 'img', 'hr', 'input', 'wbr'): stack.append(m.group(2).lower())
            continue
        if 'a' in stack: continue
        left += [v for v in re.findall(r"[A-Z][\w’'.\-]+ v\. [A-Z][\w’'.\-]+(?: [A-Z][\w’'.\-]+)*", html.unescape(part)) if not v.startswith('Muhlach')]  # Muhlach v. Fuentebella is a 2013 exam hypothetical
    return left
