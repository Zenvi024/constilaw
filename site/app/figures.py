"""Diagrams for the rule maps (build-time).

Every figure follows one visual language:
  blue = the rule; green (✓) = valid, or the case goes on; red (✕) = void, or the case ends;
  yellow (!) = the trap or the exception.
Each figure can carry a "Use it when" trigger, a memory hook, and a "Say it in orals" line (no CLEAR boxes).
Gate diagrams carry fact patterns that the page turns into click-through walk-throughs.

build.py calls insert(src, prefix) on each rule-map file before case names are linked, so case
names inside figures become links too. All law here restates the rule maps and case cards.
"""
import re

FIGS = {}    # file prefix -> [(mode, anchor, html)]
WALL = []    # (prefix, figure id, title, hook html) for the hook wall
SEC = {'00': 'method', '01': 'interp', '02': 'jr', '03': 'terr', '04': 'cit', '05': 'suff', '06': 'gov', '07': 'comp',
       '08': 'internal', '09': 'priv', '10': 'et', '11': 'powers', '12': 'money', '14': 'legproc', '15': 'ocong', '90': 'news'}
SHORT = {'00': 'Exam method', '01': 'Interpretation', '02': 'Judicial review', '03': 'Territory', '04': 'Citizenship', '05': 'Suffrage',
         '06': 'Government', '07': 'Composition', '08': 'Internal', '09': 'Privileges', '10': 'Tribunals and CA', '11': 'Powers',
         '12': 'Money', '14': 'Legislative process', '15': 'Other powers, impeachment', '90': 'News'}


# ---------- small builders ----------
def C(cid, t): return f'<a class="cref" data-c="{cid}">{t}</a>'
def X(fid, t): return f'<a class="xref" data-h="{fid}">{t}</a>'
def N(b, s='', cls=''): return f'<div class="vn {cls}"><b>{b}</b>' + (f'<span class="s">{s}</span>' if s else '') + '</div>'
def VE(t=''): return f'<div class="ve">{t}</div>'
def HE(t=''): return f'<div class="he">{t}</div>'
def vflow(*xs): return '<div class="vflow">' + ''.join(xs) + '</div>'
def hflow(*xs): return '<div class="hflow">' + ''.join(xs) + '</div>'
def grid(*xs, m=150): return f'<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min({m}px,100%),1fr));gap:8px">' + ''.join(xs) + '</div>'
def sp(x): return f'<div class="vsp">{x}</div>'
def sub(t): return f'<div class="vsub">{t}</div>'
def cmp(cols, rows, lab=True):
    n = len(cols)
    out = f'<div class="vcmp{" lab" if lab else ""}" style="--n:{n}">' + ('<div class="e"></div>' if lab else '') + ''.join(f'<div class="h">{c}</div>' for c in cols)
    for r in rows:
        out += (f'<div class="rl">{r[0]}</div>' if lab else '') + ''.join(f'<div class="c">{x}</div>' for x in r[1:])
    return out + '</div>'
def hub(center, spokes):
    pos = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2), (3, 3)]
    return '<div class="hub">' + ''.join(f'<div class="vn hs {k}" style="--r:{pos[i][0]};--c:{pos[i][1]}"><b>{a}</b><span class="s">{b}</span></div>'
                                         for i, (a, b, k) in enumerate((s + ('',))[:3] for s in spokes)) + f'<div class="ctr"><span>{center}</span></div></div>'
def tl(items):
    return '<ul class="vtl">' + ''.join(f'<li class="{k}"><span class="y">{y}</span><span class="t">{t}</span></li>' for y, t, k in items) + '</ul>'
def ladder(rungs):
    return '<div class="ladder">' + ''.join(f'<div class="rung" data-r="{r}"><div class="lab">{l}<small>{sm}</small><span class="cnt"></span></div><div class="bar"><i style="width:{w}%"></i><span>{t}</span></div></div>'
                                            for l, sm, w, t, r in rungs) + '</div>'
def stepper(stages, start=0):
    btns = ''.join(f'<button type="button" class="{z}">{b}</button>' for b, z, _ in stages)
    ps = ''.join(f'<div class="sp-p">{p}</div>' for _, _, p in stages)
    return f'<div class="stepper" data-start="{start}"><div class="sp-btns">{btns}</div><div class="sp-panel">{ps}</div></div>'
def acro(*pairs):
    rows = max(len(re.sub(r'<[^>]+>', '', w)) for _, w in pairs) > 45  # long glosses read better as a list
    return f'<div class="acro{" rows" if rows else ""}">' + ''.join(f'<span class="al"><span class="L">{l}</span><span class="w">{w}</span></span>' for l, w in pairs) + '</div>'
def plates(*ps): return '<div class="plates">' + ''.join(f'<div class="plate"><span class="pn">{n}</span><span class="pl">{l}</span></div>' for n, l in ps) + '</div>'
def zones(items, cols=None):
    st = f' style="--cols:{cols}"' if cols else ''
    return f'<div class="zones"{st}>' + ''.join(f'<div class="zone {k}"><b>{b}</b><span class="s">{s}</span></div>' for b, s, k in items) + '</div>'
def door(big, title, s, tag, tagcls=''): return f'<div class="door"><span class="big">{big}</span><b>{title}</b><span class="s">{s}</span><span class="tag {tagcls}">{tag}</span></div>'

def fact(label, text, path, why):
    """A fact pattern for a walk-through. path: the answer at each gate (y/n), '?' marks an arguable answer."""
    return (label, text, path, why)

def G(q, s, xb, xs='', on='no', cls='no'):
    """One gate: question, hint, exit title, exit detail, the answer that exits ('no' or 'yes'), exit color."""
    return (q, s, xb, xs, on, cls)

def gates(rows, end, facts=()):
    """rows: G(...) tuples; end: (title, detail, color) reached when no gate exits."""
    out = '<div class="gates">'
    for i, (q, s, xb, xs, on, cls) in enumerate(rows):
        if i: out += VE('yes' if rows[i - 1][4] == 'no' else 'no')
        out += (f'<div class="gate" data-exit="{on}"><div class="vn q"><span class="gn">{i + 1}</span><b>{q}</b>' + (f'<span class="s">{s}</span>' if s else '') + '</div>'
                f'<span class="x {on}">{on}</span>' + N(xb, xs, cls + ' gx') + '</div>')
    eb, es, ec = end
    out += VE('yes' if rows[-1][4] == 'no' else 'no') + N(eb, es, ec + ' gend') + '</div>'
    for l, t, p, w in facts:  # a path must end exactly where the walk ends: at a firing exit, or after the last gate
        toks = [x.rstrip('?') for x in p.split(',')]
        assert all(x in ('y', 'n') for x in toks), (l, p)
        for i, x in enumerate(toks):
            fires = x == ('n' if rows[i][4] == 'no' else 'y')
            assert not fires or i == len(toks) - 1, f'path for {l!r} goes past a firing exit'
            if fires: break
        else:
            assert len(toks) == len(rows), f'path for {l!r} stops before the last gate'
    if facts:
        out += '<div class="vfacts">' + ''.join(f'<div class="vfact" data-path="{p}"><span class="fn">{l}</span><span class="vft">{t}</span><span class="vwhy">{w}</span></div>' for l, t, p, w in facts) + '</div>'
    return out

def write(*lines):
    """The CLEAR lines to write on the back of the questionnaire: (letter, html). Text in [brackets] is for you to fill."""
    def fill(t): return re.sub(r'\[([^\]]+)\]', r'<span class="fill">[\1]</span>', t)
    return ''.join(f'<div class="ln"><i class="{"e" if k == "E" else ""}">{k}</i><span>{fill(t)}</span></div>' for k, t in lines)

def fig(prefix, mode, anchor, fid, title, body, kind='diagram', when=None, hook=None, wr=None, cap='', notest=False, wall=True, oral=None):
    tidy = prefix >= '14' and prefix != '90' and kind != 'review'   # finals rule maps: the tidy face (hints one tap away)
    h = (f'<figure class="viz{" vtidy" if tidy else ""}" id="fig-{fid}" data-kind="{kind}"' + (' data-notest' if notest else '') + f' aria-label="{re.sub(r"<[^>]+>", "", title)}">'
         f'<div class="vt"><span class="vtt">{title}</span> <small>{kind}</small></div>')
    if when: h += f'<p class="vwhen"><span class="vlab">Use it when</span>{when}</p>'
    h += body
    if hook: h += f'<div class="hook"><span class="vlab">Hook</span><div class="hk">{hook}</div></div>'
    if oral: h += '<div class="vor"><span class="vlab">Say it in orals</span><p>' + re.sub(r'\[([^\]]+)\]', r'<span class="fill">[\1]</span>', oral) + '</p></div>'
    if cap: h += f'<figcaption>{cap}</figcaption>'
    h += '</figure>\n'
    FIGS.setdefault(prefix, []).append((mode, anchor, h))
    if hook and wall: WALL.append((prefix, fid, title, hook))
    return h


def insert(src, prefix):
    """Insert this file's figures. Each anchor must occur exactly once; the figure goes to the END of the h3 section the
    anchor sits in (provision, explanation, professor boxes, then the diagrams), keeping document order."""
    placed = []
    for n, (mode, anchor, h) in enumerate(FIGS.get(prefix, [])):
        c = src.count(anchor)
        assert c == 1, f'figure anchor in {prefix} found {c} times: {anchor[:70]}'
        pos = src.index(anchor) + (len(anchor) if mode == 'after' else 0)
        ends = [x for x in (src.find('<h3', pos), src.find('</section>', pos)) if x >= 0]
        placed.append((min(ends) if ends else len(src), pos, n, h))
    groups = {}
    for end, pos, n, h in sorted(placed, key=lambda t: (t[1], t[2])):
        groups.setdefault(end, []).append(h)
    for end in sorted(groups, reverse=True):   # from the back, so earlier offsets stay valid
        src = src[:end] + ''.join(groups[end]) + src[end:]
    return src


# =====================================================================
# 00 · exam method
# =====================================================================
fig('00', 'before', '<h3 id="method-rules">', 'legend', 'How to read every diagram in the rule maps',
    '<div class="legend4">' + N('Blue', 'the rule, the test, the default', 'acc') + N('Green', 'valid, or the case goes on', 'ok') + N('Red', 'void, or the case ends', 'no') + N('Yellow', 'the trap or the exception', 'sun') + '</div>'
    + sp(grid(N('Use it when', 'the fact-pattern words that should make you reach for the diagram', 'plain'),
              N('Walk it', 'run a fact pattern through the questions one at a time, and see whether you land where the Court did', 'plain'),
              N('Test me', 'covers the details; tap each grey box to check your recall', 'plain'),
              N('Hook · Say it in orals', 'the mnemonic to carry into the room, and the spoken answer it turns into', 'plain'), m=150)),
    kind='key', cap='Four colors, everywhere: once you know them, a red box at the end of a path means you write “void” or “dismissed” in your C line.', notest=True, wall=False)

_clock = '<div class="xclock" role="img" aria-label="The 90 minutes: two minutes of setup, then four 22-minute blocks">' + \
    '<div style="flex:2"><span class="hd">ID</span><span class="bands"><i class="b-set" style="flex:1"></i></span><span class="tm">10:00</span></div>' + \
    ''.join(f'<div style="flex:22"><span class="hd">Q{i + 1}</span><span class="bands"><i class="b-read" style="flex:4"></i><i class="b-an" style="flex:4"></i><i class="b-wr" style="flex:11"></i><i class="b-ck" style="flex:3"></i></span><span class="tm">{a}–{b}</span></div>'
            for i, (a, b) in enumerate([('10:02', '10:24'), ('10:24', '10:46'), ('10:46', '11:08'), ('11:08', '11:30')])) + '</div>' + \
    '<div class="xclockkey"><span><i class="b-set"></i>student no. + four boxes</span><span><i class="b-read"></i>read twice 4</span><span><i class="b-an"></i>analyze 4</span><span><i class="b-wr"></i>write 11</span><span><i class="b-ck"></i>check 3</span></div>'
_wbar = '<div class="wbar"><div style="flex:9;background:var(--accent);color:var(--accent-ink)">C<small>9</small></div><div style="flex:32;background:var(--accent-soft)">L<small>32 words</small></div><div style="flex:61;background:var(--sun-soft)">A · Analysis<small>61 words: the facts, applied</small></div><div style="flex:7;background:var(--accent);color:var(--accent-ink)">R<small>7</small></div></div>'
_sheet = '<div class="qsheet" role="img" aria-label="The back of the questionnaire divided into four answer boxes, student number at the top"><div class="id">student no. only</div>' + ''.join(f'<div>Q{i}<i class="c"></i><i></i><i></i><i></i><i style="width:60%"></i></div>' for i in range(1, 5)) + '</div>'
fig('00', 'before', '<aside class="note trap"><strong>Length trap:</strong>', 'clock', 'Your 90 minutes on one strip; one answer in one box',
    _clock + sp(sub('Inside each 22-minute block') + '<div class="tbar"><div style="flex:4;background:var(--sun-soft)">Read twice<small>0–4</small></div><div style="flex:4;background:var(--accent-soft)">Analyze<small>4–8</small></div><div style="flex:11;background:var(--accent);color:var(--accent-ink)">Write in CLEAR<small>8–19 · 80–120 words</small></div><div style="flex:3;background:var(--good-soft)">Check<small>19–22</small></div></div>')
    + sp('<div class="vrow"><div>' + sub('Where the words go (average of the 26 back-page answers in the Essay trainer: 112 words)') + _wbar
         + sp(vflow(N('C · Conclusion', 'the short answer, first line', 'acc'), VE(), N('L · Legal basis', 'rule + provision; case only if sure'), VE(), N('E · Exception', 'only if one applies (4 of the 26 answers needed one)', 'sun'), VE(), N('A · Analysis', 'the law applied to these facts: half the box', 'plain'), VE(), N('R · Restatement', 'must agree with C', 'acc'))) + '</div>' + _sheet + '</div>'),
    kind='timeline', when='the papers are handed out: before you read Q1, write your student number and box the back of the questionnaire.',
    hook='Move on at <em>:24</em>, <em>:46</em> and <em>:08</em>; pens down at <em>:30</em>.<small>C-L-(E)-A-R, and A is half the box. If R does not agree with C, fix C or R before you move on.</small>',
    cap='Four problems × 22 minutes = 88 minutes; the spare 2 go to your student number and to dividing the back into one box per question before you read. Times assume a 10:00 AM start; shift them if the papers come late, and if there are not four problems, divide 88 minutes by the number you get.')

_RADAR = [
  ('Can the Court even hear it?', [
    ('“a bill”, “a draft IRR”, “a resolution calling for Charter change”, “a peace agreement that needs a law”', 'Not ripe: no actual case yet', 'ripe'),
    ('“the ordinance was lifted”, “replaced by a new code”, “the proclamation has ended”', 'Moot, unless one of the four exceptions applies', 'ripe'),
    ('“as a taxpayer”, “as a citizen”, “as a voter”, “a senator sues”, “an association files”', 'Standing: which kind, and why', 'standing'),
    ('“filed directly in the Supreme Court”, “also filed in the RTC”', 'Remedy and forum; hierarchy of courts; forum shopping', 'forum'),
    ('“the decision is political and final”, “wisdom of the policy”', 'Political question, or are there constitutional limits? (Francisco)', 'jr'),
  ]),
  ('Who read or changed the Constitution?', [
    ('“the law clarifies what the Constitution means”, “Congress responds to a Supreme Court ruling”', 'Only courts interpret (Endencia)', 'salary'),
    ('“people’s initiative”, “signature sheets”, “Charter change”, “constituent assembly”', 'Art. XVII: which door; amendment or revision; full text', 'doors'),
    ('“shall … as may be defined by law”, “Congress has not acted for decades”, “mandamus against Congress”', 'Self-executing? Duty, definition, default (Kapatiran)', 'kapatiran'),
    ('“a curfew”, “an age cap”, “only for some group”', 'Equal protection: pick the level of scrutiny', 'scrutiny'),
  ]),
  ('Voters, candidates and seats', [
    ('“voters must pass, pay or show”, “registration closes on”, “deactivated”', 'Qualification (void) or regulation (valid if reasonable)', 'suffrage'),
    ('“moved to”, “leased a condo”, “works abroad”, “after marriage”', 'Residence means domicile: three elements', 'domicile'),
    ('“candidates for Senator or the House who fail to … are disqualified”', 'Adding qualifications by law (SJS v. DDB)', 'quals'),
    ('“party-list nominee”, “substitution”, “age cap for nominees”, “sectoral”', 'Party-list doctrine; COMELEC or HRET', 'plhist'),
    ('“was proclaimed”, “took his oath”, “before June 30”', 'COMELEC or the tribunal: proclamation, oath, assumption', 'hret'),
    ('“the seat fell vacant”, “special election”', 'Who calls the special election, and when', 'vacancy'),
  ]),
  ('Inside Congress', [
    ('“elected with 12 votes”, “how many votes are needed”', 'The vote ladder: present, each House, all the Members', 'votes'),
    ('“some senators were abroad, detained or absent”', 'Quorum: majority within reach (Avelino)', 'quorum'),
    ('“suspended for 90 days”, “expelled”, “disorderly behavior”', 'Discipline: two-thirds of all, 60-day cap', 'discipline'),
    ('“violated its own rules”, “the minority leader”', 'Courts and internal rules', 'internal'),
    ('“the enrolled bill says … but the Journal shows …”', 'Enrolled bill or Journal', 'journal'),
    ('“arrested”, “warrant”, “protective custody”, “detained member wants to attend”', 'Arrest privilege: six years, in session', 'arrest'),
    ('“privilege speech”, “press conference”, “interview”, “libel suit”', 'Speech and debate: legislative act or not', 'speech'),
    ('“appointed chairman of …”, “an office created during his term”', 'Incompatible or forbidden office', 'office'),
    ('“salary increase”, “retirement benefits”', 'Sec. 10: only after all the approvers’ terms', 'salary10'),
    ('“CA seats”, “lone senator”, “rounded up”', 'CA proportional representation', 'ca'),
  ]),
  ('Laws, delegation and money', [
    ('“the oversight committee shall approve …”, “may deputize …”', 'Legislative veto (ABAKADA)', 'oversight'),
    ('“the agency shall issue the IRR”, “published in a newspaper”, “effective immediately”', 'Delegation tests; valid IRR; publication', 'delegation'),
    ('“shall not be repealed”, “amended only by three-fourths”', 'Substantive limits (I SURF)', 'isurf'),
    ('“the title of the Act”, “a provision unrelated to the title”', 'One subject, expressed in the title', 'title'),
    ('“the Senate passed its own tax bill first”, “the bicameral conference inserted”', 'Origination (TRIPAL; ' + C('tolentinofinance', 'Tolentino') + ')', 'tripal'),
    ('“the President vetoed a provision”, “vetoed the condition”', 'Item veto and riders', 'veto'),
    ('“savings”, “realigned”, “transferred to another office”, “unprogrammed”', 'Augmentation: four gates', 'augment'),
    ('“lump sum”, “legislators identify projects after the GAA”', 'Pork and singular correspondence (Belgica)', 'budget'),
    ('“Congress raised the President’s budget”, “no GAA by January”', 'The five money rules', 'money5'),
    ('“COA disallowed … must refund”', 'Who returns disallowed amounts (Madera)', 'madera'),
    ('“exempt by proclamation”, “leased portion of the hospital”', 'Tax exemptions', 'tax'),
  ]),
  ('The State and its powers', [
    ('“sued the agency”, “sued a foreign government or its agent”, “garnished”', 'Immunity: the State? consent? collect?', 'immunity'),
    ('“businesses must give free …”, “set aside part of their land”, “discount”', 'Police power or taking', 'taking'),
    ('“revolutionary government”, “occupation”', 'Kinds of government', 'govkinds'),
  ]),
]
fig('00', 'before', '<h3 id="method-model">', 'radar', 'Issue radar: the words in the facts, the issue they signal',
    '<div class="radar">' + ''.join('<div class="grp">' + sub(g) + ''.join(f'<div class="rrow"><span class="tr">{t}</span><span class="is" data-cover>{i}</span><span class="go">{X("fig-" + f, "diagram")}</span></div>' for t, i, f in rows) + '</div>' for g, rows in _RADAR) + '</div>',
    kind='checklist', when='you finish your second read: run your eye down the left column and mark every phrase that appears in the facts.',
    hook='Words in the facts fire the issue. <em>Test me</em> hides the middle column: read the trigger words and name the issue before you tap.',
    cap='Gatmaytan’s stories “may have been altered”, so the trigger is usually a phrase, a number or a date. Each row jumps to the diagram that answers it.', wall=False)


# =====================================================================
# 01 · interpretation and amendment
# =====================================================================
fig('01', 'before', '<div class="test"><b>Self-executing test (Manila Prince Hotel)</b>', 'www', 'Reading a provision: Words, Will, Whole',
    hflow(N('1 · Words', '<em>verba legis</em>: ordinary meaning unless technical terms are used; the Constitution is not a lawyer’s document (J.M. Tuason; Francisco)', 'acc'), HE('unclear?'),
          N('2 · Will', '<em>ratio legis est anima</em>: the intent of the framers and of the people who ratified it, shown by the records (Nitafan; Francisco)', 'acc'), HE('then'),
          N('3 · Whole', '<em>ut magis valeat quam pereat</em>: harmonize the provisions so every word has effect (Francisco)', 'acc'))
    + sp(grid(N('Presumed self-executing', 'unless it says legislation is needed; Art. II policies generally are not (' + C('manilaprince', 'Manila Prince') + ')', 'plain'),
              N('Prospective', 'unless it says otherwise (Filoteo)', 'plain'),
              N('Courts interpret', 'Congress cannot declare by statute what a provision means (Endencia)', 'plain'),
              N('Mandatory as a rule', 'directory only if no rights depend on it, no injury results, and its purpose can be met another way', 'plain'),
              N('No mandate outranks another', 'unless the Constitution makes its primacy clear (Kida)', 'plain'),
              N('Literal reading yields', 'where it would be impossible, absurd or unjust (Vicencio)', 'sun'),
              N('<em>Expressio unius</em>', 'express mention of some things of a class excludes the others', 'plain'), m=160))
    + sp(sub('Name your mode of argument (Tribe, in Gatmaytan’s <em>Legal Method Essentials</em>)') + acro(('T', 'text'), ('S', 'structure'), ('O', 'original intent'), ('N', 'norms and pragmatics'), ('P', 'precedent'), ('+', 'a combination'))),
    kind='flow', when='the question turns on what a word or clause of the Constitution means.',
    hook='<em>Words, Will, Whole.</em> Start with the text; go to the framers only if it is unclear; then read it with everything around it.',
    cap='Naming the canon you use (and, if the question invites it, the mode of argument) is the fastest way to show method in a one-paragraph answer.')

fig('01', 'before', '<h4>The judges’ salary line: a lesson in who interprets</h4>', 'kapatiran', 'Self-executing? And Kapatiran’s three questions',
    gates([G('Is it complete in itself, operative without enabling legislation?', '', 'Needs a law first', 'not enforceable as a right until Congress acts', 'no', 'sun'),
           G('Are the nature and extent of the right, and the liability, fixed by the Constitution?', '', 'Needs a law first', 'not enforceable as a right until Congress acts', 'no', 'sun'),
           G('Is the subject left to Congress (“as may be provided by law”)?', 'any sign that the framers referred it to Congress', 'Needs a law first', 'but its “shall” may still bind Congress now: see Kapatiran below', 'yes', 'sun')],
          ('Self-executing', 'enforceable without a law (Manila Prince Hotel)', 'ok'),
          facts=[fact('Filipino First (' + C('manilaprince', 'Manila Prince') + ')', 'GSIS sells a controlling share of the Manila Hotel to a foreign bidder over a qualified Filipino bidder who matched the bid. The Filipino bidder invokes the constitutional preference for qualified Filipinos.', 'y,y,n', 'The provision is complete in itself and judicially enforceable without a law; provisions are presumed self-executing (Manila Prince Hotel).'),
                 fact('Political dynasties (Art. II, Sec. 26)', 'The provision says the State shall “prohibit political dynasties as may be defined by law”. A group asks COMELEC to disqualify dynastic candidates now.', 'n', 'As a ban, it cannot operate until Congress defines “political dynasty”, so COMELEC cannot disqualify anyone yet (Kapatiran). But Kapatiran abandoned the old statements that Sec. 26 is not self-executing in another sense: the duty itself binds Congress now, and mandamus lies to compel it.')])
    + sp(sub('Kapatiran Party v. Congress (2026): keep three questions apart') + zones([
        ('Duty', '“shall prohibit”: a mandatory command to Congress, not an aspiration. Earlier statements that Sec. 26 is not self-executing were abandoned.', 'acc'),
        ('Definition', '“as may be defined by law”: Congress defines “political dynasty” and the scope of the ban; the Court does not.', 'acc'),
        ('Default', '39 years of inaction is grave abuse (Art. VIII, Sec. 1): mandamus granted by majority (unanimous on the duty); no deadline, “utmost urgency”.', 'ok')])
       + sp(grid(N('COMELEC must wait', 'it cannot disqualify dynastic candidates without the law; the petition against it was denied', 'no'),
                 N('Art. II is usually not enforceable', 'aids to interpretation and guides for legislation; exceptions: Secs. 15–16 (health, ecology: Oposa), and now Sec. 26’s duty (Kapatiran)', 'sun'), m=200))),
    kind='gates + three questions', when='a provision says “shall … as may be defined by law” and Congress has not acted, or someone asks a court or COMELEC to enforce an Art. II policy.',
    hook='Three D’s: <em>Duty</em> (shall), <em>Definition</em> (by law, so Congress), <em>Default</em> (decades of inaction = grave abuse).<small>The Court can compel the duty; only Congress writes the definition; COMELEC waits for the law.</small>',
    cap='Kapatiran is the 2026 case most likely to reach a news question. Answer the three questions in order and you will not confuse “the Court ordered Congress” with “the Court banned dynasties”.')

fig('01', 'after', '<h4>The judges’ salary line: a lesson in who interprets</h4>\n', 'salary', 'The judges’ salary line: who gets the last word', tl([
    ('1950', f'<b>The Court</b> · {C("perfecto", "Perfecto v. Meer")}: income tax on a judge’s salary is a prohibited diminution (1935 text).', ''),
    ('1953', f'<b>Congress tries</b> · {C("endencia", "Endencia v. David")}: Congress passes RA 590 saying it is not; void, because only the Court interprets the Constitution.', 'key'),
    ('1987', f'<b>The Court, on new text</b> · {C("nitafan", "Nitafan v. CIR")}: under the 1987 Constitution the framers intended judges’ salaries to be taxable; Perfecto and Endencia discarded on that point.', 'key')]),
    kind='timeline', when='a bill “clarifies” a constitutional term or answers a Supreme Court ruling.',
    hook='<em>P-E-N</em>: Perfecto (no tax), Endencia (Congress cannot say otherwise), Nitafan (new text, framers say tax).<small>The answer changed only when the text changed; Congress never had the power to change it.</small>',
    cap='Same question, three answers: the text changed in 1987, and the framers’ intent (ratio legis) settled it. Congress never had the power to settle it by statute.')

fig('01', 'before', '<h4>Leading cases in order</h4>', 'doors', 'Art. XVII: three doors in, one door out',
    '<div class="doors">' + door('¾', 'Congress as constituent assembly', 'three-fourths of all its Members (Sec. 1(1))', 'amendment or revision')
    + door('⅔ · ½', 'Constitutional convention', 'called by two-thirds of all Members, or a majority of all Members submits the question of calling one to the voters (Sec. 3)', 'amendment or revision')
    + door('12% + 3%', 'People’s initiative', 'petition of 12% of all registered voters, at least 3% in every district; not within five years of ratification nor more than once every five years (Sec. 2)', 'amendments only', 'sun') + '</div>'
    + '<div class="funnel"><span>▼</span><span>▼</span><span>▼</span></div>'
    + vflow(N('Plebiscite', 'held not earlier than 60 nor later than 90 days after approval of the proposal, or after COMELEC certifies the initiative’s sufficiency (Sec. 4)', 'acc'), VE('majority of the votes cast'), N('Ratified', 'the change takes effect', 'ok'))
    + sp(grid(N('Same day as an election? Allowed', 'the plebiscite may coincide with a general election (Gonzales)', 'ok'),
              N('One convention, one package', 'no piecemeal submission of a convention’s proposals (Tolentino, 1971)', 'no'),
              N('Jointly or separately?', 'the ¾ vote: the text is silent. Argue separate voting (bicameralism); Mendoza: joint session, separate votes, so 24 senators are not outvoted', 'sun'),
              N('The initiative door is stuck', 'Congress must provide the implementing law; RA 6735 is inadequate (Santiago) and was never fixed', 'sun'), m=160)),
    kind='flow', when='a story mentions Charter change, a constituent assembly, a convention or a “people’s initiative”.',
    hook='Three doors, one exit. Doors: <em>¾</em> · <em>⅔ (or ½ to the voters)</em> · <em>12 + 3</em>. Exit: <em>60–90 days</em>, majority of votes cast.<small>Only the people’s door is “amendments only”, and it is locked until Congress passes an adequate law.</small>',
    cap='Every proposal, whatever its source, needs a plebiscite. Only the people’s initiative is limited to amendments (Lambino); Santiago held RA 6735 inadequate for it.')

fig('01', 'before', '<h4>Leading cases in order</h4>', 'lambino', 'Amendment or revision, and a valid initiative? (Lambino)',
    gates([G('Does it leave the substantial entirety of the Constitution intact?', 'quantitative test: how many provisions change', 'Revision', 'Congress or a convention only', 'no', 'no'),
           G('Does it leave the basic plan of government intact?', 'qualitative test: separation of powers, checks and balances; presidential, bicameral', 'Revision', 'Congress or a convention only', 'no', 'no'),
           G('If by initiative: did the people author and sign a petition containing the full text?', 'the full text on the petition or attached to it; a signature sheet with a summary is not the petition. Not an initiative? Answer yes.', 'Void initiative', 'Lambino', 'no', 'no')],
          ('Valid amendment', 'any of the three doors; then the plebiscite. But an initiative still has no adequate enabling law (Santiago).', 'ok'),
          facts=[fact('Lambino (2006)', 'The Lambino group gathers 6.3 million signatures to shift from a bicameral presidential system to a unicameral parliamentary one. The signature sheets do not contain the full text.', 'n', 'Quantitatively it overhauled Arts. VI and VII (105 provisions) and qualitatively it changed the basic plan, so it is a revision; and the signature sheet was not the petition. Any one defect is enough (8–7).'),
                 fact('Economic provisions drive', 'A “people’s initiative” would let Congress amend the economic provisions by ordinary law (“unless otherwise provided by law”). Local officials hand out signature sheets that describe the change in one sentence.', 'y?,y?,n', 'Whether it is a revision is arguable, so the walk moves on. The one-line summary fails Lambino’s full-text rule; Santiago still blocks initiatives; and if officials drive it, it is not a <em>people’s</em> initiative.'),
                 fact('A term change by Congress', 'Congress, sitting as a constituent assembly and voting by three-fourths of all its Members, proposes to lengthen the terms of district representatives.', 'y,y,y', 'One provision, no change to the basic plan: an amendment, which Congress may propose. It still needs a plebiscite 60 to 90 days later, and the joint-or-separate voting question remains open.')]),
    kind='gates', when='the facts describe a proposed change and ask whether the people can make it by initiative.',
    hook='Revision if <em>Quantity</em> or <em>Quality</em> fails; a valid initiative needs the people to <em>author and sign</em> the <em>full text</em>.',
    cap='Either test alone can make a change a revision. Lambino’s proposal (presidential to parliamentary, bicameral to unicameral, 105 provisions) failed both.')


# =====================================================================
# 02 · judicial review
# =====================================================================
fig('02', 'before', '<div class="test"><b>Levels of scrutiny (class reviewer)</b>', 'review', 'Two clauses of judicial power, three things it does',
    cmp(['Classical (first clause)', 'Expanded (second clause)'], [
        ('What', 'settle actual controversies involving rights which are legally demandable and enforceable', 'determine whether there has been grave abuse of discretion amounting to lack or excess of jurisdiction by any branch or instrumentality'),
        ('Why it is there', 'the traditional judicial function', 'Marcos’s Court hid behind the political question doctrine; the framers closed that door (Gatmaytan)'),
        ('Effect', 'courts decide cases, not questions', '“almost every political issue now reaches the Supreme Court”; the political question doctrine is narrow')])
    + sp(acro(('C', 'checking: striking down'), ('L', 'legitimating: upholding'), ('S', 'symbolic: controlling principles for bench and bar (the root of a mootness exception)')))
    + sp(N('Express, not implied', 'unlike the US, where judicial review rests on <i>Marbury v. Madison</i>, ours is granted in the text (Art. VIII, Secs. 1 and 5(2))', 'plain')),
    kind='comparison', when='a respondent says the issue is “political” or that the Court has no business reviewing Congress or the President.',
    hook='Clause 1 decides <em>disputes</em>; clause 2 polices <em>grave abuse</em> by anyone. The Court <em>checks</em>, <em>legitimates</em>, <em>symbolizes</em>.',
    cap='Angara: when the Court draws constitutional boundaries it asserts no superiority; it performs a duty, limited to actual cases and the lis mota, with a presumption of constitutionality.')

fig('02', 'before', '<p>Use the levels when a news question', 'scrutiny', 'From deference to suspicion: the three levels',
    '<div class="scale"><div class="z3" style="flex:1">Rational basis</div><div class="z2" style="flex:1">Intermediate</div><div class="z1" style="flex:1">Strict scrutiny</div></div><div class="scale-l"><span>law presumed valid · the challenger’s burden</span><span>the burden moves to the government →</span></div>'
    + sp(cmp(['Rational basis', 'Intermediate', 'Strict'], [
        ('Applies to', 'everything else', 'quasi-suspect classes (sex, illegitimacy); important but not fundamental rights', 'fundamental rights; suspect classes'),
        ('End', 'a legitimate interest', 'an important objective', 'a compelling interest'),
        ('Means', 'reasonably related; not arbitrary', 'substantially related', 'narrowly tailored; the least restrictive means'),
        ('Seen in', 'Albano: nominee rules by law must at least pass this; the ban on losing candidates did not', '(no case in your coverage)', 'SPARK: curfews of Manila and Navotas struck down; Kabataan: biometrics passed')])),
    kind='scale', when='a law classifies people (an age cap, a curfew for minors, a rule for one group) or burdens a right such as suffrage.',
    hook='Ends climb <em>legitimate → important → compelling</em>; means tighten <em>reasonable → substantial → narrowest</em>.<small>Pick the level in one sentence, then apply it. Saying which level and why is half the credit.</small>',
    cap='Pick the level first, in one sentence, then apply it. SPARK applied strict scrutiny to the curfews and struck down the Manila and Navotas ordinances.')

fig('02', 'after', '<h3 id="jr-req">The requisites of judicial review</h3>\n', 'jr', 'Can the Court rule on it? Six gates before the merits',
    gates([G('Justiciable?', 'not a truly political question: the Constitution sets limits or standards (Francisco)', 'Political question', 'review only for grave abuse', 'no', 'sun'),
           G('Actual case: is it ripe?', 'an accomplished act with a direct adverse effect; not a bill, a draft, a proposal', 'Advisory opinion: dismiss', 'Montesclaros; Lozano', 'no', 'no'),
           G('… and not moot, or an exception applies?', 'if moot, does one of the four exceptions apply? (David; Sanlakas)', 'Moot, no exception: dismiss', 'KAPIT; Lacson', 'no', 'no'),
           G('Proper party?', 'direct injury, or a recognized kind of standing; transcendental importance can relax it', 'No standing: dismiss', 'AIWA; Joya', 'no', 'no'),
           G('Raised at the earliest opportunity?', 'in the pleadings before a competent court', 'Too late: not considered', 'Arceta', 'no', 'no'),
           G('Is it the lis mota?', 'the case cannot be decided on another ground', 'Decide on the other ground', 'Arceta', 'no', 'sun')],
          ('The Court reaches the merits', 'and the presumption of constitutionality applies', 'ok'),
          facts=[fact('A bill on second reading', 'A party-list representative and a citizens’ group file certiorari in the Supreme Court against a House bill, approved on second reading, that would cap party-list nominees’ age at 60.', 'y,n', 'A bill creates no rights and imposes no duties; ruling on it would be an advisory opinion (Montesclaros; In re JDF). Dismiss, without prejudice to a challenge once it becomes law.'),
                 fact('KAPIT (2026)', 'Transport groups challenge the cities’ no-contact apprehension ordinances. Before the decision, the ordinances are suspended and the 2023 Metro Manila Traffic Code takes over.', 'y,y,n', 'Supervening events left no practical relief. The exceptions apply to the issuance under challenge, not to an unchallenged successor, and motorists’ interest alone is not paramount public interest. Most petitioners also lacked standing or capacity.'),
                 fact('Sanlakas (2004)', 'Legislators and groups challenge a declared state of rebellion after a mutiny; the President lifts it before the Court decides.', 'y,y,y,y,y,y', 'Moot, but capable of repetition yet evading review, so the Court ruled. Only the legislator-petitioners had standing. On the merits: valid, but legally superfluous.'),
                 fact('A highway route', 'Residents ask the Court to order a different alignment for a government expressway because the chosen route is unwise.', 'n', 'Choosing a route on grounds of wisdom is for the political branches (Torrecampo); the Court asks only whether there was grave abuse.')]),
    kind='gates', when='the question says “resolve” or “will the petition prosper”: these gates are your procedural paragraph.',
    hook=acro(('A', 'actual case: ripe, not moot'), ('P', 'proper party'), ('E', 'earliest opportunity'), ('L', 'lis mota')) + '<em>APEL</em>: no appeal to the Court without all four, and justiciability before any of them.',
    cap='Read the gates top to bottom in the procedural paragraph of your answer. Any “no” ends the case before the merits, which is why KAPIT (2026) never reached the NCAP ordinances.')

fig('02', 'before', '<h4>1. Actual case: ripeness</h4>', 'ripe', 'The ripeness window: too early, just right, too late',
    zones([('Too early: not ripe', 'a bill (Montesclaros; In re JDF); a House resolution calling for a constituent assembly (Lozano); a peace agreement that needs a law (PHILCONSA 2016); fear that a power may be abused (PACU); the mere passage of a law with no injury (Falcis)', 'no'),
           ('Ripe: the Court decides', 'an accomplished act with a direct adverse effect on the petitioner', 'ok'),
           ('Too late: moot', 'a supervening event leaves no practical relief: a lifted proclamation (Lacson v. Perez); a later ruling and an amendatory law (' + C('atlas', 'Atlas') + '); replaced ordinances (KAPIT)', 'no')], cols='1.2fr .8fr 1.2fr')
    + '<div class="zarrow"><span>proposal stage</span><span>law in force, applied to you</span><span>events overtake the case</span></div>'
    + sp(sub('Moot? Four ways back in (David v. Macapagal-Arroyo; Sanlakas)') + acro(('G', 'grave violation of the Constitution'), ('E', 'exceptional character and paramount public interest'), ('F', 'formulate controlling principles for bench, bar and public'), ('C', 'capable of repetition yet evading review')))
    + sp(grid(N('KAPIT’s limit', 'the exceptions attach to the issuance under challenge, not to an unchallenged successor; motorists’ interest alone is not paramount public interest', 'sun'),
              N('Gatmaytan on Pangilinan (ICC withdrawal)', '“variant technicalities”: the Court called it moot and denied senators standing; he argues an invalid withdrawal could not take effect and the case fit every exception', 'sun'), m=200)),
    kind='timeline', when='the facts mention a bill, a draft, a proposal, or an event that ended before the case was decided.',
    hook='Goldilocks: <em>too early</em> (a bill), <em>too late</em> (moot), <em>just right</em> (an accomplished act that hurts you). Moot rescue: <em>G-E-F-C</em>.',
    cap='Ripeness and mootness are two ends of the same “actual case” requirement. Say which end you are at in one sentence.')

fig('02', 'after', '<h4>2. Proper party (standing)</h4>\n', 'standing', 'Who may sue? The rule and seven doors around it',
    hub('Direct injury: injured, traceable, redressable (AIWA; Joya)', [
        ('Citizen', 'a public right or duty: publication, information (Tañada; Chavez v. PEA)'),
        ('Taxpayer', 'illegal disbursement of public funds, or an unconstitutional tax (' + C('itf', 'ITF') + '; not in Joya or AIWA)'),
        ('Voter', 'validity of an election law or election (Tolentino v. COMELEC, 2004)'),
        ('Legislator', 'the act impairs Congress’s or the legislator’s prerogatives (Ople; Sanlakas)'),
        ('Association / third party', 'members injured and the interest germane (KMU; CHREA; not IBP v. Zamora); or injury-in-fact, close relation, hindrance (White Light)'),
        ('Government', 'the State challenging its own law (People v. Vera)'),
        ('Environment', 'any citizen as steward of nature (Resident Marine Mammals)'),
        ('Transcendental importance', 'relaxes all of the above; factors: the funds involved, a clear disregard of a prohibition, no party with a more direct interest. IBP v. Zamora: ruled anyway; AIWA: refused', 'sun')]),
    kind='mind map', when='you reach the “proper party” sentence of your procedural paragraph: name the door and justify it in one line.',
    hook=acro(('C', 'citizen'), ('T', 'taxpayer'), ('V', 'voter'), ('L', 'legislator'), ('A', 'association / third party'), ('G', 'government'), ('E', 'environment')) + '“<em>C</em>an <em>T</em>he <em>V</em>oters <em>L</em>ift <em>A</em> <em>G</em>rave <em>E</em>rror?”',
    cap='The center is the general rule; each spoke is an exception you must name and justify in one line.')

fig('02', 'after', '<h3 id="jr-effects">Effects of a declaration of unconstitutionality</h3>\n', 'effects', 'Void from the start, but…',
    zones([('Void from the start', 'orthodox view (Civil Code, Art. 7): an unconstitutional act confers no rights, imposes no duties, creates no office; as if never passed', 'acc'),
           ('…the past may stand', 'operative fact: acts done in good-faith reliance before the declaration may be respected. Araullo (DAP projects that could not be undone, but not the authors absent findings of good faith); Macalintal 2023 (the October 2023 barangay elections went ahead). Refused where it would reward the beneficiary of the void law (Fertiphil).', 'sun'),
           ('…the rest may stand', 'partial unconstitutionality: valid parts survive if separable; a separability clause only creates a presumption (ABAKADA kept RA 9335 but Sec. 12; Lidasan voided a whole law). Gatmaytan: severability should not depend on the clause.', 'sun')]),
    kind='three panels', when='the question asks what happens to acts already done under the void law, or to the rest of the statute.',
    hook='<em>Void</em>… but the <em>past</em> may stand (operative fact) and the <em>rest</em> may stand (separability).',
    cap='These are the E lines of CLEAR: write them only when the facts ask about consequences, not as filler.')

fig('02', 'after', '<h3 id="jr-forum">Remedies and forum (quick guide)</h3>\n', 'forum', 'Where does the case go?',
    grid(N('Supreme Court · Rule 65', 'certiorari or prohibition under expanded jurisdiction; directly only for issues of transcendental importance, otherwise mind the hierarchy of courts', 'acc'),
         N('RTC · declaratory relief', 'for a law not yet violated (Exec. Sec. v. CA; White Light)', 'acc'),
         N('COMELEC → HRET or SET', 'COMELEC until the winner is a Member; the tribunal after proclamation, oath and assumption; the Supreme Court as PET for President and Vice President', 'acc'),
         N('COA first', 'money claims against the State (Fetalvero)', 'acc'), m=160)
    + sp(grid(N('Hierarchy of courts; forum shopping', 'separate grounds for dismissal: KAPIT went straight to the Supreme Court and filed related cases in different courts', 'no'),
              N('Raise it below first', 'in Arceta the accused should first have moved to quash in the trial court', 'sun'), m=200)),
    kind='map', when='you write the first clause of the procedural paragraph.',
    hook='<em>Remedy and forum</em> first, then <em>A-P-E-L</em>, then the merits.',
    cap='Two or three lines of procedure, in this order, then turn to the merits.')


# =====================================================================
# 03 · territory (finals coverage)  ·  04 · citizenship (finals coverage)
# =====================================================================
fig('03', 'after', '<h3 id="terr-zones">Territory versus maritime zones</h3>\n', 'zones', 'Maritime zones measured from the baselines',
    '<div class="scale"><div class="z1" style="flex:12">TS</div><div class="z2" style="flex:12">CZ</div><div class="z3" style="flex:176">Exclusive economic zone</div></div><div class="scale-l"><span>baseline 0</span><span>12 nm</span><span>24 nm</span><span>200 nm</span></div>'
    + sp(grid(N('Internal / archipelagic waters', 'landward of the baselines: sovereignty (innocent and sea-lanes passage apply)', 'acc'), N('Territorial sea (TS)', '12 nm: sovereignty, subject to innocent passage', 'acc'),
              N('Contiguous zone (CZ)', 'to 24 nm: customs, fiscal, immigration, sanitary control', 'plain'), N('EEZ', 'to 200 nm: sovereign rights over resources, not sovereignty', 'sun'),
              N('Continental shelf', 'natural prolongation, at least 200 nm (up to 350 nm in some cases): sovereign rights over the seabed', 'plain'), m=140))
    + sp(sub('What a feature generates (UNCLOS Art. 121, as applied in the 2016 Award)') + grid(N('Island', 'sustains human habitation or economic life of its own: EEZ and continental shelf', 'ok'), N('Rock', 'cannot: a 12-nm territorial sea only', 'sun'), N('Low-tide elevation', 'none; judged in its natural condition, so reclamation does not upgrade it', 'no'), m=150)),
    kind='scale', when='a West Philippine Sea story asks about “territory”, “sovereignty” or “sovereign rights”.',
    hook='<em>12 · 24 · 200</em>. Sovereignty stops at 12; beyond it, sovereign rights, not territory.',
    cap='Sovereignty stops at 12 nm; beyond it the Philippines has sovereign rights, not territory. Magallona: baselines laws mark zones; they neither add nor cede territory.')

fig('04', 'after', '<h3 id="cit-natural">Natural-born or naturalized</h3>\n', 'natural', 'Natural-born or naturalized?',
    vflow(N('Was either parent a Filipino citizen at birth?', 'Art. IV, Sec. 1(2); no act needed to acquire or perfect it (Sec. 2)', 'acc'), VE('yes'), N('Natural-born', 'eligible for natural-born offices', 'ok'))
    + sp(grid(N('Born before Jan. 17, 1973 of a Filipino mother, elected at majority', 'deemed natural-born (Secs. 1(3), 2)', 'sun'), N('Foundling', 'presumed natural-born (David v. SET; RA 11767)', 'sun'),
              N('Reacquired under RA 9225 or by repatriation', 'natural-born status restored (David v. SET; Bengson)', 'sun'), N('Naturalized (CA 473; RA 9139; by statute)', 'not natural-born', 'no'), m=150)),
    kind='flow', when='the facts ask whether someone may hold an office reserved for natural-born citizens.',
    hook='<em>Blood, not soil.</em> A Filipino parent at birth = natural-born; three yellow side doors also lead there: <em>elected</em>, <em>found</em>, <em>reacquired</em>.',
    cap='The yellow boxes are the routes students forget: election under the 1935 rule, foundlings, and reacquisition all end at natural-born.')


# =====================================================================
# 05 · suffrage
# =====================================================================
fig('05', 'after', '<h3 id="suff-quals">Qualifications versus regulation</h3>\n', 'suffrage', 'Is the new voting condition valid?',
    cmp(['Substantive qualifications', 'Procedural regulation'], [
        ('Source', 'Art. V, Sec. 1: citizen, 18, one year in the Philippines, six months in the place of voting, not disqualified by law', 'statute and COMELEC rules: registration, deadlines, biometrics'),
        ('Can Congress add to it?', 'no literacy, property or other substantive requirement', 'yes, if reasonable and it serves a valid end'),
        ('Cases', 'Ceniza: a burden with no permissible State objective is barred', 'Kabataan; Palatino; AKBAYAN')])
    + sp(gates([G('Is it procedure (registration, deadlines, biometrics), not a new qualification?', 'a test, a fee, property, or a burden that serves no permissible State objective (Ceniza) is a prohibited substantive requirement', 'Void', 'a substantive requirement (Art. V, Sec. 1)', 'no', 'no'),
                G('Is it reasonable, and if it burdens the right, does it pass strict scrutiny?', 'compelling interest, least restrictive means (Kabataan)', 'Void', 'an unreasonable regulation', 'no', 'no'),
                G('Did the right body make it, within the law?', 'registration runs until 120 days (regular) or 90 days (special) before the election (RA 8189, Sec. 8); COMELEC may fix other dates only if it shows the pre-election acts cannot otherwise be done (Palatino)', 'Void', 'beyond COMELEC’s power (Palatino)', 'no', 'no')],
               ('Valid regulation of suffrage', 'e.g., no special registration inside the prohibitive period (AKBAYAN)', 'ok'),
               facts=[fact('No Bio, No Boto (2015)', 'COMELEC will deactivate registered voters who have not had their biometrics taken before the 2016 elections; deactivated voters may reactivate.', 'y,y,y', 'Biometrics validation is part of registration, not a qualification, and it passes strict scrutiny: a clean voters’ list is compelling, and reactivation keeps the means least restrictive (Kabataan).'),
                      fact('A reading test', 'A new law requires first-time voters to pass a short reading test before they may register.', 'n', 'A literacy requirement is expressly barred by Art. V, Sec. 1. No balancing is needed.'),
                      fact('An early deadline', 'COMELEC sets the registration deadline for the May 2028 elections on September 30, 2027, citing its new automated system, and shows nothing more.', 'y,y?,n', 'Congress fixed continuing registration until 120 days before a regular election. COMELEC’s stand-by power needs proof that pre-election acts cannot reasonably be done in time (Palatino; AKBAYAN); convenience is not enough.')])),
    kind='gates', when='a law or COMELEC rule adds anything a voter must do, show, pass or pay, or moves a registration deadline.',
    hook='<em>18 · 1 · 6</em>, and no <em>L-P-S</em> (literacy, property, other substantive requirement).<small>Registration is procedure: valid if reasonable; the 120/90-day wall belongs to Congress.</small>',
    cap='Sort the measure first: a new qualification is void; a registration rule is valid if reasonable and made by the body the law empowers.')

fig('05', 'after', '<h3 id="suff-residence">Residence</h3>\n', 'domicile', 'Did he really move? Three keys to a new domicile',
    acro(('1', 'bodily presence in the new place'), ('2', 'intent to remain there (<i>animus manendi</i>)'), ('3', 'intent to abandon the old (<i>animus non revertendi</i>)'))
    + '<p style="font-size:.84rem;color:var(--muted);margin:2px 0 10px!important">…shown by acts consistent with that intention. Change is not presumed: whoever alleges it must prove all three, and it must be voluntary (Gallego; Romualdez).</p>'
    + cmp(['Does not lose the old domicile', 'Does not prove a new one'], [
        ('Examples', 'absence to work or study; forced exile (Romualdez); marriage, for a wife (Marcos). A minor simply follows the parents’ domicile.', 'leasing a unit, which shows an intent to lease (Aquino); registering, voting and getting a residence certificate where one works (Gallego); a sitting official who keeps serving elsewhere (Mangudadatu)')]),
    kind='keys', when='a voter or candidate “moved”, “transferred”, “leased”, “works abroad” or married into another place.',
    hook='Body there, heart staying, heart left home: <em>all three</em>, or you never moved.',
    cap='The same rule governs voters and candidates (Aquino; Marcos; Mangudadatu), so this figure also answers the residence question for Senators and Representatives.')


# =====================================================================
# 06 · government, immunity, inherent powers
# =====================================================================
fig('06', 'after', '<h3 id="gov-defacto">De jure, de facto and revolutionary governments</h3>\n', 'govkinds', 'Kinds of government',
    '<div class="tree"><div class="root">Government</div><div class="tstem"></div><div class="kids">'
    + N('De jure: of right', 'placed in power under the constitution and laws', 'ok')
    + '<div>' + N('De facto: in fact', 'must be obeyed in civil matters while it lasts; its non-political acts survive restoration (postliminy)', 'acc')
    + '<div style="display:flex;flex-direction:column;gap:6px;margin-top:6px">' + N('1 · Usurper', 'usurps the legitimate government by force or the majority’s will', 'plain') + N('2 · Invader', 'established by an invading force: paramount force (Co Kim Cham); may suspend laws but must respect those on public order and commerce', 'plain') + N('3 · Secessionist', 'set up by insurgents who secede', 'plain') + '</div></div>'
    + N('Revolutionary', 'bound by no constitution, but by the ICCPR and the UDHR; its directives bind only if enforcers stay within its grant and respect those instruments (Republic v. Sandiganbayan)', 'sun')
    + '</div></div>',
    kind='tree', when='a story mentions a “revolutionary government”, an occupation, or acts done under a government that later fell.',
    hook='De facto comes in three: <em>Usurp</em>, <em>Invade</em>, <em>Secede</em>.<small>A sitting president who declares a revolutionary government repudiates the Constitution that gave him office.</small>',
    cap='De facto governments must be obeyed in civil matters while they last; their non-political acts survive restoration.')

fig('06', 'after', '<h3 id="gov-immunity">Immunity from suit</h3>\n', 'immunity', 'Can the State be sued here, and can you collect?',
    gates([G('Is it really a suit against the State?', 'a judgment would make the State pay or act (Arigo)', 'Not against the State: the suit proceeds', 'the officer acted ultra vires, is sued personally for a tort, or only nullification is sought (PASI)', 'no', 'ok'),
           G('Has the State consented?', 'expressly by law; impliedly when it sues or enters a commercial (jure gestionis) contract; for an incorporated agency, read its charter (GTZ). Foreign States: sovereign acts (jure imperii) are immune, and so are agents acting within official functions with the host State’s consent (Minucher; Arigo)', 'Immune: dismiss', '', 'no', 'no')],
          ('The suit proceeds, but suability is not liability', 'no garnishment of public funds; money claims go to COA (Fetalvero); no unjust enrichment for completed public works (Vigilar)', 'sun'),
          facts=[fact('Tubbataha (Arigo, 2014)', 'After the USS Guardian runs aground on Tubbataha Reef, petitioners sue the US Navy officers for damages and to nullify the VFA.', 'y,n', 'Sued in their official capacity, the officers stand for the United States; satisfying the judgment would need US action and funds. The flag State answers internationally under UNCLOS.'),
                 fact('Orbital slot (PASI, 2006)', 'A DOTC undersecretary offers for bidding an orbital slot already promised to PASI, and allegedly defames its CEO. PASI sues him to nullify the act and for damages.', 'n', 'Nullifying an ultra vires act and suing an official personally for torts charge nothing to the treasury: not a suit against the State.'),
                 fact('Garnished funds (Fetalvero, 2019)', 'A landowner obtains a judgment for just compensation against DPWH, and the trial court garnishes DPWH funds when payment does not come.', 'y,y', 'Liability was fixed, but government funds cannot be garnished even if appropriated; the claimant files a money claim with COA, with legal interest.'),
                 fact('GTZ (2009)', 'Filipino employees sue GTZ, a German implementing agency, for illegal dismissal. It claims immunity but shows no charter, no proof of German law and no DFA certification.', 'y?,y', 'An incorporated agency’s suability depends on its charter or the general law; GTZ, organized under private law, failed to establish immunity, so the Labor Arbiter had jurisdiction.')]),
    kind='gates', when='anyone sues an agency, an officer, a foreign State or its agent, or tries to garnish or levy on public funds.',
    hook='Three questions: <em>Is it the State? Did it consent? Can you collect?</em><small>Winning the suit is not collecting the money: COA first.</small>',
    cap='Two questions in order, then the payoff warning. Most exam traps are in the last box: winning the suit is not collecting the money.')

fig('06', 'before', '<h4>Regulation or taking?</h4>', 'powers3', 'The three inherent powers side by side', cmp(['Police power', 'Eminent domain', 'Taxation'], [
    ('Does what', 'regulates liberty and property for the general welfare', 'takes private property for public use', 'raises revenue (also regulates)'),
    ('Compensation', 'none: the owner keeps the property', 'just compensation (Art. III, Sec. 9)', 'none directly; the benefit is government'),
    ('Limits', 'lawful subject + lawful means; strict scrutiny if rights are burdened', 'public use + just compensation', 'public purpose; uniform and equitable; Art. VI, Sec. 28'),
    ('Cases', 'Rubi; Agustin; Zabal; White Light; Iloilo I', 'Ericta; PPI v. COMELEC', 'Lung Center; John Hay')]),
    kind='comparison', when='a measure burdens a business or property and you must say which power the State is using.',
    hook='Police <em>restrains</em> · Domain <em>takes, and pays</em> · Tax <em>raises</em>.',
    cap='The exam question is usually the first column against the second: if the measure appropriates property or its use for the public, it is a taking and must be paid for.')

fig('06', 'before', '<aside class="note news"><strong>In a news question (2023: Manila cinemas', 'taking', 'Regulation or taking? Walk the measure',
    gates([G('Does the measure appropriate property, or its beneficial use, for the public?', 'rather than restraining a noxious or harmful use', 'Police power: test it', 'lawful subject (public, not class, interest) + lawful means (reasonably necessary, not unduly oppressive); for an LGU also: within its delegated power, consistent with law, and regulating rather than prohibiting a lawful business (Cruz v. Paras; White Light)', 'no', 'acc'),
           G('Does the owner hold a franchise or privilege over a public resource, such as the airwaves?', 'the condition then comes with the privilege', 'Valid condition of the franchise, not a taking', 'TELEBAP', 'yes', 'ok')],
          ('A taking: it must be paid for', 'just compensation (Art. III, Sec. 9); without it, void (Ericta; PPI)', 'no'),
          facts=[fact('Paupers’ graves (Ericta, 1983)', 'A Quezon City ordinance requires private cemeteries to set aside 6% of their land for paupers’ graves.', 'y,n', 'The ordinance appropriates land for public use without paying for it: a taking, not a police measure; void.'),
                 fact('Free print space (PPI, 1995)', 'COMELEC requires newspapers to give it free print space for election information.', 'y,n', 'Commandeering private property for public use requires just compensation; COMELEC may buy the space, not take it.'),
                 fact('Free airtime (TELEBAP, 1998)', 'The law requires broadcasters to give COMELEC free airtime.', 'y,y', 'The airwaves are public property and a franchise is a privilege subject to amendment for the common good; the free airtime is a condition of the franchise.'),
                 fact('Senior citizens’ discount', 'The law grants seniors a 20% discount that establishments may claim only as a tax deduction, not a full tax credit.', 'n', 'A valid exercise of police power, not a taking requiring full compensation (Manila Memorial Park v. DSWD).'),
                 fact('Cinema screen time (2023 Q3)', 'A Manila ordinance requires every cinema to show city messages before each screening, free of charge.', 'y?,n', 'Answer either way, but apply both tests to the exact words. Cinemas hold no franchise over a public resource, so PPI and Ericta point to a taking.')]),
    kind='gates', when='a law or ordinance makes private businesses give something for free, set aside property, or grant discounts.',
    hook='<em>Restrain</em> = police power, no pay. <em>Take</em> = eminent domain, pay. <em>Franchise over a public resource</em> = the condition rides with the privilege.',
    cap='Non-impairment yields to police power (Iloilo I), but only to a valid exercise of it.')


# =====================================================================
# 07 · composition, qualifications, party-list, vacancies
# =====================================================================
fig('07', 'after', '<h3 id="comp-quals">Qualifications cannot be added by law</h3>\n', 'quals', 'Senator, Representative, party-list nominee; and can Congress add a condition?',
    cmp(['Senator (Sec. 3)', 'District Representative (Sec. 6)', 'Party-list nominee (RA 7941)'], [
        ('Citizenship', 'natural-born', 'natural-born', 'natural-born'),
        ('Age on election day', 'at least 35', 'at least 25', 'at least 25 (youth sector: 25 to 30)'),
        ('Literacy', 'able to read and write', 'able to read and write', 'able to read and write'),
        ('Voter', 'registered voter', 'registered voter in the district', 'registered voter'),
        ('Residence', 'the Philippines: at least 2 years before election day', 'the district: at least 1 year before election day', '1 year in the Philippines; bona fide member of the party for 90 days'),
        ('Term · limit', '6 years · 2 consecutive terms', '3 years · 3 consecutive terms', '3 years · 3 consecutive terms')])
    + sp(gates([G('Are the office’s qualifications fixed by the Constitution?', 'yes for President, Vice President, Senators and district Representatives; no for local offices, the SK and party-list nominees (“as provided by law”)', 'Statutory office: Congress may add conditions', 'if reasonable and consistent with equal protection (Albano)', 'no', 'acc'),
                G('Does the law add a condition for running or being elected?', 'a test, a requirement or a disqualification not in Secs. 3 and 6, direct or indirect', 'Void: it adds a qualification', 'SJS v. DDB', 'yes', 'no')],
               ('Valid', 'it regulates without adding to the constitutional list', 'ok'),
               facts=[fact('Drug tests (SJS v. DDB, 2008)', 'A law requires every senatorial candidate to pass a mandatory drug test.', 'y,y', 'Senators’ qualifications are fixed by Art. VI, Sec. 3; a drug test adds one, so it is void.'),
                      fact('Debate law (2023 Q4)', 'A law disqualifies candidates for Senator and Representative who skip COMELEC-sponsored debates.', 'y,y', 'Disqualifying for skipping debates adds a qualification (SJS v. DDB). Add free speech: a candidate cannot be compelled to speak.'),
                      fact('SK anti-dynasty rule (2015)', 'The SK Reform Act bars relatives of elected officials from SK office.', 'n', 'SK office is statutory, so Congress may set its qualifications; the rule is also germane to the SK law’s title.'),
                      fact('Nominee age cap', 'A new law caps party-list nominees’ age at 60.', 'n', 'Nominee qualifications are “as provided by law”, so Congress may legislate them, but they must pass equal protection (Albano): argue whether the cap has a rational basis.')])),
    kind='comparison + gates', when='a law, COMELEC rule or proposal disqualifies candidates who do, or fail to do, something.',
    hook=plates(('35·2·6·2', 'Senator: age · years in PH · years per term · terms'), ('25·1·3·3', 'Representative: age · years in district · years per term · terms')) + 'Fixed by the Constitution, so <em>Congress cannot add</em>; only party-list nominees’ rules are “as provided by law”.',
    cap='These are fixed by the Constitution; Congress cannot add to them (SJS v. DDB). Only party-list nominees’ qualifications are “as provided by law” (Albano).')

_PL_GROUPS = '[["Group A",1000000],["Group B",600000],["Group C",400000],["Group D",300000],["Group E",250000],["Group F",200000],["Group G",190000],["Group H",100000]]'
fig('07', 'after', '<h3 id="comp-partylist">The party-list system</h3>\n', 'partylist', 'Party-list seats: run the BANAT rounds',
    '<div class="scale"><div class="z3" style="flex:80">District representatives · 80%</div><div class="z1" style="flex:20">Party-list 20%</div></div>'
    + sp(vflow(N('Seats available', '(district seats ÷ 0.80) × 0.20', 'acc'), VE('rank groups by votes'), N('Round 1 · guaranteed', 'each group with at least 2% of valid party-list votes gets 1 seat; the divisor includes votes for groups later disqualified (Araro)', 'acc'), VE('remaining seats'), N('Round 2 · additional', 'remaining seats × each group’s %; whole numbers only; no 2% floor in this round (AKMA-PTM)', 'acc'), VE('if seats remain'), N('Round 3 · one each down the ranking', 'until all seats are filled', 'acc'), VE('cap'), N('No group gets more than 3 seats', '', 'sun')))
    + sp(f'<div class="calc plcalc" data-district="252" data-groups=\'{_PL_GROUPS}\' data-others=\'{{"n":100,"v":69600}}\'><div class="ctl"><label>District seats<input type="number" min="0" data-v="district"></label><button type="button" class="btn small ghost" data-a="reset">Reset the example</button></div><div class="tw2"><table><thead><tr><th>Group</th><th>Votes</th><th class="pc">Share</th><th>Rd 1</th><th>Rd 2</th><th>Rd 3</th><th>Seats</th></tr></thead><tbody></tbody></table></div><div class="msg"></div></div>'),
    kind='interactive', when='the facts give vote shares, ask how many seats a group gets, or propose changing the formula.',
    hook='<em>80/20</em> · <em>2%</em> buys one seat · the rest by share, no 2% floor · <em>3</em> seats max.<small>Try it: in the example, Group G has only 1.9% yet wins a round-2 seat, and Group A is stopped by the cap.</small>',
    cap='Change the district seats or any group’s votes; the table reruns all three rounds. The example is invented; the rounds are BANAT’s.', notest=True)

fig('07', 'before', '<h4>Nominees</h4>', 'plhist', 'How party-list doctrine moved, and who decides what',
    tl([('2001', 'Ang Bagong Bayani: the system is for the marginalized and underrepresented', ''),
        ('2009', 'BANAT: the seat formula; no 2% floor for additional seats', ''),
        ('2010', f'{C("angladlad", "Ang Ladlad")}: no exclusion on moral grounds', ''),
        ('2013', f'{C("atongpaglaum", "Atong Paglaum")}: national, regional and sectoral parties; national and regional parties need not be marginalized; six parameters. A party with district candidates joins only through a separately registered sectoral wing. Later: no track record required (Abang Lingkod). Sereno, C.J., dissented.', 'key'),
        ('2023', f'{C("albano", "Albano")}: Congress may set nominee qualifications, but they must pass equal protection; the ban on losing candidates was void', ''),
        ('2024', f'{C("duterteyouth", "Duterte Youth")}: substitution deadlines stay mandatory after the election; {C("anwaray", "An Waray")}: COMELEC may cancel a group’s registration even with a sitting member', '')])
    + sp(cmp(['COMELEC', 'HRET'], [
        ('Decides', 'registration and cancellation of the group (An Waray; due process: Senior Citizens); internal leadership and nominations before assumption (Lokin); substitution of nominees (Duterte Youth)', 'the qualifications or expulsion of a sitting member, once the group is proclaimed and the nominee has taken the oath and assumed office (Lico; Abayon v. HRET, 2010)')]))
    + sp(grid(N('At least five nominees', 'one qualified nominee saves the group from others’ disqualification, but not from failing to submit five (COCOFED)', 'plain'),
              N('No term-sharing', 'contrary to the three-year term and public policy (Senior Citizens)', 'no'),
              N('Membership is continuing', 'a nominee must stay a bona fide member; expelling a sitting member is for the HRET (Lico)', 'plain'), m=160)),
    kind='timeline + forum', when='a story is about who may join the party-list system, nominee rules, substitution, or expelling a party-list member.',
    hook='Atong Paglaum <em>opened the door</em>; Albano lets Congress <em>set nominee rules, rationally</em>.<small>COMELEC keeps <em>the group</em>; the HRET gets <em>the seated member</em>.</small>',
    cap='Atong Paglaum is the turning point; every later case applies it. Read the forum column before you name a remedy.')

fig('07', 'after', '<h3 id="comp-elections">Elections and vacancies</h3>\n', 'vacancy', 'A seat falls vacant: who calls the special election, and when?',
    grid(N('Senate vacancy', 'the special election is held with the next regular election (Tolentino v. COMELEC, 2004)', 'acc'),
         N('House vacancy, at least one year before the term ends', 'COMELEC must call a special election 60 to 90 days after the vacancy, without waiting for a House resolution; mandamus lies against COMELEC, not the House, since Sec. 9 says “may” (Hagedorn, 2025)', 'acc'), m=200)
    + sp(grid(N('The winner', 'serves only the unexpired term (Sec. 9)', 'plain'),
              N('Election day', 'second Monday of May unless a law provides otherwise; COMELEC cannot suspend an election on its own (Bañas-Nograles)', 'sun'),
              N('A new district mid-period', 'applies at the next regular election; resetting the vote would cut the three-year term (Bañas-Nograles)', 'sun'), m=160)),
    kind='two lanes', when='a member dies, resigns or is removed, or someone wants an election moved.',
    hook='The Senate waits for May; the House gets <em>60–90 days</em>, and <em>COMELEC</em> calls it.',
    cap='COMELEC may rely on official press releases or a certification from the Speaker or the Secretary-General that the seat is vacant (Hagedorn).')


# =====================================================================
# 08 · officers, quorum, rules, discipline, Journal
# =====================================================================
fig('08', 'before', '<h3 id="internal-officers">', 'votes', 'The vote ladder, counted for a real chamber',
    '<div class="votec"><div class="calc"><div class="ctl"><label>All the Members<input type="number" min="1" value="24" data-v="all"></label><label>Members present<input type="number" min="0" value="24" data-v="present"></label><button type="button" class="btn small ghost" data-set="24">The Senate (24)</button></div>'
    + '<p style="font-size:.8rem;color:var(--muted)">Type the House’s membership to count it instead. Each rung shows the number of votes it takes.</p></div>'
    + sp(ladder([
        ('One-fifth', 'of Members present', 20, 'yeas and nays entered in the Journal on request (Sec. 16(4))', 'p5'),
        ('Majority', 'of each House', 51, 'quorum to do business; a smaller number may adjourn and compel attendance (Sec. 16(2))', 'quorum'),
        ('Majority', 'of all Members', 51, 'elect the Senate President or Speaker (Sec. 16(1)); grant a tax exemption (Sec. 28(4))', 'maj'),
        ('Two-thirds', 'of all Members', 67, 'suspend or expel a Member; override a veto (each House); declare war (both Houses in joint session, voting separately); call a convention', 'two3'),
        ('Three-fourths', 'of all Members', 75, 'propose amendments or revisions as a constituent assembly (Art. XVII, Sec. 1); whether the Houses vote jointly or separately is open', 'three4')])) + '</div>',
    kind='interactive', when='the facts give a vote count (“elected with 12 votes”, “expelled by 200 of 316”) or ask how many votes something needs.',
    hook='Stakes climb, fractions climb: <em>record</em> (⅕ present) → <em>do business</em> (½) → <em>choose leaders</em> (½ of all) → <em>punish, override, war, convention</em> (⅔ of all) → <em>rewrite the Constitution</em> (¾ of all).<small>In the Senate: 13 · 16 · 18. Watch the denominator: “present”, “each House” and “all the Members” are three different numbers, and Gatmaytan alters them.</small>',
    cap='The bar shows the share of votes needed. Test me hides the fractions: read what each rung is for and name its vote before you tap.')

fig('08', 'before', '<h3 id="internal-quorum">', 'internal', 'Will the courts enforce the chamber’s own rules?',
    gates([G('Is a constitutional requirement involved?', 'quorum, voting, publication', 'Courts may review', 'Pimentel v. Senate Committee of the Whole', 'yes', 'ok'),
           G('Are the rights of third parties affected?', 'someone outside the chamber whose office or rights turn on the rule', 'Courts may enforce the rule', 'Pacete', 'yes', 'ok')],
          ('Purely internal: the courts stay out', 'rules are procedural and may be waived (Arroyo v. De Venecia); officers other than the Senate President and Speaker are for the chamber (Santiago v. Guingona; Baguilat)', 'no'),
          facts=[fact('The railroaded report (Arroyo v. De Venecia)', 'House members say the chair declared the sin tax bicameral report approved without letting them question the quorum.', 'n,n', 'Violating internal rules alone is not grave abuse; absent a constitutional violation, the Court will not look behind the Speaker’s ruling and the enrolled bill.'),
                 fact('The minority leader', 'Senators ask the Court to declare who the rightful Minority Leader is.', 'n,n', 'Only the Senate President and the Speaker are elected under the Constitution; other officers are for the chamber (Santiago v. Guingona; Baguilat).'),
                 fact('The recalled confirmation (Pacete)', 'One CA member files a motion to reconsider a judge’s confirmation; it is never acted on, and the Secretary of Justice treats the confirmation as recalled.', 'n,y', 'A third party’s office was at stake, so the Court enforced the CA’s rules: only a majority of the members present can reopen a confirmation.')]),
    kind='gates', when='members complain that their own chamber broke its rules, or fight over an office the Constitution does not create.',
    hook='Courts stay out of the House’s <em>house rules</em>, unless the <em>Constitution</em> or an <em>outsider’s rights</em> are at stake.',
    cap='Only the Senate President and the Speaker are constitutionally elected (majority of all Members). Everything else is for the chamber.')

fig('08', 'after', '<h3 id="internal-quorum">Quorum</h3>\n', 'quorum', 'Quorum calculator: try Avelino',
    '<div class="qwidget calc" data-total="24"><div class="row" style="margin-bottom:10px"><button type="button" class="btn small" data-q="avelino">Load Avelino (1949)</button><button type="button" class="btn small ghost" data-q="reset">All present</button></div><div class="qdots" role="group" aria-label="24 senators"></div><div class="qread"></div></div>'
    + sp(grid(N('Member or present?', '2013 midterm: a detained Member (Dimaporo) is still counted in the base for the majority of the House; whether he is “present” is a different question. Read the exact verb.', 'sun'),
              N('Presumed to continue', 'once there, a quorum is presumed to continue unless challenged under the chamber’s procedure; the Journal and the enrolled bill control (Tinio)', 'plain'), m=200)),
    kind='interactive', when='some members are absent, abroad, detained or hospitalized and the facts ask whether the chamber could act.',
    hook='Quorum counts heads <em>within reach</em> (Avelino); electing the leader counts <em>all</em> (Sec. 16(1)).',
    cap='Tap a senator to cycle: present (filled) → absent in the country (hollow) → abroad (dashed). Senators abroad leave the base; absent ones in the country still count. In Avelino, 12 present out of a base of 23 was a quorum; under the 1987 text, electing the Senate President still needs 13.', notest=True)

fig('08', 'after', '<h3 id="internal-discipline">Discipline of members</h3>\n', 'discipline', 'Is the suspension or expulsion valid?',
    gates([G('Is the ground disorderly behavior, as the House determines?', 'wide deference (Osmeña); no conviction needed', 'Void', 'not a ground for discipline', 'no', 'no'),
           G('Did two-thirds of ALL its Members concur?', 'not just those present; needed for suspension or expulsion (censure, reprimand, fines need no two-thirds)', 'Void penalty', '', 'no', 'no'),
           G('If a suspension: 60 days or less?', 'expulsion has no cap but is the gravest penalty', 'Void', 'beyond the 60-day cap', 'no', 'no'),
           G('Was he given notice and a chance to be heard?', 'Pimentel v. Senate Committee of the Whole', 'Void', 'no due process', 'no', 'no')],
          ('Valid discipline', 'the courts will not review what the House calls disorderly', 'ok'),
          facts=[fact('Teves, argued for him (2023 Q1)', 'After two 60-day suspensions for absence, the House expels Rep. Teves by two-thirds of all its Members, citing his absence, a terrorist designation, a dance video and an asylum bid.', 'n?', 'Neutral answer: the House decides what is disorderly and the Court defers (Osmeña). Arguing for Teves: the absence was already punished twice, so expelling him for it evades the 60-day cap; the terrorist designation is an executive act, not his conduct as a Member; a video and an asylum bid do not obstruct legislative work.'),
                 fact('A 90-day suspension', 'After a hearing, the Senate suspends a senator for 90 days for disorderly behavior, by two-thirds of all its Members.', 'y,y,n', 'Discipline by the chamber is capped at 60 days. (The 90-day preventive suspension you may remember belongs to the Sandiganbayan, not the Senate.)'),
                 fact('Osmeña (1960)', 'The House suspends Rep. Osmeña for 15 months for a privilege speech accusing the President of bribery.', 'y,y,n', 'Today the 15 months would break the 60-day cap. In 1960 it stood: the 1935 text mentioned only expulsion and set no cap, and the Court treated suspension as an inherent prerogative.')])
    + sp(cmp(['The chamber (Sec. 16(3))', 'The Sandiganbayan (RA 3019, Sec. 13)'], [
        ('Nature', 'punishment for disorderly behavior', 'precaution while a case is pending'),
        ('Vote / trigger', 'two-thirds of all its Members', 'mandatory once a valid information is filed'),
        ('Limit', 'suspension at most 60 days; expulsion possible', 'at most 90 days (jurisprudence)'),
        ('Cases', 'Osmeña; Alejandrino', 'Santiago v. Sandiganbayan; De Venecia')])),
    kind='gates + comparison', when='a chamber suspends, expels, censures or otherwise punishes one of its Members.',
    hook='<em>⅔ of ALL</em> · <em>60 days</em> max · no conviction needed · hear him first.<small>A court’s 90-day preventive suspension is not discipline: different power, different cap.</small>',
    cap='Two different powers, two different limits. The 60-day cap binds only the chamber.')

fig('08', 'after', '<h3 id="internal-journal">Journal, Record and the enrolled bill</h3>\n', 'journal', 'Enrolled bill or Journal: which one wins?',
    gates([G('Do the presiding officers still stand by their signatures?', 'if they withdrew them because the enrolled text is not what was passed, there is no enrolled bill', 'Consult the Journal', 'Astorga v. Villegas', 'no', 'sun'),
           G('Is the disputed fact one the Constitution requires in the Journal?', 'yeas and nays on third reading; the veto message and override votes; yeas and nays on request of one-fifth; each Member’s impeachment vote', 'The Journal prevails on that point', 'Morales v. Subido; the Journal is conclusive on what it records (Pons)', 'yes', 'sun')],
          ('The enrolled bill is conclusive', 'the presiding officers’ signatures and the secretaries’ certification (Arroyo v. De Venecia; CoTeSCUP; Tinio); errors are fixed by amendment, not by the courts', 'acc'),
          facts=[fact('Astorga (1974)', 'After signing, the Senate President and the President withdraw their signatures: the enrolled text omitted the Senate’s floor amendments.', 'n', 'With the signatures withdrawn there was no enrolled bill, so the Court consulted the Journal: the bill never became law.'),
                 fact('Morales v. Subido (1969)', 'An applicant says the enrolled Police Act omitted a phrase approved on the floor.', 'y,n', 'The wording of a provision is not something the Constitution requires in the Journal, so the enrolled text controls; the remedy is an amendment.'),
                 fact('The missing roll call', 'A petitioner says the yeas and nays on third reading were never taken, though the enrolled bill is duly signed.', 'y,y', 'The yeas and nays on third reading must be entered in the Journal (Art. VI, Sec. 26(2)), so on that point the Journal prevails over the enrolled bill.')]),
    kind='gates', when='someone claims the law as printed is not what Congress passed, or that a required vote was never taken.',
    hook='The signed bill wins, unless the <em>signers take it back</em> (Astorga) or the <em>Constitution requires the fact in the Journal</em> (Morales).',
    cap='The enrolled bill doctrine is court-made, grounded on respect for a coequal branch.')


# =====================================================================
# 09 · salaries, privileges, offices
# =====================================================================
fig('09', 'after', '<h3 id="priv-salary">Salaries</h3>\n', 'salary10', 'A raise for Congress: when can anyone get it?',
    hflow(N('Raise approved', 'Congress passes the increase (RA 4134 in PHILCONSA v. Mathay)', 'acc'), HE('wait'),
          N('Every approver’s full term ends', '“all the Members” means both Houses together: senators who voted for it included', 'sun'), HE('then'),
          N('The raise takes effect', 'for RA 4134: not before Dec. 30, 1969, when the last approving senators finished their terms', 'ok'))
    + sp(N('No back door', 'a retirement gratuity computed on the raise is compensation: an indirect increase (Ligot v. Mathay)', 'no')),
    kind='flow', when='a law raises legislators’ pay or benefits, or a retiring member wants benefits computed on a new rate.',
    hook='Vote it now; enjoy it only after <em>all</em> who voted for it are gone.',
    cap='The delay is deliberate: it deters legislators from voting themselves raises.')

fig('09', 'after', '<h3 id="priv-arrest">Freedom from arrest</h3>\n', 'arrest', 'Is the Member privileged from arrest?',
    gates([G('Is the offense punishable by not more than six years?', 'check the penalty, not the label of the charge', 'Arrest allowed', 'Jalosjos; murder in the dela Rosa news', 'no', 'no'),
           G('Is Congress in session?', 'regular or special; attendance not required under the 1987 text', 'Arrest allowed', 'during recess', 'no', 'no')],
          ('Privileged from arrest', 'but election never frees a convicted or detained Member to attend sessions (Jalosjos; Trillanes)', 'ok'),
          facts=[fact('Dimaporo (2013 midterm)', 'A congressman charged with malversation punishable by more than six years is arrested while confined in a hospital.', 'n', 'The privilege covers only offenses punishable by not more than six years. He may be counted in the House’s membership, but cannot insist on attending sessions (Jalosjos).'),
                 fact('dela Rosa (2026 news)', 'NBI agents try to arrest a senator in the Senate on an ICC warrant for the crime against humanity of murder; the Senate places him under “protective custody”.', 'n', 'The offense is punishable by far more than six years. Nothing in Sec. 16 (officers, quorum, attendance, discipline) lets the Senate shield a member from law enforcement.'),
                 fact('A light offense, in session', 'A representative is arrested on a warrant for an offense punishable by at most four years, on a day the House is in session; he was not at the session.', 'y,y', 'Both conditions are met, and under the 1987 text attendance is not required: he is privileged from arrest.'),
                 fact('The same offense, in recess', 'The same warrant is served during the congressional recess.', 'y,n', 'The privilege runs only while Congress is in session.')])
    + sp(cmp(['1935', '1973', '1987'], [
        ('Offenses', 'all, except treason, felony and breach of the peace', 'punishable by not more than six years', 'punishable by not more than six years'),
        ('When', 'during attendance at sessions', 'during attendance; the Batasan surrenders the member within 24 hours after adjournment', 'while Congress is in session; attendance not required')])),
    kind='gates + history', when='a Member is arrested, served a warrant, detained, or asks to attend sessions while detained.',
    hook='Two S’s: <em>Six years or less</em>, and in <em>Session</em>. Both, or no privilege.',
    cap='Two conditions, both required. The 1935 and 1973 texts were different; use the 1987 rule.')

fig('09', 'after', '<h3 id="priv-speech">Speech and debate</h3>\n', 'speech', 'Speech and debate: inside or outside the shield?',
    gates([G('Was it said or done in the performance of legislative functions?', 'floor speeches and votes in session; statements in the halls in session; bills introduced; other official acts in legislative or committee duties (Jimenez)', 'Not privileged', 'ordinary civil and criminal liability: press statements, interviews, open letters (Jimenez; Trillanes v. Castillo-Marigomen)', 'no', 'no'),
           G('Is he being questioned “in any other place”: a court, an agency, a disbarment case?', 'the shield faces outward only', 'His own chamber may still discipline him', 'Osmeña; Pobre', 'no', 'sun')],
          ('Privileged: no liability in any other place', 'the purpose: to let members speak with the fullest liberty, free from the resentment of the powerful (Osmeña)', 'ok'),
          facts=[fact('Media interviews (Trillanes v. Castillo-Marigomen, 2018)', 'A senator repeats his corruption accusations against a businessman in media interviews; the businessman sues for libel.', 'n', 'Talking to the press is “political in nature, rather than legislative”: no privilege, so the libel suit proceeds.'),
                 fact('Privilege speech, disbarment (Pobre, 2009)', 'In a privilege speech, a senator says she would spit on the Justices and calls the Court a court of idiots. A citizen asks the Court to disbar her.', 'y,y', 'Parliamentary immunity covers the speech; the Senate, not the Court, disciplines her (the Court still criticized her language).'),
                 fact('Privilege speech, own House (Osmeña, 1960)', 'A congressman’s privilege speech accuses the President of bribery; the House investigates and suspends him.', 'y,n', 'The privilege protects him from being questioned elsewhere, not from discipline by his own House.'),
                 fact('Open letter (Jimenez, 1966)', 'During recess, a congressman releases an open letter to the President, published in newspapers, alleging plots by army officers.', 'n', 'An open letter published in newspapers during recess is not a legislative act; it is not privileged (though the letter was found not libelous).')])
    + sp(cmp(['Protected (Jimenez)', 'Not protected'], [
        ('Acts', 'speeches on the floor in session; statements and votes in the halls in session; bills introduced; other official acts in legislative or committee duties', 'press statements and interviews (Trillanes v. Castillo-Marigomen); acts outside official duties'),
        ('Effect', 'no liability in any other place; the House may still discipline (Pobre)', 'ordinary civil and criminal liability')])),
    kind='gates + comparison', when='a Member is sued, charged or disbarred for something he said.',
    hook='Inside the legislative work = <em>shield</em>; on TV = <em>no shield</em>; and the shield never works against <em>your own chamber</em>.',
    cap='Ask whether the statement furthered legislation, not whether a legislator said it.')

fig('09', 'after', '<h3 id="priv-office">Incompatible and forbidden offices</h3>\n', 'office', 'Another office: keep the seat, lose it, or not at all?',
    gates([G('Is it an office or employment in the government, including GOCCs and their subsidiaries?', '', 'Not covered: he keeps his seat', 'Liban: the PNRC chairmanship is not a government office', 'no', 'ok'),
           G('Was the office created, or its emoluments increased, during the term for which he was elected?', '', 'Forbidden office', 'he cannot be appointed during that term, even if he resigns', 'yes', 'no')],
          ('Incompatible office', 'he may accept, but forfeits his seat (Adaza); the 1987 text has no Cabinet exception', 'sun'),
          facts=[fact('Red Cross chairman (Liban)', 'A senator is elected chairman of the Philippine National Red Cross.', 'n', 'The PNRC chairman is elected by a private-sector-controlled board and appointed by neither the President nor a department head, so it is not a government office. RA 10530 later recognized the PNRC as an independent, autonomous, non-governmental auxiliary.'),
                 fact('A Cabinet post', 'A senator accepts appointment as Secretary of a department that has existed for decades.', 'y,n', 'An incompatible office: he may take it, but he forfeits his Senate seat. The 1973 Cabinet exception (Adaza) is gone.'),
                 fact('A new commission', 'Congress creates a new commission; during the same term, a representative who voted for it resigns his seat and is appointed its chairman.', 'y,y', 'A forbidden office: resigning does not help, since the bar runs for the whole term for which he was elected.')])
    + sp(N('Do not confuse with Art. IX-B, Sec. 7', 'no elective official is eligible for appointment to any public office during his tenure; resigning after the appointment does not cure it (Flores v. Drilon)', 'sun')),
    kind='gates', when='a Member is appointed, elected or designated to another post.',
    hook='<em>Incompatible</em>: you may choose, but you lose the seat. <em>Forbidden</em>: you may not choose at all.',
    cap='Incompatible: you may choose, but you lose the seat. Forbidden: you cannot choose at all.')


# =====================================================================
# 10 · electoral tribunals and the Commission on Appointments
# =====================================================================
_dots = lambda cls, n: ''.join(f'<i class="{cls}"></i>' for _ in range(n))
fig('10', 'before', '<h3 id="et-jurisdiction">', 'etseats', 'Who sits: the tribunals and the CA in dots',
    grid('<div>' + sub('Each Electoral Tribunal (Sec. 17): 9') + f'<div class="seats" role="img" aria-label="three Justices and six legislators">{_dots("j", 3)}<span class="eq">+</span>{_dots("", 6)}<span class="eq">= 9</span></div>'
         + sp(N('3 Justices + 6 Members', 'Justices designated by the Chief Justice; the senior Justice chairs; the six are chosen by proportional representation from the parties and party-list groups', 'acc')) + '</div>',
         '<div>' + sub('Commission on Appointments (Sec. 18): 25') + f'<div class="seats" role="img" aria-label="the Senate President, twelve senators and twelve representatives">{_dots("c", 1)}<span class="eq">+</span>{_dots("", 12)}<span class="eq">+</span>{_dots("o", 12)}</div>'
         + sp(N('Senate President + 12 + 12', 'the chair votes only to break a tie; acts on appointments within 30 session days; rules by a majority of all its Members', 'acc')) + '</div>', m=240)
    + sp(grid(N('Constituted within 30 days', 'after each chamber organizes (Sec. 19)', 'plain'), N('All must sit', 'the Justices alone cannot decide (Abbas); a rule requiring at least one Justice for a quorum is valid (Reyes v. HRET)', 'plain'),
              N('Security of tenure', 'no removal for voting against one’s party (Bondoc v. Pineda)', 'sun'), m=160)),
    kind='seats', when='the facts ask how a tribunal or the CA is composed, or whether it could act.',
    hook='Tribunal <em>3 + 6 = 9</em>; CA <em>1 + 12 + 12 = 25</em>.<small>The tribunal is “a non-political body in a sea of politicians”; the CA is proportional politics.</small>',
    cap='Filled dots: legislators; yellow: Justices; the square is the Senate President, who chairs the CA.')

fig('10', 'after', '<h3 id="et-jurisdiction">When does the tribunal take over from COMELEC?</h3>\n', 'hret', 'Who decides? Tap a stage', stepper([
    ('COC filed', 'z-a', N('COMELEC', 'petitions to deny due course to or cancel a COC; disqualification. A COC finally cancelled before the election leaves no “member” for the HRET: votes for that candidate are stray (Velasco).', 'sun')),
    ('Election and canvass', 'z-a', N('COMELEC', 'pre-proclamation issues; declaring a failure of elections (administrative, followed by a special election), unlike the tribunal’s annulment (Abayon).', 'sun')),
    ('Proclamation', 'z-a', N('Still COMELEC', 'proclamation alone is not enough (Reyes v. COMELEC). If the proclamation’s validity is pending on a timely motion for reconsideration, COMELEC keeps it and the tribunal cannot review it (Codilla).', 'sun')),
    ('Oath', 'z-a', N('Still COMELEC', 'the oath (for the House, before the Speaker in open session) is the second of three events; the tribunal still waits for assumption (Reyes v. COMELEC).', 'sun')),
    ('Assumption (June 30)', 'z-b', N('HRET or SET', 'proclamation, oath and assumption have concurred: the tribunal is the sole judge of election, returns and qualifications. Party-list nominees too (Lico); the group’s registration stays with COMELEC (An Waray).', 'acc'))], start=4),
    kind='interactive', when='a winner’s qualifications are challenged around proclamation time: read every date in the facts.',
    hook='<em>P-O-A</em>: Proclamation, Oath, Assumption. The tribunal gets the “power of attorney” only when all three have happened.',
    cap='Yellow stages belong to COMELEC, blue to the tribunal. Read the dates in the facts: the 2013 midterm (Muhlach) turned on whether the winner had assumed office.')

fig('10', 'after', '<h3 id="et-ca">Commission on Appointments</h3>\n', 'ca', 'CA seat calculator (Guingona v. Gonzales)',
    N('Each party’s seats = (its members ÷ chamber size) × 12, rounded down', 'in the Senate that is simply its senators ÷ 2', 'acc')
    + sp('<div class="calc cacalc" data-parties=\'[["LDP",15],["NPC",5],["LP",3],["LP-PDP-LABAN",1]]\'><div class="ctl"><label>Chamber size<input type="number" min="1" value="24" data-v="total"></label><button type="button" class="btn small ghost" data-a="guingona">Load Guingona (1992)</button></div><table><thead><tr><th>Party</th><th>Members</th><th>Exact share</th><th>Seats</th></tr></thead><tbody></tbody></table><div class="msg"></div></div>')
    + sp(grid(N('No rounding up', 'a fraction cannot become a seat at another party’s expense (Guingona)', 'no'), N('Minority is not enough', 'a party must be big enough for a seat: about one-twelfth of the House (some 17 members in Coseteng); endorsements from other parties do not count', 'sun'),
              N('Realignment', 'membership may change when alignments change permanently (Daza), not for temporary alliances', 'plain'), N('Go to the chamber first', 'challengers need standing and must raise it in the chamber (Drilon v. De Venecia; Pimentel v. HRET)', 'plain'), m=150)),
    kind='interactive', when='the facts give party strengths in a chamber and ask who sits in the CA.',
    hook='Senate: <em>halve the senators, then round down</em>. A lone senator is <em>0.5</em>, and 0.5 is no seat.',
    cap='Guingona (1992): LDP 15 senators → 7.5 → 7; NPC 5 → 2.5 → 2; LP 3 → 1.5 → 1; LP-PDP-LABAN 1 → 0.5 → 0. The Senate rounded the LDP up to 8 and gave the lone senator a seat; the Court voided both elections, leaving ten senators, and the CA could work with fewer than 12.', notest=True)


# =====================================================================
# 11 · powers, limits, oversight, delegation, titles
# =====================================================================
fig('11', 'after', '<h3 id="powers-substantive">Substantive limits (Gatmaytan, P&amp;S)</h3>\n', 'isurf', 'What even a plenary Congress cannot do',
    acro(('I', 'irrepealable laws: none can be put beyond repeal'), ('S', 'supermajority votes: no higher vote to amend or repeal; one Congress cannot bind the next'), ('U', 'unconstitutional laws: beyond its power, or by purpose or effect'), ('R', 'retroactive laws: generally prospective; no ex post facto law or bill of attainder (Art. III, Sec. 22)'), ('F', 'fiscal autonomy of the Court: no exemption from court fees; no changing the rules of procedure; no added appellate jurisdiction without its advice and concurrence (Art. VI, Sec. 30)'))
    + sp(grid(N('No added qualifications', 'for constitutional offices (SJS v. DDB)', 'no'), N('No interpreting the Constitution', 'by statute (Endencia)', 'no'), N('No titles of nobility', 'Sec. 31', 'no'),
              N('The procedural limits', 'riders; no amendment on third reading (the bicameral conference may still reconcile); one subject, one title', 'no'), N('The money provisions', 'Secs. 24 to 29; uniform and equitable taxation', 'no'), N('The Bill of Rights', 'and the rest of the Constitution', 'no'), m=150)),
    kind='acronym', when='a law says it “shall not be repealed”, may be amended “only by three-fourths”, reaches back in time, or touches the Court’s fees or rules.',
    hook='<em>I SURF</em>: Irrepealable, Supermajority, Unconstitutional, Retroactive, Fiscal autonomy.<small>Gatmaytan’s book lists exactly these five.</small>',
    cap='The grant of legislative power is plenary: Congress may legislate on anything not forbidden or lodged elsewhere (Torralba). These are the “forbidden” list.')

fig('11', 'after', '<h3 id="powers-veto">Procedural limits: the legislative veto (ABAKADA)</h3>\n', 'oversight', 'After the law passes: how far may Congress follow it?',
    hflow(N('Scrutiny', 'reports, budget hearings, question hour, confirmations', 'ok'), HE('more intense'), N('Investigation', 'inquiries in aid of legislation', 'ok'), HE('continuing'), N('Supervision', 'approving or disapproving rules before they take effect', 'no'))
    + sp(gates([G('Does the law let Congress, a committee or members approve or disapprove rules, budgets or projects after enactment?', 'a say in implementation without passing a new law', 'Legislative veto: void', 'separation of powers, bicameralism, presentment (ABAKADA; the JCOC in Macalintal 2003)', 'yes', 'no'),
                G('Does it let them deputize, direct or otherwise take part in enforcing the law?', 'execution belongs to the President (Art. VII, Sec. 17)', 'Execution by Congress: void', 'Belgica (post-enactment identification of projects) is the same idea', 'yes', 'no')],
               ('Valid oversight', 'scrutiny and investigation in aid of legislation; strike only the bad clause if separable (ABAKADA kept RA 9335 except Sec. 12)', 'ok'),
               facts=[fact('ABAKADA (2008)', 'RA 9335 creates a Joint Congressional Oversight Committee with power to approve the law’s implementing rules.', 'y', 'Approval of the IRR lets Congress take part in implementation: a legislative veto. Sec. 12 fell; the reward system and the rest of the law stood.'),
                      fact('Illicit trade JCOC (2023 Q3)', 'Tax Code Sec. 290-A’s committee may review BIR and BOC performance, require reports, hold hearings, recommend legislation, and deputize the BIR, BOC, PNP and NBI “in undertaking its duties”.', 'n,y', 'Review, reports, hearings and recommendations are valid oversight. Deputizing law enforcers lets Congress direct execution, so that clause is void; the rest may stand.'),
                      fact('Quarterly reports', 'A law requires an agency to send quarterly reports to a congressional committee, which may hold hearings and recommend amendments.', 'n,n', 'Pure scrutiny and investigation in aid of legislation: valid.')])),
    kind='spectrum + gates', when='a law creates an oversight committee, or gives legislators any role after the law is passed.',
    hook='<em>S-I-S</em>: Scrutinize ✓, Investigate ✓, Supervise ✕. After enactment, Congress may only <em>amend</em>.',
    cap='The first two survive enactment. Once Congress keeps a say over how the law is carried out, it is a legislative veto and void (ABAKADA); after enactment, Congress may only amend the law.')

fig('11', 'after', '<h3 id="powers-delegation">Delegation of legislative power</h3>\n', 'delegation', 'Is the delegation, and the rule made under it, valid?',
    hub('What has been delegated cannot be delegated, except…', [
        ('People', 'initiative and referendum (Sec. 32)'), ('Local governments', 'local legislation'), ('Administrative bodies', 'subordinate rule-making'),
        ('Tariff powers', 'to the President, within limits Congress sets (Sec. 28(2); Garcia v. Executive Secretary)'), ('Emergency powers', 'to the President (Sec. 23(2))')])
    + sp(gates([G('Completeness: does the law itself set the policy?', 'leaving the delegate only how to carry it out', 'Undue delegation: void', 'People v. Vera', 'no', 'no'),
                G('Sufficient standard: are there determinate or determinable limits?', '“public interest”, “reasonable”, “just and equitable” pass when read with the law’s policy', 'Undue delegation: void', '', 'no', 'no'),
                G('Did the delegate keep the power?', 'no subdelegation, least of all to the regulated parties', 'Void subdelegation', 'KMU: operators setting their own fares', 'no', 'no'),
                G('Is the rule a valid IRR?', 'authorized; within the scope of the law; issued by the prescribed procedure; reasonable. It cannot amend, expand or contradict the law (Lokin)', 'The rule is void', '', 'no', 'no'),
                G('Published, and filed with the UP Law Center (ONAR)?', '15 days after publication (Tañada; EO 200); agency rules 15 days after filing', 'Not yet effective', '', 'no', 'sun')],
               ('Valid delegation and rule', '', 'ok'),
               facts=[fact('The Probation Act (People v. Vera, 1937)', 'The Probation Act applies only in provinces whose boards decide to fund a probation officer.', 'n', 'The law left to provincial boards whether it would apply at all: the policy itself was delegated. Undue delegation (and unequal application).'),
                      fact('The fare band (KMU, 1994)', 'DOTC and LTFRB orders let bus operators raise fares within a band without LTFRB approval.', 'y,y,n', 'The LTFRB cannot hand its rate-fixing power to the operators themselves.'),
                      fact('Bulacan Freeport IRR (2024 Q3)', 'The law tells DTI to issue the IRR within 90 days, in consultation with DOF, NEDA, the province and a representative of the airport project, effective 15 days after publication in a newspaper of general circulation.', 'y,y,y,y,y', 'Valid. Consultation is not subdelegation, as long as DTI alone promulgates; the 90 days is directory; newspaper publication satisfies Tañada, but the IRR must also be filed with ONAR to bind the public.')])),
    kind='mind map + gates', when='a law tells an agency, the President or an LGU to fill in details, set rates, or issue rules.',
    hook=acro(('P', 'people'), ('L', 'local governments'), ('A', 'administrative bodies'), ('T', 'tariff powers'), ('E', 'emergency powers')) + '<em>PLATE</em> may receive power; the law must be <em>complete</em> and set a <em>standard</em>; the rule must <em>ASPiRe</em> (Authorized, within Scope, by Procedure, Reasonable), then be <em>published</em> and <em>filed</em>.',
    cap='The mind map lists who may receive power (PLATE); the gates test any delegation to an administrative body, and the rule made under it.')

fig('11', 'after', '<h4>Publication and effectivity</h4>\n', 'publication', 'No publication, no law: the 15-day clock',
    sub('Laws (Civil Code, Art. 2, as amended by EO 200)') + hflow(N('Published', 'in the Official Gazette or a newspaper of general circulation', 'acc'), HE('+ 15 days'), N('In force', 'unless the law fixes another date', 'ok'))
    + sub('Agency rules (Administrative Code, Book VII)') + hflow(N('Published, and filed with the UP Law Center (ONAR)', '', 'acc'), HE('+ 15 days after filing'), N('In force', 'unless a different date is fixed', 'ok'))
    + sp(grid(N('“Unless otherwise provided”', 'changes the date, never the publication: all statutes, including those of local application and private laws, must be published (Tañada, 1986)', 'sun'),
              N('Need not be published', 'interpretative rules; purely internal rules; letters of instruction to subordinates', 'plain'), m=200)),
    kind='timeline', when='a law or rule says it is “effective immediately”, was never published, or was published only in one newspaper.',
    hook='Publish → wait <em>15</em> → in force. <em>No publication, no law.</em>',
    cap='Tañada began as a citizen’s suit to enforce a public right: the publication of laws.')

fig('11', 'after', '<h3 id="powers-titles">Title and one subject (Art. VI, Sec. 26(1))</h3>\n', 'bill', 'How a bill becomes law', vflow(
    N('First reading', 'title read; referral to committee'), VE(), N('Second reading', 'debate and amendments'), VE('printed copies 3 days before, unless certified urgent'),
    N('Third reading', 'no amendment; yeas and nays entered in the Journal (Sec. 26(2))'), VE('other House: same steps'),
    N('Bicameral conference', 'reconciles versions; may add germane provisions (Tolentino)', 'sun'), VE('enrolled bill signed by presiding officers'),
    N('To the President', '', 'acc')) + hflow(N('Signs', 'law', 'ok'), N('Vetoes within 30 days', 'returns with objections; override by two-thirds of all Members of each House', 'no'), N('No action in 30 days', 'becomes law', 'ok'))
    + vflow(VE('then'), N('Effectivity', f'15 days after publication (Tañada; EO 200), unless the law sets another date: see {X("fig-publication", "the 15-day clock")}', 'acc')),
    kind='flow', when='the facts describe how a law was passed: readings, an urgency certification, a bicameral insertion, a veto.',
    hook='<em>3 · 3 · 30 · 15</em>: three readings on separate days, printed three days before, thirty days to veto, fifteen days after publication.<small>A certification of urgency waives both “threes” (' + C('tolentinofinance', 'Tolentino') + ').</small>',
    cap='The title rule applies to the bill as passed; the procedural rules are why a rider or a third-reading amendment is void.')

fig('11', 'before', '<aside class="note trap"><strong>2015 midterm (anti-dynasty rule in the SK Reform Act)', 'title', 'One bill, one subject, one umbrella',
    '<div class="umb"><div class="canopy">The title<small>states the general subject</small></div><div class="under">' + N('Germane provision', 'a means of carrying out the subject', 'ok') + N('Germane provision', 'the title need not list it (Giron)', 'ok') + N('Germane provision', 'construed liberally', 'ok') + '</div>'
    + '<div class="out">' + N('A provision foreign to the title', 'a rider: void, and the whole law if the parts cannot be separated (Lidasan)', 'no') + '</div></div>'
    + sp(gates([G('Is every provision germane to the subject expressed in the title?', 'not foreign to it, and a means of carrying it out', 'Rider: void', 'the whole law if inseparable', 'no', 'no'),
                G('Does the title inform without misleading?', 'not misleading, not too restrictive, not hiding essential matter; it should make readers look into the body', 'Void title', 'Lidasan', 'no', 'no')],
               ('Valid', 'no hodgepodge, no surprise', 'ok'),
               facts=[fact('Dianaton (Lidasan, 1967)', '“An Act creating the Municipality of Dianaton in Lanao del Sur” also moves twelve barrios of Cotabato into the new town.', 'y?,n', 'The title hid that the law took territory from Cotabato. Since the town was premised on all its barrios, the parts could not be separated: the whole law fell.'),
                      fact('Fair Election Act (Giron, 2013)', 'RA 9006, which lifted the political ad ban, also repealed the rule deeming elective officials resigned once they file a COC.', 'y,y', 'The repeal is germane to the law’s subject of fair and honest elections; titles are read liberally, and Congress framed this one to cover broader reforms.'),
                      fact('SK anti-dynasty rule (2015 midterm)', 'The SK Reform Act, whose title concerns the SK’s structure and eligibility, bars relatives of officials from SK office.', 'y,y', 'Germane to eligibility for SK office: not a rider. And since SK office is statutory, adding the qualification is valid.')])),
    kind='picture + gates', when='a law contains a provision that seems unrelated to its title, or its title hides what it does.',
    hook='One bill, one subject, <em>one umbrella</em>: everything must fit under the title.<small>The two purposes (Lidasan): no <em>hodgepodge</em> or log-rolling, and no <em>surprise</em> or fraud on legislators and the public.</small>',
    cap='A title also limits how far an enabling law can be read: power to “regulate” is not power to “prohibit” (Cruz v. Paras).')


# =====================================================================
# 12 · appropriations and taxation
# =====================================================================
fig('12', 'before', '<h3 id="money-pork">', 'money5', 'The five money rules',
    acro(('1', 'no increase: Congress may cut or delete, never raise, the President’s recommended appropriations for the operation of government (Sec. 25(1))'),
         ('2', 'no riders: every GAA provision must relate specifically to a particular appropriation, and is limited to it (Sec. 25(2))'),
         ('3', 'no transfers: except augmentation from savings, by law, by the five named officers (Sec. 25(5))'),
         ('4', 'no gap: no GAA by year-end, and last year’s is deemed re-enacted (Sec. 25(7))'),
         ('5', 'no money without law: nothing is paid out of the Treasury except under an appropriation made by law (Sec. 29(1))'))
    + sp(grid(N('What is an appropriation?', 'a bill whose primary aim is to set apart public money; one that creates and funds an office is not. It need not be in the GAA: a law setting a determinate or determinable amount for a stated purpose is enough, so continuing appropriations (debt service; the Malampaya Fund) need no yearly re-enactment (Guingona v. Carague; Belgica)', 'acc'),
              N('The other limits', 'special appropriations must state their purpose and be backed by funds actually available (25(4)); discretionary funds only for public purposes, with vouchers (25(6)); no public money for any church or religious dignitary, though an incidental benefit is allowed (29(2)); special-purpose taxes form a special fund (29(3))', 'plain'), m=220)),
    kind='checklist', when='any story about the budget: a cut, an increase, a transfer, a fund sweep, a missing GAA, or a payment with no appropriation.',
    hook='Five No’s: <em>no raise</em>, <em>no riders</em>, <em>no transfers</em>, <em>no gap</em>, <em>no money without law</em>.',
    cap='Most budget questions are one of these five rules applied to a fresh set of facts.')

fig('12', 'after', '<h3 id="money-pork">The pork barrel line: how doctrine changed</h3>\n', 'budget', 'The budget cycle, and where each case sits', hflow(
    N('Preparation', 'the President’s budget', 'acc'), HE(), N('Legislation', 'GAA; item veto (Philconsa)', 'acc'), HE(), N('Execution', 'releases, savings, transfers (Araullo; Nazareth; Pichay)', 'sun'), HE(), N('Accountability', 'COA audit, disallowance and refunds (Madera)', 'acc'))
    + sp(N('Belgica (2013): the line', 'after the GAA passes, legislators have no role in execution: post-enactment identification of projects is void; oversight only. The PDAF was “a budget within a budget”.', 'no'))
    + sp(cmp(['Valid lump sum (Belgica 2019)', 'Pork (Belgica 2013)'], [
        ('Shape', 'one singular purpose, however general, so the President can still veto it as a unit', 'several purposes, with amounts and projects chosen after enactment'),
        ('Examples', 'the 2014 Unprogrammed Fund, Contingent Fund, E-Government Fund and LGSF', 'the PDAF: legislators identified projects after the GAA')]))
    + sp(tl([('1991', f'{C("guingonacarague", "Guingona v. Carague")}: automatic debt-service appropriations are valid', ''), ('1994', f'{C("philconsaenriquez", "Philconsa v. Enriquez")}: CDF upheld (legislators only recommend); item-veto rules', ''), ('2012', f'{C("lamp", "LAMP")}: PDAF challenge fails for lack of proof', ''), ('2013', f'{C("belgica2013", "Belgica")}: PDAF void; Philconsa and LAMP abandoned on this point', 'key'), ('2014', f'{C("araullo", "Araullo")}: DAP practices void', ''), ('2019', f'{C("belgica2019", "Belgica")}: lump sums valid if one singular purpose', ''), ('2025', f'{C("pimentelhouse2025", "Pimentel v. House")}: the PhilHealth fund sweep voided', '')])),
    kind='flow + timeline', when='legislators have any say after the GAA passes, or a lump sum is challenged as pork.',
    hook='<em>P-L-E-A</em>: Prepare, Legislate, Execute, Account. Legislators belong only in <em>L</em> (Belgica).',
    cap='Locate the challenged act in the cycle first: Congress acts only in the second box, the Executive in the third, COA in the fourth.')

fig('12', 'before', '<h3 id="money-transfer">', 'veto', 'Can the President veto just that part?',
    gates([G('Is it an appropriation, revenue or tariff bill?', 'the item veto exists only for these (Sec. 27(2))', 'No item veto', 'the President approves or vetoes the whole bill', 'no', 'no'),
           G('Is the vetoed part an item, or an inappropriate provision?', 'item: an indivisible sum for a stated purpose, vetoed whole. Inappropriate provision (rider): relates to no particular appropriation, or amends substantive law', 'Void veto', 'an appropriate provision or condition can be struck only by vetoing the item it qualifies', 'no', 'no')],
          ('Valid veto', 'Congress may override by two-thirds of all the Members of each House', 'ok'),
          facts=[fact('Debt service condition (Philconsa)', 'The President vetoes the GAA provision limiting the debt service fund to principal and interest on foreign and domestic debt, but leaves the fund itself.', 'y,n', 'That provision was an appropriate condition, inseparable from its item: it could be struck only by vetoing the item. Void veto (likewise the DPWH 70/30 rule and the AFP medicines provision).'),
                 fact('SUC revolving funds (Philconsa)', 'The President vetoes a GAA provision letting state universities keep their income in revolving funds, which amended existing law.', 'y,y', 'A provision that amends substantive law is an inappropriate provision and may be vetoed as if it were an item.'),
                 fact('Reorganization by budget', 'A GAA provision lets the DBM change agencies’ organizational structures; the President vetoes it.', 'y,y', 'Substantive legislation in a budget law relates to no particular appropriation: a rider (Sec. 25(2)), vetoable as an item.'),
                 fact('One section of a health law', 'The President signs a public health law but “vetoes” one section of it.', 'n', 'Outside appropriation, revenue and tariff bills the veto is all-or-nothing.')]),
    kind='gates', when='the President vetoes a provision, a condition, or a single section rather than a whole bill.',
    hook='Item veto: <em>money bills only</em>; strike a <em>whole item</em> or a <em>rider</em>; a <em>condition</em> falls only with its item.',
    cap='Philconsa also upheld a veto of a provision letting the AFP Chief of Staff augment pension funds from savings: only the five named officers may augment (Sec. 25(5)).')

fig('12', 'after', '<h3 id="money-transfer">Transfers, savings and augmentation</h3>\n', 'augment', 'Is the transfer valid? (Sec. 25(5))',
    gates([G('Does a law authorize this officer to augment?', 'only the President, Senate President, Speaker, Chief Justice and heads of Constitutional Commissions', 'Void', 'blanket authority (Demetria); wrong officer', 'no', 'no'),
           G('Are there actual savings?', 'the purpose was completed or abandoned, or efficiencies achieved, after the item was fully provided for', 'Void', 'unobligated allotments withdrawn mid-year are not savings (Araullo)', 'no', 'no'),
           G('Does it augment an existing item in the GAA?', 'not a project with no appropriation', 'Void', 'no item to augment (Nazareth; Araullo)', 'no', 'no'),
           G('Within the officer’s own branch or office?', 'no cross-border transfers', 'Void', 'cross-border (Araullo); a disguised transfer (Macalintal 2023)', 'no', 'no')],
          ('Valid augmentation', 'an item for a major final output covers its integral components (Dela Cruz)', 'ok'),
          facts=[fact('DAP “savings” (Araullo, 2014)', 'Mid-year, the DBM withdraws unobligated allotments, declares them savings, and uses them to fund projects across branches.', 'y,n', 'Funds withdrawn before year-end are not savings under the GAA. Araullo also struck the cross-border transfers and the funding of projects with no appropriation.'),
                 fact('Judiciary year-end savings', 'Under a GAA provision, the Chief Justice uses actual savings from completed judiciary projects to augment a judiciary item that ran short.', 'y,y,y,y', 'Every requisite is present: a law, real savings, an existing item, the officer’s own branch.'),
                 fact('Cross-border', 'The President uses actual executive savings to augment an item in the budget of the House of Representatives.', 'y,y,y,n', 'Savings may augment items only within the officer’s own branch (Araullo).'),
                 fact('A blanket decree (Demetria, 1987)', 'A decree lets the President transfer any appropriated fund of the Executive to any program or project in the GAA.', 'n', 'An indiscriminate transfer power is void: transfers only from savings, to augment an existing item, within the branch.')]),
    kind='gates', when='funds are “realigned”, “pooled”, declared “savings”, or moved to another office or project.',
    hook='<em>L</em>awful <em>S</em>avings <em>I</em>nto <em>O</em>wn items: a law authorizes, real savings, an existing item, your own branch.',
    cap='Four gates, each with the case that failed it. Macalintal (2023): a law postponing elections to free election funds for other uses was a disguised transfer.')

fig('12', 'before', '<aside class="note news"><strong>In a news question:</strong> (1) <em>Confidential', 'madera', 'COA disallowed it: who must give the money back? (Madera)',
    gates([G('Is the disallowance upheld?', '', 'No one returns anything', '', 'no', 'ok')], ('Then split the people into two groups', 'officers and payees are treated differently', 'acc'))
    + sp(cmp(['Approving and certifying officers', 'Payees (recipients)'], [
        ('Rule', 'good faith, regular performance of duties and diligence: not liable. Bad faith, malice or gross negligence: solidarily liable for the net disallowed amount', 'return what they received (solutio indebiti), even in good faith'),
        ('Way out', 'badges of good faith: a certificate of availability of funds; a legal opinion; no precedent disallowing a similar case; long practice without a disallowance; a reasonable reading of the law', 'what was genuinely for services rendered; or excused for undue prejudice, social justice or other bona fide reasons, case by case')]))
    + sp(N('Net disallowed amount', 'the total disallowed, less what the payees are excused from returning', 'plain')),
    kind='decision + matrix', when='COA disallows allowances or benefits and the question asks who must refund.',
    hook='Officers: <em>good faith saves</em>. Payees: <em>good faith does not</em>, because they have the money.',
    cap='In Madera itself, the allowances were void under the Salary Standardization Law, but the officials were excused for good faith.', notest=False)

fig('12', 'after', '<h3 id="money-tax">Taxation</h3>\n', 'tripal', 'Money bills start in the House (Sec. 24)',
    acro(('T', 'tariff bills'), ('R', 'revenue bills'), ('I', 'bills increasing the public debt'), ('P', 'private bills'), ('A', 'appropriation bills'), ('L', 'bills of local application'))
    + sp(gates([G('Is it one of the TRIPAL bills?', '', 'Sec. 24 does not apply', 'either House may start it', 'no', 'acc'),
                G('Did the Senate wait for the House bill before acting as a body?', 'it may file its own version in anticipation, but must withhold action on it until the House bill arrives', 'Void', 'the bill did not originate in the House', 'no', 'no')],
               ('Valid origin', 'even if the law that emerges is the Senate’s substitute: it is the bill, not the law, that must originate in the House', 'ok'),
               facts=[fact('E-VAT (Tolentino, 1994)', 'The House passes an expanded VAT bill; the Senate, which had filed its own version in anticipation, approves a substitute after receiving the House bill; the bicameral conference adds germane provisions found in neither version.', 'y,y', 'The Senate may propose amendments, even a substitute; the conference committee may insert germane provisions; and the President’s urgency certification dispensed with three readings on separate days and with printing three days before.'),
                      fact('The Senate goes first', 'The Senate passes its own tax bill on third reading before any House tax bill exists, and the House simply concurs.', 'y,n', 'A revenue bill must originate exclusively in the House; the Senate may only propose or concur with amendments.')])),
    kind='acronym + gates', when='the Senate filed, passed or rewrote a tax, tariff, budget, debt, local or private bill.',
    hook='<em>TRIPAL</em> bills start in the House. The <em>bill</em>, not the law, must start there.<small>Why the House: district representatives are closer to local needs; senators, elected at large, bring the national view.</small>',
    cap='A presidential certification of urgency dispenses with both the three readings on separate days and the printing three days before (Tolentino).')

fig('12', 'before', '<aside class="note news"><strong>2015 midterm (income tax reform', 'tax', 'Is the property tax-exempt? (Sec. 28(3), Lung Center)',
    gates([G('Is the owner a charitable institution?', 'exists for a purpose the law recognizes as charitable, not for gain; paying patients and subsidies do not defeat it', 'Taxable', '', 'no', 'no'),
           G('Is this portion actually, directly and exclusively used for charitable purposes?', 'the exemption follows the use of the property, not the owner or the income', 'Taxable portion', 'leased clinics, a canteen, stores, a garden center', 'no', 'no')],
          ('Exempt portion', 'only the part so used; exemptions are construed strictly against the claimant, who bears the burden', 'ok'),
          facts=[fact('Leased spaces (Lung Center)', 'The Lung Center leases parts of its land and building to private doctors for clinics, to a canteen and stores, and to a garden center.', 'y,n', 'It is a charitable institution, but the leased portions are not used actually, directly and exclusively for charity: taxable.'),
                 fact('Wards and paying patients (Lung Center)', 'The same hospital’s wards serve both paying and non-paying patients.', 'y,y', 'Charging paying patients does not defeat charitable use; the portions used for patients are exempt.')])
    + sp(grid(N('Who may grant exemptions?', 'the Constitution itself, or Congress by a majority of all its Members, expressly (Sec. 28(4)); not a proclamation (John Hay); LGUs only from local taxes', 'sun'),
              N('Uniform and equitable (Sec. 28(1))', 'same class, same rate. A classification is valid if it rests on substantial distinctions, is germane to the law’s purpose, is not limited to existing conditions, and applies equally to the whole class (Tan v. Del Rosario)', 'plain'),
              N('Tariff powers', 'may be delegated to the President within limits Congress sets (Sec. 28(2); Garcia)', 'plain'), m=180)),
    kind='gates', when='someone claims a tax exemption: by proclamation, by charity, or for a building that is partly leased out.',
    hook='The exemption follows the <em>USE</em> (actually, directly, exclusively), <em>portion by portion</em>: not the owner, not the income.<small>And only the Constitution or Congress (majority of all) grants exemptions: never a proclamation (John Hay).</small>',
    cap='Apply it portion by portion. Only the Constitution or Congress grants exemptions; a proclamation cannot (John Hay).')


# =====================================================================
# 13 · news watch
# =====================================================================
def _story(title, rules, practice):
    return ('<div class="vn acc"><b>' + title + '</b><span class="s">' + ' · '.join(rules) + '</span>'
            + '<span class="s" style="margin-top:6px">Practice: ' + '; '.join(f'<a class="eref" data-e="{e}">{t}</a>' for e, t in practice) + '</span></div>')
fig('90', 'before', '<h3 id="news-dynasty">', 'news', 'Five stories, the rules they wear',
    grid(_story('Political dynasties (Kapatiran)', [X('fig-kapatiran', 'duty, definition, default'), X('fig-review', 'expanded review of inaction'), X('fig-quals', 'adding qualifications (Sec. 26 is the source)')], [('n26-1', 'a senator’s critique'), ('n26-7', 'a dynasty law')]),
         _story('VP impeachment: “all the Members”', [X('fig-www', 'Words: “present” versus “all”'), X('fig-votes', 'the denominators'), X('fig-quorum', 'Avelino'), X('fig-jr', 'ripeness and standing')], [('n26-2', 'the two-thirds count')]),
         _story('Sen. dela Rosa and the ICC warrant', [X('fig-arrest', 'six years, in session'), X('fig-votes', 'electing the Senate President'), X('fig-discipline', 'what Sec. 16 lets the Senate do')], [('n26-3', 'immunity and the Senate’s actions')]),
         _story('BSKE moved to 2028 (RA 12326)', [X('fig-scrutiny', 'Macalintal 2023: postponement needs important, substantial or compelling reasons and must be narrowly tailored'), X('fig-title', 'one subject (Giron)'), X('fig-augment', 'a disguised transfer?')], [('n26-4', 'resolve the petition')]),
         _story('The budget: unprogrammed funds, fund sweeps', [X('fig-money5', 'the five money rules'), X('fig-augment', 'augmentation'), X('fig-budget', 'Belgica 2019 lump sums'), X('fig-veto', 'riders')], [('n26-5', 'unprogrammed appropriations'), ('n26-6', 'a 2027 fund sweep')]), m=230),
    kind='map', when='the problem reads like a headline: find the story here, then walk the diagrams it points to.',
    hook='Every story is an <em>old rule in new clothes</em>: name the rule, then the case, then apply it to the new facts.',
    cap='Impeachment itself (Art. XI) is not in the midterm syllabus: use that story for interpretation, quorum and judicial review only.', notest=True)


# =====================================================================
# 14 · legislative process and investigations (finals)
# =====================================================================
fig('14', 'after', '<h3 id="legproc-sc30">Congress and the Supreme Court’s appellate jurisdiction (Art. VI, Sec. 30)</h3>\n', 'sc30', 'May Congress send this case to the Supreme Court, or take a remedy away?',
    gates([G('Does the law prescribe remedies or procedure, or bar courts from issuing writs?', 'e.g., “no court shall enjoin an Ombudsman investigation”', 'Void, or ineffective until the Court adopts it', 'rule-making belongs to the Court alone (Art. VIII, Sec. 5(5)); ' + C('carpiomorales', 'Carpio-Morales') + ', RA 6770 Sec. 14', 'yes', 'no'),
           G('Does it add a new appeal to the Supreme Court?', 'a new class of cases, or a direct appeal from an agency', 'No Sec. 30 problem', 'Congress may define and apportion lower courts’ jurisdiction (Art. VIII, Sec. 2)', 'no', 'ok'),
           G('Did the Court give its advice and concurrence?', '', 'Void (Art. VI, Sec. 30)', C('fabian', 'Fabian') + ': appeals go to the CA under Rule 43', 'no', 'no')],
          ('Valid', 'the Court concurred in the new appeal', 'ok'),
          facts=[fact('Fabian v. Desierto (1998)', 'RA 6770, Sec. 27 allows appeals by certiorari to the Supreme Court from the Ombudsman’s decisions in administrative disciplinary cases.', 'n,y,n', 'A new appeal to the SC, passed without its advice and concurrence: void. The appeal goes to the Court of Appeals.'),
                 fact('Carpio-Morales v. CA (2015)', 'RA 6770, Sec. 14 bars any court except the SC from hearing an appeal or application for remedy against an Ombudsman decision, and bars injunctions against Ombudsman investigations.', 'y', 'Congress cannot dictate remedies or bar a court from issuing writs incidental to its jurisdiction: par. 2 void; par. 1 ineffective until the Court adopts it.'),
                 fact('New Family Courts', 'A law creates new Family Courts with exclusive jurisdiction over child-custody cases, appealable to the Court of Appeals.', 'n,n', 'Apportioning lower courts’ jurisdiction is Congress’s to do; nothing is added to the SC.')]),
    kind='gates', when='a statute routes appeals from an agency to the Supreme Court, or tells courts which remedies they may (not) grant.',
    hook='<em>No A&amp;C, no appeal</em>: no new appeal to the SC without its Advice and Concurrence; and the rules of procedure are the Court’s alone.',
    oral='The issue is whether Congress may send these appeals straight to the Supreme Court. Article VI, Section 30 says no law may increase the Court’s appellate jurisdiction without its advice and concurrence. In Fabian v. Desierto, Section 27 of the Ombudsman Act did exactly that and was struck down, so the appeals went to the Court of Appeals. Here, there was no concurrence, so the provision is void.',
    cap='Two different limits: Sec. 30 protects the Court’s docket; Art. VIII, Sec. 5(5) protects its rule-making. Carpio-Morales used both.')

fig('14', 'after', '<h3 id="legproc-bills">Passing a bill: readings, urgency, the bicameral committee and the enrolled bill</h3>\n', 'passage', 'Did the measure validly become a law?',
    hflow(N('1st reading', 'title; referral to committee', 'acc'), HE(''), N('2nd reading', 'debate and amendments', 'acc'), HE('printed copies 3 days before'), N('3rd reading', 'no amendment; vote at once; yeas and nays in the Journal', 'acc'), HE('other House, then'), N('Bicameral committee', 'reconciles; may add germane provisions (Tolentino)', 'acc'), HE(''), N('Enrolled bill', 'signed by both presiding officers: conclusive', 'acc'), HE(''), N('President', 'sign · veto within 30 days · or it lapses into law', 'acc'))
    + sp(gates([G('Is it a bill?', 'a joint resolution, or a plan Congress merely failed to disapprove, is not', 'Not a law', C('angnars', 'Ang Nars') + ' (joint resolution); ' + C('millermardo', 'Miller v. Mardo') + ' (silence)', 'no', 'no'),
                G('Three readings; no amendment on the last; vote immediately, with the yeas and nays in the Journal?', 'a certification of urgency cannot waive these', 'Not validly passed', '', 'no', 'no'),
                G('Readings on separate days and printed copies 3 days before, or a presidential certification of urgency?', 'certified: necessity of immediate enactment to meet a public calamity or emergency', 'Not validly passed', 'the Court generally does not review the certification’s factual basis (Kida)', 'no', 'no'),
                G('Signed by the President, not vetoed within 30 days, or the veto overridden by two-thirds of all the Members of each House?', '', 'Not a law (vetoed)', '', 'no', 'no')],
               ('A law', 'effective 15 days after publication, unless it fixes another date (Tañada; EO 200)', 'ok'),
               facts=[fact('Ang Nars (2019)', 'Joint Resolution No. 4 (2008), passed by both Houses and approved by the President, set the nurses’ entry salary below the grade fixed by RA 9173, Sec. 32.', 'n', 'A joint resolution is not a bill, so it cannot amend RA 9173 even if it went through the steps for passing a bill.'),
                      fact('Kida v. Senate (2011)', 'RA 10153 (ARMM synchronization) passed both Houses after three readings, on the President’s certification of urgency, without readings on separate days.', 'y,y,y,y', 'The certification dispenses with the separate-day readings and the 3-day printing; the three readings were held. Valid law.'),
                      fact('A same-day bill', 'A bill passes second and third reading on the same day, without printed copies three days earlier and without any certification from the President.', 'y,y,n', 'Without a certification, separate days and the 3-day printing are required. Not validly passed.'),
                      fact('Reorganization Plan 20-A (Miller v. Mardo)', 'RA 997 says reorganization plans take effect unless Congress disapproves them; Congress did nothing about Plan 20-A.', 'n', 'Congressional silence is not lawmaking: the plan did not become a statute.')])),
    kind='flow + gates', when='a law was passed in a day, by joint resolution, or “unless Congress disapproves”, or someone attacks the bicameral committee’s changes.',
    hook='<em>Bill · 3 readings · separate days · 3 days printed · signed</em>. A certification waives only the <em>separate days</em> and the <em>3 days</em>, never the readings.',
    oral='The issue is whether the law was validly passed. Under Article VI, Section 26(2), a bill needs three readings on separate days and printed copies three days before passage, unless the President certifies it as urgent. In Kida v. Senate, the Court held that the certification waives only the separate days and the three-day printing, not the three readings. Here, [it was certified and had three readings], so the law is valid.',
    cap='The enrolled bill, signed by the Senate President and the Speaker, is conclusive on the Court as to internal procedure (Tolentino); the constitutional steps in Sec. 26(2) remain the floor.')

fig('14', 'after', '<h3 id="legproc-veto">The veto: whole bills, items, and inappropriate provisions</h3>\n', 'itemveto', 'Is this partial veto valid?',
    gates([G('Is it an appropriation, revenue or tariff bill?', 'any other bill: the President signs or vetoes the whole', 'Whole-bill veto only', 'a partial veto of an ordinary bill is not allowed', 'no', 'sun'),
           G('Is the vetoed part an item, or an inappropriate provision?', 'item: an indivisible sum of money for a stated purpose; inappropriate provision: general legislation unrelated to a particular appropriation (Sec. 25(2))', 'Invalid veto', 'no vetoing part of an item, or a provision that is not an item (' + C('bengzondrilon', 'Bengzon v. Drilon') + ')', 'no', 'no'),
           G('Does the veto dictate how a fiscally autonomous body uses its funds, or try to repeal an existing law?', 'the Judiciary, ConComs, Ombudsman, CHR', 'Invalid veto', C('bengzondrilon', 'Bengzon v. Drilon') + ': violates fiscal autonomy and automatic release', 'yes', 'no')],
          ('Valid item veto', 'Congress may override by two-thirds of all the Members of each House; the rest of the bill stands', 'ok'),
          facts=[fact('Gonzales v. Macaraig (1990)', 'The President vetoes Sec. 55 (on the use of savings) and Sec. 16 of the 1989 General Appropriations Bill.', 'y,y,n', 'Secs. 55 and 16 were inappropriate provisions, so they could be vetoed as items. Valid.'),
                 fact('Bengzon v. Drilon (1992)', 'In the 1992 GAA, the President vetoes the special provisions authorizing the use of the Judiciary’s savings to pay retired justices’ adjusted pensions under RA 1797.', 'y,n', 'The special provisions were not items; the veto also dictated how the Judiciary may use its funds and in effect repealed RA 1797. Void.'),
                 fact('An anti-hazing amendment', 'The President approves an amendment to the Anti-Hazing Law but vetoes one section.', 'n', 'Not an appropriation, revenue or tariff bill: the President must approve or veto the whole bill.'),
                 fact('Half an item', 'The GAA appropriates ₱10 billion for farm-to-market roads; the President vetoes ₱5 billion of it.', 'y,n', 'An item is indivisible: the President may veto the whole ₱10 billion or none of it.')]),
    kind='gates', when='the President vetoes a “provision”, a condition, a rider, or part of an amount in the budget or a tax bill.',
    hook='<em>ART</em> bills only (Appropriation, Revenue, Tariff). Veto a <em>whole item</em> or an <em>inappropriate provision</em>, never a slice, and never to <em>dictate</em> or <em>repeal</em>.',
    oral='The issue is whether the President may veto that part of the budget. Article VI, Section 27(2) allows item vetoes only in appropriation, revenue or tariff bills, and an item is an indivisible sum for a stated purpose. In Gonzales v. Macaraig, the Court allowed vetoing inappropriate provisions as items; but in Bengzon v. Drilon, it voided a veto of special provisions that dictated how the Judiciary may use its funds. Here, [the vetoed part is or is not an item], so the veto is [valid or void].',
    cap='The money-provisions map has the related rule on riders (Sec. 25(2)); see the midterm figure on the GAA.')

fig('14', 'after', '<h3 id="legproc-qh">The question hour (Sec. 22) is not an inquiry (Sec. 21)</h3>\n', 'qh21', 'Question hour or inquiry: can Congress compel this official?',
    cmp(['Question hour (Sec. 22)', 'Inquiry in aid of legislation (Sec. 21)'], [
        ('Purpose', 'oversight: how laws are being carried out', 'legislation: information to make or change laws'),
        ('Who', 'heads of departments only', 'anyone: officials and private persons'),
        ('Attendance', 'on their own initiative, with the President’s consent, or on request: discretionary', 'compulsory, by subpoena; contempt for refusal'),
        ('Who may decline', 'the department head, if the President withholds consent', 'only the President and SC Justices, or anyone with a valid claim of privilege'),
        ('Closed door', 'executive session when the President states in writing that security or public interest requires', 'per the published rules'),
        ('Leading case', C('senateermita', 'Senate v. Ermita') + ' (2006)', C('senateermita', 'Senate v. Ermita') + '; ' + C('sabio', 'Sabio v. Gordon')),
    ]),
    kind='comparison', when='an official “declines the invitation” or the President orders officials not to attend.',
    hook='<em>22 asks; 21 compels.</em> A requirement of prior consent can work for the question hour, never for a Sec. 21 inquiry (EO 464).',
    oral='The issue is whether officials may skip the Senate hearing on the President’s order. Senate v. Ermita distinguishes the question hour under Section 22, where department heads appear with the President’s consent, from inquiries in aid of legislation under Section 21, where appearance is compulsory. The only way out of a Section 21 inquiry is a valid, specific claim of executive privilege. Here, [it is a Section 21 inquiry and no specific privilege was claimed], so the officials must appear.',
    cap='The 1987 Constitution removed the mandatory question hour (Gatmaytan), which makes the compulsory power of inquiry all the more important.')

fig('14', 'after', '<h3 id="legproc-inq">Inquiries in aid of legislation: the three requisites</h3>\n', 'inquiry', 'Must this witness answer the committee?',
    gates([G('Is the inquiry in aid of legislation?', 'judged by the speech or resolution behind it; probing whether specific persons committed a crime already pending in court is not', 'Void inquiry; may be enjoined', C('bengzonbr', 'Bengzon v. Senate Blue Ribbon') + '; mere pendency of a case is no bar (' + C('sabio', 'Sabio') + ')', 'no', 'no'),
           G('Were its rules duly published in this Congress?', 'Official Gazette or a newspaper of general circulation; a website or booklet is not enough, unless the rules say they continue until amended', 'Enjoined until published', C('garcillano', 'Garcillano') + '; ' + C('neri', 'Neri'), 'no', 'no'),
           G('Can Congress compel this witness?', 'not the President or SC Justices; military officers barred by the Commander-in-Chief need a court order; no statute exempts anyone else', 'Cannot be compelled by Congress alone', C('gudani', 'Gudani') + ' (go to court); ' + C('sabio', 'Sabio') + ' (no statutory exemption)', 'no', 'sun'),
           G('Does the witness validly claim privilege for this information?', 'claimed by the President or the ES “by order of the President”, specific; presidential communications or diplomatic negotiations', 'May refuse those questions', C('neri', 'Neri') + '; ' + C('akbayanjpepa', 'AKBAYAN v. Aquino') + '; ' + C('senateermita', 'Senate v. Ermita'), 'yes', 'sun'),
           G('Are the witness’s rights respected?', 'self-incrimination only per question; no custodial rights; a chance to explain before contempt for false or evasive testimony', 'Contempt or arrest void', C('ong2023', 'Ong (2023)') + '; ' + C('ong2025', 'Ong v. Senate Tricomm'), 'no', 'no')],
          ('Must testify; contempt valid', 'detention lasts only until the committee report is acted on or the Congress ends (' + C('balag', 'Balag') + ')', 'ok'),
          facts=[fact('Bengzon v. Senate Blue Ribbon (1991)', 'After a privilege speech, the Blue Ribbon Committee investigates whether the sale of Kokoy Romualdez’s corporations to the Lopa Group violated RA 3019, while the same transactions are in a pending Sandiganbayan case against the witnesses.', 'n', 'An inquiry into whether specific persons broke the law, already before a court, is not in aid of legislation. Enjoined.'),
                 fact('Garcillano (2008)', 'In the 14th Congress, the Senate opens an inquiry into the “Hello Garci” tapes; its rules were published in an earlier Congress and posted on its website.', 'y,n', 'The rules must be published in each Congress, in the OG or a newspaper. Enjoined until published.'),
                 fact('Neri (2008)', 'Neri refuses three questions about his conversations with the President on the NBN–ZTE deal; the Executive Secretary claims privilege “by order of the President”.', 'y,y,y,y', 'Presidential communications privilege, validly claimed; the committees did not show the answers were critical to legislation. The contempt order was void.'),
                 fact('Gudani v. Senga (2006)', 'Two generals testify at a Senate hearing despite the President’s order, through the AFP Chief of Staff, not to appear.', 'y,y,n', 'The Commander-in-Chief may bar military officers; Congress must go to the courts to compel them. The officers may be disciplined.'),
                 fact('Sabio v. Gordon (2006)', 'PCGG commissioners refuse a Senate subpoena, citing EO 1, Sec. 4(b), which exempts them from testifying in legislative proceedings.', 'y,y,y,n,y', 'No statute can exempt anyone from Sec. 21 without a constitutional basis: they must testify, and contempt was proper.'),
                 fact('Ong (2023)', 'In the Pharmally hearings, two witnesses are cited for testifying “falsely and evasively” and ordered arrested the same day, without being asked to explain.', 'y,y,y,n,n', 'Contempt for false or evasive testimony is punitive: the witness must first get a chance to explain. The order was void.'),
                 fact('Ong v. Senate Tricomm (2025)', 'A witness in the POGO hearings refuses to testify at all, invoking the rights to remain silent, against self-incrimination and to counsel.', 'y,y,y,n,y', 'A witness, not an accused: she must take the stand and may refuse only specific incriminating questions. No custodial rights before Congress.')]),
    kind='gates', when='someone refuses a subpoena, refuses to answer, or is cited in contempt by the Senate, the House or a committee.',
    hook=acro(('A', 'in aid of legislation'), ('P', 'published rules, each Congress'), ('R', 'rights respected'), ('P', 'privilege, validly claimed'), ('P', 'persons beyond compulsion')) + '<em>A-P-R</em> are the three requisites of Sec. 21; the two <em>P</em>s are the only ways out.',
    oral='The issue is whether the witness must answer the committee. Article VI, Section 21 lets Congress conduct inquiries in aid of legislation, under duly published rules, with the witnesses’ rights respected. In Bengzon v. Senate Blue Ribbon, an inquiry into whether specific persons broke the law was not in aid of legislation; in Neri, a valid presidential communications privilege let the witness refuse. Here, [apply the gates], so the witness [must testify or may refuse].',
    cap='The first three gates are the requisites in the text of Sec. 21; the last two are the defenses the Court has recognized. Detention for contempt lasts only until the inquiry ends (Balag).')

fig('14', 'after', '<h3 id="legproc-priv">Executive privilege</h3>\n', 'privilege', 'Is the privilege validly claimed, and does it hold?',
    sub('How it must be claimed (Senate v. Ermita)') + grid(N('By the President', 'or the Executive Secretary “by order of the President”', 'acc'), N('Expressly and specifically', 'stating the kind of privilege and why; no blanket order', 'acc'), N('For information, not persons', 'EO 464’s coverage of whole classes of officials (Secs. 2(b), 3) was void', 'no'), m=170)
    + sub('Presidential communications (Neri)') + vflow(N('1 · A quintessential, non-delegable power', 'e.g., entering into an executive agreement', 'acc'), VE('and'), N('2 · Operational proximity', 'authored, or solicited and received, by the President or a close advisor', 'acc'), VE('then'), N('3 · Presumed privileged', 'overcome only by a showing of compelling need and unavailability elsewhere; against Congress, the information must be critical to legislation, not merely pertinent', 'sun'))
    + sub('Diplomatic negotiations (AKBAYAN v. Aquino)') + grid(N('Offers stay privileged', 'even after the treaty’s final text is public', 'acc'), N('Burden shifts', 'once the privilege is shown, citizens or Congress must show sufficient need', 'sun'), m=170),
    kind='checklist', when='an official refuses to answer “by order of the President”, or the executive withholds drafts, offers or conversations.',
    hook='<em>Who, how, what</em>: the President, expressly, for information. Neri’s three: <em>Quintessential power, Proximity, No compelling need shown</em>.',
    oral='The issue is whether the executive may withhold this information from Congress. Under Senate v. Ermita, privilege covers kinds of information, not classes of persons, and must be claimed expressly by the President or the Executive Secretary by order of the President. In Neri, conversations with the President on the NBN–ZTE deal were presumptively privileged because they concerned a quintessential power and a close advisor, and the Senate did not show a compelling need. Here, [apply], so the privilege [holds or fails].',
    cap='The presumption runs against secrecy in general (Senate v. Ermita), but for presidential communications it runs in favor of privilege (Neri). Know which presumption you are in.')

fig('14', 'after', '<h3 id="legproc-contempt">Contempt, arrest and detention</h3>\n', 'contempt', 'From subpoena to release: the contempt clock',
    tl([('1', 'Subpoena; the witness refuses to appear, to answer, or answers falsely or evasively', ''),
        ('2', 'A chance to explain, required before citing for false or evasive testimony (' + C('ong2023', 'Ong 2023') + ')', 'key'),
        ('3', 'Contempt order: a majority of all the committee’s members, after deliberation (Senate Rules, Sec. 18; ' + C('neri', 'Neri') + ')', ''),
        ('4', 'Arrest and detention under the inherent power of contempt (' + C('sabio', 'Sabio') + ')', ''),
        ('5', 'Release: when the committee report is approved or disapproved, or the Congress ends; recess does not end it (' + C('balag', 'Balag') + ')', 'key'),
        ('6', 'Longer punishment: only statutory contempt (Art. 150, RPC), tried in court with a definite term', '')])
    + sub('The detained witness’s remedies') + grid(N('Habeas corpus', 'SC, CA and RTC have concurrent jurisdiction; the SC will not take a case already with the CA (' + C('agcaoili', 'Agcaoili') + ')', 'acc'),
                                                    N('Certiorari or prohibition', 'needs grave abuse; if the President attacks the inquiry’s purpose, the committee decides that first (' + C('senatemedialdea', 'Senate v. Medialdea') + ')', 'sun'),
                                                    N('Amparo', 'not available: only extralegal killings and enforced disappearances (' + C('agcaoili', 'Agcaoili') + ')', 'no'), m=170),
    kind='timeline', when='a witness has been detained by the Senate or House, and you are asked whether, how long, and what remedy.',
    hook='<em>Explain, vote, detain, release</em>: a chance to explain; a majority of all; detention only until the report or the Congress ends.',
    oral='The issue is how long the Senate may detain the witness. In Balag v. Senate, the Court held that detention under the Senate’s inherent contempt power lasts only until the inquiry ends, that is, when the committee report is approved or disapproved, or when the Congress ends. And under Ong v. Senate (2023), a witness cited for lying must first be given a chance to explain. Here, [the report was approved on __], so the detention must end.',
    cap='The Senate is a continuing body for some purposes, but its business, and the inherent-contempt detention tied to it, ends with each Congress (Balag; Neri).')


# =====================================================================
# 15 · other powers of Congress and impeachment (finals)
# =====================================================================
fig('15', 'after', '<h3 id="ocong-votes">The votes: who decides, how many, together or apart</h3>\n', 'cvotes', 'Count the vote first: every non-legislative power has a number',
    cmp(['Who votes', 'How many', 'Together or apart'], [
        ('Tie in the canvass for President or VP (VII, 4)', 'both Houses', 'majority of all the Members', 'voting separately'),
        ('Confirming a new Vice-President (VII, 9)', 'both Houses', 'majority of all the Members', 'voting separately'),
        ('Special election, both offices vacant (VII, 10)', 'Congress, convening on the 3rd day without a call', 'a law within 7 days; deemed certified; law on third reading', 'as a bill'),
        ('Presidential inability, contested (VII, 11)', 'both Houses', 'two-thirds', 'voting separately'),
        ('Revoking or extending martial law (VII, 18)', 'Congress', 'majority of all its Members', '<b>voting jointly</b>: a joint session only for this (' + C('padilla', 'Padilla') + ')'),
        ('Amnesty (VII, 19)', 'Congress', 'majority of all the Members', 'not stated'),
        ('Treaty (VII, 21)', 'Senate', 'two-thirds of all the Members', '—'),
        ('War (VI, 23(1))', 'both Houses, in joint session', 'two-thirds', 'voting separately'),
        ('Emergency powers (VI, 23(2))', 'Congress, by law', 'as for any law; withdrawn by resolution', 'as a bill'),
        ('Amending or revising (XVII, 1)', 'Congress', 'three-fourths of all its Members', 'not stated'),
        ('Calling a convention (XVII, 3)', 'Congress', 'two-thirds of all its Members, or a majority to submit the question to the voters', 'not stated'),
        ('Impeaching (XI, 3(3)–(4))', 'House', 'one-third of all the Members', '—'),
        ('Convicting (XI, 3(6))', 'Senate', 'two-thirds of all the Members', '—'),
    ]),
    kind='comparison', when='a news card reports a vote in Congress or the Senate: count it before you argue anything else.',
    hook='<em>Separately</em> unless the text says <em>jointly</em>: only martial law pools the votes. <em>1/3 impeaches, 2/3 convicts; 2/3 of the Senate for treaties; 3/4 to amend; a majority of all for amnesty.</em>',
    oral='The first question is whether the right body voted by the right number. Here, the Constitution requires [two-thirds of all the Members of the Senate] for [concurrence in a treaty]. [Seventeen of twenty-four] meets the [sixteen] required, so the [concurrence] is valid.',
    cap='“Of all the Members” counts every seat. Whether “all the Members of the Senate” counts only senators able to take part was decided by the impeachment court on September 23, 2026 (13–1, yes); see the trial section.')

fig('15', 'before', '<div class="codal"><span class="art">Art. VII, Sec. 10</span>', 'canvass', 'Congress has adjourned sine die: may it still canvass and proclaim?',
    gates([G('Is the task legislative: passing bills in the ordinary course?', 'adjournment sine die ends the regular session', 'Not without a special session', 'the President may call one at any time (Art. VI, Sec. 15)', 'yes', 'sun'),
           G('Is the non-legislative task already done?', 'the canvass is complete and the winners proclaimed', 'Functus officio', 'the board’s work is over', 'yes', 'sun')],
          ('It continues, without a call', 'the joint public session cannot adjourn sine die until it canvasses and proclaims; members may change, the board remains (' + C('pimentelcongress', 'Pimentel') + ')', 'ok'),
          facts=[fact('Pimentel v. Joint Committee (2004)', 'Both Houses adjourn their last regular session sine die on June 11, 2004, while the Joint Committee is still canvassing the votes for President and Vice-President.', 'n,n', 'Canvassing is non-legislative and unfinished, and the Twelfth Congress exists until noon of June 30: the Joint Committee may finish and the joint session may reconvene without a call.'),
                 fact('The 1992 canvass', 'Both Houses adjourn sine die on May 25, 1992; the Joint Committee finishes tallying on June 16; Congress, as the National Board of Canvassers, proclaims Ramos and Estrada on June 22.', 'n,n', 'The precedent the Court relied on: the canvass may be finished after adjournment.'),
                 fact('A June budget bill', 'After adjourning sine die in early June, the leadership wants to pass a supplemental budget before June 30 without a call from the President.', 'y', 'Ordinary legislation needs a session; after sine die, only a special session called by the President.')]),
    kind='gates', when='Congress has adjourned or is in recess, and someone says it can no longer canvass, proclaim, or meet without a call.',
    hook='<em>Sessions end; duties don’t.</em> Sine die closes the session, not the term (noon of June 30), and never a constitutional task half done.',
    oral='The issue is whether Congress may keep canvassing after adjourning sine die. Article VII, Section 4 makes Congress the national board of canvassers for President and Vice-President. In Pimentel v. Joint Committee, the Court held that adjournment sine die ends the regular session, not the term, and that canvassing is a non-legislative duty that continues until done, without a call from the President. Here, [the canvass is unfinished], so Congress may reconvene and proclaim.',
    cap='The same idea runs through Art. VII: Congress convenes without a call for a special election (Sec. 10), for a contested inability (Sec. 11) and after a martial law proclamation (Sec. 18).')

fig('15', 'after', '<h3 id="ocong-ml">The legislative check on martial law and the suspension of the writ</h3>\n', 'mljoint', 'Must Congress meet in joint session?',
    gates([G('Is either House moving to revoke, or has the President asked for an extension?', 'mere support or concurrence: the Constitution does not say how, so each House uses its own rules', 'No joint session required', C('padilla', 'Padilla') + ': the Houses may deliberate and resolve separately', 'no', 'sun'),
           G('Did Congress convene jointly and vote jointly, by a majority of all its Members?', 'a single House cannot revoke alone; once either House resolves to revoke, Congress must convene jointly', 'No valid revocation or extension', 'one House’s resolution is not an act of Congress', 'no', 'no')],
          ('Revocation binds; extension valid', 'the President cannot set aside a revocation; an extension lasts for the period Congress fixes, if the rebellion persists and public safety requires it', 'ok'),
          facts=[fact('Padilla v. Congress (2017)', 'After Proclamation No. 216, the Senate adopts a resolution not to revoke (17–5) and rejects a motion to meet jointly (9–12); the House adopts a resolution of full support.', 'n', 'No House moved to revoke, so the joint-vote clause never came into operation; mandamus denied.'),
                 fact('The July 2017 extension', 'At the President’s request, Congress meets in joint session on July 22, 2017 and extends martial law in Mindanao to December 31, 2017 (261–18).', 'y,y', 'Extension “in the same manner” as revocation: a joint vote of a majority of all the Members. Valid.'),
                 fact('A Senate-only revocation', 'The Senate alone votes 13–11 to revoke a proclamation; the House does not act.', 'y,n', 'Revocation is by Congress voting jointly. Once a House resolves to revoke, Congress must convene jointly and vote; the Senate’s vote alone revokes nothing.')]),
    kind='gates', when='Congress responds to a martial law proclamation or a suspension of the writ: separately, jointly, or not at all.',
    hook='<em>Meet jointly only to vote jointly.</em> Support: each House, its own rules. Revoke or extend: one joint vote, a majority of all.',
    oral='The issue is whether Congress must meet in joint session after a martial law proclamation. Article VII, Section 18 lets Congress, voting jointly by a majority of all its Members, revoke the proclamation, and extend it on the President’s initiative. In Padilla v. Congress, the Court held that the duty to meet jointly arises only to vote on revocation; mere support may be expressed by each House under its own rules. Here, [no House moved to revoke], so no joint session was required.',
    cap='Leonen, J.’s dissent is the best argument the other way: the power to revoke includes the duty to deliberate in one forum. The midterm-style answer gives both.')

fig('15', 'before', '<div class="test"><b>Executive agreements after Saguisag: four rules</b>', 'treatysteps', 'How a treaty is made: who does what',
    hflow(N('Negotiation', 'the President, as sole organ, or agents with full powers', 'acc'), HE(''), N('Signature', 'authenticates; shows good faith; does not bind', 'acc'), HE(''), N('Ratification', 'by the President: the state accepts', 'acc'), HE(''), N('Senate concurrence', 'two-thirds of all the Members (Art. VII, Sec. 21)', 'acc'), HE(''), N('Exchange of instruments', 'entry into force', 'acc')),
    kind='flow', when='someone says the Senate “ratifies” a treaty, or wants the President forced to submit or ratify one.',
    hook='<em>Negotiate, sign, ratify, concur, exchange.</em> The President ratifies; the Senate only concurs (Pimentel).',
    oral='The President negotiates and ratifies treaties; the Senate only concurs, by two-thirds of all its Members, under Article VII, Section 21. In Pimentel v. Executive Secretary, the Court held that signing does not bind and that the President may refuse to submit a signed treaty to the Senate, or refuse to ratify it after concurrence; mandamus will not lie. Here, [apply].',
    cap='Signature authenticates; ratification binds. The Court cannot compel the President to transmit or ratify (Pimentel v. Executive Secretary).')

fig('15', 'before', '<div class="test"><b>Executive agreements after Saguisag: four rules</b>', 'treaty', 'Treaty or executive agreement?',
    gates([G('Does it allow the initial entry of foreign military bases, troops or facilities?', 'Art. XVIII, Sec. 25', 'Treaty required', 'concurred in by the Senate and recognized as a treaty by the other state; a referendum if Congress requires', 'yes', 'acc'),
                G('Does it implement an existing treaty or law, within its terms?', 'traceable authority; no new or expanded obligations', 'Executive agreement suffices', C('saguisag', 'Saguisag') + ': EDCA implements the VFA and the MDT', 'yes', 'ok'),
                G('Does it amend a statute, or create obligations only a treaty can?', 'an executive agreement is inferior to treaties and statutes', 'Needs a treaty (two-thirds of the Senate)', 'it cannot prevail over the law (Saguisag’s guidelines; Carpio, J., dissenting in ' + C('bayanmuna', 'Bayan Muna') + ')', 'yes', 'no')],
               ('Executive agreement: valid without concurrence', 'the form follows the parties’ intent; an exchange of notes will do (' + C('bayanmuna', 'Bayan Muna') + ')', 'ok'),
               facts=[fact('Saguisag v. Ochoa (2016)', 'EDCA (2014) gives US forces access to Agreed Locations, rotational presence and the prepositioning of equipment; the VFA, concurred in by the Senate in 1999, already allows US troops in.', 'n,y', 'Not initial entry; it implements the VFA and the MDT within their terms: a valid executive agreement.'),
                      fact('Bayan Muna v. Romulo (2011)', 'By exchange of notes, the Philippines and the US agree not to surrender each other’s nationals and officials to an international tribunal without consent.', 'n,n,n', 'No bases or troops; RA 9851’s surrender clause is permissive, so no law is amended: a valid executive agreement.'),
                      fact('The Philippines–France SOVFA (2026)', 'The first visiting forces agreement with France lets French troops enter the Philippines for joint activities.', 'y', 'Initial entry of foreign troops: a treaty is required. The Senate concurred 17–0 on October 8, 2026.'),
                      fact('A tax side letter', 'An exchange of notes under the VFA exempts US contractors from Philippine income tax, which no treaty or law provides.', 'n,n,y', 'It adds an obligation found in no treaty or law and overrides the tax code: it needs Senate concurrence.')]),
    kind='gates', when='the executive signs an “agreement”, “arrangement” or exchange of notes with another state, especially on troops, extradition or surrender.',
    hook='<em>Entry needs a treaty; implementation needs only authority.</em> The Senate <em>concurs</em>; the President <em>ratifies</em> (Pimentel).',
    oral='The issue is whether the agreement needs Senate concurrence. Article VII, Section 21 requires two-thirds of all the Senators for treaties, and Article XVIII, Section 25 requires a treaty for foreign bases, troops or facilities. But in Saguisag v. Ochoa, the Court held that Section 25 covers only initial entry, so an executive agreement that implements an existing treaty, within its terms, is valid; Bayan Muna v. Romulo adds that the form follows the parties’ intent. Here, [the agreement implements the VFA and adds no new obligation], so no concurrence is needed.',
    cap='Only the initial entry of foreign bases, troops or facilities dictates a treaty by subject (Art. XVIII, Sec. 25); everything else turns on the parties’ intent and on staying within existing law.')

fig('15', 'before', '<aside class="note gat"><strong>Gatmaytan (“Variant Technicalities”', 'withdraw', 'May the President withdraw from this treaty alone?',
    gates([G('Was the treaty entered into pursuant to a prior law, or affirmed by a later law that is still in force?', 'the treaty carries Congress’s imprimatur', 'No unilateral withdrawal', 'unless the law is repealed', 'yes', 'no'),
           G('Did the Senate condition its concurrence on its concurrence in withdrawal?', 'in the concurring resolution, a later resolution, a law, a joint resolution, or a comprehensive Senate resolution', 'No unilateral withdrawal', 'withdrawal needs the Senate', 'yes', 'no'),
           G('Does the President act bona fide, on a ground that the treaty is contrary to the Constitution or a law?', 'a court ruling, a later law, or the President’s own judgment', 'Reviewable for grave abuse', 'never unbridled; an arbitrary withdrawal may be struck down in a justiciable case', 'no', 'sun')],
          ('The President may withdraw', 'through the treaty’s own exit clause (Rome Statute, Art. 127: written notice to the UN Secretary-General, effective one year later)', 'ok'),
          facts=[fact('Pangilinan v. Cayetano (2021)', 'The Philippines withdraws from the Rome Statute by note verbale in March 2018. RA 9851 (2009) predates the concurrence but stands on its own and is broader; Senate Resolution No. 546 has no withdrawal clause; Resolution No. 289 was never adopted.', 'n,n,y?', 'Neither limit applied, so the President had leeway; but the Court did not rule on the merits, because the withdrawal had taken effect (moot).'),
                 fact('A conditioned concurrence', 'The Senate concurs in a treaty on condition that the Philippines will not withdraw without the Senate’s concurrence; years later the President withdraws alone.', 'n,y', 'Guideline (c): no unilateral withdrawal.'),
                 fact('A treaty backed by a statute', 'Congress passes a law to implement a treaty and keeps it in force; the President withdraws from the treaty alone.', 'y', 'Guideline (b): no unilateral withdrawal while the law stands.')]),
    kind='gates', when='the President announces an exit from a treaty (the Rome Statute, the VFA, the MDT) without asking the Senate.',
    hook='<em>Two mirrors</em>: no exit alone if a <em>law</em> stands behind the treaty or the <em>Senate</em> conditioned its yes; otherwise <em>bona fide</em> leeway, reviewable.',
    oral='The issue is whether the President may withdraw from the treaty alone. The Constitution is silent, but Pangilinan v. Cayetano laid down guidelines: the President has leeway to withdraw from a treaty bona fide contrary to the Constitution or a law, but not unilaterally where a law backs the treaty or the Senate conditioned its concurrence on concurring in any withdrawal. Here, [the Senate’s resolution has no such condition and no law backs the treaty], so the President may withdraw, subject to review for grave abuse.',
    cap='The guidelines were laid down “as guide for future cases”; the fallo only dismissed for mootness. Say so in orals, then add Gatmaytan’s critique.')

fig('15', 'before', '<aside class="note gat"><strong>Gatmaytan (<em>Government Structure</em>, ch. 5):</strong>', 'emerg', 'Three emergency provisions: whose power is it?',
    cmp(['Emergency powers (Art. VI, Sec. 23(2))', 'Commander-in-Chief (Art. VII, Sec. 18)', 'Takeover (Art. XII, Sec. 17)'], [
        ('The power', 'delegated legislative power', 'calling out the armed forces; suspending the writ; martial law', 'temporary takeover or direction of private public utilities and businesses affected with public interest'),
        ('Trigger', 'war or other national emergency', 'lawless violence, invasion or rebellion (calling out); invasion or rebellion when public safety requires (writ, martial law)', 'national emergency, when the public interest requires'),
        ('Whose', 'Congress, by law, to the President', 'the President’s own', '“the State” = Congress by law; the President carries it out (' + C('davidgma', 'David') + ')'),
        ('Limits', 'limited period; restrictions; a declared policy; ends at the next adjournment or by resolution', '60 days; report within 48 hours; Congress may revoke or extend (' + C('padilla', 'Padilla') + '); the SC reviews the factual basis within 30 days', 'during the emergency, on reasonable terms the law prescribes'),
    ]),
    kind='comparison', when='the President declares a state of emergency or calamity and wants to take over businesses, spend, or legislate.',
    hook='<em>Congress lends, the President borrows</em>: emergency powers and takeovers need a law; only the Commander-in-Chief powers are the President’s own, and Congress can revoke them.',
    oral='The issue is whether the President may take over [the power plants] in an emergency. The President alone may declare a national emergency, but the takeover of a private business under Article XII, Section 17 needs a law, as do emergency powers under Article VI, Section 23(2): in David v. Macapagal-Arroyo, the Court held that “the State” means Congress. Here, [there is no law], so the takeover is void.',
    cap='The Commander-in-Chief clause gets its own map in Batch 7 (V.B.2(f)).')

fig('15', 'after', '<h3 id="ocong-impeach">Impeachment: who, for what, and how</h3>\n', 'impflow', 'From complaint to judgment: tap a stage', stepper([
    ('File (first mode)', 'z-a', N('A verified complaint', 'by a Member of the House, or by a citizen with a Member’s resolution or endorsement', 'acc')),
    ('Order of Business', 'z-a', N('Within 10 session days', 'mandatory and ministerial: the Secretary General and the Speaker cannot sit on it; a session day is a calendar day with a plenary session (' + C('duterte2025', 'Duterte') + ', Resolution)', 'sun')),
    ('Referral', 'z-a', N('Within 3 session days after', 'referral initiates the proceeding and starts the one-year bar (' + C('francisco', 'Francisco') + '); two complaints referred together are one proceeding (' + C('gutierrez', 'Gutierrez') + ')', 'sun')),
    ('Committee', 'z-a', N('Form, substance, grounds; hearing; report within 60 session days', 'by a majority of all its Members, with the resolution; calendared within 10 session days of receipt', 'acc')),
    ('Plenary', 'z-a', N('One-third of all the Members', 'to affirm a favorable resolution with the Articles, or override a contrary one; each vote recorded', 'acc')),
    ('Or: one-third files', 'z-b', N('Second mode: the complaint is the Articles', 'initiated on valid endorsement by one-third, each Member verifying; the evidence available to all Members at plenary (' + C('duterte2025', 'Duterte') + ', Resolution)', 'sun')),
    ('Senate trial', 'z-b', N('Trial shall forthwith proceed', 'within a reasonable time (' + C('generillo', 'Generillo') + '); senators on oath; the Chief Justice presides only if the President is on trial', 'acc')),
    ('Judgment', 'z-b', N('Two-thirds of all the Members of the Senate', 'removal and disqualification only; criminal liability remains (Sec. 3(7); ' + C('recorona', 'Re: Corona') + ')', 'acc'))], start=0),
    kind='interactive', when='a news card describes any step of an impeachment: place it on the line before you argue.',
    hook='<em>10 · 3 · 60 · 10, then 1/3 and 2/3.</em> Session days for the House; “forthwith” for the Senate; one proceeding a year.',
    oral='Impeachment has two halves: the House initiates and the Senate tries. Under Article XI, Section 3, a verified complaint goes into the Order of Business within ten session days and to the Committee within three; one-third of all the Members impeaches, or one-third can file the Articles directly; and conviction needs two-thirds of all the Senators. Francisco holds that the proceeding is initiated on filing and referral, which starts the one-year bar. Here, [place the facts on the steps].',
    cap='The z-b stages are the second mode and the Senate. The first-mode periods are House session days; the Senate has no fixed period (Generillo).')

fig('15', 'before', '<div class="tw"><table><thead><tr><th>Point</th>', 'initiate', 'Is this impeachment complaint barred by the one-year rule?',
    gates([G('Was it referred together with the earlier complaint, at the same time?', 'simultaneous referral by the plenary', 'One proceeding: no bar', C('gutierrez', 'Gutierrez') + ': two matches, one flame', 'yes', 'ok'),
           G('Was another proceeding against the same official initiated within the past year?', 'first mode: on referral, or when the 10- or 3-session-day period lapsed, or if left unacted on at sine die; second mode: on valid one-third endorsement', 'Barred (Art. XI, Sec. 3(5))', C('francisco', 'Francisco') + '; ' + C('duterte2025', 'Duterte v. House'), 'yes', 'no'),
           G('Were the constitutional steps and due process followed?', 'the session-day periods; one-third of all the Members, each verifying; evidence available to all Members at plenary; acts in relation to the office in the current term', 'Void ab initio', 'the Senate acquires no jurisdiction (' + C('duterte2025', 'Duterte v. House') + ')', 'no', 'no')],
          ('Validly initiated', 'committee hearings follow (first mode), or trial by the Senate shall forthwith proceed (second mode)', 'ok'),
          facts=[fact('Francisco v. House (2003)', 'The first complaint against CJ Davide is filed on June 2 and referred on August 5, 2003, then dismissed; on October 23, 2003, more than one-third of the House files a second complaint.', 'n,y', 'The first was initiated on referral, so a second within a year is barred; the House rules saying otherwise are void.'),
                 fact('Gutierrez (2011)', 'Two complaints against the Ombudsman, filed in July and August 2010, are referred to the Committee on Justice together on August 11, 2010.', 'y', 'Simultaneous referral initiates a single proceeding: no violation of the bar.'),
                 fact('Duterte v. House (2025)', 'Three citizens’ complaints filed in December 2024 are never put in the Order of Business or referred; on February 5, 2025, 215 Members sign a fourth complaint that goes straight to the Senate.', 'n,y', 'Under the Resolution, the first complaint was deemed initiated when the periods lapsed in January 2025: the fourth, within a year, is barred and void.'),
                 fact('The 2026 Articles', 'A complaint filed February 2, 2026 is set aside under the bar; complaints filed February 9 and 18, after the bar lapsed on February 6, are referred on February 23; the Committee finds probable cause and the House approves the Articles on May 11, 2026, well above one-third.', 'n,n,y?', 'More than a year after the 2025 initiation, and the House followed the steps; the petitions against the Committee’s hearings were dismissed as moot (Torreon).')]),
    kind='gates', when='a new impeachment complaint is filed against an official who faced another one in the past year, or the House sits on complaints.',
    hook='<em>Filed + referred = initiated</em>; two at once = one; sitting on it = initiated anyway (Duterte). <em>One proceeding, one year.</em>',
    oral='The issue is whether the new complaint is barred by the one-year rule in Article XI, Section 3(5). Francisco and Gutierrez hold that a proceeding is initiated by filing and referral, and that complaints referred together are one proceeding. Duterte v. House adds that a complaint the House fails to put in the Order of Business or refer within the constitutional periods is deemed initiated anyway. Here, [the earlier complaint was initiated on __, less than a year before], so the new complaint is barred.',
    cap='Gatmaytan’s objection to the third trigger: it lets allies file defective complaints that the House ignores, so the bar runs and protects the official.')

fig('15', 'after', '<h3 id="ocong-review">Judicial review of impeachment</h3>\n', 'jrimp', 'Will the Supreme Court rule on this impeachment step?',
    gates([G('Does the petition invoke a limit the Constitution itself sets?', 'the modes and periods, the votes, the one-year bar, due process; not whether the acts are impeachable', 'Political question: not for the Court', 'what counts as betrayal of public trust is for Congress (' + C('francisco', 'Francisco') + ')', 'no', 'sun'),
           G('Is the controversy still live?', 'not if the conviction was accepted, the Articles are already void, or the House has already sent the Articles to the Senate', 'Dismissed as moot', C('coronasenate', 'Corona v. Senate') + '; ' + C('torreon', 'Torreon'), 'no', 'sun'),
           G('Is the remedy proper, and grave abuse shown?', 'certiorari or prohibition for grave abuse; mandamus only for a clear ministerial duty, not the Senate’s timing', 'Dismissed', C('generillo', 'Generillo') + ': no mandamus to make the Senate try forthwith', 'no', 'no')],
          ('The Court rules on the limit', 'and may void the act; but it never decides when, who or whether to remove (' + C('duterte2025', 'Duterte v. House') + ')', 'ok'),
          facts=[fact('Corona v. Senate (2012)', 'CJ Corona challenges the complaint and the impeachment court’s rulings on evidence and bank subpoenas; while the case is pending, he is convicted, accepts the verdict and leaves office.', 'y,n', 'Mooted by supervening events and his own acts. Dismissed.'),
                 fact('Generillo v. Senate (2026)', 'A lawyer asks the Court to compel the Senate to convene at once on the Articles received February 5, 2025; the Senate convenes June 10; in July the Articles are voided.', 'y,n', 'Moot: the Articles were void. Even on the merits, mandamus does not lie and the Senate acted within a reasonable time.'),
                 fact('Duterte v. House (2025)', 'The VP challenges Articles signed by 215 Members while three earlier complaints were never referred, and without being given the evidence.', 'y,y,y', 'The one-year bar and due process are constitutional limits; the Articles were void and the Senate never acquired jurisdiction.'),
                 fact('Torreon (2026)', 'Lawyers challenge the House Committee’s sufficiency findings and subpoenas in March 2026; the House impeaches the VP on May 11 and sends the Articles to the Senate on May 14.', 'y,n', 'Dismissed as moot on August 5, 2026: the accusatory phase was over.'),
                 fact('“Not betrayal of public trust”', 'A respondent asks the Court to rule that the acts charged do not amount to betrayal of public trust.', 'n', 'What is an impeachable offense is a truly political question left to Congress (Francisco).')]),
    kind='gates', when='anyone runs to the Supreme Court during an impeachment: against the House committee, the plenary, the Senate’s timing, or a ruling of the impeachment court.',
    hook='<em>Limit? Live? Lawful remedy?</em> Then the Court rules: on the limit, never on the removal.',
    oral='The issue is whether the Court may review this step of the impeachment. Francisco holds that impeachment is reviewable where the Constitution sets limits, like the one-year bar, and Duterte v. House adds that it is not purely political, so due process applies. But the case must be live: Corona’s petition and the 2026 Torreon petition were dismissed as moot, and Generillo holds that mandamus cannot set the Senate’s timetable. Here, [the petition invokes the one-year bar and the Articles are pending], so the Court may rule on it.',
    cap='The September 30, 2026 dismissal of the petitions against the two-thirds ruling fits the same gates: no verdict yet, so no live injury (see the midterm news box).')

fig('15', 'after', '<h3 id="ocong-effects">The judgment, its effects, and quo warranto</h3>\n', 'qwimp', 'Impeachment, quo warranto, or a criminal case?',
    cmp(['Impeachment', 'Quo warranto', 'Criminal or administrative case'], [
        ('Nature', 'political; sui generis', 'judicial', 'judicial or administrative'),
        ('Tests', '<b>fitness</b>: acts in office', '<b>title</b>: eligibility at appointment or election', 'liability for an offense'),
        ('Started by', 'the House (one-third of all the Members)', 'the State, through the Solicitor General', 'the prosecutor, the Ombudsman, the disciplining authority'),
        ('Decided by', 'the Senate (two-thirds of all the Members)', 'the courts (the SC has original jurisdiction)', 'the courts, or the disciplining authority'),
        ('Judgment', 'removal and disqualification only', 'ouster: the officer never validly held the office (a de facto officer)', 'penalties, including forfeiture of benefits if imposed'),
        ('Retirement benefits', 'kept, unless liability is judicially established (' + C('recorona', 'Re: Corona') + ')', '—', 'forfeited only if the judgment says so'),
        ('Time bar', 'one proceeding a year (Sec. 3(5))', 'one year under Rule 66, but not against the State (' + C('sereno', 'Sereno') + ')', 'prescription under the law'),
        ('Leading case', C('francisco', 'Francisco') + '; ' + C('duterte2025', 'Duterte v. House'), C('sereno', 'Republic v. Sereno') + ' (8–6)', C('recorona', 'Re: Corona') + ' (later liability is a resolutory condition)'),
    ]),
    kind='comparison', when='the government tries to remove an impeachable officer outside impeachment, or asks what else follows from a Senate conviction.',
    hook='<em>Title or fitness?</em> A defect before the oath: quo warranto (title). Acts in office: impeachment (fitness). Impeachment takes the <em>office</em>, never the <em>pension</em>.',
    oral='The issue is whether [the officer] can be removed outside impeachment. Republic v. Sereno holds that impeachment is not exclusive: quo warranto tests title, meaning eligibility at appointment, while impeachment tests fitness for acts in office. And Re: Letter of Mrs. Corona holds that an impeachment judgment goes no further than removal and disqualification. Here, [the defect existed at appointment], so quo warranto lies.',
    cap='Six Justices dissented in Sereno; Carpio, J.: SALN lapses are impeachable and only Congress removes. The Judiciary batch revisits the case with the June 19, 2018 Resolution.')

fig('15', 'after', '<h3 id="ocong-2026">VP Sara Duterte, 2024 to 2026: the whole story for a news card</h3>\n', 'sara', 'VP Sara Duterte’s two impeachments, step by step', tl([
    ('Dec 2024', 'Three citizens’ complaints are filed and endorsed; none is referred to the Committee on Justice.', ''),
    ('Feb 5, 2025', '215 Members sign a fourth complaint; it reaches the Senate at 4:47 PM on the last session day. The first three are archived.', 'key'),
    ('Jun 10, 2025', 'The Senate convenes as an impeachment court, 126 days later, and returns the Articles to the House.', ''),
    ('Jul 25, 2025', C('duterte2025', 'Duterte v. House') + ': the Articles are barred and void; no new proceeding before February 6, 2026. Reconsideration denied January 28, 2026.', 'key'),
    ('Feb–Mar 2026', 'New complaints: the one filed February 2 is set aside under the bar; those of February 9 and 18 are referred February 23 and found sufficient in form, substance and grounds.', ''),
    ('Mar 27, 2026', C('torreon', 'Torreon et al.') + ' challenge the Committee’s findings and subpoenas in the Supreme Court.', ''),
    ('Apr 22, 2026', C('generillo', 'Generillo v. Senate') + ': “forthwith” means within a reasonable time.', 'key'),
    ('May 11, 2026', 'The House impeaches the VP a second time; the Articles reach the Senate May 14; the impeachment court convenes May 18.', 'key'),
    ('Jul 6, 2026', 'The trial opens; the presiding officer rules that 16 votes are needed to convict.', ''),
    ('Aug 5, 2026', 'The Torreon and Duterte petitions against the House proceedings are dismissed as moot.', ''),
    ('Sep 23, 2026', 'The impeachment court rules 13–1 that two-thirds is counted from senators able to take part (14 of 20). On September 30, the Supreme Court dismisses three petitions against it.', 'key'),
    ('Oct 13, 2026', 'Three of the four Articles are withdrawn; Article 2 (unexplained wealth, SALN, business interests) remains.', ''),
    ('Nov 2026', 'The defense presents its case (from November 9); a verdict is expected 20 to 25 days after it rests.', '')]),
    kind='timeline', when='a news card names VP Sara Duterte, the impeachment court, or the House Committee on Justice.',
    hook='<em>2025: barred. 2026: impeached again.</em> Bar, forthwith, moot, two-thirds of the able.',
    oral='For any news card on the Vice President’s impeachment, place the event on the timeline first. Then pick the rule: initiation and the one-year bar under Francisco, Gutierrez and Duterte v. House; the Senate’s timing under Generillo; mootness once the Articles reach the Senate, as in Torreon; and the two-thirds vote under Article XI, Section 3(6). Here, [the event is __], so the governing rule is [__].',
    cap='Dates from the digests and saved news articles. The verdict had not been rendered as of the latest news item (November 13, 2026).')


# =====================================================================
# 00 · the hook wall (built last, from every hook above)
# =====================================================================
def _plain(t): return re.sub(r'<[^>]+>', '', t)
fig('00', 'before', '</section>', 'wall', 'Every hook on one screen',
    '<div class="hwall">' + ''.join(f'<div class="ht"' + (f' data-scope="{SEC[p]}"' if p in ('03', '04') else '') + f'><span class="tp">{SHORT[p]}</span>{X("fig-" + fid, _plain(t))}<div class="hk">{h}</div></div>' for p, fid, t, h in WALL) + '</div>',
    kind='review', when='the night before and the morning of the exam: read each hook, say the rule aloud, then tap through to check yourself.',
    cap='Test me hides the words under each acronym. The link on every tile jumps to its diagram.', wall=False)
