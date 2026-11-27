# PLAN.md: Consti 1 finals desk

Read `CLAUDE.md` first. Do **one batch per session** (two at most for small ones). At the end of each batch: run every check, commit, push, tick the box, add a short entry to the progress log, then stop and tell Zen what was done and what's next.

## Starter prompt (Zen pastes this into a fresh session)

```
Repo zenvi024/constilaw. First fetch and check out the branch claude/nifty-pascal-4lhm8i and continue on it. Read CLAUDE.md and PLAN.md in full, then do Batch [N] only. When it's done, run the checks, commit, push, update the progress log in PLAN.md, and stop.
```

Before starting a batch, Zen checks usage (claude.ai: Settings → Usage). If a batch could run past the limit, wait for the reset. If a limit cuts a batch off midway, the last commit is safe; redo that batch.

## Batches

Case counts are finals syllabus entries (see `finals-intake/FINALS_COVERAGE.md` for each case's sources).

- [x] **Batch 1: Intake.** Commit both zips; verify checksums; parse the syllabus; index every digest; match sources to every syllabus case; lossless-parse all single digests and pass the word check; write `CLAUDE.md`, `PLAN.md`, `FINALS_COVERAGE.md`.
- [x] **Batch 2: Desk scaffolding.** Read the live desk first (artifact read). Add the finals syllabus parts and topic keys to `build.py` (scope toggle for Citizenship and Territory unchanged); add a full-digest viewer that embeds the parsed digests gzip-compressed and decodes on demand (with "other version" tabs for the four cases that have two digests); countdown to Dec 16, 2026; rename the desk for the whole course; a rendered-text word check in Playwright. Parse the block and manual compilations per case (they use the same headnote-table template) for the 19 cases that only have block or manual digests. No content cards yet. Tests pass; publish.
- [ ] **Batch 3: V.A.7(c)–8, Congress part 1** (21 cases): SC appellate jurisdiction (Fabian, Carpio-Morales), procedure for the passage of bills, effectivity of laws, question hour, legislative investigations (Balag through Agcaoili issue 4). Cards, hooks, rule map with figures, "Say it in orals", lists, flashcards.
- [ ] **Batch 4: V.A.9, Congress part 2** (14 cases): canvassing, special election, disability, legislative veto of martial law, amnesty, treaties (Pimentel, Bayan Muna, Saguisag, Pangilinan), war, emergency powers, natural resources, amendment, impeachment (Francisco through Torreon, including Duterte v. HoR 2025 and 2026, Generillo 2026, the 2026 Senate trial rulings in the news). Use the professor's impeachment videos.
- [ ] **Batch 5: V.B.1–2(c), the President part 1** (20 cases): qualifications, privileges, succession, prohibitions and exceptions, executive power, control, supervision of local governments.
- [ ] **Batch 6: V.B.2(d)–(e), appointment and clemency** (24 cases).
- [ ] **Batch 7: V.B.2(f)–(k) and V.B.3** (19 cases): Commander-in-Chief (use the professor's martial law video series), emergency powers, foreign loans, foreign affairs, legislation, immunity from suit, the Vice President.
- [ ] **Batch 8: V.C.1–2(o), the judiciary part 1** (28 cases): composition, modes of sitting, appointments, no non-judicial work, salary, removal, fiscal autonomy (RA 12233), jurisdiction, deliberations, voting, requirements as to decisions (LME ch. 7; we have LME 4.0), MR, periods, the PET.
- [ ] **Batch 9: V.C.2(p), administrative and rule-making powers** (about 23 cases): supervision of lower courts, change of venue, the writs of amparo, habeas data and kalikasan (with the rules in `C_statutes/`), RA 10353, rule-making, admission to the bar, integration of the bar.
- [ ] **Batch 10: lower courts, the JBC, automatic release, and the Constitutional Commissions** (about 22 cases): RA 11459, the JBC rules in `C_statutes/JBC_rules/`, Chavez v. JBC with Leonen's dissent, the 2026 Chief Justice selection (news), the CSC, COMELEC and COA cases.
- [ ] **Batch 11: Orals.** The fishbowl simulator: news cards from `E_news/` and `NEWS_INDEX.md` (40 events, March to November 2026), plus the past finals and midterm questions and the earlier news watch. Each card has the facts, the likely follow-up, and a model "Say it in orals" outline with the doctrines and cases to cite. Thinking and answer timers; optional microphone recording for self-review. Update the news watch to the latest available date.
- [ ] **Batch 12: Whole-course pass.** The hook wall, issue radar, comparison tables and flashcards across all topics; "Say it in orals" lines for the midterm parts too; printables (folio); full QA; publish.

## Open items for Zen

- Not obtainable by the gatherer (see `sources/finals/sources_zip/MISSING.md`): P&S (2024) and LME 5th ed. (only LME 4.0 is here); the Gatmaytan articles "Judicial Historical Revisionism", "Averting Diversity", "House Rules" and "Illusion of Intergenerational Equity"; the Senate impeachment trial rules and their 2026 amendment (senate.gov.ph blocks automated downloads; Zen can download manually); De Lima v. Duterte's Nov. 3, 2020 resolution and Leonen's dissent; Torreon's Aug. 5, 2026 resolution; A.M. No. 18-01-05-SC; the SC's 2025 annual report.
- Two cases have digests only inside compilations: Kida v. Senate and Gudani v. Senga (block and manual files). 19 cases in all have only block or manual digests (listed in the Batch 1 report).

## Progress log

- **Batch 1 (Nov. 27, 2026):** Committed both zips (206 digest files, checksums all verified; 294 source files). Parsed the syllabus (335 case entries; 170 in the finals portion). Every finals case has at least one digest: 150 have Zen's own single digest, 1 only Zen's compilation, 19 only block or manual digests; 121 have the full-text decision. All 183 single digests parse losslessly (word check: 0 missing). Fixed the parser to keep a second "FINAL DECISION (RESOLUTION)" label. Wrote CLAUDE.md, PLAN.md and the coverage checklist.
- **Batch 2 (Nov. 27, 2026):** Saved Zen's four extra uploads to `sources/finals/extra/` (the Judicial Historical Revisionism article, the 94 PLJ 493 article, the UP Law impeachment primer, and one page of the 2011 Senate impeachment rules). Confirmed the live desk equals the repo build (title kept as "CONSTI Desk"). Added the nine finals topic keys to `build.py` (hidden in pickers until they have cases), the countdown to Wed, Dec 16 (orals), and a **Digests** tab: the whole syllabus as a list (finals by default), each case opening its full digest in a reader (headnote, facts, every issue, WRITE ▸ boxes, the 5×8 card), with version tabs (Fabian and others with both a manual and a block digest; the four cases with two digests of Zen's), recall mode, full-text search and a "Read the full digest" button on case cards. Digests come from `finals-intake/tools/digest_data.py`: 153 of Zen's digests (30 copies dropped) plus 29 block or manual digests for the cases without one of Zen's (only the two Block I-B masterfiles and the manual file are used; the dated midterm-week block files are unfinished templates). Data: `site/data/finals/syllabus.json` and `digests.json.gz` (2.5 MB gzip, embedded base64; desk now 4.9 MB). New test `site/tests/digests.js`: phone and laptop, both themes, no horizontal scroll, and every word of all 182 digests found in the rendered text (0 missing). All five suites pass. Fixed along the way: content under a part heading inside a digest (Aguinaldo's Part II) was not rendered. **Next:** Batch 3 (V.A.7(c)–8).

