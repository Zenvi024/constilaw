# Recit Deck: Tuesday, November 3, 2026

Published at https://claude.ai/artifact/N7FiLtQAZQaeAbbR7pEqa7. The page is `recit-deck-nov3.html`.

Rebuild:

    python3 -I tools/parse.py <digest-dir> cases.json        # lossless .docx -> JSON
    python3 -I tools/build_portal.py cases.json tools/template.html recit-deck-nov3.html

Verify:

    node tests/run.js $PWD/recit-deck-nov3.html               # views, drills, search, overflow at 400/1280 px in both themes
    python3 -I tests/words_strict.py <digest-dir> tests/rendered.json tools   # every docx word appears in the rendered digest
