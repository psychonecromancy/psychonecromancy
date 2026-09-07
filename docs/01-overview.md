# Overview

## Goal

One input string naming a society and time period (e.g. `"1300's Bulgarian
Empire"`) goes in. One finished video comes out, depicting a historically
grounded day in the life of a 22-year-old man at the **median**
socio-economic stratum of that society.

## Creative thesis

Historical content — documentary, museum exhibits, popular history video —
skews toward extremes: monarchs, saints, soldiers, or the destitute. That's
where the written and material sources concentrate, so it's what gets
depicted. The broad middle of any given society — a man doing an ordinary
job, eating ordinary food, living in an ordinary dwelling — is
underrepresented not because it's less real, but because it's less
documented and less dramatic.

This project targets that middle deliberately. The hard part isn't
generating a plausible-looking peasant or artisan; it's generating a
*specific, defensible* median for a *specific* society and decade, rather
than a generic pre-modern everyman. The historical grounding step (see
[04-grounding.md](04-grounding.md)) is the actual product; image generation,
narration, and assembly are downstream of getting that right.

## Scope boundaries — v1

**In scope:**
- One input string in, one finished video out (see
  [05-open-decisions.md](05-open-decisions.md) for the current output-format
  decision — this has been revised from the original short-form-vertical
  framing to dual vertical + horizontal, 5 minutes each).
- Run manually, triggered by a human, not on a schedule.
- Reproducible: same input should be able to produce a comparable output.
- Every intermediate artifact (grounding brief, scene list, generated
  images, generated video clips, narration audio, final render) inspectable
  on disk / in the repo's artifact storage, not just the final video.

**Out of scope for v1** (noted here so the architecture isn't closed off to
them, not because they're unimportant):
- Multi-tenant anything (multiple users, multiple concurrent jobs with
  isolation).
- A UI. Interaction is via n8n and the filesystem/repo.
- Automated publishing to any platform.
- Scheduling / unattended queue processing (the long-term goal per the
  project description, but not a v1 requirement — v1 proves the pipeline
  works for one input at a time).
- Series or character continuity across videos (e.g. a recurring "cast" of
  median-men across episodes).
- Non-English narration.

## Non-goals

Not aiming for photorealism as an end in itself, and not aiming for
entertainment-first pacing at the expense of grounding accuracy. If a choice
has to be made between "more historically defensible" and "more visually
striking," the project's thesis says pick the former.
