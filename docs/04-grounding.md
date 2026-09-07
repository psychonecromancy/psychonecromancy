# Historical grounding

This is the project's quality bottleneck and its actual creative
contribution — see [01-overview.md](01-overview.md). Everything downstream
(scene decomposition, image prompts, narration) is only as good as the
brief this stage produces.

## Decision: build a research step specific to this project

There is existing prior work generating historically grounded narratives
for randomly selected pre-modern polities. That pipeline was considered as
a reuse candidate but the decision is to **build a research step specific
to Psychonecromancy** rather than adapt it, because this project's
requirement is narrower and more specific than a general polity narrative:
it needs to answer, concretely, what an unremarkable median 22-year-old man
in a *given* society and decade actually did with his day — his labour,
diet, dress, dwelling, and daily rhythm — not a general historical
narrative about the polity itself.

The existing pipeline may still be a useful reference or a source of
reusable prompting technique, but is not the basis this stage is built on.

## What "median" means here, operationally

The brief for a given input needs to avoid two failure modes:
- **Generic pre-modern everyman.** A brief that would be equally true of
  any pre-industrial agrarian society is not grounded — it isn't using the
  specific society/period input for anything.
- **Elite or destitute drift.** Sources are disproportionately about
  rulers, clergy, warriors, or the very poor. A median brief has to
  actively correct for this bias rather than default to whichever archetype
  the sources make easiest to describe.

## Required brief contents

At minimum, a grounding brief needs to cover, for the specific society and
period given:
- Material culture and dress appropriate to his economic stratum
- Diet and food access
- Labour — his likely occupation and what his working day involved
- Built environment — dwelling, settlement type, immediate surroundings
- Daily rhythm — what hours of the day were spent on what

## Quality bar

Not yet formally defined. At minimum, a brief should be specific enough
that a domain-knowledgeable reader could distinguish it from a brief for a
different society/period in the same broad era (e.g. a brief for 1300s
Bulgaria should not read the same as one for 1300s rural England). Formal
criteria (e.g. citation requirements, a checklist, a rubric) are an open
question — not designed yet.

## Open questions

- Exact schema for the grounding brief artifact (structured JSON vs. prose
  vs. hybrid) — not decided; will likely be settled when this stage is
  actually implemented in Phase 2.
- How much of the research step is LLM-generated-from-training-knowledge
  vs. backed by retrieval against actual sources. Not decided. This has
  direct implications for the quality bar above and for hallucination risk
  in obscure/under-documented societies.
- What happens when the input names a society/period with genuinely thin
  historical documentation for ordinary people (a real risk given the
  project's own thesis about source bias) — does the pipeline flag lower
  confidence, degrade gracefully, or refuse? Not decided.
