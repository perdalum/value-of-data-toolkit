# A framework for discussing the value of data

Based on *Slides to be shown at interview.pptx*, slides 1–3. This framework preserves the slides’ five named value types and their distinction between intrinsic and extrinsic factors. The discussion structure and modelling rules are an interpretive adaptation.

The value of data can be discussed through three connected questions: **What kind of value is at stake? Which characteristics of the data support that value? Under what conditions can that value be realised?** These questions distinguish the reasons for valuing data from the factors that influence those reasons.

The unit of discussion is a claim about a particular dataset: it has a certain kind of value, for particular stakeholders, in a particular context. Making these elements explicit allows people to disagree about the value of the same data without assuming that one of them has misunderstood the data. They may be considering different benefits, purposes or time horizons.

## Types of value

**Cultural and societal value** concerns what data contribute to cultural heritage and our understanding of society, both now and in the future. The discussion asks what understanding the data preserve or make possible, and what their loss would mean.

**Scientific value** concerns the contribution data make to conceptual frameworks and the advancement of a research field. The discussion asks which research questions the data help address and how they support or extend scientific understanding.

**Market value** concerns direct financial gains and indirect contributions to future economic value. Commercialisation is one possibility. The discussion should also identify wider economic benefits and who would receive them.

**Replacement value**, labelled “(Re)placement value” in the slides, concerns the resources required to produce or replace the data. This includes whether recreation is possible at all. Data documenting an unrepeatable event illustrate why the discussion must address irrecoverability as well as cost. High production cost alone does not establish scientific or societal benefit.

**Compliance value** concerns the consequences of failing to meet ethical, legal or contractual obligations. The slides associate more serious consequences with greater value. In this framework, that is a reason to examine the importance of responsible stewardship, including who or what could be affected. It does not establish permission to use or share a dataset.

These types can coexist. A dataset can have considerable scientific and cultural value, limited market value and high replacement value. The slides leave a sixth type unnamed. This framework retains that openness without inventing another category.

## Factors influencing value

The slides identify five groups of **intrinsic factors**: originality and uniqueness; reliability; representativeness; standardisation and organisation of data; and standardisation and richness of metadata. These direct attention to the dataset’s characteristics and the way it was produced and documented.

The intrinsic label needs a qualification. Reliability and representativeness depend partly on the research question, while originality requires comparison with other data. The framework therefore retains the slides’ grouping but treats these as dataset characteristics whose assessment may require an explicit reference point.

The six groups of **extrinsic factors** concern the context of use: relevance; demand; exclusivity; innovation and technological compatibility; accessibility; and the reputation of the source. They help explain why the value attributed to the same dataset may change across users, technologies or time.

The slides describe exclusivity in terms of abundance when data are in high demand. The framework interprets this as a question about abundance or scarcity relative to demand, leaving its effect on each type of value open. Scarcity and accessibility need not influence every type of value in the same direction. Source reputation also remains separate from reliability: trust in a producer and evidence about collection methods are distinct grounds for assessment.

## Using the framework in discussion

Begin with a dataset, the people or organisations concerned, the purpose under consideration and the time horizon. Identify the relevant value types and state a reason for each value claim. Then examine which intrinsic and extrinsic factors support or limit the claim, recording evidence and uncertainty.

A useful discussion statement is:

> These data have [type of value] for [stakeholders], in relation to [purpose and time horizon], because [reason]. This claim is supported or limited by [factors], on the basis of [evidence], with [uncertainties].

For example, a historical survey might have scientific value because it enables comparison across time. Its representativeness and documentation would affect that claim. Access conditions and compatibility with available analytical tools would affect the ability to realise the value. Its replacement value could also be high because the original observations cannot be collected again. This is an illustration of the framework, not a finding from the slides.

The result is a reasoned profile of value. The framework does not assume that all value types can be expressed in a common unit or added into a single score.

## Simple ontology

The accompanying [ontology in Markdown](ontology.md), also available as [YAML](framework.yaml), defines five classes: Dataset, Stakeholder, Context, ValueClaim and FactorAssessment. A ValueClaim concerns a Dataset, has a value type, identifies stakeholders and applies within a Context. FactorAssessments explain how intrinsic or extrinsic factors support or limit that claim.

The YAML is a readable conceptual description, not a formal validation schema or an executable scoring model. The value types and factors derive from the slides. The classes and relations provide an additional structure for using them in discussion.
