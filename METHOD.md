# Method and codebook

Use directed qualitative content analysis with an inductive extension register and a case-by-concept matrix. The framework supplies the initial concepts; the notes may support, oppose, qualify or extend them. The aim is a defensible description of the evidence and a set of candidate revisions, not a single approval score.

## Read, segment and code

Read all documents before finalising the coding protocol. Inspect source headings, speaker attribution, note-taker additions, duplicate files and empty templates. Assign a `case_id` to the underlying interview: two sets of notes from the same interview can share a case ID. Do not infer duplicates or identities from filenames alone. Give each included case an explicit reason, and explain exclusions. A blank template is missing evidence.

Use the question numbering in `framework/questions.json`. Q7–Q8 is available for combined presentation/feedback, Q10a for missing-type prompts, QX for interviewer reflections, and Q0 for front matter/unmapped text. Review mapping manually when headings differ. Substantive participant statements cannot remain under Q0. A unit belongs to one question; split across question boundaries.

A meaning unit is one proposition or a connected argument. Split independent or conflicting propositions; preserve conditions and reasons. Use Unicode character offsets in extracted paragraphs. Exact text is assembled from the source, never generated as a substitute quotation. For multiple adjacent paragraphs, the separator is a newline. Every non-empty paragraph must be either completely covered by non-overlapping units or assigned an explicit non-coding disposition. Prompt text, headings, cross-references and scaffolding are not endorsements.

Retain all substantive statements, including background and interviewer interpretation, but distinguish provenance. Do not count repeated statements as extra interview votes. Multiple concept assignments may occur in one unit, with a separate stance and strength for each.

## Stances

| Code | Include when | Do not confuse with |
| --- | --- | --- |
| SUP | Explicit endorsement, relevance or importance of the target | A compatible practice or an example; praise of a list does not endorse every item |
| OPP | Explicit rejection of a concept or its place in the model | Low relevance in one professional role |
| QUAL | A condition, restricted scope, definition problem or suggested restructuring | Unqualified acceptance or categorical rejection |
| NR | Low/no relevance in the respondent's setting | Universal invalidity |
| ILL | An example fits a concept without explicit evaluation | Support |
| PRO | An actual proposal to add, change or operationalise something | An analyst's own recommendation |
| UNC | Recorded wording is insufficient to resolve a position | Silence or a missing answer |
| CTX | Background without evaluation | Framework endorsement |

For SUP, OPP, QUAL, NR and PRO, use **strong** when the note contains a clear priority/rejection, reason, consequence, criterion or concrete proposal; **weak** for bare agreement, tentative preferences or undeveloped proposals. Use **n/a** for ILL, UNC and CTX. Strength describes the surviving note's articulation, not personal conviction or evidential truth.

Record coding confidence separately: high, medium or low. Explain the interpretation in `rationale`. An LLM cannot label its own pass as independent human validation. Use `unreviewed`, `reviewed` or `adjudicated`, naming the reviewer when applicable.

## Concepts, extensions and suggestions

Use [target definitions](framework/target-definitions.md) alongside the [framework](framework/framework.md). T1–T5 are value types; I1–I5 intrinsic factors; E1–E6 extrinsic factors. F codes assess the scheme or its underlying claims. F-INHERENT (value without context) is distinct from F-INTRINSIC (the factor grouping).

X codes are optional candidate extensions; O codes address operation of the framework; C0 is background. Their inclusion in this toolkit preserves vocabulary from earlier method development, not prior interview evidence. Do not force a new idea into an inherited code. Add a clearly defined target to the run's `config/codebook.json` when needed, documenting its boundary and reason in the review log. A new code does not automatically become an accepted value type.

Assess `framework_fit` separately as `in_framework`, `partial_extension`, `outside_framework` or `context_only`. Explain the decision, especially where an inherited X theme overlaps an original factor. This is an explicit qualitative decision in this edition, rather than a fixed lookup that decides conceptual fit for you.

Use `suggestion` only for an actual recorded proposal: `new_value`, `new_factor`, `refine_definition`, `restructure`, `operationalise`, or `none`. Analyst recommendations belong in the synthesis and must be identified as such. An omission is not automatically a suggestion.

## Attribution and primary evidence

Choose `reported`, `mixed`, `researcher`, `background`, `supplementary` or `ambiguous` for every unit. `reported` means notes attribute the material to the interview subject; it does not imply a verbatim transcript. Institutional practices described by the subject may be reported; inserted institutional documents are supplementary. Split distinguishable interviewer remarks from answers where possible. Never assume that a person's label identifies the respondent without contextual evidence.

Primary counts include reported and mixed units in included cases, excluding Q0/QX. Mixed material needs careful review. Reported-only sensitivity removes mixed units. Another sensitivity includes ambiguous attribution; another removes cases explicitly flagged `sensitivity_exclude`. The last alternative changes the denominator; the first two keep the same included-case denominator.

Source extraction excludes deleted tracked changes and includes inserted text. It flags drawings/text boxes and extracts auxiliary text separately. Inspect comments, notes and images in the original Word file where necessary. Auxiliary text is not automatically included in the paragraph inventory. If it contains essential interview evidence, create a documented, manually checked derivative Word file in a separate input collection and prepare a new run; keep the original unchanged. Document that derivation and avoid counting the same material twice.

## Measure support

Each included case counts at most once per target per stance. SUP, OPP and QUAL may coexist; do not erase contradictions. NR remains a separate category. Strong SUP is a subset of SUP, never an extra vote.

Report both SUP / all included cases and SUP / evaluating cases. Evaluating cases have at least one SUP, OPP, QUAL or NR assignment for that target. ILL, PRO, UNC and CTX do not count as evaluation. Zero denominators yield null, not zero approval. Show coverage separately from support. Report scheme-level approval, factor approval and framework usefulness separately.

Do not add the stance columns, weight weak/strong numerically, interpret missing evidence as rejection or calculate a universal framework approval percentage. These are descriptive case counts, affected by the question wording, note-taking and sampling. They establish neither population prevalence, saturation nor theoretical validity.

## Synthesis and comparison

Discuss agreements, negative cases, within-case conflicts, attribution uncertainty and possible framework changes. Cite stable `doc_id/unit_id` references for every finding and recommendation. The validator checks that references exist; a reviewer must check that they support the claim. A synthesis should cover both the five types and the factors, including unevaluated concepts.

For comparisons across collections, keep target definitions, question mapping, inclusion rules and stance rules stable. Record version differences before comparing results. Identical scripts do not guarantee identical LLM interpretations: independent coding or targeted human adjudication is needed to assess consistency.
