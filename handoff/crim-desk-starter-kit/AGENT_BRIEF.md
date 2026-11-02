# Agent brief: build Zen's Crim Midterm Desk

## 1. The user

- **Zen** (Vinzen Josh L. Borja), first-year student at the **UP College of Law**, block 1-B. From Lucena City, Quezon; lives in Quezon City during the term. Studies on a MacBook and an iPhone, often on commutes.
- His other skills/environments may include **crim-case-digest** and **crim-reviewer** (Criminal Law 1, LAW 109, Prof. Gutierrez). If they are available, read them first: they encode his block's digest format and his professor. Confirm the course code, professor and exam date from the syllabus he uploads; do not assume.
- **Writing rules he set:** always grammatically correct; APA 7 citations unless told otherwise; SI units; Philippine pesos (₱); 12-hour time ("10:00 AM", never "10:00").
- He reads a lot of what you write on his phone. Be clear and specific; no filler.

## 2. What to build

A **single self-contained HTML file** (one page, all CSS/JS/data inlined, works offline, phone and laptop, light and dark mode) that is his entire midterm review for Criminal Law. It should match the Consti site in `reference/consti1-midterm-desk.html` feature for feature, with the content replaced and the crim-specific features in `CRIM_PLAN.md` added.

The Consti site has these tabs (keep them all):

| Tab | What it does |
|---|---|
| **Today** | Countdown; day-by-day study plan with one-tap actions; "Start session" (fix list + due cards + new items mixed); fix list (missed items return until answered right twice); stats; rule-map reading progress |
| **Rule maps** | One reviewer section per syllabus part, written by you from his materials: codal boxes, tests, traps, professor's views, news, worked examples, last-minute checklist. Sticky heading bar, blur mode (hide key terms/numbers, tap to reveal), "Mark this part read", local search, every case name linked to its card. **Diagrams** inside: decision gates with click-through fact-pattern walk-throughs, comparisons, timelines, calculators, memory hooks, "On the exam, write" CLEAR lines, Test-me covers |
| **Lists** | Every enumeration and set of requisites (elements, requisites, kinds) as recall drills |
| **Cases** | Browse all case cards (filters, hooks, anchor tag) and a **flashcard drill**: Case → rule, Facts → case, Rule → case, Mixed. Flip cards, self-graded Again/Hard/Good/Easy with spaced repetition; streak counter; Previous (with full undo); keyboard (Space, 1–4, ←); swipe on phones; focus mode; color-coded 1–3 word hooks |
| **Past exams** | Professor's past MCQs as quizzes (with notes where the circulated key is doubtful) and essay problems |
| **Issue spotter** | Read a past problem, tick the issues you see, compare with the key; misses go to the fix list |
| **Essay trainer** | Timed writing pad with word target, model answer, a short "back-page" CLEAR answer, and a self-grading rubric |
| **Printables** | One-page folio (8.5 × 13 in) PDFs: issue checklist and anchor cases, auto-fitted |

Plus: universal search (one box searches everything), theme switch, countdown in the header.

## 3. How to work

1. **Read everything he uploads first**: syllabus (it defines coverage and the case list), codal, class reviewers, block digests, past exams, professor's own writings. Build an inventory before writing anything.
2. **Ask only what you cannot find**: exam date/time/format/coverage cut-off, how many problems, answer-sheet rules, professor's known preferences. Ask once, in one message.
3. **Build the data first, then adapt the code** (see ARCHITECTURE.md porting checklist). Validate in `build.py` with asserts, as the Consti build does.
4. **Verify every case card** against the block digest and the class reviewer; where sources conflict, follow the decision itself, note the conflict on the card (`w` field), and never invent a fact, year, vote or G.R. number. Where the class reviewer is wrong, do not adopt the error; flag it.
5. **Test** with Playwright at 400 px and 1280 px, light and dark (tests in `code/tests/` show how). Screenshot and actually look at new screens.
6. **Publish** as an Artifact (the single HTML file) when he asks, and republish to the same URL on updates. Commit and push to the branch you are given.
7. **When he asks for suggestions and says "don't implement yet", only suggest.** Number them so he can pick ("implement 1, 2, 5").
8. **Do not run multi-agent workflows or fan-out without asking him first.**
9. **Calendar:** he may ask you to plan his review week and block it on his Google Calendar (the personal one, `[ Zen's Calendar ] 2026+`). Always show the plan first and wait for "go"; he decides when the site's Today plan is updated too.
10. **Exam day:** the room rules for Consti banned all devices (a violation meant a 5.0). If he asks about an exam question on exam day, check the time first; only discuss it after the exam has ended.

## 4. Quality bar

- **Accuracy over volume.** Every rule, number, period, penalty and case holding must come from the codal or his materials. Crim is number-heavy (penalty ranges, periods, ages, amounts): one wrong number costs him points.
- **Answer-ready writing.** Rule maps state the rule, then the test, then the trap, then how to write it in an exam answer. Model answers use **CLEAR** (Conclusion, Legal basis, Exception if any, Analysis, Restatement), about 80–120 words, because that is the format his school's essay module teaches and he trained on it. Confirm whether his Crim professor wants the same.
- **Look and feel:** the Consti design (Spectral display, Libre Franklin body, IBM Plex Mono for small labels only; navy accent; yellow for traps). One color code everywhere: blue = the rule, green = valid/convicted/goes on, red = void/acquitted/ends, yellow = trap/exception. Calm, quick motion (≈0.16 s fades), centered case names on flashcards.
- **No multiple-choice hints in flashcards.** He asked for flip-and-self-grade only.

## 5. Deliverables checklist

- [ ] Data: topics, cases (all syllabus cases), hooks, rule maps (one per syllabus part + exam method + news if relevant), lists, past MCQs, essays with model + CLEAR answers + rubrics, issue taxonomy, numbers table, day plan
- [ ] Crim features from CRIM_PLAN.md (penalty trainer at minimum)
- [ ] Diagrams for every decision-type rule (gates + fact patterns that walk through)
- [ ] Build passes all asserts; all tests pass at 400/1280, light/dark; no horizontal overflow; no console errors
- [ ] Printables generated
- [ ] Published, link given to him
