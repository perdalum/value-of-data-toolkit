# How AI did this: implementation and pipeline

## What this edition does

This is a reusable implementation of the earlier Value of Data interview-analysis method. It retains the slide-derived conceptual framework, question numbering, target vocabulary, stance/strength rules and case-based aggregation. It removes all original interview files, extracted notes, personal details, case-specific exceptions, coding decisions, counts and findings.

The runner was rewritten rather than copying scripts with fixed corpus assumptions. Its implementation differs in several explicit ways: interview counts are dynamic; multiple documents can share one underlying case; paragraph dispositions, attribution and confidence require explicit decisions; framework fit is a coder judgment; runs record inference provenance and configuration hashes; report generation is one command; outputs are numbered snapshots. The portable edition uses Markdown/JSON/TSV rather than the earlier custom Excel workbook.

## Components

| Component | Implementation | Deterministic? |
| --- | --- | --- |
| Word extraction | Python reads DOCX/DOTX ZIP archives and WordprocessingML XML | Yes, for the same source bytes and runtime |
| Input manifest | Relative filenames, document IDs, SHA-256 hashes and runtime record | Deterministic except path/runtime/timestamps |
| Heading suggestions | Normalised exact matching to the saved questions | Yes; suggestions require review |
| Corpus familiarisation | Human/LLM reads the entire collection and assesses context | Interpretive; LLM results may vary |
| Meaning units and coding | Human/LLM writes spans, meanings, target/stance/strength, provenance, confidence and suggestions | Interpretive; not calculated by the runner |
| Coding validation | Schema/enumeration, source hashes, paragraph/span coverage, unique IDs, evidence references | Deterministic |
| Case support and sensitivity | Deduplicated sets of cases for each target/stance, with documented eligibility filters | Deterministic conditional on saved coding |
| Qualitative synthesis | Human/LLM writes findings/recommendations with evidence references | Interpretive; LLM results may vary |
| Report assembly | Python renders saved decisions and calculated results to JSON, TSV and Markdown | Deterministic content conditional on inputs; build paths/timestamps vary |
| Verification | Hashes, exact text comparison and an independent set-based support recount | Deterministic implementation checks, not semantic validation |

## Software and versions

The required runtime is **Python 3.10 or later**. The exact runtime used to test this distribution is recorded in TEST-RESULTS.md. Each future preparation/build records `sys.version`, executable path, operating system, tool version and script hash in its manifest/provenance, so later environment checks are not misrepresented as proof of an earlier run's environment.

Only Python's standard library is used. The runner imports `argparse`, `csv`, `hashlib`, `html`, `json`, `platform`, `re`, `shutil`, `sys`, `zipfile`, `collections`, `datetime`, `pathlib` and `xml.etree.ElementTree`. The test suite additionally uses `copy`, `importlib.util`, `tempfile`, `unittest` and `xml.sax.saxutils`. There are no third-party Python packages, OCR engines, LLM SDKs or API clients.

**JavaScript and Node.js are not components of the shipped pipeline.** During toolkit development, the assistant used the Codex tool interface, whose orchestration calls are expressed in JavaScript, to issue local file and Python operations. That does not make Node.js a dependency of this toolkit, and no JavaScript runtime version is asserted for that hosted interface. No `@oai/artifact-tool`, spreadsheet-authoring package or Word library is needed to run the portable edition. There is no package installation step or hidden network inference call.

## Word extraction details

The extractor opens `word/document.xml`, enumerates non-empty body paragraphs in XML order, including paragraphs in tables, and preserves text, tabs and line breaks. Paragraph IDs count original XML paragraph positions, including gaps from empty paragraphs. They are not page numbers. Inserted tracked text is included; deleted tracked text is excluded. Drawings, tracked changes and text boxes produce warnings. Comments, footnotes, endnotes, headers and footers are retained in `auxiliary_text` for explicit review.

It does not render Word pages or perform OCR. XML order is not guaranteed to reproduce visual reading order in complex layouts. Tables, text boxes, embedded images and attribution still require source review. Auxiliary material is not silently counted as participant statements. See METHOD.md for how to handle essential evidence outside the main body inventory.

## LLM inference: when and how

The Python program never calls a model. An assistant or human uses `prompts/analyse.md` to read the new corpus, select boundaries, interpret meanings, assign codes, assess attribution and prepare narrative conclusions. These are the semantic inference stages. Subsequent Python processing uses their saved JSON decisions as inputs.

For LLM work, inference may be stochastic and results can also vary with context order, model revisions and undocumented service settings. This distribution does not promise that repeating the prompt yields identical coding. Setting a seed, where supported, would not establish semantic correctness or guarantee portability across models.

Record each session's kind, date, model/provider, model revision, sampling settings, prompt files, conversation/request identifiers and available usage information in `inference-log.json`. Unknown values must be null. Unit-level `author_session` and the synthesis session point to that log. Human coding is supported using kind `human` and null model fields. Review history records who changed which decision and why.

For this toolkit's development, the assistant used LLM inference to redesign the reusable workflow, write code/documentation and assess test results. It did not recode the original interviews. The exact serving model revision, sampling settings and seed were not exposed in the development record; they are not invented here. The reusable framework and methodological vocabulary came from the existing project artifacts. Prior interview-specific results were not used as a template for future findings.

## Pipeline

```text
Read-only Word folder + reusable framework
                  |
          prepare (Python)
                  |
 frozen source manifest + extracted paragraphs + empty coding records
                  |
     corpus familiarisation and coding (human/LLM)
                  |
    saved coding + inference log + review decisions
                  |
          validate (Python)
                  |
      draft build and evidence review
                  |
        qualitative synthesis (human/LLM)
                  |
         build -> verify (Python)
                  |
  new Markdown / JSON / TSV snapshot + provenance
```

A failed validation stops report creation. A synthesis-pending build requires explicit `--draft`. Rebuilding creates a fresh numbered directory. Source documents and earlier output files are not rewritten. `verify` rechecks the current run inputs against the selected snapshot; it correctly fails after substantive coding changes until a new snapshot is built.

## What is reproducible, and what is not

With the same source files, script, configuration and coding decisions, the statement extraction and case counts can be regenerated. File hashes capture the inputs and output contents; timestamps, filesystem paths and build numbers intentionally vary. The output provenance stores configuration/coding hashes, not a full backup of each coding version. Keep versioned run inputs if exact historical reconstruction is needed.

Technical tests can establish exact excerpts, complete paragraph accounting, valid references, stable case counting and source immutability. They cannot establish that a note supports a target, that an attribution is right, that an exclusion is justified, or that an evidence reference actually entails a narrative claim. Those require substantive review. No human adjudication or intercoder reliability is claimed by a successful test run.
