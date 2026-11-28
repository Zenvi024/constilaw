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
       '08': 'internal', '09': 'priv', '10': 'et', '11': 'powers', '12': 'money', '14': 'legproc', '15': 'ocong', '16': 'pres', '17': 'appt', '18': 'cinc', '19': 'court', '90': 'news'}
SHORT = {'00': 'Exam method', '01': 'Interpretation', '02': 'Judicial review', '03': 'Territory', '04': 'Citizenship', '05': 'Suffrage',
         '06': 'Government', '07': 'Composition', '08': 'Internal', '09': 'Privileges', '10': 'Tribunals and CA', '11': 'Powers',
         '12': 'Money', '14': 'Legislative process', '15': 'Other powers, impeachment', '16': 'The President', '17': 'Appointment, clemency', '18': 'Commander-in-Chief', '19': 'The Supreme Court', '90': 'News'}


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
    cap='The Commander-in-Chief powers are compared side by side on their own map: ' + X('fig-cincpowers', 'calling out, the writ, martial law') + '.')

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
# 16 · the President: office, succession, executive power (finals)
# =====================================================================
fig('16', 'after', '<h3 id="pres-quals">Qualifications, election, term and oath</h3>\n', 'presquals', 'Can this presidential candidate be stopped, and where?',
    gates([G('Has the winner been proclaimed, taken the oath and assumed office?', 'all three; until then, petitions from the COMELEC stay with the Court under Rules 64 and 65', 'The PET’s turn', 'protest within 30 days (second or third placer) or quo warranto within 10 days (any voter); a private quo warranto under Rule 66 needs a claim to the office and one year (' + C('pamatong', 'Pamatong') + ')', 'yes', 'sun'),
           G('Does the candidate meet all five constitutional qualifications?', 'natural-born; registered voter; reads and writes; 40 on election day; 10 years’ residence (Art. VII, Sec. 2)', 'Not qualified', 'cancel the certificate of candidacy if it claimed otherwise (OEC Sec. 78)', 'no', 'no'),
           G('Is there a statutory ineligibility?', 'a final sentence over 18 months, a crime of moral turpitude, insanity (OEC Sec. 12); perpetual disqualification only if the fallo imposes it', 'Disqualified', 'and a sworn claim of eligibility is a false material representation (' + C('buenafe', 'Buenafe') + ')', 'yes', 'no'),
           G('Was the candidate elected President before, or did he succeed and serve more than four years?', 'Art. VII, Sec. 4: “not eligible for any reelection”; the successor’s four-year rule', 'Barred by Sec. 4', 'a non-immediate run by a former President was never ruled on (' + C('pormento', 'Pormento') + ')', 'yes', 'sun')],
          ('Qualified', 'winning never cures a missing qualification, and a challenge to it is not mooted by the votes (' + C('buenafe', 'Buenafe') + ')', 'ok'),
          facts=[fact('Buenafe v. COMELEC (2022)', 'Before the 2022 election, Marcos Jr.’s certificate of candidacy is challenged: his 1995 conviction for not filing income tax returns (fines only, final in 2001) allegedly carries perpetual disqualification and moral turpitude.', 'n,y,n,n', 'Not yet sworn in, so the Court rules; non-filing is not moral turpitude and the fallo imposed no perpetual disqualification: qualified.'),
                 fact('Pormento v. Estrada (2010)', 'Former President Estrada, elected in 1998 and out of office since 2001, files to run for President in 2010.', 'n,y,n,y?', 'The text bars “any reelection,” but the Court never decided whether that covers a non-immediate run: Estrada lost and the case became moot.'),
                 fact('Pamatong v. Duterte (2019)', 'Two years after the inauguration, a man whose own candidacy was rejected as a nuisance files quo warranto against the sitting President.', 'y', 'Too late and the wrong party: a private quo warranto needs a claim to the office and must be filed within one year.'),
                 fact('A young candidate', 'A senator who turns 40 a week after election day files a certificate of candidacy for President, stating that she is eligible.', 'n,n', 'Age is counted on the day of the election (Sec. 2). Not qualified; the false claim supports a Sec. 78 petition.')]),
    kind='gates', when='a presidential candidate’s eligibility is questioned: age, citizenship, residence, a criminal conviction, or a second run.',
    hook='<em>Who, what, when</em>: before the oath, the COMELEC and then the Court; after it, the PET. Constitution plus statute; the votes cure nothing.',
    oral='The issue is whether [the candidate] may be stopped from running for President. Article VII, Section 2 lists five qualifications, and in Buenafe v. COMELEC the Court held that statutory ineligibilities count as well, so a false claim of eligibility is a material misrepresentation; but the candidate there was qualified because the fallo imposed no perpetual disqualification. Here, [he has not yet taken his oath, so the case stays with the Court, and he meets all the qualifications], so the petition fails.',
    cap='Election does not waive a qualification; it only changes the forum once the winner is proclaimed, sworn in and seated.')

fig('16', 'after', '<h3 id="pres-priv">Privileges and salary</h3>\n', 'pressalary', 'The President’s pay: what Sec. 6 allows and what it proves',
    cmp(['The rule (Art. VII, Sec. 6)', 'What it means on a news card'], [
        ('Residence', 'an official residence', 'Malacañang is provided by the Constitution, not a perk granted by law'),
        ('Salary', 'determined by law; never decreased during the tenure', 'a pay cut cannot reach the incumbent'),
        ('Raise', 'takes effect only after the term of the incumbent who approved it', 'compare Congress: after the terms of all the Members who approved it (Art. VI, Sec. 10)'),
        ('Other income', 'no other emolument from the Government or any other source', 'the salary is the whole lawful income from office; wealth far beyond it is presumed ill-gotten (' + C('swissdeposits', 'Swiss deposits') + ')'),
        ('Ill-gotten wealth', 'RA 1379, Sec. 2: public officer + considerable acquisition in office + manifestly out of proportion', 'forfeited unless the officer proves lawful acquisition; assets abroad included (' + C('arelma', 'Arelma') + ')'),
    ]),
    kind='comparison', when='a news card mentions the President’s salary, a raise, gifts or side income, or a former President’s hidden wealth.',
    hook='<em>One salary, no extras</em>: no cut for the incumbent, no raise until the next term, and whatever exceeds the salary must be explained.',
    oral='The issue is whether [the raise] may apply to the incumbent President. Article VII, Section 6 provides that the President’s salary is fixed by law, may not be decreased during the tenure, and that an increase takes effect only after the term of the incumbent who approved it; the President may receive no other emolument. That is why, in the Swiss deposits case, the Marcoses’ salaries were their only lawful income, and wealth beyond them was presumed ill-gotten. Here, [the raise approved in 2026 takes effect only in 2028].',
    cap='Sec. 6 bars other emoluments “from the Government or any other source”; the 1935 and 1973 Constitutions also barred them, which is how the Court fixed the Marcoses’ lawful income.')

fig('16', 'after', '<h3 id="pres-succ">Succession, disability and serious illness</h3>\n', 'presvacancy', 'Who becomes, or acts as, President? Tap a stage', stepper([
    ('Before the term', 'z-a', N('Sec. 7: the VP-elect steps in', 'the President-elect fails to qualify, or no President is chosen: the VP-elect <em>acts as</em> President until one qualifies. The President-elect dies or is permanently disabled at the start of the term: the VP-elect <em>becomes</em> President. Neither chosen nor qualified, or both dead or disabled: the Senate President, or if unable the Speaker, <em>acts as</em> President.', 'acc')),
    ('Vacancy in office', 'z-b', N('Sec. 8: the VP becomes President', 'on the President’s death, permanent disability, removal or resignation, for the unexpired term. Resignation: intent plus acts of relinquishment, by the totality of the circumstances (' + C('estradaarroyo', 'Estrada v. Arroyo') + ').', 'acc')),
    ('VP office vacant', 'z-b', N('Sec. 9: the President nominates', 'a VP from among the Members of the Senate and the House, who takes office on confirmation by a majority of all the Members of both Houses, voting separately.', 'sun')),
    ('Both offices vacant', 'z-b', N('Secs. 8 and 10: someone acts; Congress calls an election', 'the Senate President (or the Speaker) acts as President. Congress convenes on the third day without a call and within seven days enacts a law calling a special election 45 to 60 days later; none if the vacancy is within 18 months of the next regular presidential election.', 'sun')),
    ('Temporary inability', 'z-a', N('Sec. 11: the VP acts as President', 'on the President’s own written declaration, or one by a majority of all the Cabinet. If the President contests the Cabinet, Congress decides by two-thirds of both Houses, voting separately. A late claim of inability can be overtaken by Congress’s recognition of a successor (' + C('estradaarroyo', 'Estrada') + ').', 'sun')),
    ('Serious illness', 'z-a', N('Sec. 12: the public is informed', 'the Cabinet members for national security and foreign relations and the AFP Chief of Staff keep access. The Office of the President chooses the means; no mandamus for the records (' + C('deleon', 'De Leon v. Duterte') + ').', 'acc'))], start=1),
    kind='stepper', when='a President resigns, dies, falls ill, is removed, or is said to be unable; or the VP office falls vacant.',
    hook='<em>Becomes for good, acts for a while.</em> Vacancy: the VP becomes President. Inability or failure to qualify: someone only acts.',
    oral='The issue is whether the Vice-President has become President or only acts as President. Under Article VII, Section 8, the Vice-President becomes President on the President’s death, permanent disability, removal or resignation; under Section 11, the Vice-President only acts as President during a temporary inability. In Estrada v. Arroyo, the Court held that resignation is shown by intent plus acts of relinquishment, judged by the totality of the circumstances. Here, [the President left the Palace, acknowledged his successor and spoke of his presidency in the past tense], so he resigned and the Vice-President is President.',
    cap='The Senate President and the Speaker only ever act as President; they never become President.')

fig('16', 'after', '<h3 id="pres-succ">Succession, disability and serious illness</h3>\n', 'resign', 'Has the office become vacant, or is the President only unable?',
    gates([G('Has the President died, become permanently disabled, been removed by impeachment, or resigned?', 'resignation: intent plus acts of relinquishment, in any form; no letter needed (totality test)', 'Vacancy: the VP becomes President', 'for the unexpired term (Sec. 8)', 'yes', 'acc'),
           G('Has the President, or a majority of all the Cabinet, sent a written declaration of inability to the Senate President and the Speaker?', 'no one else may declare it; a serious illness alone only triggers Sec. 12', 'No change: the President stays', 'and if seriously ill, the public must be informed (Sec. 12)', 'no', 'sun'),
           G('Has the President since declared in writing that no inability exists, and has that declaration stood?', 'it stands unless a Cabinet majority repeats its declaration within five days and Congress then finds inability by two-thirds of both Houses, voting separately (Sec. 11)', 'The President reassumes office', 'the VP’s acting term ends', 'yes', 'ok')],
          ('The VP acts as President', 'until the President transmits a written declaration to the contrary, or for as long as Congress finds him unable', 'sun'),
          facts=[fact('Estrada v. Arroyo (2001)', 'The AFP withdraws support; the President negotiates only the terms of his exit, says “Ayoko na,” leaves the Palace “for the sake of peace,” and acknowledges his successor’s oath. He later sends a letter claiming temporary inability.', 'y', 'Resignation by acts (totality test). The late inability letter changes nothing: Congress recognized Arroyo, a political question.'),
                 fact('De Leon v. Duterte (2020)', 'A citizen says the President is seriously ill and asks the Court to compel the release of his medical records; the President keeps holding meetings and televised addresses.', 'n,n', 'No declaration of inability, so the President stays; Sec. 12 leaves the means of disclosure to the Office of the President.'),
                 fact('A planned operation', 'Before surgery, the President sends the Senate President and the Speaker a written declaration that he is unable to discharge his duties; two weeks later he sends one saying he can.', 'n,y,y', 'Sec. 11: the VP acts as President only until the President’s written declaration to the contrary.'),
                 fact('A split Cabinet', 'A majority of the Cabinet declares the President unable; he answers in writing that he is fine; within five days the majority repeats its declaration. The Senate finds him unable by more than two-thirds, but the House vote falls short of two-thirds.', 'n,y,y', 'Inability must be found by two-thirds of both Houses, voting separately; one House is not enough, so the President continues.')]),
    kind='gates', when='a President is ill, hospitalized, absent, or has left the Palace, and someone asks who is in charge.',
    hook='<em>Gone or just away?</em> Death, disability, removal, resignation: vacancy. Only a written declaration makes the VP act.',
    oral='The issue is whether the presidency is vacant. Under Article VII, Section 8, the Vice-President becomes President upon the President’s resignation, among other causes, and in Estrada v. Arroyo the Court held that resignation needs no letter: intent plus acts of relinquishment suffice, judged by the totality of prior, contemporaneous and posterior acts. If there is no vacancy, the Vice-President acts as President only on a written declaration of inability under Section 11. Here, [apply].',
    cap='Congress is the judge of a contested inability (Sec. 11); Estrada treated its recognition of the successor as a political question.')

fig('16', 'after', '<h3 id="pres-prohib">Removal, prohibitions, and the ex officio exception</h3>\n', 'exofficio', 'May this official take the second post, and be paid for it?',
    gates([G('Is the official the President, the VP, a Cabinet member, or a deputy or assistant (Assistant Secretary and up)?', 'Art. VII, Sec. 13 covers the official family; alternates and representatives follow their principals', 'Art. IX-B, Sec. 7(2) instead', 'another office only if allowed by law or by the primary functions of the position', 'no', 'sun'),
           G('Does the Constitution itself provide for the second post?', 'the VP as a Cabinet member; the VP acting as President; the Secretary of Justice on the JBC', 'Allowed', 'Sec. 13’s own exceptions (' + C('clu', 'Civil Liberties Union') + ')', 'yes', 'ok'),
           G('Is it an ex officio post, provided by law and required (not merely allowed) by the primary functions of the office?', 'additional duties, not “any other office”', 'Prohibited', 'EO 284’s two extra posts were void (' + C('clu', 'Civil Liberties Union') + ')', 'no', 'no')],
          ('Allowed, but unpaid', 'no per diem, honorarium or allowance by any name, for the Secretary, the alternate or the representative (' + C('cruzcoa', 'Cruz') + '; ' + C('nacoa', 'NAC') + ')', 'sun'),
          facts=[fact('Civil Liberties Union (1991)', 'Under EO 284, a Secretary sits on two GOCC boards besides heading the department, and is paid by both.', 'y,n,n', 'Not provided by the Constitution and not required by the Secretary’s primary functions: prohibited.'),
                 fact('The Monetary Board', 'The Secretary of Finance sits on the Monetary Board, as the law provides.', 'y,n,y', 'Ex officio and required by the Finance Secretary’s functions: allowed, but with no extra pay.'),
                 fact('Cruz v. COA (2001)', 'A division chief sits on the NHA Board as the alternate of the Secretary of Labor and receives per diems.', 'y?,n,y', 'The alternate stands in the Secretary’s shoes: the post is allowed, but the per diems are disallowed; no better right than the principal.'),
                 fact('The VP in the Cabinet', 'The President appoints the Vice-President as Secretary of a department, without CA confirmation.', 'y,y', 'Art. VII, Sec. 3 allows it and requires no confirmation; Sec. 13’s “unless otherwise provided in this Constitution” covers it.'),
                 fact('A bureau director', 'A law names the director of a bureau, below Assistant Secretary, to the board of a GOCC in the same sector.', 'n', 'Not in the official family: Art. IX-B, Sec. 7(2) applies, and the law allows it.')]),
    kind='gates', when='a Cabinet member, undersecretary or assistant secretary is named to a GOCC board, a commission or a private post, or is paid for one.',
    hook='<em>By law, required, unpaid.</em> Miss one and the second hat comes off; alternates and representatives get nothing their principals cannot.',
    oral='The issue is whether [the Secretary] may hold the second post. Article VII, Section 13 bars Cabinet members and their deputies and assistants from holding any other office unless the Constitution provides otherwise, and in Civil Liberties Union v. Executive Secretary the Court held that this is stricter than the rule for other appointive officials. The only exception is an ex officio post, provided by law and required by the primary functions of the office, held without additional compensation. Here, [the post is not required by the Secretary’s functions], so it is prohibited.',
    cap='Sec. 13 reaches private offices too, and also bars practicing a profession, participating in business, and financial interests in government contracts or franchises.')

fig('16', 'after', '<h3 id="pres-exec">Executive power and the President’s residual powers</h3>\n', 'residual', 'Where does this presidential act get its power?',
    gates([G('Does a specific clause cover it?', 'control (Sec. 17), appointments, Commander-in-Chief, clemency, loans, treaties, the budget', 'Use that clause, with its limits', 'e.g., control for orders to executive offices (' + C('blaquera', 'Blaquera') + ')', 'yes', 'acc'),
           G('Does a statute delegate it?', 'the Administrative Code’s power to reorganize; the GAA; a calamity or environmental law', 'Delegated power', 'stay within the law and its standards (' + C('banda', 'Banda') + '; ' + C('zabal', 'Zabal') + ')', 'yes', 'ok'),
           G('Is it needed to execute the laws or protect the general welfare, without taking a power the Constitution gives another branch?', 'no lawmaking, no appropriation of new funds, no constituent power', 'Void', 'the President cannot guarantee amendments (' + C('northcotabato', 'North Cotabato') + ') or create offices that need a law', 'no', 'no')],
          ('Residual executive power', 'valid if factual bases support it (' + C('manglapus', 'Manglapus') + '), and only if it respects the Bill of Rights (' + C('biraogo', 'Biraogo') + ': equal protection)', 'ok'),
          facts=[fact('Marcos v. Manglapus (1989)', 'Amid coup attempts and insurgencies, President Aquino bars the dying former dictator and his family from returning.', 'n,n,y', 'No specific clause or statute; the residual power to protect the peace, with factual bases. Valid.'),
                 fact('Biraogo v. PTC (2010)', 'President Aquino creates a Truth Commission by executive order to investigate graft “during the previous administration,” funded from existing OP appropriations.', 'n,n,y', 'The faithful-execution clause supports a fact-finding body; but singling out one administration violates equal protection.'),
                 fact('North Cotabato (2008)', 'The peace panel initials a MOA-AD promising that the Constitution and laws will be amended to create an associative Bangsamoro entity.', 'n,n,n', 'Peace talks are a residual power, but guaranteeing amendments usurps constituent power: grave abuse.'),
                 fact('Banda v. Ermita (2010)', 'An executive order ends the National Printing Office’s monopoly and caps its budget at its income.', 'n?,y', 'The power to reorganize the Office of the President, delegated by the Administrative Code and the GAA, read with control: valid.')]),
    kind='gates', when='the President acts by executive order or proclamation with no obvious clause behind it: bars entry, creates a commission, negotiates peace, restructures an agency.',
    hook='<em>Clause, law, residue</em>: look for a specific grant, then a statute, then the residual power, and never past the Bill of Rights.',
    oral='The issue is whether the President has the power to [create the commission]. Article VII, Section 1 vests the executive power in the President, and in Marcos v. Manglapus the Court held that executive power is more than the sum of the powers enumerated. In Biraogo v. Philippine Truth Commission, the Court located the power to create a fact-finding body in the duty to ensure that the laws are faithfully executed, but struck down the order for singling out one administration. Here, [the body only gathers facts with existing funds, and it covers all similarly situated officials], so it is valid.',
    cap='Residual power answers “who may act”; the Bill of Rights still answers “how far.”')

fig('16', 'after', '<h3 id="pres-control">Control of the executive departments, and reorganization</h3>\n', 'ctrlsup', 'Control or supervision: what may the President do to this office?',
    cmp(['Control (Art. VII, Sec. 17)', 'General supervision (Art. X, Secs. 4 and 16)'], [
        ('Over whom', 'executive departments, bureaus and offices, and GOCCs and chartered agencies under them', 'local governments and autonomous regions'),
        ('What it allows', 'alter, modify, nullify or set aside the subordinate’s act and substitute the President’s judgment, motu proprio', 'see that the rules are followed; order work redone to conform; investigate and discipline as the law provides'),
        ('What it does not allow', 'creating offices (' + C('biraogo', 'Biraogo') + '); reaching bodies with fiscal autonomy (' + C('blaquera', 'Blaquera') + ')', 'laying down, changing or replacing the rules; withholding the IRA (' + C('pimentelaguirre', 'Pimentel v. Aguirre') + ')'),
        ('Through whom', 'the Secretaries, as alter egos (qualified political agency: ' + C('denr12', 'DENR v. DENR Region 12') + ')', 'directly, or through the DILG; provinces over component cities and municipalities'),
        ('Cases', C('blaquera', 'Blaquera') + ', ' + C('neacoa', 'NEA v. COA') + ', ' + C('hutchison', 'Hutchison') + ', ' + C('zabal', 'Zabal'), C('pimentelaguirre', 'Pimentel v. Aguirre') + '; the ' + C('zabal', 'Zabal') + ' dissent'),
    ]),
    kind='comparison', when='the President orders, reverses, caps or claws back something done by an agency, a GOCC or a local government.',
    hook='<em>Control substitutes; supervision only checks.</em> Departments are the President’s hands; LGUs answer to their voters.',
    oral='The issue is whether the President may [reverse the board’s award]. Article VII, Section 17 gives the President control of all executive departments, bureaus and offices: the power to alter or set aside a subordinate’s act and substitute his judgment, as in Blaquera v. Alcala. Over local governments, Article X, Section 4 gives only general supervision, which, under Pimentel v. Aguirre, lets him see that the rules are followed but not replace them. Here, [the SBMA is a chartered agency under the Office of the President], so the President may set the award aside.',
    cap='Book: control “is not absolute”: Congress may define the structure of the executive branch (Moran v. OP, 2014); but it cannot withdraw the control itself (NEA v. COA).')

fig('16', 'after', '<h3 id="pres-control">Control of the executive departments, and reorganization</h3>\n', 'reorg', 'Is this executive reorganization valid?',
    gates([G('Is the office part of the Executive?', 'not the Judiciary, Congress, a constitutional commission or another constitutional body', 'Beyond the President', 'only the Constitution or Congress can restructure it', 'no', 'no'),
           G('Does the order alter an existing office (abolish, merge, transfer, trim functions) rather than create a new public office?', 'reorganizing presupposes an existing structure', 'Not a reorganization', 'a new office needs a law; an ad hoc fact-finding body may rest on the faithful-execution clause (' + C('biraogo', 'Biraogo') + ')', 'no', 'sun'),
           G('Is there a statutory basis?', 'Administrative Code, Book III, Secs. 20 and 31; reorganization provisions in the GAA', 'Void', 'control alone does not authorize restructuring (Carpio, J., in ' + C('banda', 'Banda') + ')', 'no', 'no'),
           G('Was it done in good faith, for economy or efficiency?', 'bad faith: a mere change of names, claims of economy belied by funds, a purge; whoever alleges it must prove it', 'Void from the start', 'positions “abolished” to oust their holders are not abolished (Dario v. Mison)', 'no', 'no')],
          ('Valid reorganization', 'even if positions are lost; there is no vested right to an office (' + C('banda', 'Banda') + ')', 'ok'),
          facts=[fact('Banda v. Ermita (2010)', 'An executive order removes the National Printing Office’s exclusive jurisdiction over government printing (except election materials) and caps its budget at its income; employees fear abolition.', 'y,y,y,y', 'A lesser change within the power to reorganize the Office of the President; no bad faith proved. Valid.'),
                 fact('DENR v. DENR Region 12 (2003)', 'The DENR Secretary orders the regional offices moved to the regional center fixed by an executive order under the ARMM Organic Act.', 'y,y,y,y', 'The President’s power to reorganize, delegated to the Secretary as alter ego; timing is a matter of wisdom. Valid.'),
                 fact('Biraogo v. PTC (2010)', 'An executive order creates a new Truth Commission inside the Office of the President, citing the power to reorganize.', 'y,n', 'Creating an office is not reorganizing; the body stands only as a fact-finding body under the faithful-execution clause.'),
                 fact('Abolishing a commission', 'An executive order abolishes the Commission on Human Rights and transfers its functions to the DOJ.', 'n', 'A constitutional body is beyond the President’s power to reorganize.'),
                 fact('A purge', 'An executive order “abolishes” fifty positions and creates fifty new ones with the same duties and new names, filled by the President’s allies.', 'y,y,y,n', 'A change of nomenclature to oust incumbents is bad faith: the abolition is void.')]),
    kind='gates', when='an executive order abolishes, merges, transfers, renames or trims an agency, or employees say a “reorganization” is a disguised dismissal.',
    hook='<em>Executive, existing, authorized, honest</em>: four yeses and the reorganization stands.',
    oral='The issue is whether [the executive order] is a valid reorganization. The President may reorganize the Office of the President and the executive agencies under the control power and the continuing authority delegated by the Administrative Code and the appropriations laws, as held in Banda v. Ermita, which allowed even lesser changes to an agency’s functions; but the reorganization must be in good faith, and it cannot create a new office or reach constitutional bodies. Here, [the order trims an executive agency’s functions for efficiency and no bad faith is shown], so it is valid.',
    cap='Biraogo held PD 1416 functus officio; Banda rests on the Administrative Code and the GAAs instead.')

fig('16', 'after', '<h3 id="pres-lgu">General supervision over local governments and autonomous regions</h3>\n', 'lguorder', 'Can the President make the local government do this?',
    gates([G('Does the order only see that the LGU follows existing law?', 'calling attention to a violation; ordering an investigation; discipline as the law provides', 'Valid supervision', 'the President may check, not substitute judgment', 'yes', 'ok'),
           G('Does it touch the LGU’s share in national taxes?', 'automatic release (Art. X, Sec. 6); no lien or holdback for whatever purpose (LGC Sec. 286)', 'Void unless LGC Sec. 284 is met', 'unmanaged deficit, consultation with Congress’s leaders and the leagues, three Secretaries’ recommendation, never below 30% (' + C('pimentelaguirre', 'Pimentel v. Aguirre') + ')', 'yes', 'no'),
           G('Is it only advice, with no sanction for an LGU that does not follow?', 'a “commanding tone” is tolerated if nothing backs it up', 'Valid as an advisory', 'Sec. 1 of AO 372 survived this way (' + C('pimentelaguirre', 'Pimentel v. Aguirre') + ')', 'yes', 'sun')],
          ('Void: control in disguise', 'the President may not lay down, change or replace the LGU’s rules or withhold its powers', 'no'),
          facts=[fact('AO 372, Sec. 4 (1997)', 'The President withholds 10% of the LGUs’ internal revenue allotment pending a review of the fiscal situation.', 'n,y', 'A holdback, even if temporary; no deficit shown and no consultation with the leagues. Void.'),
                 fact('AO 372, Sec. 1 (1997)', 'The President “directs” LGUs to cut non-personal spending by 25%, with no penalty stated.', 'n,n,y', 'Valid only as an advisory; no sanction may be imposed on LGUs that ignore it.'),
                 fact('A road-clearing order', 'The DILG orders mayors to clear public roads as existing laws require and to report; it threatens administrative cases under the Local Government Code against those who refuse.', 'y?', 'Arguably supervision: it enforces existing law and uses the discipline the law provides. The mayor will say it dictates priorities.'),
                 fact('A budget order', 'The President orders every city to spend 30% of its budget on a national program, on pain of losing its share in national taxes.', 'n,y', 'It replaces the LGU’s own budget choices and backs them with a holdback: control, and void.')]),
    kind='gates', when='the President or a department tells LGUs to spend, cut, close, implement or report, or holds back their money.',
    hook='<em>Check, don’t replace; advise, don’t hold back.</em> The IRA goes out automatically.',
    oral='The issue is whether the President may [withhold part of the LGUs’ allotment]. Article X, Section 4 gives the President only general supervision over local governments, and in Pimentel v. Aguirre the Court held that supervision lets him see that the rules are followed but not replace them; the LGUs’ share is released automatically and may not be held back, even temporarily, unless the conditions of Section 284 of the Local Government Code are met. Here, [no deficit was declared and the leagues were not consulted], so the withholding is void.',
    cap='The same general supervision applies to autonomous regions (Art. X, Sec. 16).')


# =====================================================================
# 17 · appointment and clemency (finals; clemency first, Batch 6a)
# =====================================================================
fig('17', 'after', '<h3 id="appt-power">The appointing power and the Commission on Appointments</h3>\n', 'apptca', 'Does this appointment go to the Commission on Appointments?',
    gates([G('Does the Constitution provide another route for this office?', 'Justices and judges, the Ombudsman and Deputies: from a JBC list (Art. VIII, Sec. 9; Art. XI, Sec. 9); the VP as a Cabinet member (Art. VII, Sec. 3)', 'No CA confirmation', 'the Constitution itself dispenses with it', 'yes', 'acc'),
           G('Is the officer in the first sentence of Sec. 16?', 'department heads; ambassadors, ministers, consuls; AFP officers from colonel or naval captain; officers the Constitution vests in the President (commissioners, regular JBC members)', 'No CA confirmation', 'groups two to four; a law adding the CA is void (' + C('calderon', 'Calderon') + '; ' + C('manalo', 'Manalo') + ')', 'no', 'ok'),
           G('Is Congress in session?', 'a recess, voluntary or compulsory, allows an ad interim appointment', 'Ad interim appointment', 'effective at once and permanent; ends on CA disapproval or the next adjournment; a by-passed one may be renewed (' + C('matibag', 'Matibag') + ')', 'no', 'sun')],
          ('Nominate, then CA consent, then appoint', 'meanwhile, an acting appointee may serve, up to a year (' + C('pimentelermita', 'Pimentel v. Ermita') + ')', 'acc'),
          facts=[fact('Sarmiento III v. Mison (1987)', 'The President appoints the Commissioner of Customs, a bureau head, without sending the name to the CA.', 'n,n', 'Not in the first sentence; the framers deleted “and bureaus.” No confirmation needed.'),
                 fact('Manalo v. Sistoza (1999)', 'RA 6975 requires CA confirmation for police directors; the President promotes 15 officers without it.', 'n,n', 'Police ranks are not “officers of the armed forces,” and Congress cannot add to the list.'),
                 fact('Soriano III v. Lista (2003)', 'Coast Guard officers are promoted to admiral and naval captain after the Coast Guard is moved to the DOTC.', 'n,n', 'No longer part of the AFP: no confirmation.'),
                 fact('Pimentel v. Ermita (2005)', 'While Congress is in session, the President names eight acting department secretaries.', 'n,y,y', 'A department head needs CA consent for a permanent appointment, but an acting appointment is valid meanwhile.'),
                 fact('Matibag v. Benipayo (2002)', 'During a recess, the President appoints three COMELEC members, ad interim.', 'n,y,n', 'Commissioners are vested in the President by the Constitution; during the recess, an ad interim appointment takes effect at once.'),
                 fact('A new Associate Justice', 'The President appoints a Justice from the JBC’s list.', 'y', 'Art. VIII, Sec. 9: no confirmation needed.')]),
    kind='gates', when='a news card asks whether an appointee must face the Commission on Appointments, or a law tries to require it.',
    hook='<em>Four groups, one door</em>: only the first sentence goes to the CA; the JBC route skips it; a recess allows ad interim.',
    oral='The issue is whether [the appointee] needs the consent of the Commission on Appointments. Article VII, Section 16 requires consent only for the first group: heads of executive departments, ambassadors, other public ministers and consuls, officers of the armed forces from colonel or naval captain, and officers whose appointments the Constitution vests in the President. In Sarmiento III v. Mison the Court held that all other appointments need no confirmation, and in Calderon v. Carale that Congress cannot add to the list. Here, [the officer is appointed under a statute], so no confirmation is needed.',
    cap='Rank titles do not decide it: the officer must be in the armed forces to be an “officer of the armed forces” (Manalo; Soriano).')

fig('17', 'after', '<h3 id="appt-kinds">Regular, ad interim and acting appointments</h3>\n', 'apptkinds', 'Regular, ad interim, acting: side by side',
    cmp(['Regular', 'Ad interim', 'Acting'], [
        ('When', 'while Congress is in session', 'during a recess of Congress', 'whenever there is a vacancy'),
        ('Takes effect', 'after CA consent', 'at once, on qualifying', 'at once'),
        ('CA', 'consent first', 'submitted; consent or disapproval follows', 'not submitted'),
        ('Nature', 'permanent', 'permanent (' + C('matibag', 'Matibag') + ')', 'temporary, at pleasure'),
        ('Ends', 'by removal for cause, end of term', 'CA disapproval, or the next adjournment (by-pass: may be renewed)', 'at the President’s pleasure; at most one year (' + C('pimentelermita', 'Pimentel v. Ermita') + '; ' + C('urro', 'Urro') + ')'),
        ('Barred for', '—', 'nothing; valid even for constitutional commissioners', 'constitutional commissioners (Art. IX-B to D) and offices repugnant to it'),
    ]),
    kind='comparison', when='the President names someone “acting,” “OIC” or “ad interim,” or keeps renewing a by-passed appointment.',
    hook='<em>Ad interim is permanent; acting is temporary.</em> Recess decides ad interim; a vacancy is enough for acting.',
    oral='The issue is whether [the appointment] is valid without the Commission on Appointments. An ad interim appointment, made during a recess, is permanent and takes effect at once, as Matibag v. Benipayo held; an acting appointment may be made even while Congress is in session, for up to a year, as Pimentel v. Ermita held, but it gives no security of tenure. Here, [the President named an acting secretary pending a permanent appointment], so it is valid.',
    cap='Appointments that need no CA are, strictly, neither regular nor ad interim (General v. Urro; the professor’s book).')

fig('17', 'after', '<h3 id="appt-midnight">The election ban on appointments (“midnight appointments”)</h3>\n', 'midnight', 'Is this a void midnight appointment?',
    gates([G('Was it made by the President or an Acting President?', 'Sec. 15 binds no one else', 'Sec. 15 does not apply', 'a mayor may appoint until the last day (' + C('derama', 'De Rama') + ')', 'no', 'ok'),
           G('Is it to the Judiciary?', 'the Supreme Court and the lower courts', 'The ban does not apply', 'JBC list; fill within 90 days (' + C('decastrojbc', 'De Castro') + ')', 'yes', 'ok'),
           G('Were all four steps complete before the ban?', 'signed, transmitted, to a vacant post, received and accepted (oath or assumption) before the two months before the presidential election', 'Valid', 'made outside the prohibited period (' + C('garafil', 'Velicaria-Garafil') + ')', 'yes', 'ok'),
           G('Is it a temporary appointment to an executive post, because a continued vacancy would prejudice public service or endanger public safety?', 'the only exception in Sec. 15', 'Allowed', 'temporary only', 'yes', 'sun')],
          ('Void midnight appointment', 'whatever the merit or motive; a successor may revoke it (EO 2 upheld)', 'no'),
          facts=[fact('Velicaria-Garafil (2015)', 'Appointment papers are dated March 1 to 5, 2010, but reach the Records Office in May; the appointees take their oaths after the March 11 cut-off.', 'y,n,n,n', 'Transmittal and acceptance fell inside the ban: void.'),
                 fact('De Rama v. CA (2001)', 'A mayor who lost re-election appoints 14 employees in her last month; her successor recalls them.', 'n', 'Sec. 15 covers only the President; the completed appointments stand.'),
                 fact('De Castro v. JBC (2010)', 'The Chief Justice retires a week after the presidential election; the outgoing President wants to appoint the successor.', 'y,y', 'The ban does not reach the Judiciary.'),
                 fact('An acting police chief', 'During the ban, the national police chief dies; the President names an officer-in-charge to keep order.', 'y,n,n,y', 'A temporary executive appointment for public safety: the exception.'),
                 fact('Done in time', 'An undersecretary’s appointment is signed, released through the Records Office, and accepted by oath three weeks before the ban.', 'y,n,y', 'All four elements were complete before the ban: valid.')]),
    kind='gates', when='an outgoing President, or a losing local official, makes appointments near the end of the term; or a new President revokes them.',
    hook='<em>President only, judges excepted, all four steps before the cut-off</em>, unless temporary for public service or safety.',
    oral='The issue is whether [the appointment] is a prohibited midnight appointment. Article VII, Section 15 bars the President from making appointments two months before the next presidential election until the end of the term, except temporary executive appointments needed for public service or safety. In Velicaria-Garafil v. Office of the President, the Court held that an appointment is a process that must be complete, including transmittal and acceptance, before the ban; De Castro v. JBC adds that the ban does not apply to the Judiciary. Here, [the appointee took the oath after the cut-off], so the appointment is void.',
    cap='Sec. 15 removed Aytona’s case-by-case inquiry into bad faith: inside the period, the appointment is void (Brion, J., agreed on this much in Garafil).')

fig('17', 'after', '<h3 id="appt-terms">Fixed terms in the constitutional offices</h3>\n', 'terms', 'How long may this appointee serve?',
    gates([G('Is the office the Ombudsman or a Deputy Ombudsman?', 'not a constitutional commission; equated only in rank and salary (Art. XI, Sec. 10)', 'A full seven years from appointment', 'even when filling a vacancy (' + C('ifurung', 'Ifurung') + ')', 'yes', 'acc'),
           G('Has the appointee already served in the same commission under a confirmed appointment?', 'a lapsed ad interim appointment is not a term (' + C('matibag', 'Matibag') + ')', 'Seven years in all, at most', 'no return after a full term; a promotion only into a seat vacated by death, resignation, disability or impeachment (' + C('funavillar', 'Funa v. Villar') + ')', 'yes', 'sun'),
           G('Did the vacancy arise from the expiration of the predecessor’s term?', 'terms run in the February 2, 1987 cycle (' + C('gaminde', 'Gaminde') + ')', 'A full seven-year term in the cycle', 'no shorter term: the President cannot split terms; a late appointment loses the gap', 'yes', 'acc')],
          ('Only the unexpired portion', 'of the predecessor’s term, no less (Art. IX, Sec. 1(2))', 'acc'),
          facts=[fact('Funa v. Villar (2012)', 'A COA Commissioner in his fourth year is appointed Chairman when the Chairman’s term expires.', 'n,y', 'A full term would exceed seven years in all, and a shorter one would split the term: void.'),
                 fact('Gaminde v. COA (2000)', 'A CSC Commissioner appointed in 1993 to the seat whose term began February 2, 1992 claims to serve until 2000.', 'n,n,y', 'The term ran in the cycle, to February 2, 1999; the late start is counted against her.'),
                 fact('Matibag v. Benipayo (2002)', 'On February 2, 2001, three COMELEC terms expire; the President appoints new members ad interim until February 2, 2008.', 'n,n,y', 'Full seven-year terms in the cycle; renewals after by-passes keep the same end date.'),
                 fact('Ifurung (2018)', 'An Ombudsman resigns mid-term; her successor is appointed in 2011.', 'y', 'A full seven years from 2011, not the rest of the predecessor’s term.'),
                 fact('A commissioner dies', 'A COMELEC Commissioner dies three years into his term; the President appoints a replacement.', 'n,n,n', 'Only the four remaining years.')]),
    kind='gates', when='a news card asks when a commissioner’s or Ombudsman’s term ends, or a commissioner is promoted to chair.',
    hook='<em>Commissions run on the February 2 clock; the Ombudsman starts a fresh seven.</em> Seven years in all, and no split terms.',
    oral='The issue is how long [the new commissioner] may serve. Under Article IX-D, Section 1(2), an appointment to a vacancy is only for the unexpired portion, and in Funa v. Villar the Court held that a seat vacated by expiration needs a full seven-year appointment, that no one may serve more than seven years in all, and that the President cannot split terms; Gaminde v. COA fixes the cycle from February 2, 1987. Here, [the predecessor resigned], so the appointee serves only the unexpired portion.',
    cap='The Ombudsman is the exception: a full seven years from appointment (Ifurung).')

fig('17', 'after', '<h3 id="appt-removal">The power to remove</h3>\n', 'removal', 'Can the President remove this official?',
    gates([G('Is the official impeachable?', 'the President, the VP, Supreme Court Justices, constitutional commissioners, the Ombudsman (Art. XI, Sec. 2)', 'Only by impeachment', 'the President cannot remove them', 'yes', 'no'),
           G('Is the official in an office the Constitution makes independent?', 'a Deputy Ombudsman shares the Ombudsman’s independence; the Special Prosecutor does not', 'Not by the President', 'the Ombudsman disciplines her deputies (' + C('gonzalesiii', 'Gonzales III') + ', 2014)', 'yes', 'no'),
           G('Does the official serve at pleasure?', 'acting, coterminous, primarily confidential, non-career', 'Removable at will', 'separation is expiration, not removal (' + C('urro', 'Urro') + ')', 'yes', 'ok')],
          ('Removable for cause only, with due process', 'the power to remove comes with the power to appoint, but security of tenure limits it; a good-faith reorganization may abolish the post (' + C('larin', 'Larin') + ')', 'sun'),
          facts=[fact('Gonzales III (2014)', 'The Office of the President dismisses a Deputy Ombudsman over the delay in a hostage-taker’s case.', 'n,y', 'Sec. 8(2) is void as to Deputies: the President has no disciplinary power over them.'),
                 fact('Larin v. Executive Secretary (1997)', 'The President dismisses a BIR Assistant Commissioner, a career executive, on the strength of a conviction later reversed.', 'n,n,n', 'Removable only for cause; with the acquittal, no cause remained.'),
                 fact('General v. Urro (2011)', 'An acting NAPOLCOM commissioner is replaced by a new appointee.', 'n,n,y', 'An acting appointee serves at pleasure; no quo warranto.'),
                 fact('The Special Prosecutor', 'The Office of the President opens a case against the Special Prosecutor over a plea bargain.', 'n,n,n', 'Sec. 8(2) stays valid as to the Special Prosecutor (8–7): removable for cause after due process.'),
                 fact('The Ombudsman', 'The President announces he is removing the Ombudsman.', 'y', 'The Ombudsman is impeachable: only Congress can remove her.')]),
    kind='gates', when='the President fires, suspends or replaces an official, or “reorganizes” an office out from under its people.',
    hook='<em>Appoint, then remove, unless impeachable, independent, or tenured.</em>',
    oral='The issue is whether the President may remove [the official]. The power to remove is generally implied from the power to appoint, but it yields where the Constitution protects the office: in Gonzales III v. Office of the President, the Court held that the President cannot discipline a Deputy Ombudsman because that would impair the Ombudsman’s independence; and under Larin v. Executive Secretary, a career officer may be removed only for cause and with due process. Here, [the official is a Deputy Ombudsman], so the President cannot remove him.',
    cap='The 2026 Carandang decision applied Gonzales III to an Overall Deputy Ombudsman.')

fig('17', 'after', '<h3 id="appt-clemency">The clemency power and its limits</h3>\n', 'pardonvalid', 'Is this pardon valid, and what does it restore?',
    gates([G('Is it an impeachment case?', 'the President cannot undo a Senate judgment of removal and disqualification', 'Void', 'Art. VII, Sec. 19: “except in cases of impeachment”', 'yes', 'no'),
           G('Is there a conviction by final judgment?', 'no pending appeal; a pardon during appeal is void (People v. Casido); amnesty is the exception', 'Void', 'the 1987 Constitution restored the final-judgment rule that the 1981 amendment had dropped (' + C('monsanto', 'Monsanto') + ')', 'no', 'no'),
           G('Is it for an election offense, without the COMELEC’s favorable recommendation?', 'Art. IX-C, Sec. 5 covers pardon, amnesty, parole and suspension of sentence', 'Void', 'the third constitutional limit (' + C('risosvidal', 'Risos-Vidal') + ')', 'yes', 'no'),
           G('Does it restore civil and political rights, or expressly the rights to vote and hold office?', 'RPC Arts. 36 and 41, harmonized with the Constitution', 'Valid, but the accessory disqualifications stay', 'pardoning the principal penalty alone does not remit them', 'no', 'sun')],
          ('Valid: the right to vote and run is restored', 'but not the forfeited office, backpay, civil liability or reputation (' + C('monsanto', 'Monsanto') + '); Congress cannot add limits (' + C('cristobal', 'Cristobal') + ')', 'ok'),
          facts=[fact('Risos-Vidal v. COMELEC (2015)', 'Estrada, finally convicted of plunder, is pardoned: “He is hereby restored to his civil and political rights.” A whereas clause notes his promise not to run again; he runs for Mayor of Manila.', 'n,y,n,y', 'Within the limits, and the rights are restored expressly enough; the whereas clause is not a condition. He may run.'),
                 fact('A pardon pending appeal', 'While a convicted official’s appeal is pending, the President pardons him, and he is released.', 'n,n', 'No final judgment: the pardon is void, and those who released him may be administratively liable.'),
                 fact('An election offender', 'A mayor convicted of vote-buying is pardoned without any COMELEC recommendation.', 'n,y,y', 'Art. IX-C, Sec. 5 requires the COMELEC’s favorable recommendation: void.'),
                 fact('A removed Chief Justice', 'After the Senate convicts and removes an impeached official, the President “pardons” him so he may hold office again.', 'y', 'The President cannot pardon in cases of impeachment.'),
                 fact('A bare pardon', 'A convict serving reclusion perpetua is pardoned “of the penalty of reclusion perpetua,” with nothing on his rights; he later runs for councilor.', 'n,y,n,n', 'The perpetual absolute disqualification is an accessory penalty not remitted: he still cannot run.')]),
    kind='gates', when='a pardoned or about-to-be-pardoned person wants release, the right to vote or run, or an old office back.',
    hook='<em>No impeachment, no appeal pending, no election offense without COMELEC.</em> Then say the rights, or the disqualification stays.',
    oral='The issue is whether [the pardon] is valid and restores [the right to run]. Article VII, Section 19 allows pardons after conviction by final judgment, except in impeachment cases, and Article IX-C, Section 5 bars pardons for election offenses without the COMELEC’s favorable recommendation; in Risos-Vidal v. COMELEC the Court held that Congress cannot add limits, and that a pardon restoring “civil and political rights” restores the right to seek office. Here, [the conviction is final and the pardon restores his political rights], so he may run.',
    cap='The President may also commute, reprieve, and remit fines and forfeitures under the same limits.')

fig('17', 'after', '<h3 id="appt-pardon">Pardon: what it does and what it does not</h3>\n', 'clemkinds', 'Pardon or amnesty: side by side',
    cmp(['Pardon', 'Amnesty'], [
        ('Who', 'the President alone', 'the President, with the concurrence of a majority of all the Members of Congress'),
        ('When', 'after conviction by final judgment', 'before charges, during trial, or after conviction'),
        ('For whom', 'an individual, for any offense (save the limits)', 'classes of persons, usually for political offenses'),
        ('Nature', 'a private act: pleaded and proved; must be accepted', 'a public act: courts take judicial notice'),
        ('Looks', 'forward: forgives the punishment', 'backward: erases the offense (' + C('barrioquinto', 'Barrioquinto') + ')'),
        ('Office and suffrage', 'restored only if the pardon restores them (RPC Art. 36; ' + C('risosvidal', 'Risos-Vidal') + ')', 'restored with the offense erased'),
        ('Civil liability', 'never remitted (Art. 36)', 'liability to private persons may survive'),
        ('Admission', 'not required (granted after conviction)', 'required: admit the acts and that they were criminal (' + C('vera63', 'Vera') + '; ' + C('trillanesmedialdea', 'Trillanes') + ')'),
        ('Undoing it', 'a conditional pardon: recommitment on breach (' + C('torresgonzales', 'Torres') + ')', 'revocation needs Congress too (' + C('trillanesmedialdea', 'Trillanes') + ')'),
    ]),
    kind='comparison', when='a news card mixes up pardon and amnesty, or asks what a grant of clemency does to office, votes and money.',
    hook='<em>Pardon forgives; amnesty forgets.</em> One person, the President alone, after final judgment; or a class, with Congress, any time.',
    oral='The issue is whether [the grant] is a pardon or an amnesty. Under Article VII, Section 19, a pardon is granted by the President alone after conviction by final judgment, while an amnesty needs the concurrence of a majority of all the Members of Congress; in Barrioquinto v. Fernandez the Court explained that a pardon looks forward and forgives the punishment, while an amnesty looks backward and erases the offense. Here, [the grant covers a class of rebels and was concurred in by Congress], so it is an amnesty.',
    cap='Monsanto: pardon “involves forgiveness and not forgetfulness”; it does not restore the forfeited office, backpay, or reputation.')

fig('17', 'after', '<h3 id="appt-conditional">Conditional pardon and its breach</h3>\n', 'condpardon', 'A condition is broken: can the convict be sent back?',
    gates([G('Did the convict accept the conditional pardon?', 'a pardon is a deed; delivery is not complete without acceptance', 'No pardon in force', 'he serves his sentence as before', 'no', 'sun'),
           G('Has the President found that a condition was broken?', 'his judgment, under RAC Sec. 64(i); a court conviction is not needed', 'The pardon stands', 'the convict stays free', 'no', 'ok'),
           G('Did the President proceed under RAC Sec. 64(i)?', 'the choice of road is the President’s and is not reviewable', 'Recommitment', 'to serve the remitted part of the original sentence; new crimes still need final convictions (' + C('torresgonzales', 'Torres') + ')', 'yes', 'acc')],
          ('Art. 159 prosecution', 'violating a conditional pardon is a crime; charge, trial and conviction by final judgment first', 'sun'),
          facts=[fact('Torres v. Gonzales (1987)', 'A convict pardoned on condition that he “not again violate any of the penal laws” is charged with 20 counts of estafa and convicted of sedition by a trial court (on appeal). The President cancels the pardon and he is recommitted.', 'y,y,y', 'Sec. 64(i): no final conviction needed; due process was had at the original trial.'),
                 fact('Charges dropped', 'A pardoned convict’s new case is provisionally dismissed for want of a witness; the Board still recommends, and the President orders, his recommitment.', 'y,y,y', 'As in Espuelas: the President’s finding of breach controls; the dismissal does not bind him.'),
                 fact('The court route', 'Prosecutors file an information for violation of a conditional pardon under RPC Art. 159.', 'y,y,n', 'The judicial road: he cannot suffer the Art. 159 penalty until convicted by final judgment.'),
                 fact('An unaccepted grant', 'A prisoner refuses a pardon conditioned on leaving the country.', 'n', 'A conditional pardon binds only if accepted; he stays in prison under his sentence.')]),
    kind='gates', when='a pardoned or paroled person is rearrested for breaking a condition, before any new conviction.',
    hook='<em>Two roads back to prison</em>: the President’s word (Sec. 64(i), no conviction needed) or the court’s judgment (Art. 159).',
    oral='The issue is whether [the convict] may be recommitted without a new conviction. In Torres v. Gonzales, the Court held that when a conditional pardon is breached, the President may proceed under Section 64(i) of the Revised Administrative Code and recommit the convict on his own finding, without any judicial conviction, because due process is not always judicial process and the convict had his day in court on the original crime; only a prosecution under Article 159 needs a final conviction. Here, [the President cancelled the pardon under Section 64(i)], so the recommitment is valid.',
    cap='Cruz, J., dissenting in Torres: “it is the conviction that makes him a criminal.” Use it for the other side.')

fig('17', 'after', '<h3 id="appt-amnesty">Amnesty: claiming it and revoking it</h3>\n', 'amnestygate', 'Can this person claim the amnesty, and can it be taken back?',
    gates([G('Did Congress concur, by a majority of all its Members?', 'Art. VII, Sec. 19, par. 2; the proclamation is the operative grant', 'No amnesty', 'the President alone cannot grant it', 'no', 'no'),
           G('Is the act within the proclamation’s class, period and crimes?', 'not excluded crimes or acts for personal ends; a guerrilla rivalry killing is outside (' + C('vera63', 'Vera') + ')', 'Not covered', 'the case goes on in the regular courts', 'no', 'no'),
           G('Did the applicant admit the covered acts and that they were criminal?', 'amnesty presupposes a crime; a specific crime need not be admitted (' + C('trillanesmedialdea', 'Trillanes') + ')', 'No amnesty', 'one who denies the act “cannot have any use for amnesty” (' + C('vera63', 'Vera') + ')', 'no', 'no'),
           G('Is a later President revoking it without Congress’s concurrence?', 'and is it final, with the case dismissed on that ground?', 'Revocation void; the amnesty stands', 'needs Congress; and due process, equal protection, ex post facto, double jeopardy (' + C('trillanesmedialdea', 'Trillanes') + ')', 'yes', 'sun')],
          ('Amnesty stands', 'the offense is erased (RPC Art. 89); a dismissal on that ground bars a new prosecution', 'ok'),
          facts=[fact('Trillanes v. Medialdea (2024)', 'Under a 2010 proclamation concurred in by Congress, a senator who led two mutinies files an application admitting his involvement violated the law; his cases are dismissed. In 2018, a new President voids his amnesty alone.', 'y,y,y,y', 'Revocation without Congress is void, and the proclamation violated four Bill of Rights guarantees.'),
                 fact('Vera v. People (1963)', 'Guerrillas accused of killing a rival guerrilla officer invoke the war amnesty but deny the killing; the motive was rivalry between units.', 'y,n', 'Not in furtherance of the resistance; and having denied the act, they could not claim amnesty anyway.'),
                 fact('Barrioquinto v. Fernandez (1949)', 'Accused guerrillas say another man fired the shot but ask for amnesty; the Commission refuses because they admitted nothing.', 'y,y?,n', 'The 1949 Court said no admission was needed; under Vera, today, the claim fails.'),
                 fact('A peace-deal amnesty', 'Congress concurs in an amnesty for rebels who return to the fold; a rebel admits his acts and that they were crimes, and no one tries to revoke it.', 'y,y,y,n', 'He may claim it; his criminal liability is extinguished.')]),
    kind='gates', when='a President grants, denies or revokes amnesty for rebels, mutineers or political offenders.',
    hook='<em>Congress in, admit it, and Congress again to undo it.</em>',
    oral='The issue is whether the President may revoke [the amnesty]. Article VII, Section 19 lets the President grant amnesty only with the concurrence of a majority of all the Members of Congress, and in Trillanes IV v. Medialdea the Court held that revocation likewise needs that concurrence, and struck down a proclamation that voided one grantee’s amnesty for violating due process, equal protection, the ban on ex post facto laws and double jeopardy. Here, [the President acted alone, years after the grant became final], so the revocation is void.',
    cap='Vera answers who may claim; Trillanes answers how much admission is enough and who may take it back.')


# =====================================================================
# 18 · Commander-in-Chief, other powers, the Vice-President (finals, Batch 7)
# =====================================================================
fig('18', 'after', '<h3 id="cinc-callout">The Commander-in-Chief and the calling-out power</h3>\n', 'cincpowers', 'Three Commander-in-Chief powers, side by side',
    cmp(['Calling out', 'Suspending the writ', 'Martial law'], [
        ('Ground', 'lawless violence, invasion or rebellion, “whenever it becomes necessary”', 'actual invasion or rebellion, when public safety requires it', 'the same'),
        ('Time limit', 'none', '60 days; Congress may extend on the President’s initiative', 'the same'),
        ('Report to Congress', 'none', 'within 48 hours', 'the same'),
        ('Congress', 'no role', 'may revoke (voting jointly, majority of all) at any time, on any ground', 'the same'),
        ('The Court', 'grave abuse only; the petitioner proves no factual basis (' + C('ibpzamora', 'IBP v. Zamora') + ')', 'sufficiency of the factual basis, on any citizen’s petition, within 30 days (' + C('lagman17', 'Lagman') + ')', 'the same'),
        ('Effect', 'troops assist the police; no new power (' + C('sanlakas', 'Sanlakas') + ')', 'no habeas corpus for persons judicially charged with rebellion or invasion offenses; charge within 3 days or release', 'the Constitution, civil courts and legislatures keep working; no military trial of civilians where courts function (' + C('olaguer', 'Olaguer') + '); the writ is not automatically suspended'),
    ]),
    kind='comparison', when='a President deploys troops, declares a “state” of something, suspends the writ or declares martial law, and you must say which power it is and what checks apply.',
    hook='<em>Call, suspend, declare</em>: the higher the power, the more checks; none of them suspends the Constitution.',
    oral='The issue is which Commander-in-Chief power [the President] used and what it allows. Article VII, Section 18 grants graduated powers: calling out the armed forces whenever necessary, and, only in case of actual invasion or rebellion when public safety requires it, suspending the writ or declaring martial law for up to 60 days. In Sanlakas v. Executive Secretary and David v. Macapagal-Arroyo the Court held that a declaration adds no power and that a calling-out cannot be used to exercise greater powers. Here, [the President only deployed troops against lawless violence], so it is a valid calling-out that needs no report to Congress.',
    cap='The graduation is in scope, not sequence: the President may go straight to martial law if its grounds exist (Lagman, 2017).')

fig('18', 'after', '<h3 id="cinc-callout">The Commander-in-Chief and the calling-out power</h3>\n', 'callout', 'Is this calling-out valid?',
    gates([G('Does the act go beyond calling out: decrees, a takeover of businesses, arrests or searches outside the Rules of Court?', 'PP 1017’s “decrees … promulgated by me”; Art. XII, Sec. 17 takeovers; warrantless arrests without a Rule 113 ground', 'That part is void', 'the President cannot legislate, and a takeover needs a law (' + C('davidgma', 'David') + ')', 'yes', 'no'),
           G('Is the military put above the civilian authorities?', 'civilian supremacy (Art. II, Sec. 3): who commands the operation?', 'Void', 'the police must stay in command; soldiers exercise no compulsory power over civilians (' + C('ibpzamora', 'IBP v. Zamora') + ')', 'yes', 'no'),
           G('Has the petitioner shown the President’s judgment was totally without factual basis?', 'grave abuse is the only ground; intelligence reports usually suffice; necessity is the President’s call', 'Void for grave abuse', 'the Court has not yet so found', 'yes', 'no')],
          ('Valid calling-out', 'no report, no time limit, no act of Congress; a “state of rebellion” label adds nothing (' + C('sanlakas', 'Sanlakas') + ')', 'ok'),
          facts=[fact('IBP v. Zamora (2000)', 'President Estrada orders Marines to join police patrols in Metro Manila to curb crime; the police command the task force.', 'n,n,n', 'Within his judgment, and civilian supremacy was kept.'),
                 fact('Sanlakas (2004)', 'After the Oakwood mutiny, the President declares a state of rebellion and calls out the AFP, then lifts it.', 'n,n,n', 'Valid, though the declaration is a superfluity.'),
                 fact('Ampatuan v. Puno (2011)', 'After the Maguindanao massacre, troops are called out in three areas under a state of emergency.', 'n,n,n', 'The feuding clans’ armed followers gave a factual basis.'),
                 fact('David (2006)', 'A proclamation calls out the AFP and orders it to enforce “all decrees … promulgated by me”; a professor is arrested at a rally without a warrant.', 'y', 'Valid as a calling-out only; the decrees clause and the arrest were void.'),
                 fact('Soldiers in charge', 'Soldiers are sent to run city checkpoints on their own and to arrest violators, with no police officer in command.', 'n,y?', 'Arguable, but civilian supremacy points to the police staying in charge.')]),
    kind='gates', when='troops are deployed against crime, unrest or violence, or a President declares a “state of emergency” or “state of rebellion.”',
    hook='<em>Necessary, civilian-led, nothing more</em>: calling out needs only necessity, but it adds no power.',
    oral='The issue is whether [the deployment] is a valid exercise of the calling-out power. Under Article VII, Section 18, the President may call out the armed forces whenever it becomes necessary to prevent or suppress lawless violence, invasion or rebellion; in IBP v. Zamora the Court held that this judgment is reviewable only for grave abuse, which the petitioner must prove, and that civilian supremacy holds while the police stay in command. Here, [the Marines only assist police patrols under police command], so the deployment is valid.',
    cap='Ampatuan adds that a calling-out is not an exercise of emergency powers, so it needs no law.')

fig('18', 'after', '<h3 id="cinc-ml">Martial law and the writ: grounds, limits and the civil courts</h3>\n', 'mldetain', 'A detainee under martial law: what protects him?',
    gates([G('Is a civilian being tried by a military tribunal while the civil courts are open?', 'Sec. 18, par. 4', 'Void trial', 'military courts have no jurisdiction over civilians where civil courts function (' + C('olaguer', 'Olaguer') + ')', 'yes', 'no'),
           G('Is he held under the final judgment of a competent court?', 'habeas corpus is not a writ of error', 'Habeas corpus only on three grounds', 'a denied constitutional right, no jurisdiction, or an excessive penalty (' + C('devilla', 'De Villa') + ')', 'yes', 'sun'),
           G('Has the privilege of the writ been suspended?', 'martial law alone does not suspend it', 'Habeas corpus lies', 'the jailer must justify the detention', 'no', 'acc'),
           G('Is he judicially charged with rebellion or an offense inherent in or directly connected with invasion?', 'the suspension covers no one else', 'Habeas corpus lies', 'the suspension does not reach him', 'no', 'acc'),
           G('Was he charged within three days of his arrest?', 'Sec. 18, last paragraph', 'He must be released', 'the detention has become illegal', 'no', 'no')],
          ('Detention continues; no habeas corpus for now', 'but the Bill of Rights, counsel and the courts still work, and the arrest needed a warrant or a Rule 113 ground', 'sun'),
          facts=[fact('Olaguer (1987)', 'Civilians accused of plotting to kill the President are tried by a military commission while the civil courts are open, and sentenced to death.', 'y', 'Void: no military jurisdiction over civilians while the civil courts function.'),
                 fact('In re De Villa (2004)', 'A convict whose rape conviction is final petitions for habeas corpus, citing DNA tests showing he did not father the victim’s child.', 'n,y', 'None of the three grounds: the writ does not re-weigh the evidence.'),
                 fact('Martial law, writ intact', 'Martial law is declared, but nothing is said of the writ; a journalist is detained without charges.', 'n,n,n', 'Martial law does not automatically suspend the writ: habeas corpus lies.'),
                 fact('An organizer held', 'The writ is suspended because of a rebellion; police hold a rally organizer who is charged with nothing.', 'n,n,y,n', 'The suspension covers only persons judicially charged with rebellion or invasion offenses.'),
                 fact('Charged on day five', 'During the suspension, a suspected rebel arrested on a Monday is charged with rebellion on Saturday.', 'n,n,y,y,n', 'Not charged within three days: he must be released.'),
                 fact('Charged in time', 'A rebel captured in the battle zone is charged with rebellion the next day.', 'n,n,y,y,y', 'The suspension applies to him: no habeas corpus for now, but he keeps his other rights.')]),
    kind='gates', when='someone is arrested, detained or tried during martial law or a suspension of the writ, or a convict seeks habeas corpus.',
    hook='<em>No soldier-judges, no writ of error; charged, connected, and within three days</em>.',
    oral='The issue is whether [the detainee] may be held without the remedy of habeas corpus. Under Article VII, Section 18, martial law does not suspend the Constitution or the functioning of the civil courts, nor give military courts jurisdiction over civilians where civil courts function, as Olaguer v. Military Commission No. 34 held; and a suspension of the writ applies only to persons judicially charged with rebellion or offenses connected with invasion, who must be charged within three days or released. Here, [he was arrested at a rally and never charged], so the suspension does not cover him and habeas corpus lies.',
    cap='Suspending the writ suspends the remedy, not the right: an illegal arrest stays illegal (Carpio, J., in Fortun).')

fig('18', 'after', '<h3 id="cinc-review">Reviewing martial law: the Court, Congress and extensions</h3>\n', 'mlrev', 'Will this martial law, or its extension, survive review?',
    gates([G('Is there an actual rebellion or invasion, not merely an imminent danger?', 'rebellion is Art. 134, RPC: a public uprising and taking up arms to remove territory from allegiance or deprive the President or Congress of powers; probable cause suffices', 'Insufficient basis: void', '“imminent danger” was deleted in 1987', 'no', 'no'),
           G('Does public safety require it?', 'the Court defers on the area covered: rebellion has no predetermined bounds (' + C('lagman17', 'Lagman, 2017') + ')', 'Insufficient basis: void', 'Congress may also revoke, at any time and on any ground', 'no', 'no'),
           G('Is it within its first 60 days, or extended by Congress on the President’s initiative?', 'a joint vote by a majority of all the Members; as often and as long as Congress fixes, while the rebellion persists (' + C('lagmanpimentel', 'Lagman v. Pimentel III') + ')', 'Lapsed', 'the 60-day “time fuse” has run', 'no', 'sun')],
          ('Sufficient factual basis: valid', 'judged on the facts known when it was issued, in their totality; some false facts do not void it; abuses go to separate cases (' + C('lagman19', 'Lagman, 2019') + ')', 'ok'),
          facts=[fact('Lagman v. Medialdea (2017)', 'Rebels besiege Marawi, burn buildings, take hostages and raise ISIS flags; martial law is declared over all of Mindanao.', 'y,y,y', 'Actual rebellion with public safety; all of Mindanao could be covered.'),
                 fact('Lagman v. Pimentel III (2018)', 'Marawi is liberated, but 185 rebels are at large, about 400 recruits join, and bomb plots continue; Congress extends martial law for a year at the President’s request.', 'y,y,y', 'The rebellion persists, and Congress may fix the period.'),
                 fact('Lagman v. Medialdea (2019)', 'Bombings, kidnappings and NPA attacks continue; Congress extends martial law a third time.', 'y,y,y', 'Reasonableness, not accuracy: the reports in their totality suffice.'),
                 fact('A planned uprising', 'Intelligence says a rebellion is being planned; the President declares martial law nationwide before any armed uprising.', 'n', 'A planned rebellion is at most an imminent danger, which the 1987 text deleted.'),
                 fact('Day 61', 'Martial law is declared on March 1; Congress never extends it; troops still enforce it on May 5.', 'y,y,n', 'Past 60 days without an extension: it has lapsed.')]),
    kind='gates', when='a petition challenges martial law, the suspension of the writ, or an extension, or Congress debates whether to extend.',
    hook='<em>Actual, safe, on time</em>: real rebellion, public safety, and 60 days or Congress.',
    oral='The issue is whether [the proclamation] has sufficient factual basis. Under Article VII, Section 18, the Court reviews only the sufficiency of the factual basis, on any citizen’s petition, within 30 days; in Lagman v. Medialdea (2017) the Court required an actual rebellion, as defined in Article 134 of the Revised Penal Code, and that public safety require martial law, judged on the facts known to the President at the time and needing only probable cause. Here, [there is no armed uprising yet, only intelligence of a plot], so there is no sufficient factual basis and the proclamation is void.',
    cap='Congress may revoke at any time, on any ground, and the President cannot set the revocation aside.')

fig('18', 'after', '<h3 id="cinc-review">Reviewing martial law: the Court, Congress and extensions</h3>\n', 'mlclock', 'Mindanao martial law, 2017 to 2019',
    tl([('May 23, 2017', 'Proclamation No. 216: martial law and the writ suspended in all of Mindanao, after the Marawi siege begins', 'key'),
        ('May 25, 2017', 'Report to Congress within 48 hours; each House adopts a resolution of support; no joint session', ''),
        ('July 4, 2017', C('lagman17', 'Lagman v. Medialdea') + ': sufficient factual basis, 11–4; Fortun’s sequential view set aside', 'key'),
        ('July 22, 2017', 'First extension by Congress in joint session, to December 31, 2017', ''),
        ('July 25, 2017', C('padilla', 'Padilla v. Congress') + ': no joint session needed except to revoke or extend', ''),
        ('Oct. 17, 2017', 'Marawi declared liberated', ''),
        ('Dec. 13, 2017', 'Second extension (RBH No. 4, 240–27), to December 31, 2018', ''),
        ('Feb. 6, 2018', C('lagmanpimentel', 'Lagman v. Pimentel III') + ': Congress may extend as often and as long as it fixes, 10–5', 'key'),
        ('Dec. 12, 2018', 'Third extension (RBH No. 6)', ''),
        ('Feb. 19, 2019', C('lagman19', 'Lagman v. Medialdea') + ': third extension upheld, 9–4', 'key')]),
    kind='timeline', when='a news card asks how long martial law can last, or recalls the Mindanao martial law.',
    hook='<em>60 days became three extensions</em>, each upheld.',
    oral='The issue is whether martial law may be extended again. Under Article VII, Section 18, Congress, voting jointly by a majority of all its Members, may extend a proclamation on the President’s initiative if the rebellion persists and public safety requires it; in Lagman v. Pimentel III the Court held that Congress may do so more than once and for any period it fixes. Here, [the rebellion persists and the President asked], so a further extension is valid, subject to the Court’s review of its factual basis.',
    cap='The professor’s point: three extensions, all upheld, show how little the 60-day limit now restrains.')

fig('18', 'after', '<h3 id="cinc-emerg">Emergency powers</h3>\n', 'emergpres', 'Can the President do this in an emergency?',
    gates([G('Is it a calling-out of the armed forces, or a mere declaration of a state of emergency or rebellion?', 'the President’s own powers', 'Valid without a new law', 'a declaration adds no power (' + C('sanlakas', 'Sanlakas') + '; ' + C('ampatuan', 'Ampatuan') + ')', 'yes', 'ok'),
           G('Does a law authorize it?', 'a Sec. 23(2) delegation (war or national emergency, a limited period, restrictions, a declared policy), a takeover law, or a statute such as RA 12287', 'Valid within the law', 'until the period ends, Congress withdraws it by resolution, or the next adjournment', 'yes', 'ok'),
           G('Does it legislate, or take over or direct a private business?', 'decrees; seizing utilities, factories or media; new crimes', 'Void', 'legislative power is Congress’s; “the State” in Art. XII, Sec. 17 means Congress (' + C('davidgma', 'David') + ')', 'yes', 'no')],
          ('Valid only within existing executive powers', 'for example, directing executive agencies, or spending funds already appropriated for the purpose', 'sun'),
          facts=[fact('David (2006)', 'The President declares a national emergency, orders the AFP to enforce her decrees, and invokes the power to take over businesses; police raid a newspaper.', 'n,n,y', 'Declaring is hers; decrees and takeovers without a law are void.'),
                 fact('Ampatuan v. Puno (2011)', 'After a massacre, the President declares a state of emergency in three areas and calls out the AFP and PNP.', 'y', 'A calling-out, not emergency powers: no law needed.'),
                 fact('The Bayanihan Act (2020)', 'During the pandemic, Congress passes a law letting the President, for a limited period, direct the operation of private hospitals and transport.', 'n,y', 'A Sec. 23(2) delegation and a takeover law: valid within its terms.'),
                 fact('RA 12287 (2025)', 'On the NDRRMC’s recommendation, the President declares a State of Imminent Disaster three days before a super typhoon, ordering pre-emptive evacuation and prepositioned relief.', 'n,y', 'Authorized by statute; lifted automatically when the typhoon hits.'),
                 fact('A power plant', 'Facing a power crisis, the President orders the military to run a private power plant; no law authorizes it.', 'n,n,y', 'Void without a law (David).')]),
    kind='gates', when='a President invokes an emergency (unrest, pandemic, typhoon, power crisis) to act without Congress.',
    hook='<em>Declare alone; legislate or take over only with a law</em>.',
    oral='The issue is whether the President may [take over the power plants] during an emergency. The President alone may declare a national emergency, but under Article VI, Section 23(2) emergency powers must be delegated by law, for a limited period and subject to restrictions; in David v. Macapagal-Arroyo the Court held that the takeover of a private business under Article XII, Section 17 likewise needs a law, because “the State” means Congress. Here, [no law authorizes the takeover], so it is void.',
    cap='RA 12287 (2025) gives the President a statutory State of Imminent Disaster; it is not a grant of legislative power.')

fig('18', 'after', '<h3 id="cinc-loans">Contracting and guaranteeing foreign loans</h3>\n', 'foreignloan', 'Is this foreign loan valid?',
    gates([G('Is it a loan or guarantee, or a necessary incident of one?', 'bond issues and conversions, buybacks, restructuring (' + C('constantino', 'Constantino') + ')', 'Outside Sec. 20', 'it needs some other authority', 'no', 'sun'),
           G('Did the Monetary Board concur before the loan took effect?', 'an Approval-in-Principle before negotiations; Final Approval after signing but before any drawdown (' + C('colmenares', 'Colmenares') + ')', 'Void', 'no prior concurrence', 'no', 'no'),
           G('Is it within the limits set by law?', 'RA 4860, RA 245, the monetary authority’s regulations (Art. XII, Sec. 21)', 'Void', '“subject to such limitations as may be provided by law”', 'no', 'no')],
          ('Valid', 'the Finance Secretary may sign as alter ego (' + C('constantino', 'Constantino') + '); its terms must be made public (Art. XII, Sec. 21)', 'ok'),
          facts=[fact('Constantino v. Cuisia (2005)', 'The Finance Secretary’s team agrees to buy back foreign debt at a discount and convert the rest into bonds.', 'y,y,y', 'Within Sec. 20, and the Secretary may act as alter ego.'),
                 fact('Colmenares v. Duterte (2022)', 'The Monetary Board gives an Approval-in-Principle; the Chico River loan is signed; Final Approval follows before any drawdown.', 'y,y,y', 'The staged procedure satisfies prior concurrence.'),
                 fact('Drawn too soon', 'An agency draws on a foreign loan before the Monetary Board has given Final Approval.', 'y,n', 'Prior concurrence was never completed: void.'),
                 fact('A secret loan', 'A loan with all the Board’s approvals bars disclosure of its terms without the lender’s consent.', 'y,y,y', 'The loan stands, but the confidentiality clause cannot stand against Art. XII, Sec. 21.')]),
    kind='gates', when='a foreign loan (China, Japan, the World Bank) is questioned: who signed, whether the Monetary Board concurred, and whether its terms can be kept secret.',
    hook='<em>Loan, Board, law, public</em>.',
    oral='The issue is whether [the loan agreement] is valid. Under Article VII, Section 20, the President may contract foreign loans with the prior concurrence of the Monetary Board and within the limits set by law; in Colmenares v. Duterte the Court held that prior concurrence is met by an Approval-in-Principle before negotiations and a Final Approval after signing but before drawdown, and in Constantino v. Cuisia that the Finance Secretary may act as the President’s alter ego. Here, [the Board gave both approvals before any drawdown], so the loan is valid, though its terms must be made public.',
    cap='The Board reports its decisions on loans to Congress every quarter; Congress does not concur.')

fig('18', 'after', '<h3 id="cinc-foreign">Foreign affairs</h3>\n', 'vfacheck', 'Can foreign troops be here, and who holds the accused?',
    gates([G('Is their presence allowed under a treaty concurred in by the Senate, or an agreement implementing one?', 'two-thirds of all the Senators (Art. VII, Sec. 21); EDCA implements the VFA and the MDT (' + C('saguisag', 'Saguisag') + ')', 'Not allowed', 'Art. XVIII, Sec. 25', 'no', 'no'),
           G('Does the other State recognize it as a treaty?', 'recognition, not ratification by its own Senate (' + C('nicolas', 'Nicolas') + ')', 'Not allowed', 'the asymmetry Sec. 25 was written to end', 'no', 'no'),
           G('Has a visiting soldier been convicted by a Philippine court?', 'before conviction, custody may stay with the sending State (VFA, Art. V, par. 6)', 'Valid; custody may stay with the sending State', 'no breach of equal protection or of the Court’s rule-making power', 'no', 'ok'),
           G('Is he detained by Philippine authorities in agreed facilities?', 'VFA, Art. V, par. 10', 'Not in accord with the agreement', 'an embassy room guarded by the sending State is not enough; renegotiate (' + C('nicolas', 'Nicolas') + ')', 'no', 'no')],
          ('Valid', 'the troops may stay, and the convict serves his sentence in Philippine custody', 'ok'),
          facts=[fact('Nicolas v. Romulo (2009)', 'A US Marine convicted of rape is moved from the Makati City Jail to the US Embassy, guarded by US personnel.', 'y,y,y,n', 'The VFA is valid, but the embassy detention is not in accord with it.'),
                 fact('Before the verdict', 'Before trial, the US holds an accused Marine at its request and produces him at every hearing.', 'y,y,n', 'Custody pending trial may stay with the US.'),
                 fact('The France SOVFA (2026)', 'The Senate concurs in a visiting forces agreement with France, which France treats as binding.', 'y,y?,n', 'Sec. 25 is satisfied if France recognizes it as a treaty.'),
                 fact('No treaty at all', 'A President signs an executive agreement letting a new ally station troops, with no treaty behind it.', 'n', 'Sec. 25 requires a treaty for their entry.')]),
    kind='gates', when='foreign troops are stationed or exercise here, or a foreign soldier is accused or convicted of a crime in the Philippines.',
    hook='<em>Treaty, recognized, then our jail</em>.',
    oral='The issue is whether [the foreign troops’ presence and the convict’s detention] comply with the Constitution. Article XVIII, Section 25 allows foreign troops only under a treaty concurred in by the Senate and recognized as a treaty by the other State; in Nicolas v. Romulo the Court held that the VFA meets this, since the Senate concurred and the US recognized it, but that a convicted American soldier must be detained by Philippine authorities. Here, [he is held in the embassy under foreign guard], so the arrangement is not in accord with the VFA.',
    cap='Deportation of undesirable aliens is part of the same field: the President decides, after investigation (Go Tek).')

fig('18', 'after', '<h3 id="cinc-legis">The President’s part in legislation</h3>\n', 'preslegis', 'The President in legislation: four roles',
    cmp(['When or how', 'The check'], [
        ('Address Congress', 'at the opening of each regular session; may appear at any other time', 'none needed: it informs, it does not bind'),
        ('The budget', 'within 30 days from the opening of the regular session, the basis of the general appropriations bill', 'Congress appropriates, but may not increase the President’s figures for the operation of the Government (Art. VI, Sec. 25(1))'),
        ('The veto', 'whole bills; items in appropriation, revenue or tariff bills; within 30 days of receipt, or the bill becomes law', 'override by two-thirds of all the Members of each House'),
        ('Emergency powers', 'by law, in war or other national emergency', 'a limited period and restrictions; they end at the next adjournment or by resolution'),
    ]),
    kind='comparison', when='a news card has the President shaping legislation: the SONA, the budget, a veto, or a request for emergency powers.',
    hook='<em>Speak, propose, veto, borrow</em>: the President addresses Congress, proposes the budget, blocks bills, and uses only the emergency powers Congress lends.',
    oral='The issue is whether [the President] may [spend on the basis of his own budget proposal]. Under Article VII, Section 22 the President only proposes the budget, within 30 days from the opening of the regular session; Congress appropriates, and the President’s check is the veto under Article VI, Section 27, including the item veto, which Congress may override by two-thirds of all its Members. Here, [no appropriation was passed for the item], so the spending is void.',
    cap='Details live elsewhere: the budget on the appropriations map, the veto on the legislative-process map.')

fig('18', 'after', '<h3 id="cinc-immunity">Immunity from suit</h3>\n', 'presimm', 'Can this suit go on?',
    gates([G('Is the incumbent President the defendant or respondent?', 'not the President’s officials, not a former President; whether it covers the Vice-President is open', 'Immunity is no bar', 'sue the officials for their own acts (' + C('gloriaca', 'Gloria') + '); a former President may be prosecuted (' + C('estradaarroyo', 'Estrada') + '); an accused cannot invoke the President’s immunity (' + C('soliven', 'Soliven') + ')', 'no', 'ok'),
           G('Has the President chosen to waive the immunity and submit to the court?', 'the privilege is the President’s alone to invoke or waive (' + C('soliven', 'Soliven') + ')', 'The case proceeds', 'the President accepts the court’s jurisdiction and its risks', 'yes', 'ok')],
          ('Dismissed, or the President dropped', 'during tenure, for any act, official or personal, in any proceeding, even habeas data, whether or not invoked; the remedy is impeachment or a suit after tenure (' + C('delima', 'De Lima') + ')', 'no'),
          facts=[fact('De Lima v. Duterte (2019)', 'A senator petitions for habeas data against the sitting President over his public statements about her.', 'y,n', 'Dismissed: the President is immune during tenure.'),
                 fact('Soliven v. Makasiar (1988)', 'President Aquino files a libel complaint; the accused columnist argues the case cannot go on because she is immune from suit.', 'n', 'She is the complainant, not the defendant; only she may invoke the privilege.'),
                 fact('Gloria v. CA (2000)', 'A superintendent sues the Education Secretary to stop a reassignment the President approved.', 'n', 'The suit is against the Secretary’s own acts.'),
                 fact('Estrada v. Arroyo (2001)', 'A President who has left office is charged with plunder for acts done in office.', 'n', 'Immunity ended with his tenure.'),
                 fact('Lagman v. Pimentel III (2018)', 'Petitioners challenging an extension of martial law name the President as a respondent.', 'y,n', 'The President is dropped; Congress and the officials remain.'),
                 fact('The Vice-President (2026)', 'The sitting Vice-President is charged with grave threats and claims immunity as an impeachable officer.', 'n?', 'Arguable: the cases speak of the President’s immunity, personal to that office.')]),
    kind='gates', when='someone sues or charges the President, the President’s officials, a former President, or the Vice-President.',
    hook='<em>Sitting President only; personal; ends with the term</em>.',
    oral='The issue is whether [the petition against the President] may proceed. The 1987 Constitution is silent, but in De Lima v. Duterte the Court held that the incumbent President is immune from suit during tenure, for any act and in any proceeding, even if the President does not invoke it; under Soliven v. Makasiar the privilege belongs to the President alone, and under Gloria v. Court of Appeals it does not cover the acts of subordinates. Here, [the President is the sole respondent], so the petition must be dismissed, though the officials who carry out the act may be sued.',
    cap='Not the same as the State’s immunity from suit (on the government map).')

fig('18', 'after', '<h3 id="cinc-vp">The Vice-President</h3>\n', 'vpprotest', 'Will this election protest before the PET prosper?',
    gates([G('Does the protest specify each irregularity and the precincts where it happened?', 'bare allegations of massive fraud are not enough', 'May be dismissed outright', 'the PET heard Marcos’s protest anyway, for due process (' + C('robredo', 'Marcos, Jr. v. Robredo') + ')', 'no', 'sun'),
           G('Did revision of the pilot provinces (at most three) show a reasonable recovery of votes?', 'the protestant picks them at the preliminary conference (PET Rule 65)', 'Dismissed', 'without revising the rest; this also bars a claim to annul elections', 'no', 'no'),
           G('For annulment: are the Abayon requisites met?', 'illegality affecting more than half the votes; lawful and unlawful ballots cannot be told apart; the protestee was responsible', 'No annulment', 'the results stand', 'no', 'no')],
          ('The protest may prosper', 'the PET may annul results, but only the COMELEC may call special elections', 'ok'),
          facts=[fact('Marcos, Jr. v. Robredo (2021)', 'A losing VP candidate alleges fraud in 39,221 precincts with few specifics; after revision of his three pilot provinces, the winner’s lead grows from 263,473 to 278,566.', 'y?,n', 'Heard despite weak allegations; no recovery in the pilots: dismissed.'),
                 fact('A strong protest', 'A protestant names 200 precincts, his pilot revision cuts the winner’s lead by 80%, and in one province armed men controlled the polls, so the ballots cannot be told apart, at the protestee’s direction.', 'y,y,y', 'The protest may prosper, and the PET may annul the results there.'),
                 fact('Annulment without proof', 'A protestant recovers some votes in the pilots but cannot show who was behind the irregularities in the provinces he wants annulled.', 'y,y,n', 'No annulment without the Abayon requisites.')]),
    kind='gates', when='a losing presidential or vice-presidential candidate files an election protest.',
    hook='<em>Specific, three pilots, then Abayon</em>.',
    oral='The issue is whether [the protest] may prosper. Under the last paragraph of Article VII, Section 4, the Supreme Court en banc is the sole judge of contests over the election of the President and Vice-President; in Marcos, Jr. v. Robredo the Tribunal held that a protest must specify the irregularities and that if revision of the pilot provinces, at most three, shows no reasonable recovery, the protest is dismissed. Here, [the winner’s lead grew after revision], so the protest must be dismissed.',
    cap='The PET itself is on the ' + X('court-pet', 'Supreme Court map') + ' (Macalintal v. PET).')

# =====================================================================
# 19 · the Supreme Court (V.C.1–2(o))
# =====================================================================
fig('19', 'after', '<h3 id="court-power">Judicial power, composition and modes of sitting</h3>\n', 'scdivision', 'Can a Division decide this?',
    gates([G('Is the constitutionality of a treaty, international or executive agreement, or law in question?', 'Sec. 4(2): these are heard en banc; so are other cases the Rules of Court send there', 'En banc', 'decided by a majority of those who took part and voted', 'yes', 'sun'),
           G('Would the ruling modify or reverse a doctrine laid down by the Court?', 'whether the doctrine came from the en banc or a Division (Sec. 4(3), proviso)', 'En banc', 'only the Court en banc may modify or reverse a doctrine', 'yes', 'sun'),
           G('Is it the dismissal of a lower-court judge, or another matter the en banc keeps for itself?', 'Sec. 11; under Bar Matter No. 209, also suspension over one year or a fine over ₱10,000 (' + C('gacott', 'Gacott') + ')', 'En banc', 'only the full Court may dismiss a judge', 'yes', 'sun'),
           G('Did a majority of the Division’s Members who took part and voted, and at least three, concur?', 'the base is those who actually deliberated and voted, not the full Division', 'Goes to the en banc', '“When the required number is not obtained, the case shall be decided en banc”', 'no', 'sun')],
          ('The Division decides', 'and its decision is the decision of the Supreme Court (' + C('gacott', 'Gacott') + ')', 'ok'),
          facts=[fact('People v. Gacott, Jr. (1995)', 'The Second Division reprimands a judge and fines him ₱10,000 for gross ignorance of the law; he says only the en banc may discipline judges.', 'n,n,n,y', 'Valid: only dismissal (and the heavier penalties the en banc keeps) needs the full Court.'),
                 fact('A law attacked', 'A petition assigned to a Division asks the Court to strike down a 2025 statute as unconstitutional.', 'y', 'It must be heard and decided en banc.'),
                 fact('Two of five', 'In a five-member Division, two Justices inhibit; the other three split 2–1 to grant.', 'n,n,n,n', 'A majority of those who voted, but not three: the case goes to the en banc.'),
                 fact('Overruling a precedent', 'A Division, 5–0, wants to abandon a doctrine laid down by another Division ten years ago.', 'n,y', 'Only the en banc may modify or reverse it.')]),
    kind='gates', when='a question is whether a Division of the Supreme Court could validly decide a case, or who must decide it.',
    hook='<em>Law, doctrine, dismissal, three votes</em>: otherwise the Division is the Court.',
    oral='The issue is whether [the Division] could validly decide [the case]. Under Article VIII, Section 4, the Court may sit in divisions, but cases on the constitutionality of a treaty or law, and the modification of a doctrine, are for the en banc, and under Section 11 only the en banc may dismiss a judge; in People v. Gacott the Court held that a Division may impose lesser discipline and that its decision is the decision of the Supreme Court. Here, [the Division only reprimanded and fined the judge], so its ruling is valid.',
    cap='A Division of 3, 5 or 7 decides by a majority of those who took part and voted, and never with fewer than three concurring.')

fig('19', 'after', '<h3 id="court-appt">Appointments and qualifications</h3>\n', 'scappt', 'Can this person be appointed to the Supreme Court?',
    gates([G('Is the appointee a natural-born citizen?', 'one who became Filipino through a parent’s naturalization is naturalized, until proved otherwise in court (' + C('kilosbayanermita', 'Kilosbayan') + ')', 'Cannot be appointed', 'the Court may enjoin the appointee from taking office', 'no', 'no'),
           G('Is the appointee at least 40, and for 15 years or more a judge or in law practice in the Philippines?', 'Sec. 7(1)', 'Cannot be appointed', 'the qualification is constitutional', 'no', 'no'),
           G('Is the appointee of proven competence, integrity, probity and independence?', 'Sec. 7(3); filing SALNs is evidence of integrity (' + C('sereno', 'Sereno') + ')', 'Ineligible', 'the State may oust the appointee by quo warranto; the JBC and the appointment do not cure it', 'no', 'no'),
           G('Was the appointee on a JBC list of at least three nominees for that vacancy?', 'Sec. 9', 'Void appointment', 'the President chooses only from the list', 'no', 'no')],
          ('Valid', 'no CA confirmation; the vacancy is filled within 90 days of its occurrence (Sec. 4(1)); the election ban does not apply (' + C('decastrojbc', 'De Castro v. JBC') + ')', 'ok'),
          facts=[fact('Kilosbayan v. Ermita (2007)', 'The appointee’s own bar petition says he became Filipino when his father was naturalized while he was a minor; BI and DOJ papers now call him natural-born.', 'n', 'Naturalized on the Court’s records: enjoined until he proves otherwise in court.'),
                 fact('Republic v. Sereno (2018)', 'A Chief Justice appointed in 2012 never filed many of her SALNs as a professor and gave the JBC only three of the ten it required.', 'y,y,n', 'No proven integrity: ousted by quo warranto, 8–6.'),
                 fact('The 2026 Chief Justice', 'A sitting Associate Justice is appointed Chief Justice from the JBC’s list of five nominees, a day before the incumbent retires at 70.', 'y,y,y,y', 'Qualified and from the list; whether an appointment may precede the vacancy is the one question to raise (Velicaria-Garafil).'),
                 fact('Off the list', 'The President appoints a respected law dean the JBC did not nominate, saying the list was too short.', 'y,y,y,n', 'Void: the President may choose only from the JBC’s nominees.')]),
    kind='gates', when='a nominee or appointee to the Court is questioned: citizenship, age, experience, integrity, or the JBC list.',
    hook='<em>Born, forty-fifteen, integrity, list</em>.',
    oral='The issue is whether [the appointee] may sit in the Supreme Court. Under Article VIII, Sections 7 and 9, a Member must be natural-born, at least forty, with fifteen years as a judge or lawyer, of proven integrity, and appointed from a JBC list of at least three; in Kilosbayan v. Ermita the Court enjoined an appointee whose own records showed he was naturalized, and in Republic v. Sereno it held that lack of proven integrity is an ineligibility that quo warranto may correct. Here, [the appointee became a citizen through his father’s naturalization], so he cannot take office until he proves natural-born status in court.',
    cap='For lower courts the President has 90 days from the JBC’s list (Sec. 9); for the Supreme Court, 90 days from the vacancy (Sec. 4(1)).')

fig('19', 'after', '<h3 id="court-nonjud">No non-judicial work for judges</h3>\n', 'scnonjud', 'Can a judge or Justice take this assignment?',
    gates([G('Is it a post in an agency or body performing quasi-judicial or administrative functions?', 'a board of arbitrators, a department, a commission, a detail to the DOJ (Sec. 12)', 'Not allowed', 'the Justices cannot take on non-judicial power (' + C('meralco32', 'Meralco') + '; ' + C('garciamacaraig', 'Garcia v. Macaraig') + ')', 'yes', 'no'),
           G('Could anyone other than the higher courts review or reverse what the judge does there?', 'a judge must never be where an executive official reviews his acts (' + C('garciamacaraig', 'Garcia') + ')', 'Not allowed', 'it erodes the separation of powers', 'yes', 'no')],
          ('Allowed', 'it is judicial work; the PET exercises judicial power, “independent, but not separate” from the Court (' + C('macalintalpet', 'Macalintal v. PET') + ')', 'ok'),
          facts=[fact('Meralco v. Pasay Transportation (1932)', 'A statute makes the Justices a board of arbitrators to fix, with a final award, what one utility pays another for using its bridge.', 'y', 'The Justices declined: a non-judicial role they cannot take.'),
                 fact('Garcia v. Macaraig (1971)', 'A new judge whose court cannot yet function is assigned to help the Department of Justice.', 'y', 'The Court condemned the practice, though it cleared the judge of dishonesty.'),
                 fact('Macalintal v. PET (2011)', 'The Justices sit as the Presidential Electoral Tribunal to hear a protest against the President’s election.', 'n,n', 'Judicial power: valid.'),
                 fact('A truth commission', 'The President names a sitting RTC judge to chair a fact-finding commission on flood-control corruption.', 'y', 'An administrative body: Sec. 12 bars the designation.')]),
    kind='gates', when='a law or the President assigns a judge or Justice to a board, commission, department or task force.',
    hook='<em>Judges judge</em>: no agency, no executive reviewer.',
    oral='The issue is whether [the judge] may be designated to [the commission]. Under Article VIII, Section 12, Members of the Supreme Court and of other courts shall not be designated to any agency performing quasi-judicial or administrative functions; in Meralco v. Pasay Transportation the Justices refused to act as arbitrators, and in Garcia v. Macaraig the Court condemned detailing judges to the DOJ, because no judge should be where anyone but the higher courts may review his acts. Here, [the commission is an executive fact-finding body], so the designation is void.',
    cap='The PET is the Court itself under another name, so Sec. 12 does not reach it (Macalintal v. PET).')

fig('19', 'after', '<h3 id="court-removal">Removal</h3>\n', 'scremove', 'Can this proceeding go on against a sitting Justice?',
    gates([G('Is it an impeachment?', 'Art. XI, Secs. 2–3: the House impeaches, the Senate tries', 'The proper route', 'removal for the six grounds (see the other-powers map)', 'yes', 'ok'),
           G('Is it quo warranto by the State on the Justice’s eligibility at appointment?', 'title, not fitness: citizenship, age, experience, proven integrity (' + C('sereno', 'Sereno') + ')', 'May proceed', 'filed by the OSG; imprescriptible when the State sues at its own instance', 'yes', 'sun'),
           G('Is it a disbarment case, or a criminal charge whose penalty is removal (or amounts to it)?', 'the officer must be a lawyer and is removable only by impeachment (' + C('ingonzalez', 'In re Gonzalez') + ')', 'Must be dismissed', 'impeach first; the prosecutor dismisses motu proprio', 'yes', 'no')],
          ('May go on', 'it does not remove the Justice: In re Gonzalez is not an immunity', 'ok'),
          facts=[fact('In re Gonzalez (1988)', 'The Tanodbayan forwards to a Justice an anonymous complaint repeating a dismissed disbarment case and asks him to answer.', 'n,n,y', 'Charges that would remove a sitting Justice must be dismissed: impeach first.'),
                 fact('Republic v. Sereno (2018)', 'While the House weighs an impeachment complaint, the Solicitor General asks the Court to oust the Chief Justice for lacking proven integrity when appointed.', 'n,y', 'Quo warranto may proceed alongside impeachment; she was ousted, 8–6.'),
                 fact('Corona (2012)', 'The House impeaches the Chief Justice for betrayal of public trust over his SALN.', 'y', 'The constitutional route; the Senate tries him.'),
                 fact('A damages suit', 'A motorist sues a sitting Justice for damages over a car accident.', 'n,n,n', 'Nothing in it removes him: the case may go on.')]),
    kind='gates', when='someone files a complaint, a criminal case, a disbarment case or a quo warranto petition against a sitting Justice or another impeachable officer.',
    hook='<em>Impeach first, unless the title was never there</em>.',
    oral='The issue is whether [the complaint] against [a sitting Justice] may proceed. Under Article XI, Section 2, Members of the Supreme Court are removable by impeachment; in In re Gonzalez the Court held that a sitting Justice cannot be disbarred or charged with an offense carrying removal, because that would circumvent impeachment, while in Republic v. Sereno it held that quo warranto may test eligibility at appointment. Here, [the charge is a disbarment complaint over acts in office], so it must be dismissed and the complainant must go to the House.',
    cap='The In re Gonzalez rule also covers other impeachable officers who must be lawyers: the Ombudsman, and the COMELEC and COA members who must be lawyers.')

fig('19', 'after', '<h3 id="court-fiscal">Fiscal autonomy</h3>\n', 'scfiscal', 'Does this respect the Judiciary’s fiscal autonomy?',
    gates([G('Does it cut the Judiciary’s appropriation below the previous year’s?', 'Sec. 3: a floor set by the Constitution', 'Void', 'Congress may not reduce it below last year’s', 'yes', 'no'),
           G('Does it withhold, delay or condition the release of approved funds?', 'vetoed conditions, work and financial plans, “upon request” (' + C('bengzondrilon', 'Bengzon v. Drilon') + '; RA 12233, Sec. 4(c))', 'Void', 'release is automatic and regular', 'yes', 'no'),
           G('Does an outside body dictate how the Court uses, charges for or disposes of its own resources?', 'COA’s formula for the Court’s property; a statutory exemption from court fees (' + C('recoa2012', 'Re: COA Opinion') + '; ' + C('phcci', 'Re: PHCCI') + ')', 'Void', 'full flexibility to allocate and use its resources is the Court’s', 'yes', 'no')],
          ('Valid', 'e.g., COA’s post-audit of all Judiciary funds (RA 12233, Secs. 4(d) and 5); quarterly reports to the President and Congress', 'ok'),
          facts=[fact('Bengzon v. Drilon (1992)', 'The President vetoes GAA special provisions funding the adjusted pensions of retired Justices.', 'n,y', 'Void: not items, and an impairment of fiscal autonomy.'),
                 fact('Re: COA Opinion (2012)', 'COA disallows the Court’s formula for selling used vehicles to retiring Justices and imposes its own appraisal.', 'n,n,y', 'COA may post-audit, but cannot dictate the formula.'),
                 fact('Re: PHCCI (2012)', 'A cooperative invokes the Cooperative Code to avoid paying filing and sheriff’s fees.', 'n,n,y', 'Legal fees are procedural rules, the Court’s alone; the exemption also drains its funds.'),
                 fact('A post-audit', 'After the year ends, COA audits how the Judiciary Trust Fund was spent and issues observations.', 'n,n,n', 'Valid: RA 12233 keeps COA’s post-audit.'),
                 fact('Release on request', 'The DBM releases the Judiciary’s monthly allotment only after the Court submits work and financial plans.', 'n,y', 'Void: RA 12233 bars the condition; release is automatic.')]),
    kind='gates', when='the Judiciary’s budget is cut, held back, vetoed or audited, or a law exempts someone from court fees.',
    hook='<em>No cut, no hold, no outside hand</em>; audit only after.',
    oral='The issue is whether [the act] violates the Judiciary’s fiscal autonomy. Under Article VIII, Section 3, the Judiciary’s appropriations may not be reduced below the previous year’s and must be automatically and regularly released; in Bengzon v. Drilon the Court read fiscal autonomy as full flexibility to allocate and use its resources, and in Re: COA Opinion it held that COA may post-audit but not dictate how the Court disposes of its property. RA 12233 now requires monthly release without conditions. Here, [COA imposed its own formula], so the disallowance is void.',
    cap='RA 12233 (2025) replaces the JDF with a Judiciary Trust Fund administered by the Chief Justice.')

fig('19', 'after', '<h3 id="court-delib">Deliberations</h3>\n', 'scpriv', 'Can Congress or a party compel this from the Court?',
    gates([G('Is it a public record of the Court (a decision, a resolution, a filed pleading)?', 'produced as certified copies through the Clerk of Court', 'Produce it', 'certified copies, under the Court’s rules', 'yes', 'ok'),
           G('Is it about an external matter, outside the Court’s adjudication (a bribe offered, a crime)?', 'not about how the case was deliberated', 'May be compelled', 'Justices and staff may testify on external matters', 'yes', 'sun'),
           G('Is it about the Court’s deliberations or predecisional records (raffle, agenda, internal memos, drafts, votes)?', 'judicial privilege, from the separation of powers and comity (' + C('inreproduction', 'In re Production of Court Records') + ')', 'Privileged', 'it belongs to the Court; no single Justice may waive it', 'yes', 'no')],
          ('Ask the Court en banc', 'it decides access under its own rules and the limits of the right to information', 'sun'),
          facts=[fact('In re Production (2012)', 'Impeachment prosecutors subpoena the rollos, the agenda and Justices’ testimony on how the Court issued a TRO in the Arroyo travel case.', 'n,n,y', 'Deliberative matters: privileged.'),
                 fact('A certified decision', 'The prosecutors ask for a certified true copy of the TRO resolution itself.', 'y', 'A public record: the Clerk may issue it.'),
                 fact('A bribe', 'A Senate committee asks a court employee about money a litigant handed her to influence a raffle.', 'n,y', 'An external matter: she may be compelled to testify.')]),
    kind='gates', when='Congress, an impeachment court or a litigant wants the Court’s records, drafts or votes, or wants Justices and staff to testify.',
    hook='<em>Public, yes; outside, yes; inside, never</em>.',
    oral='The issue is whether [the impeachment court] may compel [the Justices’ testimony on their deliberations]. Under Article VIII, Section 13, the Court’s conclusions are reached in consultation, and in In re Production of Court Records the Court held that its deliberations and predecisional records are covered by judicial privilege, which belongs to the Court and cannot be waived by one Justice; only external matters such as bribery may be inquired into. Here, [the subpoena asks how the Justices voted on the TRO], so it cannot be enforced.',
    cap='The certification of consultation itself (Sec. 13) is a separate matter: its absence does not void a decision (Consing).')

fig('19', 'after', '<h3 id="court-voting">Voting</h3>\n', 'scvotes', 'How many votes, and what if it ties?',
    cmp(['En banc', 'Division', 'Tie in the en banc'], [
        ('Cases', 'a treaty, agreement or law attacked as unconstitutional; other cases the Rules send en banc; dismissal of judges; modifying a doctrine', 'all others the Court assigns', 'any en banc case'),
        ('Votes needed', 'a majority of the Members who actually took part in the deliberations and voted', 'that majority and at least three', '—'),
        ('If not reached', '—', 'the case goes to the en banc (Sec. 4(3))', 'original action dismissed; on appeal, the judgment below stands (Rule 56, Sec. 7)'),
        ('Case', C('gacott', 'Gacott') + ' (a Division’s decision is the Court’s)', C('gacott', 'Gacott'), C('cruzdenr', 'Cruz v. DENR') + ': IPRA stands, 7–7, undecided'),
    ]),
    kind='comparison', when='a news card reports a split vote, an inhibition, or a tie, and you must say whether the Court decided anything.',
    hook='<em>Count those who voted</em>; a tie decides nothing.',
    oral='The issue is the effect of [the 7–7 vote on the petition]. Under Article VIII, Section 4(2), en banc cases are decided by a majority of the Members who actually took part and voted; in Cruz v. Secretary of Environment and Natural Resources the Court, tied 7–7 after redeliberation, dismissed the petition under Rule 56, so IPRA stood without a ruling on its validity. Here, [the Court tied], so [the law] stands, but no doctrine was laid down.',
    cap='Members who inhibit or do not vote are left out of the count; those who took no part must say why (Sec. 13).')

fig('19', 'after', '<h3 id="court-mr">Petition for review and motion for reconsideration</h3>\n', 'scdecision', 'Does this decision or resolution satisfy Sec. 14?',
    gates([G('Is it a decision on the merits of a case submitted for decision, by a court or a quasi-judicial body?', 'labor arbiters and the NLRC too (' + C('miguel', 'Miguel') + '); not minute resolutions refusing due course or denying reconsideration', 'Needs only a legal basis', '“lack of merit,” “factual issues,” “nothing new” (' + C('nunal', 'Nuñal') + '; ' + C('martinez', 'Martinez') + '; ' + C('tichangco', 'Tichangco') + ')', 'no', 'sun'),
           G('Does it state the facts (its own findings, or adopted from a brief) and the law?', 'evidentiary facts, not conclusions; adoption is allowed (' + C('hernandez', 'Hernandez') + ')', 'Void', 'no facts, no law: a decision in name only (' + C('bugarin', 'Bugarin') + '; ' + C('miguel', 'Miguel') + ')', 'no', 'no'),
           G('If it adopts the lower court’s decision by reference: are the Permskul conditions met?', 'the findings annexed and made part of it; the adopted decision complies; a simple case (' + C('yao', 'Yao') + ')', 'Void', 'remand for a proper decision', 'no', 'no')],
          ('Valid', 'brevity is allowed; substance is not optional', 'ok'),
          facts=[fact('People v. Bugarin (1997)', 'A rape conviction summarizes the testimony and says only that the complainant is credible.', 'y,n', 'No reasons: the Court reviewed the whole record itself.'),
                 fact('Miguel v. JCT (2005)', 'A labor arbiter holds two respondents liable without finding who employed the workers.', 'y,n', 'Void: quasi-judicial decisions must state the facts too.'),
                 fact('Nuñal v. COA (1989)', 'The Court refuses due course to a certiorari petition by minute resolution, stating its legal basis.', 'n', 'Sec. 14’s “facts and law” does not apply; a legal basis suffices.'),
                 fact('Martinez v. CA (2001)', 'The CA denies reconsideration in one paragraph: nothing new, already passed upon.', 'n', 'A legal basis: valid.'),
                 fact('Hernandez v. CA (1993)', 'The CA adopts the Solicitor General’s narration of facts and then rules on each assigned error.', 'y,y,y', 'Valid: adoption is not abdication.'),
                 fact('Yao v. CA (2000)', 'An RTC affirms the MTC in one page: “no cogent reason to disturb,” with nothing annexed.', 'y,y?,n', 'Not even a valid memorandum decision: nullified and remanded.')]),
    kind='gates', when='a party attacks a decision, resolution or denial as unexplained, too short, or merely adopting someone else’s findings.',
    hook='<em>Decisions: facts and law. Denials: a legal basis</em>.',
    oral='The issue is whether [the decision] complies with Article VIII, Section 14. A decision must state clearly and distinctly the facts and the law on which it is based, while a denial of a petition for review or reconsideration needs only a legal basis; in People v. Bugarin the Court held that a decision that merely calls a witness credible fails, and in Yao v. Court of Appeals that a memorandum decision is valid only if it annexes the findings it adopts and is used in simple cases. Here, [the RTC affirmed in one page with no findings], so the decision is void and must be remanded.',
    cap='This diagram covers both paragraphs of Sec. 14: requirements as to decisions (V.C.2(l)) and petitions for review and motions for reconsideration (V.C.2(m)).')

fig('19', 'after', '<h3 id="court-periods">Periods for deciding cases</h3>\n', 'scdelay', 'Is the judge liable for delay?',
    gates([G('Did the period lapse without a decision or resolution?', '24 months for the SC; 12 for the CA; 3 for the Sandiganbayan (PD 1606) and trial courts (90 days), counted from submission', 'No delay', 'the case was decided on time', 'no', 'ok'),
           G('Did the judge ask for an extension before the period lapsed, and did the Court grant it?', 'a judge cannot set his own deadline (' + C('fuentes', 'Fuentes') + ')', 'Not liable', 'decided within the extended period', 'yes', 'ok')],
          ('Gross inefficiency', 'even one late case; illness, travel or docket are no excuse after the fact; the court must still decide (Sec. 15(4)) (' + C('delayssb', 'Re: Delays in the Sandiganbayan') + '; ' + C('fuentes', 'Fuentes') + ')', 'no'),
          facts=[fact('OCA v. Fuentes III (2013)', 'A trial judge sets his own deadlines and decides several cases months after the 90 days, without asking for an extension.', 'y,n', 'Gross inefficiency: fined ₱40,000.'),
                 fact('Re: Delays (2001)', 'Sandiganbayan cases wait years after submission; the Presiding Justice says the 12-month period for collegiate courts applies.', 'y,n', 'Three months apply; he was fined and relieved as division chair.'),
                 fact('An extension granted', 'A judge with a complex case asks the Court for 60 more days before the 90 lapse, gets them, and decides on day 140.', 'y,y', 'Not liable.'),
                 fact('Day 85', 'A trial judge decides a case 85 days after the last memorandum is filed.', 'n', 'On time.')]),
    kind='gates', when='a news card reports a long-pending case, a backlog, or a complaint against a judge for delay.',
    hook='<em>From submission: 24, 12, 3</em>; extend before, not after.',
    oral='The issue is whether [the judge] is liable for delay. Under Article VIII, Section 15, cases must be decided within twenty-four months in the Supreme Court, twelve in lower collegiate courts and three in other lower courts, from submission; in OCA v. Fuentes the Court held that a trial judge who fails to decide within 90 days without an extension granted by the Court is guilty of gross inefficiency, and Re: Delays in the Sandiganbayan applied three months to the Sandiganbayan. Here, [the judge decided months late without asking for more time], so he is liable.',
    cap='Expiration does not divest the court of jurisdiction: it must still decide, “without further delay” (Sec. 15(4)).')

fig('19', 'after', '<h3 id="court-pet">The Presidential Electoral Tribunal</h3>\n', 'sctribunals', 'Who judges this election dispute?',
    cmp(['President or VP', 'Senator', 'Representative'], [
        ('The tribunal', 'the Supreme Court en banc, as the PET (Art. VII, Sec. 4)', 'the Senate Electoral Tribunal (Art. VI, Sec. 17)', 'the House Electoral Tribunal (Art. VI, Sec. 17)'),
        ('Members', 'all fifteen Justices', '3 Justices + 6 Senators', '3 Justices + 6 Representatives'),
        ('Jurisdiction', '“all contests relating to the election, returns, and qualifications”', 'the same, for Senators', 'the same, for Representatives'),
        ('Nature', 'judicial power, “independent, but not separate” from the Court (' + C('macalintalpet', 'Macalintal v. PET') + ')', 'an independent constitutional body', 'an independent constitutional body'),
        ('Case', C('robredo', 'Marcos, Jr. v. Robredo') + ' (pilot provinces; no special elections)', '—', '—'),
    ]),
    kind='comparison', when='a losing candidate contests an election and you must name the tribunal, its make-up and the nature of its power.',
    hook='<em>Fifteen for the top two</em>; nine for the rest.',
    oral='The issue is whether [the PET] may validly hear [the protest]. Under the last paragraph of Article VII, Section 4, the Supreme Court en banc is the sole judge of contests over the election, returns and qualifications of the President and Vice-President; in Macalintal v. PET the Court held that the Tribunal is constitutional and exercises judicial power, independent but not separate from the Court, so its Justices are not designated to a quasi-judicial agency. Here, [the protest was filed after proclamation], so the PET has jurisdiction.',
    cap='Before proclamation, disputes go to the COMELEC and Congress as canvassers; the PET takes contests after proclamation. The electoral tribunals are on the ' + X('et', 'electoral tribunals map') + '.')

# =====================================================================
# 00 · the hook wall (built last, from every hook above)
# =====================================================================
def _plain(t): return re.sub(r'<[^>]+>', '', t)
fig('00', 'before', '</section>', 'wall', 'Every hook on one screen',
    '<div class="hwall">' + ''.join(f'<div class="ht"' + (f' data-scope="{SEC[p]}"' if p in ('03', '04') else '') + f'><span class="tp">{SHORT[p]}</span>{X("fig-" + fid, _plain(t))}<div class="hk">{h}</div></div>' for p, fid, t, h in WALL) + '</div>',
    kind='review', when='the night before and the morning of the exam: read each hook, say the rule aloud, then tap through to check yourself.',
    cap='Test me hides the words under each acronym. The link on every tile jumps to its diagram.', wall=False)
