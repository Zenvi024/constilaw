# Finals intake (Batch 1)

- `syllabus.json`: the syllabus as ordered headings, case entries and readings (`tools/syl_parse.py`).
- `digest_index.json`: every digest found (single files and cases inside compilations) (`tools/index_digests.py`).
- `coverage.json` and `FINALS_COVERAGE.md`: sources for every syllabus case (`tools/match.py`, then `tools/report.py`).
- `parsed/my_digests.json`: lossless parse of all 183 single digests (`tools/parse.py`); `parsed/word_check.txt`: 0 missing words.

Rebuild: `cd finals-intake/tools && python3 -I syl_parse.py ../../sources/finals/syllabus.txt ../syllabus.json && python3 -I index_digests.py ../../sources/finals/digests_zip ../digest_index.json && python3 -I match.py && python3 -I report.py`
