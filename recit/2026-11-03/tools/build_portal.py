"""Build the Nov 3 recit portal: cases.json (lossless parse) + syllabus order -> one HTML file.

usage: python3 -I build_portal.py <cases.json> <template.html> <out.html>
"""
import sys, json, re

ORDER = [  # (file prefix, short title, syllabus group)
    ('Funa_v_Villar', 'Funa v. Villar (COA Chair)', 'appt'),
    ('Funa_v_Agra', 'Funa v. Agra', 'appt'),
    ('Funa_v_CSC', 'Funa v. CSC', 'appt'),
    ('Gaminde_v_COA', 'Gaminde v. COA', 'appt'),
    ('Ifurung_v_Carpio-Morales', 'Ifurung v. Carpio-Morales', 'appt'),
    (None, 'Gonzales III v. Office of the President', 'appt', 'G.R. No. 196231 · Sept. 4, 2012 and Jan. 28, 2014'),
    ('Barrioquinto_v_Fernandez', 'Barrioquinto v. Fernandez', 'clem'),
    ('Vera_v_People', 'Vera v. People', 'clem'),
    ('Cristobal_v_Labrador', 'Cristobal v. Labrador', 'clem'),
    ('Monsanto_v_Factoran', 'Monsanto v. Factoran, Jr.', 'clem'),
    ('Torres_v_Gonzales', 'Torres v. Gonzales', 'clem'),
    ('Risos-Vidal_v_COMELEC', 'Risos-Vidal v. COMELEC', 'clem'),
    ('Trillanes_IV_v_Medialdea', 'Trillanes IV v. Medialdea', 'clem'),
    ('IBP_v_Zamora', 'IBP v. Zamora', 'cinc'),
    ('Ampatuan_v_Puno', 'Ampatuan v. Puno', 'cinc'),
    ('Sanlakas_v_Reyes', 'Sanlakas v. Executive Secretary', 'cinc'),
    ('Fortun_v_Macapagal-Arroyo', 'Fortun v. Macapagal-Arroyo', 'cinc'),
    ('Lagman_v_Medialdea_2017_Digest', 'Lagman v. Medialdea', 'cinc'),
    ('Lagman_v_Medialdea_2017_Resolution', 'Lagman v. Medialdea (Resolution on MR)', 'cinc'),
    ('Padilla_v_Congress', 'Padilla v. Congress', 'cinc'),
    ('Lagman_v_Pimentel', 'Lagman v. Pimentel III', 'cinc'),
    (None, 'Lagman v. Medialdea', 'cinc', 'G.R. No. 243522 · Feb. 19, 2019'),
    ('Olaguer_v_Military', 'Olaguer v. Military Commission No. 34', 'cinc'),
    ('In_re_De_Villa', 'In re De Villa', 'cinc'),
]
GROUPS = [
    {'key': 'appt', 'code': 'V.B.2(d)', 'name': 'Power of Appointment', 'note': 'continued from Thursday’s set (after Larin)'},
    {'key': 'clem', 'code': 'V.B.2(e)', 'name': 'Executive Clemency', 'note': ''},
    {'key': 'cinc', 'code': 'V.B.2(f)', 'name': 'Commander-in-Chief', 'note': ''},
]


def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


cases = json.load(open(sys.argv[1]))
byfile = {c['file']: c for c in cases}
out, used, n = [], set(), 0
for row in ORDER:
    pre, short, grp = row[0], row[1], row[2]
    if pre is None:
        out.append({'missing': True, 'short': short, 'group': grp, 'gr': row[3], 'id': 'missing-' + slug(short + row[3][-4:])})
        continue
    hits = [f for f in byfile if f.startswith(pre)]
    assert len(hits) == 1, (pre, hits)
    c = byfile[hits[0]]; used.add(hits[0]); n += 1
    hw = [p['text'] for p in c['sections'][0]['write']]
    parts = re.split(r'\s+–\s+', hw[0]) if hw else []
    yr = re.search(r'\((\d{4})', c['title'])
    c.update({'id': slug(short) + '-' + (yr.group(1) if yr else ''), 'n': n, 'short': short, 'group': grp,
              'year': yr.group(1) if yr else '', 'outcome': (parts[-1].strip() if len(parts) > 1 else ''),
              'dlines': [t for t in hw if re.match(r'^D\d', t.strip())],
              'assailed': next((t for t in hw if t.strip().startswith('ASSAILED')), '')})
    out.append(c)
assert used == set(byfile), set(byfile) - used
ids = [c['id'] for c in out]; assert len(ids) == len(set(ids)), ids
data = {'groups': GROUPS, 'cases': out, 'date': 'Tuesday, November 3, 2026'}
t = open(sys.argv[2]).read()
blob = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
assert '/*__DATA__*/null' in t
open(sys.argv[3], 'w').write(t.replace('/*__DATA__*/null', blob))
print('built', sys.argv[3], len(out), 'entries,', n, 'digests')
