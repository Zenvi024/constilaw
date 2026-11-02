# Crim Midterm Desk — starter kit

Hand this whole folder to the agent that will build the Criminal Law midterm site, together with Zen's Crim repo (syllabus, codal, class reviewers, block digests, past exams).

It contains the complete code of the **Consti 1 Midterm Desk**, the single-file study site Zen used for his Constitutional Law 1 midterm (October 2026), and everything a new agent needs to rebuild the same thing for Crim.

## Read in this order

1. **`AGENT_BRIEF.md`** — who Zen is, what to build, how to work with him, the quality bar. Start here.
2. **`CRIM_PLAN.md`** — how to adapt the site to Criminal Law: topics, data, crim-only features (penalty computation trainer, elements drills, circumstance classifier), and the RPC numbers to verify.
3. **`ARCHITECTURE.md`** — how the code works: build pipeline, every data schema with examples, app modules, the diagram engine, tests, publishing, and a line-by-line porting checklist.
4. **`LESSONS.md`** — bugs that happened, what Zen asked to change and why, and his preferences. Reading this saves hours.

## What's inside

```
code/app/        build.py, app.js, style.css, template.html, figures.py, caselink.py, print_sheets.js
code/tests/      smoke.js, features.js, viz.js, drill.js (Playwright)
reference/
  consti1-midterm-desk.html   the finished Consti site (open it in a browser: this is the target)
  consti-rule-maps/           the 14 Consti rule maps (HTML): the writing standard to match
  data-samples/               1–5 real records of every data file, showing the exact schemas
  consti-README.md            the Consti repo's README
```

## Quick start for the new agent

```bash
mkdir -p site/app site/data site/tests site/dist
cp code/app/* site/app/ && cp code/tests/* site/tests/
# write site/data/... for Crim (see ARCHITECTURE.md), adapt build.py TOPICS etc. (porting checklist)
python3 site/app/build.py            # -> site/dist/<name>.html
node site/tests/smoke.js             # needs Playwright + Chromium
```

The code runs as-is only with Consti data; it is a template to adapt, not a generic engine. `ARCHITECTURE.md` lists every Consti-specific line.

Not included on purpose: the Consti casebook and digest PDFs (copyrighted; keep any repo with course materials **private**), and the full Consti data (the samples show the format).
