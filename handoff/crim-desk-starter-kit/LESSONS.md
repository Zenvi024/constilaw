# Lessons from building the Consti desk

## Things Zen asked for (keep them)

- **Flashcards are flip-and-grade, never multiple choice.** He found choices to be hints. Every direction (Case → rule, Facts → case, Rule → case, Mixed) is a flip card graded Again / Hard / Good / Easy.
- **Rounds must feel random.** Due cards are picked first, then new, then soon-due, and the round is then shuffled so topics and formats interleave. A Mixed direction picks a random format per case.
- **Case names centered and prominent** on cards (large italic display type), with a one-line cue and a light "Show the rule" pill.
- **Motion: quick and calm.** A 0.16 s fade-in for cards and answers. He rejected a 3D flip and fly-off animations as jarring.
- **Streak counter** (correct in a row, best remembered), **Previous card with full undo** (schedule, fix list, streak), keyboard (Space, 1–4, ←), **swipe on phones** (tap flips; right good, left again, up easy), grade buttons pinned at the bottom on phones, **focus mode** while drilling (header and tabs hidden, slim bar with countdown and Exit; Esc exits).
- **1–3 word color-coded hooks for every case**, shown on the back of the card, in Browse and in the case card.
- **Diagrams that make him apply the law**: decision gates with real fact patterns he can walk through, "Use it when" trigger lines, memory hooks, "On the exam, write" CLEAR lines, Test me covers, a hook wall and an issue radar on the method page.
- **Universal search**, **blur mode**, **lists drill**, **one-button session**, **fix list**, **rule-map reading progress**, **theme switch**, one-line countdown, readable labels (body font for chips and labels; mono only for tiny caps).
- Printables on **folio (8.5 × 13 in)**, one page each, text auto-fitted to fill the page.

## Bugs that happened (don't repeat)

1. **CSS class collision blanked the drills.** New diagram CSS used generic names (`.facts{display:none}`, `.clock`, `.chip`, `.test`) that the app already used, hiding drill prompts and the essay text. Prefix every new component class; `tests/viz.js` checks for leaks.
2. **Animation races.** A flip that swaps content after a timeout crashed when the user graded or left during it. Capture element references and check `isConnected` before swapping. Overlay "ghost" cards confused tests and caused horizontal scroll on phones; avoid them (and clip run boxes with `overflow-x: clip`).
3. **Tests must wait** for anything animated (`waitForSelector`) and must end a round before switching tabs (focus mode hides the tabs).
4. **Search indexing** picked up button text inside figure titles; index the title span only, and skip calculators and hidden fact patterns.
5. **Case linking**: names that are also people (Marcos, Aquino) or organizations (IBP) must be cite-only or stopped; full names shared by two cases need year or file-based resolution.

## Content rules that mattered

- Verify every card against the block digest **and** the class reviewer; the class reviewer had errors (vote thresholds, years, who issued an order). Flag them; do not copy them.
- Keep the professor's own views (his book, articles, block intel) in a separate highlighted box: he tests them.
- Mark doubtful past-exam keys with a note instead of silently "correcting" them.
- News questions: his professor built questions from recent news. A dated news watch with practice essays paid off (one news problem appeared almost verbatim on the exam).

## How he likes to work

- Wants plans and suggestions before changes when he says so ("show me the plan first", "don't implement yet").
- Reports bugs with screenshots and short messages ("case → rule doesn't show the rule bruh"): fix the root cause, explain it in one or two plain sentences, and test the exact flow he used.
- Appreciates honest assessments (e.g. grading his exam answers) delivered kindly and concretely.
- He studies until about 1 AM, commutes with his phone, and uses study days at Malcolm Hall (Kapihan): plan phone-friendly tasks for commutes.
