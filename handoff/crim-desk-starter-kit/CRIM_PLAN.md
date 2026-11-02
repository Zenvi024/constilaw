# Adapting the desk to Criminal Law

Everything here is a plan, not content. **Build the topic list, cases and rules only from Zen's syllabus, the codal and his class materials.** The RPC figures in §4 are reminders of what to check; verify every one against the codal text he uploads (and later amendments, e.g. RA 7659, RA 9346, RA 10951, RA 9344 as amended by RA 10630, PD 968 as amended by RA 10707) before using it.

## 1. Topics and rule maps

Derive `TOPICS` from the syllabus headings (one topic per part he will be examined on), and write one rule map per topic plus `00_method` (exam method) and, if his professor uses current events, a news watch. A Crim 1 (RPC Book I) syllabus typically covers: fundamental principles (generality, territoriality, prospectivity; pro reo); felonies (dolo and culpa; motive vs. intent; mala in se vs. mala prohibita); Art. 4 (proximate cause, error in personae, aberratio ictus, praeter intentionem; impossible crimes); stages of execution (Art. 6); conspiracy and proposal (Art. 8); classification of felonies (Art. 9); justifying, exempting, mitigating, aggravating and alternative circumstances (Arts. 11–15); persons liable (Arts. 16–20); penalties (classes, duration, effects, graduation); Arts. 48 (complex crimes), 61–64, 71, 76; the Indeterminate Sentence Law; probation; RA 9344; civil liability. **Use his syllabus's actual order, numbering and coverage cut-off.**

Rule-map structure that worked: the codal provision in a `codal` box → the elements/requisites in a `test` box → cases in order → traps → the professor's views → a worked problem → last-minute checklist.

## 2. Case cards for Crim

Most cases are *People v. [Accused]*, so:
- `id` = accused surname + year if needed (`dela-cruz-2019`); `n` keeps the full title.
- In caselink.py put **People** in `STOP` and link by the accused's name; use `AMBIG` for repeated surnames.
- Add crim fields if useful (the app shows unknown fields only if you add them to the case modal): e.g. `crime` (crime charged → crime convicted), `pen` (penalty imposed and how it was computed), `circ` (circumstances appreciated or rejected).
- **Hook colors for Crim** (update `HC_LBL` in app.js and the legend in template.html): green = conviction affirmed; red = acquitted or conviction reversed; yellow = modified (different crime, penalty or circumstance); blue = a principle or definition (no simple outcome).
- Hooks are 1–3 words, vivid and accurate ("Fake gun robbery", "Dead before stabbing"). Never crude about victims.

## 3. Crim-only features (highest value first)

1. **Penalty computation trainer** (a calculator + drill). Inputs: the prescribed penalty, the stage of execution or degree of participation, privileged mitigating circumstances, ordinary mitigating and aggravating circumstances. Output, step by step: degrees lowered (Arts. 50–57, 61, 68, 69, 71) → the period under Art. 64 (or Art. 63 for indivisible penalties) → the indeterminate sentence (maximum within the period; minimum anywhere within the penalty next lower) → probation eligibility. Show each step as its own line so he learns the method, and add drill problems built from the decided cases with the Court's actual computation as the answer.
2. **Elements drills**: every crime and every circumstance as a list (`lists/*.json`, `ordered: false`), e.g. "Elements of self-defense", "Requisites of treachery".
3. **Circumstance classifier**: a fact → which circumstance (justifying / exempting / mitigating / aggravating / alternative; qualifying vs. generic; privileged vs. ordinary) as flip cards.
4. **Decision gates** (figures.py `gates` + fact patterns): self-defense (unlawful aggression → reasonable necessity → lack of sufficient provocation); stages of execution (subjective vs. objective phase); impossible crime; conspiracy; Art. 4 (proximate cause, aberratio ictus, error in personae, praeter intentionem); minors under RA 9344 (age and discernment); complex crimes (Art. 48); probation eligibility.
5. **Penalty scale ladder** (static figure + Test me): the scale of penalties with durations and periods, so he can recite them.

## 4. Numbers to verify against the codal before use

| Rule | What to confirm |
|---|---|
| Art. 27 durations | reclusion perpetua (as amended by RA 7659); reclusion temporal 12 y 1 d–20 y; prisión mayor 6 y 1 d–12 y; prisión correccional 6 mo 1 d–6 y; arresto mayor 1 mo 1 d–6 mo; arresto menor 1–30 d |
| Art. 76 periods | each divisible penalty split into three equal periods (e.g. prisión correccional 6 mo 1 d–2 y 4 mo / 2 y 4 mo 1 d–4 y 2 mo / 4 y 2 mo 1 d–6 y) |
| Art. 64 | none → medium; only mitigating → minimum; only aggravating → maximum; both → offset; two or more mitigating and no aggravating → next lower penalty |
| Art. 61 / 71 | frustrated one degree lower, attempted two; accomplices one, accessories two; the graduated scale in Art. 71 |
| Art. 26 fines | the afflictive / correctional / light fine thresholds as amended by RA 10951 |
| ISL | when it does not apply (e.g. life imprisonment or reclusion perpetua; maximum term not exceeding one year) |
| Probation | the maximum-term ceiling and the disqualifications under PD 968 as amended by RA 10707 |
| RA 9344 | the ages for exemption and discernment as amended by RA 10630 |

Put the verified table in the method page's `method-numbers` table (it feeds search and the "Numbers" group).

## 5. Exam method

Find out from Zen and the past exams: number of problems, time, answer-sheet rules, MCQ or essay, whether computations are required. If problems ask for a penalty, the model answers and CLEAR lines should end with the computation (crime → penalty prescribed → degree → period → indeterminate sentence). Build `00_method.html` and the exam clock figure around those facts.
