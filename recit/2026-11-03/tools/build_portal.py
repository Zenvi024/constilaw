"""Build the recit portal: lossless digest JSON per day + syllabus order -> one HTML file.

usage: python3 -I build_portal.py <nov3 cases.json> <nov5 cases.json> <template.html> <out.html>
"""
import sys, json, re

# Each group is one syllabus heading. hue drives its accent colour in both themes.
SETS = [
    {'key': 'nov3', 'label': 'Tue · Nov 3', 'date': 'Tuesday, November 3, 2026', 'groups': [
        {'key': 'appt', 'hue': 222, 'code': 'V.B.2(d)', 'name': 'Power of Appointment', 'note': 'Continued from Thursday’s set (after Larin).', 'rows': [
            ('Funa_v_Villar', 'Funa v. Villar (COA Chair)'),
            ('Funa_v_Agra', 'Funa v. Agra'),
            ('Funa_v_CSC', 'Funa v. CSC'),
            ('Gaminde_v_COA', 'Gaminde v. COA'),
            ('Ifurung_v_Carpio-Morales', 'Ifurung v. Carpio-Morales'),
            (None, 'Gonzales III v. Office of the President', 'G.R. No. 196231 · Sept. 4, 2012 and Jan. 28, 2014')]},
        {'key': 'clem', 'hue': 318, 'code': 'V.B.2(e)', 'name': 'Executive Clemency', 'note': '', 'rows': [
            ('Barrioquinto_v_Fernandez', 'Barrioquinto v. Fernandez'),
            ('Vera_v_People', 'Vera v. People'),
            ('Cristobal_v_Labrador', 'Cristobal v. Labrador'),
            ('Monsanto_v_Factoran', 'Monsanto v. Factoran, Jr.'),
            ('Torres_v_Gonzales', 'Torres v. Gonzales'),
            ('Risos-Vidal_v_COMELEC', 'Risos-Vidal v. COMELEC'),
            ('Trillanes_IV_v_Medialdea', 'Trillanes IV v. Medialdea')]},
        {'key': 'cinc', 'hue': 95, 'code': 'V.B.2(f)', 'name': 'Commander-in-Chief', 'note': '', 'rows': [
            ('IBP_v_Zamora', 'IBP v. Zamora'),
            ('Ampatuan_v_Puno', 'Ampatuan v. Puno'),
            ('Sanlakas_v_Reyes', 'Sanlakas v. Executive Secretary'),
            ('Fortun_v_Macapagal-Arroyo', 'Fortun v. Macapagal-Arroyo'),
            ('Lagman_v_Medialdea_2017_Digest', 'Lagman v. Medialdea'),
            ('Lagman_v_Medialdea_2017_Resolution', 'Lagman v. Medialdea (Resolution on MR)'),
            ('Padilla_v_Congress', 'Padilla v. Congress'),
            ('Lagman_v_Pimentel', 'Lagman v. Pimentel III'),
            ('Lagman_v_Medialdea_2019', 'Lagman v. Medialdea (2019)'),
            ('Olaguer_v_Military', 'Olaguer v. Military Commission No. 34'),
            ('In_re_De_Villa', 'In re De Villa')]},
    ]},
    {'key': 'nov5', 'label': 'Thu · Nov 5', 'date': 'Thursday, November 5, 2026', 'groups': [
        {'key': 'emer', 'hue': 18, 'code': 'V.B.2(g)', 'name': 'Emergency Powers', 'note': 'Also listed: RA 12287, Declaration of State of Imminent Disaster Act (Sept. 12, 2025).', 'rows': [
            ('David_v_Macapagal-Arroyo', 'David v. Macapagal-Arroyo')]},
        {'key': 'loan', 'hue': 160, 'code': 'V.B.2(h)', 'name': 'Contracting and Guaranteeing Foreign Loans', 'note': '', 'rows': [
            ('Constantino_v_Cuisia', 'Constantino v. Cuisia'),
            ('Colmenares_v_Duterte', 'Colmenares v. Duterte')]},
        {'key': 'fora', 'hue': 200, 'code': 'V.B.2(i)', 'name': 'Foreign Affairs', 'note': '', 'rows': [
            ('Nicolas_v_Romulo', 'Nicolas v. Romulo'),
            ('Go_Tek_v_Deportation', 'Go Tek v. Deportation Board')]},
        {'key': 'immu', 'hue': 268, 'code': 'V.B.2(k)', 'name': 'Immunity from Suit', 'note': 'The syllabus lists Soliven as “Beltran v. Macasiar” (G.R. No. 82585).', 'rows': [
            ('Soliven_v_Makasiar', 'Soliven v. Makasiar (Beltran)'),
            ('Gloria_v_CA', 'Gloria v. Court of Appeals'),
            ('De_Lima_v_Duterte', 'De Lima v. Duterte')]},
        {'key': 'vice', 'hue': 340, 'code': 'V.B.3(a)', 'name': 'Vice President', 'note': '', 'rows': [
            ('Marcos_Jr_v_Robredo', 'Marcos, Jr. v. Robredo')]},
        {'key': 'sitt', 'hue': 228, 'code': 'V.C.2(b)', 'name': 'SC: Modes of Sitting', 'note': '', 'rows': [
            ('People_v_Gacott', 'People v. Gacott, Jr.')]},
        {'key': 'scap', 'hue': 250, 'code': 'V.C.2(c)', 'name': 'SC: Appointments and Qualifications', 'note': '', 'rows': [
            ('Kilosbayan_Foundation', 'Kilosbayan Foundation v. Ermita')]},
        {'key': 'nonj', 'hue': 34, 'code': 'V.C.2(d)', 'name': 'No Non-Judicial Work for Judges', 'note': '', 'rows': [
            ('Meralco_v_Pasay', 'Meralco v. Pasay Transportation Co.'),
            ('Garcia_v_Macaraig', 'Garcia v. Macaraig, Jr.')]},
        {'key': 'sala', 'hue': 140, 'code': 'V.C.2(e)', 'name': 'SC: Salary', 'note': '', 'rows': [
            ('Nitafan_v_CIR', 'Nitafan v. CIR')]},
        {'key': 'remo', 'hue': 0, 'code': 'V.C.2(g)', 'name': 'SC: Removal', 'note': 'The May 11, 2018 Sereno decision was covered under Impeachment; this digest is the June 19, 2018 Resolution.', 'rows': [
            ('In_re_Gonzalez', 'In re Gonzalez'),
            ('Rep_v_Sereno', 'Republic v. Sereno (Resolution on MR)')]},
        {'key': 'fisc', 'hue': 182, 'code': 'V.C.2(h)', 'name': 'Fiscal Autonomy', 'note': 'Also listed: RA 12233 (2025).', 'rows': [
            ('Re_COA_Opinion', 'Re: COA Opinion (Retired Justices’ Properties)'),
            ('Re_PHCCI', 'Re: PHCCI (Cooperatives’ Court Fees)')]},
        {'key': 'juri', 'hue': 290, 'code': 'V.C.2(i)', 'name': 'SC: Jurisdiction', 'note': '', 'rows': [
            ('Felipe_v_Leuterio', 'Felipe v. Leuterio'),
            ('Almora_v_Dela_Rosa', 'Almora v. Dela Rosa')]},
    ]},
]


def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


src = {'nov3': json.load(open(sys.argv[1])), 'nov5': json.load(open(sys.argv[2]))}
out_sets, out_cases, out_groups, ids = [], [], [], set()
for st in SETS:
    byfile = {c['file']: c for c in src[st['key']]}; used = set(); n = 0
    for g in st['groups']:
        out_groups.append({k: g[k] for k in ('key', 'hue', 'code', 'name', 'note')} | {'set': st['key']})
        for row in g['rows']:
            pre, short = row[0], row[1]
            if pre is None:
                out_cases.append({'missing': True, 'short': short, 'group': g['key'], 'set': st['key'], 'gr': row[2], 'id': 'missing-' + slug(short + row[2][-4:])})
                continue
            hits = [f for f in byfile if f.startswith(pre)]
            assert len(hits) == 1, (pre, hits)
            c = byfile[hits[0]]; used.add(hits[0]); n += 1
            hw = [p['text'] for p in c['sections'][0]['write']]
            parts = re.split(r'\s+–\s+', hw[0]) if hw else []
            yr = re.search(r'\((\d{4})', c['title'])
            c.update({'id': slug(short) + '-' + (yr.group(1) if yr else ''), 'n': n, 'short': short, 'group': g['key'], 'set': st['key'],
                      'year': yr.group(1) if yr else '', 'outcome': (parts[-1].strip() if len(parts) > 1 else ''),
                      'dlines': [t for t in hw if re.match(r'^D\d', t.strip())],
                      'assailed': next((t for t in hw if t.strip().startswith('ASSAILED')), '')})
            assert c['id'] not in ids, c['id']; ids.add(c['id'])
            out_cases.append(c)
    assert used == set(byfile), set(byfile) - used
    out_sets.append({'key': st['key'], 'label': st['label'], 'date': st['date'], 'count': n})
data = {'sets': out_sets, 'groups': out_groups, 'cases': out_cases}
t = open(sys.argv[3]).read()
blob = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
assert '/*__DATA__*/null' in t
open(sys.argv[4], 'w').write(t.replace('/*__DATA__*/null', blob))
print('built', sys.argv[4], {s['key']: s['count'] for s in out_sets}, 'digests;', len(out_cases), 'entries')
