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
2. **Nothing omitted.** Digests are parsed with `finals-intake/tools/parse.py` (lossless: text, tables, highlights, colors, lists). Every word of every source digest must appear in the built desk's full-digest view; run the word check (`finals-intake/tools/check.py`, and a rendered-text check in Playwright) before publishing.
3. **Different versions:** 25 groups of files are byte-identical copies; use one. Four cases have two genuinely different digests (Bengzon v. Senate Blue Ribbon, Padilla v. Congress, Neri, Agcaoili); show the fuller one as the main digest and keep the other one tab away. Funa v. Villar's versions differ only in their topic line.
4. Syllabus typos: "General v. Urra" = General v. Urro; "Gudani v. Sena" = Gudani v. Senga; "Demaisip v. Bacal" = Cuevas v. Bacal (G.R. 139382); "Beltran v. Macasiar" = Soliven v. Makasiar (G.R. 82585); "Zaldivar v. Gonzales" = Zaldivar v. Sandiganbayan (1988); Ong v. Senate Tricomm is G.R. No. 275469.
5. Some cases appear under two headings, with a different focus in each (e.g. Agcaoili: issue 4 under legislative investigations, issues 1–3 under amparo; Padilla; Gaminde; Bengzon v. Drilon; Republic v. Sereno; Marcos v. Robredo; Francisco). One card, tagged to both places, with the right issue emphasized in each.
6. News items in `E_news/` were gathered after the model's knowledge cutoff. Use the saved article PDFs and the full-text decisions as the source of truth; never fill gaps from memory.
7. **New uploads:** when Zen uploads more files (for example the Senate impeachment rules, P&S, or articles), first commit them to `sources/finals/extra/` and push, then use them. Chat uploads vanish when the container resets.
8. Books on hand: `Constitutional Law in the Philippines.pdf` at the repo root is Gatmaytan's 2015 *Government Structure*, the predecessor of the assigned *P&S* (2024); use it for his views until P&S arrives, and note where it may be outdated. *LME* 4.0 is in `A_my_files/books/` (the syllabus assigns the 5th ed.; 4.0 is accepted).
9. The professor's own views (his articles in `B_articles/`, video transcripts in `F_videos/`, LME 4.0) go in highlighted "professor" boxes and the card's `g` field. He tests them.

## Quality bar (same as midterms, or better)

Every finals case gets a full card (`id n y t sub a r f h test x g w s`, see ARCHITECTURE.md), a 1–3 word color-coded hook in `case_hooks.json`, and a link from its rule map. Every syllabus part gets a rule map with figures that make Zen **apply** the law (decision gates with real fact patterns, walk-throughs, "Use it when" triggers, memory hooks, Test me covers), a **"Say it in orals"** line (the spoken structure: rule, case, application, answer), recall lists, and flashcards in every direction (Case → rule, Rule → case, Facts → case, Mixed), **flip-and-grade, never multiple choice**. The orals batch adds the fishbowl simulator (draw a news card, thinking timer, answer timer, likely follow-up, model outline with the doctrines and cases to cite).

Don't let quality slide in later batches: copy the patterns already in `site/` (look at an existing rule map and its figures before writing a new one), and run every check.

## UI rules Zen set

- Flashcards: flip and self-grade (Again, Hard, Good, Easy); never multiple choice. Rounds feel random.
- Motion: quick and calm (about 0.15 s fades). No 3D spins, no fly-outs.
- Case names on cards centered and prominent. Streak counter. Previous card with full undo. Swipe on phones. Focus mode.
- Readable sans-serif type (the Recit Deck uses Atkinson Hyperlegible); tight but comfortable spacing; nothing tiny. Light and dark themes.
- Prefix every new CSS class; generic names (`.facts`, `.test`, `.chip`, `.clock`) once blanked the drills. `site/tests/viz.js` checks for leaks.

## Verification before every publish

`python3 site/app/build.py`, then `node site/tests/smoke.js`, `features.js`, `viz.js`, `drill.js` (all must pass at 400 px and 1280 px, light and dark, no console errors, no horizontal scroll), plus the digest word check. Look at one or two screenshots. Then commit, push and publish to the desk URL.

## Size

Artifact pages max out at 16 MB. The desk is about 1.5 MB. All 183 single digests as parsed JSON are 15 MB but gzip to about 2.8 MB, so embed them compressed (base64 of gzip, decoded in the browser with `DecompressionStream('gzip')`) and decode on demand.
