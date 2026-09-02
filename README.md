# COSsse — Experimental Flow & Memory Habitat

> Experimental habitat for generalized Flow and Memory behavior in the GooleOS/COSMOS ecosystem.

## Purpose

COSsse is where generalized capability behavior is exercised against real living needs before anything is treated as mature ecosystem architecture.

The current proven spine is:

> Meaning flows. Independent capability boundaries recognize alignment. Aligned capabilities act through temporary coupling. Their results return to Flow as further meaning.

Collector remains unchanged and unaware of Flow. Memory remains unaware of Flow, Collector, and applications.

## Proven current behavior

### Flow

- carries `Meaning` without receiver identity;
- presents meaning to independent capability adapters;
- records `claimed`, `unclaimed`, `contested`, or `expired` disposition;
- does not interpret application meaning;
- does not select capabilities by identity;
- does not analyse capability outcomes.

### Collector boundary

- recognizes a usable collection need;
- translates it to Collector's existing native `collect(domain_path, source, ...)` contract;
- invokes Collector without modifying Collector;
- returns the Collector report to Flow as experience meaning;
- detaches after the action completes.

### Memory

- preserves opaque supported values faithfully across time;
- preserves binary material as part of an experience;
- records `memory_id`, `stored_at`, and SHA-256 integrity metadata;
- survives process restart and reproduces preserved values exactly;
- can enumerate memory receipts without interpreting stored payloads;
- can recall a preserved value by `memory_id`.

### Memory boundary

The Flow-facing Memory adapter currently recognizes three minimum behaviors proven by living use:

- preserve experience meaning;
- discover which preserved experiences exist;
- recall one preserved experience.

Discovery is deliberately **enumeration, not search**. Memory exposes only its own housekeeping receipts. It does not add tags, indexing, domain knowledge, semantic retrieval, ranking, or interpretation.

## Living Habitat evidence

NOKKU → Lottery → India → Kerala is the first living habitat currently pressure-testing COSsse.

A real Kerala Lottery collection has proven the end-to-end path:

`Need → Meaning → Flow → Collector → experience Meaning → Flow → Memory → restart → discover → recall`

The live Memory workflow currently uses Kerala Lottery DrawSerial `75356`. After restart, the prior `memory_id` is not handed to the consumer; preserved receipts are discovered through the Memory boundary, candidates can be recalled, and relevance remains the consumer's responsibility.

Nothing application-specific from NOKKU is embedded into Flow or Memory.

## Boundaries deliberately preserved

COSsse currently does **not** provide:

- a planner or central dispatcher;
- semantic memory search;
- tags or application-owned indexes inside Memory;
- pattern recognition;
- an evolution engine;
- automatic resolution when multiple capabilities align;
- NOKKU/Lakshmi-specific business logic.

Those remain absent until living evidence justifies a new capability or a minimal evolution of an existing one.

## Tests

Install COSsse and the development dependency:

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
```

The GitHub Actions live workflows additionally install the stable Collector v1.0.0 release commit:

`2923a0d24ded7c4e3fff30d9045e0fcd2612d2a4`

and exercise real Collector/Flow and Collector/Flow/Memory encounters against the Kerala Lottery source.

## Status

COSsse remains an **experimental habitat**, not GooleOS Core. Behavior is promoted only after repeated real-world evidence justifies it.

## Rights

Copyright © 2026 Sathya P B / GooleOS. All rights reserved.

This repository is publicly viewable, but no open-source license is granted. No permission is granted to copy, modify, redistribute, sublicense, or commercialize this code except as permitted by applicable law and GitHub's Terms of Service. Separate release terms may be published when the project reaches a public release stage.
