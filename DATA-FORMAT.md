# Run format and coding contract

`prepare` produces a frozen manifest and extracted files. Edit only the run's coding records, configuration (with recorded changes), inference log and synthesis. Do not edit source files, manifest or extracted text. The validator detects source/extraction changes using SHA-256. Manifest hashes are accidental-change checks, not tamper-proof signatures.

## Coding documents

Each `coding/Dxxxx.json` includes these required fields:

| Field | Meaning |
| --- | --- |
| `doc_id` | Fixed ID assigned during preparation |
| `status` | `pending` until the document is fully coded; then `complete` |
| `case_id` | Underlying interview ID; can link multiple documents |
| `case_decision` | `include`, `exclude` or `empty` |
| `case_reason` | Inclusion/exclusion rationale |
| `sensitivity_exclude` | Boolean indicating a case-level sensitivity concern |
| `source_review` | Heading/attribution/layout/auxiliary-text review and limitations |
| `dispositions` | Exactly one entry per non-empty extracted paragraph |
| `units` | All substantive meaning units, including material outside primary evidence |
| `review_log` | Dated record of decisions, reviewer/session and accepted changes |

A disposition has `paragraph`, `question`, `kind`, `reason`. `kind` is `coded`, `heading`, `front_matter`, `scaffold`, `cross_reference` or `excluded`. All non-coded kinds require a reason. `heading_suggestion` is a preparation hint only. If part of a paragraph is substantively coded, cover the entire paragraph with units; incidental text can be a separate background unit. Do not drop whitespace at split boundaries.

Copy the empty unit skeleton in templates/unit.json and fill it. Offsets use Python Unicode characters: start inclusive, end exclusive. Whole paragraph means `start: 0`, `end: len(text)`, not null. Spans must be in source order, within one question and adjacent paragraphs. Coverage must be complete without overlap. Newlines between paragraph excerpts are inserted by the runner. Preserve original-language text, punctuation and spelling. The output is a quotation of **notes**, not necessarily participant speech.

`author_session` links to inference-log.json. A subsequent review can change that to the latest responsible session, while recording the history in review_log. Set `reviewer` if reviewed/adjudicated. Do not claim a human review unless a human actually performed it. Additional metadata is allowed but not all extra fields are validated.

The first seven output columns are exactly:

`S-number, filename, Q-number, meaning of statement, code, weak/strong, full text of statement`

S numbers are assigned in document/source order at build time. They may shift after segmentation changes. Use `Dxxxx/Uxxxx` (`unit_ref`) for persistent references across builds. Assignments remain individually structured in JSON; the TSV joins them with semicolons.

## Sessions

See templates/inference-log.json. The prepared run starts with an empty session list. Each session needs a unique ID, kind `llm` or `human`, date and notes. Model/provider/temperature/top_p/seed must be present but may be null. Add context window, model revision, API request IDs, token usage, exact prompt path and conversation ID when actually available. For human sessions, model-related fields are null. Never store credentials.

## Synthesis

See templates/synthesis.json. Mark `status: complete` only after reading calculated results and reviewing the evidence. Each finding/recommendation is an object with `text` and `evidence`, a list of `Dxxxx/Uxxxx` references. `author_session` links to the session log. `limitations` is a non-empty array of strings for a completed synthesis. References establish traceability, not automatic entailment.

## Configuration

The run receives a copy of the framework and codebook. Add target labels with clear definitions; append extra definitions and rationales to its target-definitions.md. Use non-conflicting IDs for new concepts. Questions are a JSON object keyed by Q label. A build records all configuration hashes. Run-wide version changes require review of affected units; a validator cannot detect semantic drift from changed definitions.

## Output preservation

Preparation refuses an existing run folder. Builds choose a new numbered snapshot. Do not run simultaneous builds against the same run. Verification requires the run inputs and original files to match the snapshot. After a review edit, build anew; older snapshots remain a record of the earlier state, and their recorded hashes explain why they no longer match current inputs. Keep versioned copies of coding/configuration externally if exact restoration of every intermediate state is required.
