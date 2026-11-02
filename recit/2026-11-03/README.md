# Recit Deck: Tuesday, November 3 and Thursday, November 5, 2026

Published at https://claude.ai/artifact/N7FiLtQAZQaeAbbR7pEqa7. The page is `recit-deck.html`.

Rebuild:

    python3 -I tools/parse.py <nov3-digest-dir> data/nov3-cases.json      # lossless .docx -> JSON
    python3 -I tools/parse.py <nov5-digest-dir> data/nov5-cases.json
    python3 -I tools/build_portal.py data/nov3-cases.json data/nov5-cases.json tools/template.html recit-deck.html

Syllabus order and headings live in `tools/build_portal.py` (`SETS`).

Verify:

    node tests/run.js $PWD/recit-deck.html     # views, drills, search, day switch, overflow at 400/1280 px in both themes
    python3 -I tests/words_strict.py <all-digests-dir> tests/rendered.json tools   # every docx word appears in the rendered digest
