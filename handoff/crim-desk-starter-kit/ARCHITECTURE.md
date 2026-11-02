# Architecture and porting guide

## 1. Pipeline

```
site/data/*  ──►  site/app/build.py  ──►  site/dist/<name>.html  (one file, everything inlined)
                    │  reads JSON + rule-map HTML, validates with asserts
                    │  figures.insert()  puts diagrams into the rule maps (figures.py)
                    │  caselink.link_file()  links every case name to its card (caselink.py)
                    └  fills template.html: __CSS__ (style.css), __REVIEWER__ (rule maps),
                                            __JS__ (app.js), __DATA__ (JSON object D)
site/app/print_sheets.js  ──►  one-page folio PDFs from the Printables tab (Playwright)
site/tests/*.js           ──►  Playwright checks at 400 px and 1280 px, light and dark
```

Commands:
```bash
python3 site/app/build.py [--out site/dist/x.html]
node site/app/print_sheets.js [built.html] [outdir]
node site/tests/smoke.js; node site/tests/features.js; node site/tests/viz.js; node site/tests/drill.js
```
Tests need Playwright with Chromium. The built file has no `<meta viewport>` because the Artifact host wraps the page with one; for phone tests use a 400 px viewport, not `isMobile` emulation.

## 2. Data (`site/data/`) and schemas

Real examples of every file are in `reference/data-samples/`.

### `cases/*.json` — case cards (array per file, any number of files)
| key | meaning |
|---|---|
| `id` | short unique slug (`kapit`, `avelino`); used everywhere as the key |
| `n`, `y` | case name, year |
| `t` | topic key (must exist in `TOPICS` in build.py) |
| `sub` | syllabus sub-heading |
| `a` | 1 = anchor case (printed on the anchor sheet, "anchors only" drill filter) |
| `r` | **rule**: the doctrine in 1–3 sentences (the back of a Case → rule card) |
| `f` | facts, short (front of Facts → case; the case name is auto-masked) |
| `h` | holding / disposition |
| `test` | the test or elements the case lays down, if any |
| `x` | exam use: when to cite it |
| `g` | the professor's own view of the case (shown in a highlighted box) |
| `w` | warning: source conflicts, things to verify |
| `s` | one-line summary (search, lists) |
| `ref` | 1 = mentioned in the rule maps but not on the syllabus: linkable, not drilled |

Attached at build time: `dg` (class-reviewer text from `dg_reviewer.json`, id → text) and `hk`/`hc` (hook from `case_hooks.json`).

### `case_hooks.json` — id → `{"k": "1–3 words", "c": "ok"|"no"|"sun"|"acc"}`
Every case must have one (build asserts). In Consti the color meant the outcome: green upheld, red struck down, yellow procedure or twist, blue principle. See CRIM_PLAN.md for the Crim meaning.

### `reviewer/NN_slug.html` — rule maps (HTML fragments, one `<section>` each)
```html
<section class="rv" id="jr" data-title="Judicial review" data-short="Part III">
<h2>Judicial review</h2>
<p class="lede">Syllabus III: …</p>
<h3 id="jr-req">The requisites of judicial review</h3>   <!-- every h3 needs an id: TOC, search, "mark read" -->
<div class="codal"><span class="art">Art. VIII, Sec. 1</span>text of the provision…</div>
<div class="test"><b>Four requisites</b><ol><li>…</li></ol></div>
<aside class="note trap"><strong>Trap:</strong> …</aside>       <!-- also: note gat (professor), note news, note warn -->
<div class="ex"><p class="q">problem</p><p class="a"><strong>Answer:</strong> …</p></div>
<div class="tw"><table>…</table></div>
<a class="eref" data-e="n26-1">practice essay link</a>
</section>
```
Case names in plain text are linked automatically (caselink.py). `00_method.html` holds the exam method; its `id="method-numbers"` table feeds the "Numbers" search group.

### `lists/*.json` — recall drills
`id`, `t` (topic), `title`, `ask` (the prompt), `items` (2–12 strings), `ordered` (true if order matters), `src`, `rv` (rule-map heading id to jump to), `hook` (mnemonic), `cases` (case ids). Build validates all references.

### `exams/mcq.json`
`id`, `exam` (e.g. "2013 Midterm"; groups the quiz), `n`, `t`, `cov` ("in"/"out" of this year's coverage), `q`, `c` (choices), `a` (index of the answer), `e` (explanation), `cs` (case ids), `k` (note when the circulated key is doubtful), `story` (id in `stories.json` for stories several items share).

### `exams/essays.json` and `exams/news.json` — essay problems
`id`, `exam`, `n`, `t` (topic keys), `cov`, `minutes`, `prompt`, `ask`, `issues` (issue ids), `core` (points a good answer must hit), `cases`, `model` (full model answer), `points` (`[[label, pts], …]` summing to 10: the self-grading rubric), `note`. build.py also needs a short title per id in its `SHORT` dict.

### `exams/clear.json` — id → `{"C","L","E"?,"A","R"}`, at most 125 words: the short back-page answer.
### `exams/issues.json` — `{"groups":[{"g": group name, "items":[{"id","l" label,"h" hint,"rv" rule-map id}]}]}`: the issue checklist, used by the Issue spotter and the printable.
### `dg_reviewer.json` — case id → the block's class-reviewer text for that case (shown collapsed in the case card).

### Built into build.py (edit there)
- `TOPICS`: `(key, name, syllabus part, rule-map section id)`.
- `SHORT`: essay id → short title.
- `plan`: the day-by-day study plan. Item = `P(time, text, rv=[ids], e=[essay ids], sp=[spotter ids], go='action', goL='button label')`. Actions: `due`, `session`, `fix`, `print`, `mcq:<exam>`, `lists:<topic|due>`, `blur:<section id>`, `drill:<cr|fc|rc|mix>:<topic,topic|all|anchors>`. All validated.
- `examDate` in `D`.

## 3. `app.js` modules (in file order)

core (`store` = localStorage with prefix `c1_` → **change it**, e.g. `cr1_`) · scope toggle (Consti hid citizenship/territory; remove or reuse for out-of-coverage topics) · tabs · countdown · theme · case modal · SRS (`rate(k, g)`, steps ladder, keys `cr:`/`fc:`/`rc:` cases, `m:` MCQ, `l:` lists, `i:` spotter issues) · Today (plan, stats, rule-map progress) · rule maps (sidebar, TOC, local search) · blur mode + sticky headings · diagrams (steppers, calculators, walk-throughs, Test me, xref links, reading progress) · cases browse · drill setup (`DIRS`, `fmtFor` for Mixed, shuffled rounds) · **card runner** (`runCards`, `drawCard`, `cardDone`, streak, `prevCard`/`undoCard`, `flipFace`, focus mode `setFocus`, swipe, keyboard) · fix list · session · lists · MCQ · essays · issue spotter · essay trainer (timer, pad, CLEAR checklist, rubric) · printables · universal search (`gIndex`, `gSearch`, `gGo`) · scope wiring · boot.

Storage keys used: `srs fix lres qhist qexams sphist spid attempts drafts wid blur sec tab ddir dtop streak focus theme read hideCitTerr`.

## 4. Diagrams (`figures.py`)

Python builds figure HTML and `insert(src, prefix)` places it at anchors in the rule-map files (file prefix = first two characters, e.g. `'02'`). **Keep the helpers, replace all content.**

```python
fig(prefix, 'after'|'before', 'exact unique anchor text in the rule map', 'fid', 'Title', body_html,
    kind='gates', when='fact-pattern trigger words', hook='mnemonic html', wr=write(('C','…'),('L','…'),…),
    cap='caption', notest=False, wall=True)
```
Helpers: `N` node, `vflow`/`hflow` arrows, `grid`, `cmp` comparison table, `hub` mind map, `tl` timeline, `ladder`, `stepper` (tap a stage), `acro` (acronym tiles), `plates`, `zones`, `door`, `X` (link to another figure), `C` (explicit case link), and:
```python
gates([G(question, hint, exit_title, exit_detail, 'no'|'yes' (answer that exits), 'no'|'ok'|'sun'|'acc' (exit color)), …],
      (end_title, end_detail, color),
      facts=[fact('label', 'fact pattern', 'y,n', 'why the Court went that way')])   # 'y?' = arguable
```
Fact paths are validated (must end at an exit or after the last gate). The page turns gates + facts into **Walk it** chips; every figure gets **Test me**; hooks are collected into a **hook wall** on the method page. Calculators are markup in figures.py plus JS in app.js (`.votec`, `.cacalc`, `.plcalc`, `.qwidget` are Consti-specific: replace with Crim calculators).

**CSS class names for new components must be prefixed** (`v…`, `x…`). Generic names collided once with existing app classes and blanked the drills (see LESSONS.md). `tests/viz.js` has a style-leak check; keep it.

## 5. `caselink.py`
Builds aliases from case names (`X v. Y`, first party, plus `EXTRA` spellings) and links mentions in rule-map text (skips headings, links, codal boxes, buttons). Configure: `AMBIG` (short names shared by several cases, resolved by year or by file prefix), `CITE_ONLY` (names that are also people; link only in citation position), `STOP` (never link alone; e.g. "People" — crucial in Crim where most cases are *People v. X*: link by the accused's surname plus year), `EXTRA`. The build prints any unlinked "X v. Y".

## 6. Porting checklist (Consti → Crim)

- [ ] `template.html`: `<title>`, eyebrow (course, professor, block), `<h1>`, scope button (remove or repurpose), focus-bar title, Rule-map legend labels (`Constitution` → `Codal` etc.), MCQ heading ("Gatmaytan's multiple-choice midterms"), footer.
- [ ] `build.py`: docstring, default `--out` name, `TOPICS`, `SHORT`, `plan`, `examDate`, the class-reviewer and hooks loaders (keep), any Consti-only asserts.
- [ ] `app.js`: `store` prefix; scope constants (`OUT_TOPICS`, `OUT_SECS`, `OUT_ISSUES`, `hideCitTerr`); countdown strings (`"Fri, Oct 16 · 10:00 AM"`); case modal's professor box (`Gatmaytan:` label); `KIND_LBL`; `STOPW` (words not masked in fronts; add `people`, `philippines`); `HC_LBL` (hook color meanings); printables text (`sheet1`, `sheet2`); CLEAR labels if his Crim professor wants another format; replace Consti calculators.
- [ ] `figures.py`: delete all `fig(...)` calls and `_RADAR`; write Crim figures; keep the hook wall and legend.
- [ ] `caselink.py`: reset `AMBIG`, `CITE_ONLY`, `STOP`, `EXTRA` for Crim names.
- [ ] `print_sheets.js`: output file names.
- [ ] Tests: `smoke.js`/`features.js` are mostly generic; `viz.js` and `drill.js` reference Consti figure ids, texts and case names. Rewrite those parts.
