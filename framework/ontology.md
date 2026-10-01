# A simple ontology for discussing the value of data

This ontology accompanies [the narrative framework](framework.md). It preserves the five named value types and eleven factor groups from *Slides to be shown at interview.pptx*, slides 1–3. The classes, relations and interpretation rules are an adaptation for structuring discussion.

The YAML below is a conceptual description, not a formal validation schema or scoring model.

```yaml
framework:
  title: Framework for discussing the value of data
  version: '0.1'
  source: Slides to be shown at interview.pptx, slides 1–3
  status: Interpretive adaptation of the slides; a simple conceptual ontology.
  premise: >-
    Discuss what kind of value a dataset has, which properties of the dataset
    support that value, and which conditions of use affect its realisation.

value_types:
  cultural_societal:
    definition: Contribution to cultural heritage and understanding society now and in the future.
    question: What would preserving or losing these data mean for our understanding of society?
  scientific:
    definition: Contribution to conceptual frameworks and the advancement of a research field.
    question: What research understanding do these data support or enable?
  market:
    definition: Direct financial gains or indirect contributions to future economic value.
    question: How could these data generate economic benefits, and for whom?
  replacement:
    source_label: (Re)placement value
    definition: Resources required to produce or replace the data, including whether recreation is possible.
    question: What would it take to recreate these data, and what could not be recovered?
  compliance:
    definition: Significance of the consequences of failing to meet ethical, legal or contractual obligations.
    question: Who or what could be affected by non-compliance, and how seriously?

factors:
  intrinsic:
    originality_uniqueness: Novelty of the data.
    reliability: Collection through quality-controlled methods appropriate to the research questions, preferably peer-reviewed.
    representativeness: Coverage of variables, cases, periods and other factors needed to address the research question.
    data_standardisation_organisation: Clear, logical and systematic organisation and widely accepted file formats.
    metadata_standardisation_richness: Richness of embedded metadata and adherence to standards, vocabularies and ontologies.
  extrinsic:
    relevance: Alignment with current scientific, societal, political or other needs.
    demand: Number of stakeholders for whom the data have value.
    exclusivity: Abundance or scarcity of data in relation to demand.
    innovation_technological_compatibility: Extent to which available technologies can exploit the data.
    accessibility: Ease of access to the data.
    source_reputation: Trust in the producer of the data.

classes:
  Dataset:
    definition: The data being discussed.
    fields: [id, description]
  Stakeholder:
    definition: A person, group or organisation making a value claim or affected by it.
    fields: [id, description]
  Context:
    definition: The purpose, setting and time horizon of an assessment.
    fields: [id, purpose, setting, time_horizon]
  ValueClaim:
    definition: A reasoned claim that a dataset has a particular type of value in a context.
    fields: [id, dataset, value_type, asserted_by, affected_stakeholders, context, rationale, evidence, uncertainty]
  FactorAssessment:
    definition: A contextual assessment of one factor and its influence on a value claim.
    fields: [id, value_claim, factor, observation, influence, explanation, evidence]
    influence_options: [supports, limits, mixed, uncertain]

relations:
  - {subject: ValueClaim, predicate: concerns, object: Dataset}
  - {subject: ValueClaim, predicate: has_type, object: value_types}
  - {subject: ValueClaim, predicate: asserted_by, object: Stakeholder}
  - {subject: ValueClaim, predicate: affects, object: Stakeholder}
  - {subject: ValueClaim, predicate: assessed_in, object: Context}
  - {subject: FactorAssessment, predicate: evaluates, object: factors}
  - {subject: FactorAssessment, predicate: qualifies, object: ValueClaim}

interpretation_rules:
  - A dataset may have several types of value at the same time.
  - A factor may influence several value types; there is no fixed one-to-one mapping.
  - Value types are dimensions of discussion, not mutually exclusive dataset categories.
  - Intrinsic factors describe the dataset, but some assessments require a research question or comparison.
  - Extrinsic factors describe conditions of use and may change across stakeholders and over time.
  - High replacement cost does not by itself establish scientific or societal benefit.
  - Compliance value concerns consequences of non-compliance, not permission to use or share data.
  - Source reputation and methodological reliability require separate assessments.
  - No common numerical scale or rule for summing value types is assumed.

source_notes:
  - The slides provide five named value types and an unnamed sixth placeholder; the placeholder is left open.
  - The intrinsic/extrinsic grouping follows the slides, including representativeness under intrinsic factors.
  - The exclusivity wording in the slide refers to abundance under high demand; the direction of its influence is left open.
  - The classes, relations and interpretation rules are additions for structuring discussion, not claims that they appear in the slides.
```
