# ADR 0006: Build a project-specific grounding/research step, don't reuse the existing polity narrative pipeline

**Date:** 2026-09-07
**Status:** Accepted

## Context

Prior work exists that generates historically grounded narratives for
randomly selected pre-modern polities. It was an open question whether
Psychonecromancy's grounding stage (see
[04-grounding.md](../04-grounding.md)) should reuse/adapt that pipeline or
be built fresh.

## Decision

Build a research step specific to this project.

## Rejected alternative

Reuse/adapt the existing pre-modern polity narrative pipeline — rejected
because its purpose (a general historical narrative about a polity) is
narrower-but-different from what this project needs (a specific,
defensible answer to what an unremarkable median 22-year-old man's day
looked like in a given society/period). Retargeting it risked inheriting
prompt assumptions and output shape built for a different goal.

## Consequences

More upfront work in Phase 2 to design and validate a new research step
rather than adapting something already proven to run. The existing
pipeline may still be consulted as a reference or a source of reusable
prompting technique, but is not the implementation basis.
