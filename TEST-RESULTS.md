# Verification of this distribution

Tested on 23 September 2026 with CPython **3.14.7**, Clang 21.0.0, macOS 27.0 on arm64. The tool targets Python 3.10+, but other Python versions and operating systems have not been exercised in this development run. No third-party Python libraries or JavaScript runtime were used by the tests.

Command:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

**27 tests passed.** The test suite creates artificial DOCX/DOTX ZIP/XML fixtures in temporary directories and removes them afterward. No interview documents or participant quotations are included as test fixtures.

The tests cover:

- Preparation, complete coding validation, synthesis, report generation and verification end to end.
- Exact original-language excerpts, embedded newlines and Unicode characters in the statement register.
- Source-file immutability, changed source/extraction detection and added-document detection.
- Multiple documents counted as one case; multiple independent cases producing a dynamic denominator.
- Support and qualification coexisting within a case; illustrations not counted as support; local non-relevance distinct from opposition.
- Reported-only, flagged-case-excluded and ambiguous-included sensitivity rules.
- Missing/pending coding, unmapped questions, missing dispositions, unknown targets, invalid strength and absent inference sessions.
- Character coverage gaps, overlaps and valid meaning-unit splits; rejection of multiple disconnected spans within a paragraph.
- Required attribution for reviewer status and valid synthesis evidence references.
- Explicit draft behaviour when synthesis is pending, and null results for zero denominators.
- Tracked changes, tabs/line breaks and auxiliary comments in Word XML.
- Preserving earlier build snapshots and detecting edited outputs or changed coding inputs.

The CLI help command was also exercised. Documentation links and JSON syntax were checked. A distribution audit compared toolkit text against long reported-note excerpts from the earlier analysis and checked that original interview filenames and output datasets were absent. The reusable question text and theoretical framework are intentionally retained.

These are implementation checks. They do not validate future qualitative coding, establish inter-coder agreement, guarantee extraction of every possible Word layout, or certify the interpretations in an AI-generated report. No real interview analysis was run or recoded to test this distribution.
