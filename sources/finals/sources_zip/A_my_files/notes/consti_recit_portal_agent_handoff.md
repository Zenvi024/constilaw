# Constitutional Law I — Recitation Case Portal: Complete AI Agent Handoff & Architecture Guide

## 1. Purpose of This Handoff Package
This document and accompanying code bundle provide a complete technical and functional handoff of the **Constitutional Law I — Recitation Case Portal** (`consti_recit_cases.html` and its generator `build_app.py`). It is designed so that another AI agent can immediately understand:
1. **What was built and how it evolved** across the conversation.
2. **How the user's `.docx` case digests are formatted and parsed** (including the `case-highlighter` color-coding system, `WRITE ▸` shorthand blocks, and verbatim `5×8 RECIT INDEX CARD NOTES`).
3. **The exact JSON data schema (`CASES_DATA`)** expected by the front-end application.
4. **All interactive features, views, state persistence (`localStorage`), Dark Mode rules, and keyboard shortcuts** that must be preserved when generating the portal for next week's Constitutional Law I recitation coverage.

---

## 2. Files Included in `consti_recit_portal_handoff_bundle.zip`
| File Name | Description |
| :--- | :--- |
| `CONSTI_RECIT_PORTAL_AGENT_HANDOFF.md` | This comprehensive handoff specification, schema reference, and step-by-step build guide. |
| `consti_recit_cases.html` | The complete, self-contained single-file production web application (34 cases: 16 Tuesday + 18 Thursday). |
| `build_app.py` | The complete Python generator script containing the `python-docx` rich-text parser (`parse_docx`), `METADATA_MAP`, `finalize_case` helper for direct JSON cases, and `HTML_TEMPLATE`. |
| `html_template_only.html` | The standalone HTML/CSS/JS shell with the `__CASES_JSON__` placeholder — allows the next agent to inject a new week's `CASES_DATA` JSON array without modifying the parser. |
| `cases_data_34.json` | The extracted, pretty-printed JSON array of all 34 cases currently in the portal, serving as a golden reference for the exact case schema. |

---

## 3. Conversation History & Chronological Evolution
Across the session, the user (a Philippine law student preparing for Tuesday and Thursday recitations in Constitutional Law I) iteratively requested the following builds and upgrades:

1. **Initial Portal Build (Turn 1 — 10 Cases)**:
   - User uploaded 10 `.docx` digests (`National_Amnesty_Commission_v_COA_2004`, `DENR_v_DENR_Region_12_Employees_2003`, `Province_of_North_Cotabato_v_GRP_Peace_Panel_2008`, `Marcos_v_Manglapus_1989`, `De_Leon_v_Duterte_2020`, `Dela_Cruz_v_COA_2001`, `Civil_Liberties_Union_v_Executive_Secretary_1991`, `Estrada_v_Desierto_2001`, `Marcos_Jr_v_Republic_2014`, `Republic_v_Sandiganbayan_2003`) and asked for a navigable website for Tuesday recitation.
2. **Syllabus Alignment & Full Tuesday Set (Turns 2–3 — Expanded to 16 Cases)**:
   - User shared syllabus screenshots and 6 additional `.docx` digests (`Duterte_v_HOR_Digest (1).docx`, `Generillo_Jr_v_Senate_2026_Digest.docx`, `Torreon_v_HOR_Committee_on_Justice_Petition_Digest (1).docx`, `Pormento_v_Estrada_2010_Digest.docx`, `Pamatong_v_Duterte_2019_Digest.docx`, `Buenafe_v_COMELEC_2022_Digest.docx`).
   - Grouped the 16 Tuesday cases into 6 syllabus clusters (`IV.A` Power of Impeachment `#109–#111`, and `IV.B.1` to `IV.B.5` Executive Department `#323–#335`).
3. **Thursday Coverage + Day Set Switcher + Distraction-Free Focus Mode (Turns 4–5 — Expanded to 31 Cases)**:
   - User uploaded 9 Thursday digests (`Banda v. Ermita`, `Biraogo v. PTC`, `Blaquera v. Alcala`, `NEA v. COA`, `Hutchison v. SBMA`, `Zabal v. Duterte`, `Pimentel v. Aguirre`, `Sarmiento v. Mison`, `Calderon v. Carale`) and then 6 more Thursday digests (`General v. Urro`, `De Rama v. CA`, `De Castro v. JBC`, `Pimentel v. Ermita`, `Soriano v. Lista`, `Manalo v. Sistoza`).
   - Added the **Recitation Day Set Switcher** (`📅 Tuesday Set`, `📅 Thursday Set`, `📚 All`) in the top header.
   - Added **Focus Mode (`🎯 Focus` / Shortcut `F`)** that hides the top navigation bar, color legend, left sidebar, and sub-toolbar, leaving a compact floating pill bar at the top.
   - Added **Tuesday ↔ Thursday Case Transfer (`↪ Move to Thu` / `↩ Move to Tue`)** on individual cases plus a bulk **`↪ Move Unready Tue → Thu`** button and **`↺ Reset Sets`** button in the sidebar so uncovered Tuesday cases can roll over to Thursday.
4. **Retention & Final Upgrades (Turns 6–8 — Expanded to 34 Cases + Auto-Save Progress + Dark Mode)**:
   - User uploaded 3 additional Thursday digests under **IV.B.8 Power of Appointment** (`Velicaria-Garafil_v_OP_2015_Digest.docx` `#356`, `Matibag_v_Benipayo_2002_Digest.docx` `#357`, and `Larin_v_Executive_Secretary_1997_Digest.docx` `#358`), bringing Thursday Set to **18 cases** and total coverage to **34 cases**.
   - Added **Full Browser Progress Persistence** (`saveAppState()` / `loadSavedState()` in `localStorage`) with a live `💾 Progress Auto-Saved` / `💾 Saved ✓` indicator in the header.
   - Added **Dark Mode Support (`🌙 Dark` / `☀️ Light` button + Shortcut `D`)** in both the main header and Focus Mode floating bar, with dark slate surfaces and contrast-adjusted highlight colors.

---

## 4. Complete Inventory of Current 34 Cases & Syllabus Clusters

### A. Tuesday Set (16 Cases · `daySet: "tuesday"`)
| Order | Day # | Syllabus # | Case ID (`id`) | Short Title & Year | G.R. No. & Date | Ponente | Cluster ID |
| :---: | :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 1 | `IV.A #109` | `duterte-v-hor-2025` | Duterte v. House of Representatives (2025; Reso 2026) | G.R. No. 278353 · July 25, 2025 / Jan. 2026 | Leonen, SAJ. (En Banc) | `cluster-cong-1` |
| 2 | 2 | `IV.A #110` | `generillo-v-senate-2026` | Generillo, Jr. v. Senate of the Philippines (2026) | G.R. No. 278334 · Feb. 10, 2026 | Hernando, J. (En Banc) | `cluster-cong-1` |
| 3 | 3 | `IV.A #111` | `torreon-v-hor-justice-2026` | Torreon v. HOR Committee on Justice (2026) | G.R. No. (2026 Petition) · Mar. 30, 2026 | Rule 65 Petition | `cluster-cong-1` |
| 4 | 4 | `IV.B #1 (323)` | `pormento-v-estrada-2010` | Pormento v. Estrada (2010) | G.R. No. 191988 · Aug. 31, 2010 | Corona, C.J. (En Banc) | `cluster-exec-1` |
| 5 | 5 | `IV.B #2 (324)` | `pamatong-v-duterte-2019` | Pamatong v. Duterte (2019) | G.R. No. 240729 · Feb. 5, 2019 | En Banc Resolution | `cluster-exec-1` |
| 6 | 6 | `IV.B #3 (325)` | `buenafe-v-comelec-2022` | Buenafe v. COMELEC (2022) | G.R. Nos. 260374 & 260426 · June 28, 2022 | Zalameda, J. (En Banc) | `cluster-exec-1` |
| 7 | 7 | `IV.B #4 (326)` | `republic-v-sandiganbayan-2003` | Republic v. Sandiganbayan (Swiss Deposits) (2003) | G.R. No. 152154 · July 15, 2003 | Corona, J. (En Banc) | `cluster-exec-2` |
| 8 | 8 | `IV.B #5 (327)` | `marcos-jr-v-republic-2014` | Marcos, Jr. v. Republic (Arelma Case) (2014) | G.R. Nos. 189434 & 189505 · Mar. 12, 2014 | Sereno, C.J. (2nd Div) | `cluster-exec-2` |
| 9 | 9 | `IV.B #6 (328)` | `estrada-v-desierto-2001` | Estrada v. Arroyo / Estrada v. Desierto (2001) | G.R. Nos. 146710-15 & 146738 · Mar. 2, 2001 | Puno, J. (En Banc) | `cluster-exec-3` |
| 10 | 10 | `IV.B #7 (329)` | `de-leon-v-duterte-2020` | De Leon v. Duterte (2020) | G.R. No. 252118 · May 8, 2020 | Leonen, J. (En Banc) | `cluster-exec-3` |
| 11 | 11 | `IV.B #8 (330)` | `clu-v-executive-secretary-1991` | Civil Liberties Union v. Executive Secretary (1991) | G.R. Nos. 83896 & 83815 · Feb. 22, 1991 | Fernan, C.J. (En Banc) | `cluster-exec-4` |
| 12 | 12 | `IV.B #9 (331)` | `dela-cruz-v-coa-2001` | Cruz v. COA (Dela Cruz v. COA) (2001) | G.R. No. 138489 · Nov. 29, 2001 | Sandoval-Gutierrez, J. (En Banc) | `cluster-exec-4` |
| 13 | 13 | `IV.B #10 (332)` | `nac-v-coa-2004` | National Amnesty Commission v. COA (2004) | G.R. No. 156982 · Sept. 8, 2004 | Corona, J. (En Banc) | `cluster-exec-4` |
| 14 | 14 | `IV.B #11 (333)` | `marcos-v-manglapus-1989` | Marcos v. Manglapus (1989) | G.R. No. 88211 · Sept. 15 / Oct. 27, 1989 | Cortes, J. (En Banc) | `cluster-exec-5` |
| 15 | 15 | `IV.B #12 (334)` | `north-cotabato-v-grp-2008` | Province of North Cotabato v. GRP Peace Panel (2008) | G.R. No. 183591 · Oct. 14, 2008 | Carpio Morales, J. (En Banc) | `cluster-exec-5` |
| 16 | 16 | `IV.B #13 (335)` | `denr-v-denr-region-12-2003` | DENR v. DENR Region 12 Employees (2003) | G.R. No. 149724 · Aug. 19, 2003 | Ynares-Santiago, J. (1st Div) | `cluster-exec-5` |

### B. Thursday Set (18 Cases · `daySet: "thursday"`)
| Order | Day # | Syllabus # | Case ID (`id`) | Short Title & Year | G.R. No. & Date | Ponente | Cluster ID |
| :---: | :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| 17 | 1 | `IV.B #14 (336)` | `banda-v-ermita-2010` | Banda v. Ermita (2010) | G.R. No. 166620 · Apr. 20, 2010 | Leonardo-De Castro, J. (En Banc) | `cluster-thu-exec-power` |
| 18 | 2 | `IV.B #15 (337–341)` | `biraogo-v-ptc-2010` | Biraogo v. Philippine Truth Commission of 2010 (2010) | G.R. Nos. 192935 & 193036 · Dec. 7, 2010 | Mendoza, J. (En Banc) | `cluster-thu-exec-power` |
| 19 | 3 | `IV.B #16 (342)` | `blaquera-v-alcala-1998` | Blaquera v. Alcala (1998) | G.R. Nos. 109406, 110642, 111494, 112056, 119597 · Sept. 11, 1998 | Purisima, J. (En Banc) | `cluster-thu-control` |
| 20 | 4 | `IV.B #17 (343)` | `hutchison-v-sbma-2000` | Hutchison Ports v. SBMA (2000) | G.R. No. 131367 · Aug. 31, 2000 | Ynares-Santiago, J. (1st Div) | `cluster-thu-control` |
| 21 | 5 | `IV.B #18 (344)` | `nea-v-coa-2002` | NEA v. Commission on Audit (2002) | G.R. No. 143481 · Feb. 15, 2002 | Carpio, J. (En Banc) | `cluster-thu-control` |
| 22 | 6 | `IV.B #19 (345)` | `zabal-v-duterte-2019` | Zabal v. Duterte (Boracay Closure) (2019) | G.R. No. 238467 · Feb. 12, 2019 | Del Castillo, J. (En Banc) | `cluster-thu-control` |
| 23 | 7 | `IV.B #20 (346)` | `pimentel-v-aguirre-2000` | Pimentel, Jr. v. Aguirre (2000) | G.R. No. 132988 · July 19, 2000 | Panganiban, J. (En Banc) | `cluster-thu-supervision` |
| 24 | 8 | `IV.B #21 (347)` | `sarmiento-v-mison-1987` | Sarmiento III v. Mison (1987) | G.R. No. 79974 · Dec. 17, 1987 | Padilla, J. (En Banc) | `cluster-thu-appointment` |
| 25 | 9 | `IV.B #22 (348)` | `calderon-v-carale-1992` | Calderon v. Carale (1992) | G.R. No. 91636 · Apr. 23, 1992 | Padilla, J. (En Banc) | `cluster-thu-appointment` |
| 26 | 10 | `IV.B #23 (349)` | `manalo-v-sistoza-1999` | Manalo v. Sistoza (1999) | G.R. No. 107369 · Aug. 11, 1999 | Purisima, J. (En Banc) | `cluster-thu-appointment` |
| 27 | 11 | `IV.B #24 (350)` | `soriano-v-lista-2003` | Soriano III v. Lista (2003) | G.R. No. 153881 · Mar. 24, 2003 | Sandoval-Gutierrez, J. (En Banc) | `cluster-thu-appointment` |
| 28 | 12 | `IV.B #25 (351)` | `pimentel-v-ermita-2005` | Pimentel, Jr. v. Ermita (2005) | G.R. No. 164978 · Oct. 13, 2005 | Carpio, J. (En Banc) | `cluster-thu-appointment` |
| 29 | 13 | `IV.B #26 (352)` | `general-v-urro-2011` | General v. Urro (General v. Urra) (2011) | G.R. No. 191560 · Mar. 29, 2011 | Brion, J. (En Banc) | `cluster-thu-appointment` |
| 30 | 14 | `IV.B #27 (353–354)` | `de-castro-v-jbc-2010` | De Castro v. Judicial and Bar Council (JBC) (2010) | G.R. No. 191002 · Mar. 17, 2010 | Bersamin, J. (En Banc) | `cluster-thu-appointment` |
| 31 | 15 | `IV.B #28 (355)` | `de-rama-v-ca-2001` | De Rama v. Court of Appeals (2001) | G.R. No. 131136 · Feb. 28, 2001 | Ynares-Santiago, J. (En Banc) | `cluster-thu-appointment` |
| 32 | 16 | `IV.B #29 (356)` | `velicaria-garafil-v-op-2015` | Velicaria-Garafil v. Office of the President (2015) | G.R. No. 203372 · June 16, 2015 | Carpio, J. (En Banc) | `cluster-thu-appointment` |
| 33 | 17 | `IV.B #30 (357)` | `matibag-v-benipayo-2002` | Matibag v. Benipayo (2002) | G.R. No. 149036 · Apr. 2, 2002 | Carpio, J. (En Banc) | `cluster-thu-appointment` |
| 34 | 18 | `IV.B #31 (358)` | `larin-v-exec-sec-1997` | Larin v. Executive Secretary (1997) | G.R. No. 112745 · Oct. 16, 1997 | Torres, Jr., J. (En Banc) | `cluster-thu-appointment` |

---

## 5. User's `.docx` Case Digest Format & Color-Coding Convention
All `.docx` digests uploaded by the user follow a strict, uniform structure and color-coding system that **must be preserved 100% verbatim**:

### A. Rich-Text Color Classes (`para_to_html` in `build_app.py`)
Each `w:r` (run) in a Word paragraph is converted into HTML spans using these classes:
- **Highlight Colors (`w:highlight`)**:
  - `yellow` → `<span class="hl-yellow">...</span>` (Facts, dates, key entities, statutory triggers)
  - `red` / `magenta` / `darkYellow` → `<span class="hl-orange">...</span>` (Issue questions / `W/N` headers in `WRITE ▸` blocks)
  - `cyan` / `green` / `pink` (or RGB `#FCE4D6` / `#FBCFE8` shading) → `<span class="hl-pink">...</span>` (Core holdings / ratio decidendi / decisive doctrinal phrases)
- **Foreground Font Colors (`w:color`)**:
  - Green (`#008000`, `#15803D`, `#2E7D32`, `#006600`, `#385723`) → `<span class="fg-green">...</span>` (Rulings, answers, disposition, ratio shorthand bullets `① ② ③`)
  - Red (`#C00000`, `#FF0000`, `#B91C1C`, `#990000`) → `<span class="fg-red">...</span>` (`MAIN` / `SIDE` tags, `ASSAILED:`, `D1:`–`D4:` headnote doctrines, cited cases/laws in `WRITE ▸` blocks)
  - Blue (`#0000FF`, `#1D4ED8`, `#1F4E79`, `#2F5597`, `#0070C0`) → `<span class="fg-blue">...</span>` (Sub-bullets `↳` in facts timeline, statutory context)
  - Grey (`#595959`, `#7F7F7F`, `#64748B`, `#808080`) → `<span class="fg-grey">...</span>` (Parenthetical notes / secondary citations)
- **Typography**:
  - `r.bold` → `<strong>...</strong>`
  - `r.italic` → `<em>...</em>`
  - `r.underline` → `<u>...</u>`

### B. Document Block Sequence in `.docx` Digests
`parse_docx(filepath)` iterates through paragraphs and tables in document order:
1. **Title Paragraph**: e.g., `De Rama v. Court of Appeals (2001)` → stored in `case["fullTitle"]`.
2. **Table 0 (Headnote Metadata Table)**:
   - Row 0: `Topic | Subtopic` (left) and `G.R. No. / Date / Ponente` (right)
   - Row 1: `Petitioner/s` (left) and `Respondent/s` (right)
   - Row 2: `Doctrine` (`case["doctrines"]` and `case["doctrinesPlain"]`)
3. **Header `WRITE ▸` Table**:
   - Single-cell table starting with `WRITE ▸` immediately after the Headnote table → `case["headerWrite"]` (contains `[  ] CASE TITLE (YEAR) · Ponente · Vote – DISPO`, `ASSAILED:`, `D1:`, `D2:`, etc.).
4. **FACTS Section**:
   - Table with header `FACTS` → `case["facts"]`, followed by a `WRITE ▸` table → `case["factsWrite"]` (`★ Ⓐ PET/RES`, `★ Ⓑ ...`, `↳ ...`).
5. **Optional Pre-Issue / Arguments Tables**:
   - `PETITIONER/S ARGUMENTS` / `RESPONDENT/S ARGUMENTS` → `case["arguments"]` and `case["argumentsWrite"]`.
   - `FRAMED ISSUE` or `OVERVIEW` blocks → `case["framedIssue"]` / `case["preIssueBlocks"]`.
6. **ISSUES / GROUNDS Section**:
   - Each issue starts with a table whose header matches `ISSUE_HEADER_RE` (`ISSUE 1`, `ISSUE 2`, `PROCEDURAL`, `GROUND I`, `RESO ISSUE 1`, etc.), containing:
     - `kind` (`Main – Substantive (SYLLABUS TOPIC)`, `Side – Procedural`, etc.)
     - `question` (`W/N ...`) and `answer` (`<strong>YES</strong>` / `<strong>NO</strong>`)
     - Optional `subIssues` rows (`1a.`, `1b.`)
     - Optional `issueArguments` (`PETITIONER/S ARGUMENTS`, `RESPONDENT/S ARGUMENTS`)
     - `rulingHeading` (`RULING and RATIO DECIDENDI`) and `ruling` paragraphs
     - Optional `legalBases` (`LEGAL BASES`)
     - Associated `WRITE ▸` table (`iss["write"]`)
7. **FINAL DECISION / RELIEFS Table + `WRITE ▸` Table**:
   - Stored in `case["finalDecision"]` and `case["finalDecisionWrite"]`.
8. **SEPARATE OPINIONS / NOTES Table + `WRITE ▸` Table**:
   - Stored in `case["separateOpinions"]` and `case["separateOpinionsWrite"]`.
9. **5×8 RECIT INDEX CARD NOTES Section (`FRONT` and `BACK` Tables)**:
   - At the end of each `.docx` digest, two tables labeled `FRONT` and `BACK` compile the exact 5×8 index card lines (`case["cardFront"]` and `case["cardBack"]`, each an array of `{"html": ..., "plain": ...}`).

---

## 6. Exact Case Object JSON Schema (`CASES_DATA[i]`)
Every object in the `CASES_DATA` JavaScript array follows this exact schema:

```json
{
  "id": "velicaria-garafil-v-op-2015",
  "daySet": "thursday",
  "dayOrder": 16,
  "order": 32,
  "shortTitle": "Velicaria-Garafil v. Office of the President",
  "year": "2015",
  "grShort": "G.R. No. 203372",
  "dateShort": "June 16, 2015",
  "ponenteShort": "Carpio, J. (En Banc)",
  "cluster": "IV.B.8 · Branches of the Government – Executive / Powers and Functions of the President: Power of Appointment",
  "clusterId": "cluster-thu-appointment",
  "syllabusNum": "IV.B #29 (356)",
  "recitTag": "Power of Appointment · Midnight Appointments Ban (Sec. 15, Art. VII), EO 2 & 4 Elements of Valid Appointment",
  "outcomeBadge": "DENIED / DISMISSED; APPTS VOID (8–6)",
  "outcomeType": "dismissed",
  "fullTitle": "Velicaria-Garafil v. Office of the President (2015)",
  "introNotes": [],
  "topicSubtopic": "The Executive – Appointing Power; Ban on Midnight Appointments (Sec. 15, Art. VII)",
  "topicSubtopicHtml": ["<strong>...</strong>"],
  "grAndPonente": ["<strong>...</strong>"],
  "petitioners": ["..."],
  "respondents": ["..."],
  "doctrines": ["<p-html-1>", "<p-html-2>"],
  "doctrinesPlain": ["<plain-1>", "<plain-2>"],
  "headerWrite": ["<line-html-1>", "<line-html-2>"],
  "headerWritePlain": ["<line-plain-1>", "<line-plain-2>"],
  "preFactsSections": [],
  "facts": ["<p-html-1>", "<p-html-2>"],
  "factsPlain": "<joined-plain-facts>",
  "factsWrite": ["<line-html-1>", "<line-html-2>"],
  "framedIssue": null,
  "arguments": [],
  "argumentsWrite": [],
  "preIssueBlocks": [],
  "issues": [
    {
      "num": 1,
      "label": "ISSUE 1",
      "part": "",
      "partContext": null,
      "kind": "Main – Substantive (SYLLABUS TOPIC)",
      "question": "W/N ...",
      "questionPlain": "W/N ...",
      "answer": "<strong>YES</strong>",
      "answerPlain": "YES",
      "subIssues": [
        { "question": "1a. W/N ...", "answer": "<strong>NO</strong>" }
      ],
      "issueArguments": [
        { "heading": "PETITIONER/S ARGUMENTS", "paras": ["..."] }
      ],
      "rulingHeading": "RULING and RATIO DECIDENDI",
      "ruling": ["<p-html-1>", "<p-html-2>"],
      "rulingPlain": "<joined-plain-ruling>",
      "legalBasesHeading": "LEGAL BASES",
      "legalBases": ["<p-html-1>"],
      "write": ["<line-html-1>", "<line-html-2>"]
    }
  ],
  "postIssueSections": [],
  "finalDecision": ["<p-html-1>", "<p-html-2>"],
  "finalDecisionWrite": ["<line-html-1>"],
  "extraDispoSections": [],
  "separateOpinions": ["<p-html-1>"],
  "separateOpinionsWrite": ["<line-html-1>"],
  "cardFront": [
    { "html": "<line-html>", "plain": "<line-plain>" }
  ],
  "cardBack": [
    { "html": "<line-html>", "plain": "<line-plain>" }
  ]
}
```
> **Tip for the Next AI Agent**: In `build_app.py`, the helper function `finalize_case(c)` (lines 1183–1211) automatically generates `doctrinesPlain`, `headerWritePlain`, `factsPlain`, `questionPlain`, `answerPlain`, `rulingPlain`, `cardFront`, and `cardBack` from `cardFrontHtml` and `cardBackHtml` whenever you construct a case dictionary in Python without a `.docx` file.

---

## 7. Complete Feature Set & UI Architecture

### 1. Recitation Day Set Switcher (`tuesday` | `thursday` | `all`)
- Located in `#mainTopHeader` (`#daySetBtnTuesday`, `#daySetBtnThursday`, `#daySetBtnAll`).
- Dynamically filters the left sidebar, 5×8 Index Cards Wall, Topic & Doctrine Synthesis Matrix, Socratic Cold-Call Recit Drill, and Master Quick-Reference Sheet to show either **Tuesday Set**, **Thursday Set**, or **All Cases**.
- Button counts (`📅 Tuesday Set (16)`, `📅 Thursday Set (18)`, `📚 All (34)`) recompute automatically in `updateDaySetUI()` whenever cases are added or transferred between days.

### 2. Tuesday ↔ Thursday Case Transfer (`state.daySetOverrides`)
- Every case has a quick transfer button (`↪ Move to Thu` / `↩ Move to Tue`) in:
  - The left sidebar case list (`[data-transfer-case]`)
  - The Case Reader sub-toolbar (`#readerTransferCaseBtn`)
  - The Focus Mode floating bar (`#focusTransferCaseBtn`)
  - The 5×8 Index Cards Wall (`[data-transfer-case]`)
  - The Master Quick-Reference Table (`[data-transfer-case]`)
- **Bulk Roll-Over**: In the sidebar header (`#sidebarTransferBar`), **`↪ Move Unready Tue → Thu`** (`#transferUnreadyTueBtn`) moves all Tuesday cases not yet marked `Ready ✓` to Thursday's session in one click. **`↺ Reset Sets`** (`#resetDaySetsBtn`) appears whenever any case has been moved, allowing instant restoration of default sets.

### 3. Five Primary Study Views (`state.mainTab`)
1. **📖 Case Reader (`view-reader`)**:
   - **Three Sub-Modes (`state.readerMode`)**:
     - `📄 Full Digest` (`digest`): Complete headnote table, `WRITE ▸ (HEADNOTE)`, quick section-jump bar (`Facts`, `Arguments`, `ISSUE 1..N`, `Final Decision & Opinions`), Facts card + `WRITE ▸ (FACTS TIMELINE)`, Issue cards (with `MAIN` issues highlighted in amber/red) + `WRITE ▸ (ISSUE #)`, and Final Decision & Separate Opinions.
     - `📇 5×8 Index Card` (`card`): Lined index-card view (`Front + Back`, `Front Only`, or `Back Only`) with interactive `[✓]` Recit-Ready checkbox synced on line 1.
     - `⚖️ Split (Digest + Card)` (`split`): Desktop 7-column Full Digest on the left + sticky 5-column scrollable 5×8 Index Card on the right.
   - **📋 Copy Card (`#copyCardNotesBtn`)**: Copies plain-text `FRONT` and `BACK` card notes to the clipboard.
2. **🗂️ 5×8 Index Cards Wall (`view-cards`)**:
   - Displays all 5×8 index cards in the active set, filterable by syllabus cluster (`#cardsClusterFilter`), with two layout modes: **Front + Back Stacked** (`both`) or **Interactive Flip Cards** (`flip`).
3. **🧭 Topic & Doctrine Matrix (`view-matrix`)**:
   - Side-by-side doctrinal comparison tables and synthesis cards organized by syllabus cluster (`renderMatrixView()`), with clickable links (`[data-open-digest]`) that jump straight to any case's full digest.
4. **⚡ Cold-Call Recit Drill (`view-drill`)**:
   - Socratic flashcard simulator with two modes:
     - **🎯 Issue & Ruling Drill (`issues`)**: Prompts with an actual `W/N` issue question (filterable by `★ Main / Syllabus Topic Issues Only` or specific cluster, plus a **🙈 Blind Case Name** toggle); reveals the Answer (`YES`/`NO`), `WRITE ▸` shorthand points, and full Ruling & Ratio Decidendi.
     - **🏛️ Case & Doctrine Spotter (`cases`)**: Prompts with the `WRITE ▸` Facts timeline; reveals the Case Title, G.R. No., Date, Ponente, Vote/Disposition, Headnote `WRITE ▸`, and Doctrines.
5. **📋 Master Sheet (`view-table`)**:
   - One-glance cheat sheet table of all cases in the active set with Syllabus #, Day Set pill, Ready checkbox, Case Title & Subtopic, G.R. No./Date/Ponente, Disposition & Vote badge, and `D1–D4` shorthand doctrines.

### 4. Distraction-Free Focus Mode (`state.focusMode` · Shortcut `F`)
- Toggled via `🎯 Focus` (`#toggleFocusModeBtn`), `#readerFocusBtn`, or pressing `F` (exit with `F` or `Esc`).
- Applies `body.focus-mode`, hiding `#mainTopHeader`, `#caseSidebar`, and `#readerSubToolbar`, and displaying `#focusFloatingBar` with Prev/Next navigation, `📄 Digest | 📇 Card | ⚖️ Split` switcher, `↪ Move to Thu/Tue`, `🖍️ Colors`, `✍️ WRITE ▸`, `🌙 Dark`, and `✕ Exit Focus (F)`.

### 5. Dark Mode Support (`state.darkMode` · Shortcut `D`)
- Toggled via `🌙 Dark` / `☀️ Light` in the top header (`#toggleDarkModeBtn`), Focus Mode bar (`#focusToggleDarkBtn`), or pressing `D`.
- Applies `body.dark-mode` with deep slate surfaces (`#0b1120` background, `#0f172a` cards/sidebar, `#1e293b` secondary panels), dark lined 5×8 index cards, and translucent high-contrast highlighter spans (`.hl-yellow`, `.hl-orange`, `.hl-pink`, `.fg-green`, `.fg-red`, `.fg-blue`, `.fg-grey`).

### 6. Automatic Browser Progress Persistence (`localStorage`)
- Wrapped in `try/catch` inside `saveAppState()` and `loadSavedState()`.
- Keys persisted:
  - `consti_tuesday_recit_ready`: `{ [caseId]: boolean }` (Recit-Ready checkboxes)
  - `consti_day_set_overrides`: `{ [caseId]: 'tuesday' | 'thursday' }` (Day transfers)
  - `consti_tuesday_hl`: `boolean` (Highlights ON/OFF)
  - `consti_active_day_set`: `'tuesday' | 'thursday' | 'all'`
  - `consti_dark_mode`: `boolean`
  - `consti_portal_full_state_v2`: JSON snapshot of `daySet`, `mainTab`, `currentCaseId`, `readerMode`, `cardSide`, `sidebarFilter`, `darkMode`, `highlightsOn`, `writeBoxesOn`, `cardWallCluster`, `cardWallLayout`, `drillType`, `drillFilter`, `drillIndex`, `drillBlindCase`.
- Flashes `#autoSaveBadge` (`💾 Saved ✓` → `💾 Progress Auto-Saved`) on every state change.

### 7. Keyboard Shortcuts
| Key | Action |
| :---: | :--- |
| `←` / `→` | Previous / Next Case (in Case Reader) or Previous / Next Flashcard (in Recit Drill) |
| `1` / `2` / `3` | Switch Reader Mode: `1` Full Digest · `2` 5×8 Index Card · `3` Split View |
| `F` / `Esc` | Toggle / Exit Distraction-Free Focus Mode |
| `D` | Toggle Dark Mode / Light Mode |
| `H` | Toggle Case-Highlighter Color Coding ON/OFF |
| `R` | Toggle Recit-Ready (`✓`) for the current case |
| `/` | Focus Global Instant Search bar |
| `Space` | Reveal Answer & Ratio in Cold-Call Recit Drill |

---

## 8. Step-by-Step Guide for the Next AI Agent (Creating Next Week's Coverage)

When the user uploads next week's `.docx` digests and syllabus screenshots, follow these steps:

1. **Decide Whether to Replace or Append**:
   - Ask or check if the user wants a **fresh portal for next week's Tuesday/Thursday sets** or a **combined multi-week portal**.
2. **Add Metadata Entries to `METADATA_MAP` in `build_app.py`**:
   - For each uploaded `.docx` file, add an entry in `METADATA_MAP` specifying `id`, `daySet` (`"tuesday"` or `"thursday"`), `dayOrder`, `shortTitle`, `year`, `grShort`, `dateShort`, `ponenteShort`, `cluster`, `clusterId`, `order`, `syllabusNum`, `recitTag`, `outcomeBadge`, and `outcomeType` (`"granted"` or `"dismissed"`).
3. **Update `CLUSTER_OPTIONS` and `renderMatrixView()`**:
   - Update the `CLUSTER_OPTIONS` array in `HTML_TEMPLATE` with the new syllabus subtopics/clusters.
   - Update `renderMatrixView()` with synthesis tables/cards for the new cases.
4. **Run `build_app.py` and Validate**:
   - Run `python3 build_app.py` to parse the `.docx` files and output `consti_recit_cases.html`.
   - Check the console output of `build_app.py` (`missing write: []`, `empty ruling: []`) to verify every issue table and `WRITE ▸` block parsed cleanly.
   - If using `html_template_only.html` directly, simply serialize your `cases` list with `json.dumps(cases, ensure_ascii=False)` and replace `"__CASES_JSON__"`.
