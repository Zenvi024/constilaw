# CLAUDE.md: Consti 1 finals desk (read this first, every session)

This repo builds Zen's personal study site for **Constitutional Law 1** (Prof. Dante B. Gatmaytan, UP College of Law, First Semester 2026). The midterm desk is done. We are now extending it into **one desk for the whole course** for the finals. `PLAN.md` holds the batch checklist and progress log; do only the batch you are asked to do.

## The person and how to talk to them

- Zen (Vinzen Josh L. Borja; "Vinzen Borja" in formal contexts). Refer to Zen by name; do not assume pronouns.
- Always grammatical. APA 7 citations unless told otherwise. SI units. Philippine pesos. 12-hour time.
- Zen reports bugs with short messages and screenshots. Fix the root cause, explain it in one or two plain sentences, and test the exact flow Zen used.
- When Zen says "suggest, don't implement" or "show me the plan first", do exactly that.
- Honest, kind, concrete assessments. No hype.

## The exam (decided; don't re-ask)

- **Finals: cumulative oral exam**, from the first syllabus case (Obergefell) to the last (Goh v. Bayron). **Citizenship and Territory (syllabus IV.A and IV.B.1) are excluded**, as at midterms: keep the existing scope toggle and those sections exactly as they are.
- Format: **fishbowl**, one-on-one with the professor, 15–30 minutes. Zen draws a prompt, mostly a **major current news event** ("news cards", like the midterm questions), gets a reasonable time to think, then applies constitutional doctrines and cases. If the first answer doesn't satisfy, a second round; then another draw.
- Zen's target date: **Wednesday, December 16, 2026** (sign-ups vary). Countdown targets that date.
- Grade weights: recitation 50%, midterm 20%, final 30%.
- **Exam-day rule:** on an exam day, check the time before discussing anything that could be an exam question. During the exam window, don't.
- Past exams in `sources/finals/sources_zip/A_my_files/past_exams/` (2024 finals, 2020 finals, midterms 2013, 2015, 2016 and 2024) show the style: a news item plus "is it constitutional / resolve / discuss the issues". Zen's own midterm answers and grading are in the session history, not in a file; the questions were: Francisco distinguished, an equal protection problem on legal aid for retired military and uniformed personnel, and Sec. 26 creating a Joint Power Commission (delegation and the ABAKADA legislative veto).

## Deliverables and links

- **The desk (extend this one):** https://claude.ai/artifact/8Qy79tVdLwLuCMArSZGDmG. From a new session, first `Artifact action: read` with that URL, then publish to the same URL (pass `url`). Keep the link and Zen's saved progress (localStorage) working.
- **Recit Deck** (full-digest reader for the Nov 3 and Nov 5 sets): https://claude.ai/artifact/N7FiLtQAZQaeAbbR7pEqa7. Leave it alone unless asked.
- The repo is **private** (it holds copyrighted books). Keep it private. Never publish source PDFs.
- Work on branch `claude/nifty-pascal-4lhm8i`. Commit and push after every batch. No pull requests unless Zen asks. Commit messages end with the attribution lines the session gives you; never put a model name in commits or code.

## Repo map

| Path | What it is |
|---|---|
| `site/` | The midterm desk. `app/build.py` → `dist/consti1-midterm-desk.html`. `app/figures.py` (diagram engine), `app/caselink.py`, `app/app.js`, `app/style.css`, `app/template.html`, `tests/*.js` (Playwright). `data/` holds case cards, rule maps, lists, exams, hooks. |
| `handoff/crim-desk-starter-kit/ARCHITECTURE.md` | **Read before touching the desk:** pipeline, every data schema, figure helpers, tests. |
| `docs/LESSONS.md` | What Zen asked for and the bugs not to repeat. Read it. |
| `recit/2026-11-03/` | The Recit Deck builder, plus `tools/parse.py`, the lossless .docx parser. |
| `sources/finals/syllabus.txt` (+ PDF) | The syllabus. |
| `sources/finals/digests_zip/` | **Original .docx digests** (206 files, checksums verified against `MANIFEST.csv`). `my_digests/` = Zen's own; `block_digests/` = Block I-B; `other/` = the Rubi-to-Mangudadatu manual file and a redline. |
| `sources/finals/sources_zip/` | Gathered sources: `A_my_files` (reviewers, notes, past exams, LME 4.0), `B_articles`, `C_statutes`, `D_decisions` (full texts; `_REQUIRED` = the 2025–2026 cases with resolutions and separate opinions), `E_news` (40 dated events; `NEWS_INDEX.md`), `F_videos` (28 transcripts of the professor's videos), `MISSING.md`. |
| `finals-intake/` | Batch 1 output: `syllabus.json` (parsed syllabus), `digest_index.json`, `coverage.json`, **`FINALS_COVERAGE.md`** (case-by-case sources), `parsed/my_digests.json` (lossless parse of all 183 single digests), `tools/`. |

## Source rules (non-negotiable)

1. **Source priority for each case:** Zen's own single digest (`my_digests/`) → Zen's compilations (`[01] Zen's Consti 1 Digests`, `ZENS CONSTI DIGESTS 2.0`) → the Rubi-to-Mangudadatu manual file → Block I-B digests. Use the full-text decision (`D_decisions/`) to verify holdings, votes, dates and ponentes, and the case's own text wins over any digest. Flag conflicts in the card's `w` field; don't silently "correct".
2. **Nothing omitted, except the WRITE boxes and the 5×8 card** (Zen, Nov. 27, 2026: see "Zen's rules from Nov. 27" below). Digests are parsed with `finals-intake/tools/parse.py` (lossless). The reader shows every word of the chosen digest's body (headnote, facts, issues, rulings, opinions) but not the yellow "WRITE ▸" boxes or the 5×8 recit card. The word checks (`finals-intake/tools/check.py`, and the rendered-text check in `site/tests/digests.js`) must compare the body only, excluding those parts.
3. **One digest per case** (replaces the old "other version" tabs). Pick by this order: Zen's own AI digest (`my_digests/`, then Zen's compilations) → the study group's manual digest (Rubi-to-Mangudadatu file) → the Block I-B digest. Where Zen has two digests of the same case (Bengzon v. Senate Blue Ribbon, Padilla, Neri, Agcaoili), keep the fuller one (more words, more issues) and drop the other. Byte-identical copies: keep one.
4. Syllabus typos: "General v. Urra" = General v. Urro; "Gudani v. Sena" = Gudani v. Senga; "Demaisip v. Bacal" = Cuevas v. Bacal (G.R. 139382); "Beltran v. Macasiar" = Soliven v. Makasiar (G.R. 82585); "Zaldivar v. Gonzales" = Zaldivar v. Sandiganbayan (1988); Ong v. Senate Tricomm is G.R. No. 275469.
5. Some cases appear under two headings, with a different focus in each (e.g. Agcaoili: issue 4 under legislative investigations, issues 1–3 under amparo; Padilla; Gaminde; Bengzon v. Drilon; Republic v. Sereno; Marcos v. Robredo; Francisco). One card, tagged to both places, with the right issue emphasized in each.
6. News items in `E_news/` were gathered after the model's knowledge cutoff. Use the saved article PDFs and the full-text decisions as the source of truth; never fill gaps from memory.
7. **New uploads:** when Zen uploads more files (for example the Senate impeachment rules, P&S, or articles), first commit them to `sources/finals/extra/` and push, then use them. Chat uploads vanish when the container resets.
8. Books on hand: `Constitutional Law in the Philippines.pdf` at the repo root is Gatmaytan's 2015 *Government Structure*, the predecessor of the assigned *P&S* (2024); use it for his views until P&S arrives, and note where it may be outdated. *LME* 4.0 is in `A_my_files/books/` (the syllabus assigns the 5th ed.; 4.0 is accepted).
9. The professor's own views (his articles in `B_articles/`, video transcripts in `F_videos/`, LME 4.0) go in highlighted "professor" boxes and the card's `g` field. He tests them.

## Zen's rules from Nov. 27, 2026 (apply to every batch, and retrofit what exists: Batch 4R)

- **No names, no sources on the page.** Zen shares the desk with others. Never show "Zen", "Zen's digest", "Zen's files", "manual digest", "block digest" or any source label in visible text (case cards, `w` fields, digest headers, tabs). Keep source notes in the repo (FINALS_COVERAGE.md, PLAN.md), not on the page. A card's `w` may still flag conflicts, phrased neutrally ("the digests disagree on…").
- **One digest per case**, chosen by the order in source rule 3. No version tabs.
- **Digest reader:** drop the yellow "WRITE ▸" boxes and the 5×8 recit card. Keep text, bold, italics, underline, indents, bullets and numbering. Font colors go; **all highlights become one yellow**.
- **Back button.** Opening a digest (from a card, a rule map, the Digests list) or a case card (from a rule map, a list, a digest) must offer "← Back" that returns to the exact place Zen came from (same tab, same scroll position, same open card). Keep a small navigation stack; Esc and the browser/phone back gesture should do the same.
- **Case card layout (three levels):**
  1. **At a glance:** the one-line summary (`s`) at the top; then the **doctrine** (`r`, the most prominent block); then quick facts (`f`) and quick ruling (`h`), each two or three lines at most; hook, professor box and warning stay.
  2. **Detailed summary** (collapsed, opens on tap): one row per issue from the digest: the issue as a question, the answer (YES/NO), and the ratio in two to four sentences; then the vote and the notable separate opinions. Stored in `site/data/case_iss.json` (id → `{"iss": [{"q", "a", "why"}], "vote", "ops"}`), merged into the card by build.py. Cover every issue in the digest, main and side.
  3. **Read the full digest** button.
  Keep `r`, `f`, `h`, `s`, `test`, `x`, `g`, `w` working: the drills (Case → rule, Rule → case, Facts → case, Mixed), search, lists and printables read them. Shorten an over-long `r` into a doctrine that fits a flashcard back; move the extra detail into `iss`.
- **Diagrams: neater, never less accurate** (Zen, confirmed Nov. 27). Keep every rule, exception, case and vote a diagram needs; if it has to be full and complicated, it stays full and complicated. What changes is the look: clean layout, consistent spacing, short labels on the face with the details one tap away (hint, walk-through, Test me), no crowding. Split a crowded diagram into two clear ones rather than cutting content.
- **No CLEAR boxes on diagrams.** Remove the "On the exam, write" (`wr=`) boxes from every diagram in every rule map, midterm and finals; don't add them to new ones. (The essay trainer's own CLEAR answer checklist is a separate feature and stays unless Zen says otherwise.) Keep hooks, "Say it in orals" and Test me.
- **Text first, diagrams last.** Within each rule-map section (each `h3`): the constitutional provision (codal box), then the explanation and cases, then the professor's boxes, traps, news and warnings, and only then the section's diagrams, placed at the end of the section. Apply to every rule map, midterm and finals.

## Quality bar (same as midterms, or better)

Every finals case gets a full card (`id n y t sub a r f h test x g w s` plus `iss`, see ARCHITECTURE.md and the Nov. 27 rules above), a 1–3 word color-coded hook in `case_hooks.json`, and a link from its rule map. Every syllabus part gets a rule map with figures that make Zen **apply** the law (decision gates with real fact patterns, walk-throughs, "Use it when" triggers, memory hooks, Test me covers), a **"Say it in orals"** line (the spoken structure: rule, case, application, answer), recall lists, and flashcards in every direction (Case → rule, Rule → case, Facts → case, Mixed), **flip-and-grade, never multiple choice**. The orals batch adds the fishbowl simulator (draw a news card, thinking timer, answer timer, likely follow-up, model outline with the doctrines and cases to cite).

Don't let quality slide in later batches: copy the patterns already in `site/` (look at an existing rule map and its figures before writing a new one), and run every check.

## UI rules Zen set

- Flashcards: flip and self-grade (Again, Hard, Good, Easy); never multiple choice. Rounds feel random.
- Motion: quick and calm (about 0.15 s fades). No 3D spins, no fly-outs.
- Case names on cards centered and prominent. Streak counter. Previous card with full undo. Swipe on phones. Focus mode.
- Readable sans-serif type (the Recit Deck uses Atkinson Hyperlegible); tight but comfortable spacing; nothing tiny. Light and dark themes.
- Prefix every new CSS class; generic names (`.facts`, `.test`, `.chip`, `.clock`) once blanked the drills. `site/tests/viz.js` checks for leaks.

## Verification before every publish

`python3 site/app/build.py`, then `node site/tests/smoke.js`, `features.js`, `viz.js`, `drill.js`, `nav.js`, `digests.js`, `fishbowl.js`, `course.js` (all must pass at 400 px and 1280 px, light and dark, no console errors, no horizontal scroll), plus the digest word check. Look at one or two screenshots. Then commit, push and publish to the desk URL.

## Size

Artifact pages max out at 16 MB. The desk is about 1.5 MB. All 183 single digests as parsed JSON are 15 MB but gzip to about 2.8 MB, so embed them compressed (base64 of gzip, decoded in the browser with `DecompressionStream('gzip')`) and decode on demand.
