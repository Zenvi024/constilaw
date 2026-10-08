# Consti 1 Midterm Desk

A single-file study site for Constitutional Law 1 (Prof. Gatmaytan), midterm of October 16, 2026.

- `data/cases/` — 167 case cards (165 syllabus cases, Obergefell to John Hay PAC v. Lim, plus two 2025–2026 rulings), 72 anchors.
- `data/reviewer/` — 14 rule maps (HTML fragments), including the exam method and the 2026 news watch.
- `data/exams/` — 59 multiple-choice items (2013, 2015, 2016 midterms; 2026 news), 26 essay prompts with model answers and rubrics, the issue taxonomy, and the news stories used by the MCQs.
- `app/` — `build.py` assembles `dist/consti1-midterm-desk.html`; `print_sheets.js` writes the one-page folio PDFs in `print/`.
- `tests/smoke.js` — Playwright run through every tab at 400px and 1280px, light and dark.

Build: `python3 site/app/build.py && node site/app/print_sheets.js && node site/tests/smoke.js`
