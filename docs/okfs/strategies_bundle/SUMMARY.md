---
description: 'Top-level OKF summary: 45 concepts across 1 domains and 1 modules'
git_branch: main
git_repo: askode
okf_version: '0.2'
timestamp: '2026-07-16T00:54:58Z'
title: strategies — Knowledge Summary
type: Index
---

# strategies — Knowledge Summary

> OKF v0.2 bundle | 45 concepts | 1 domains | 1 modules

## Stats

| Type | Count |
|------|-------|
| Function | 43 |
| Module | 1 |
| Class | 1 |

| Language | Concepts |
|----------|----------|
| python | 45 |

## Domain Map

Use these links to navigate the bundle or prime an AI agent with focused context.

### [Strategy322sgo.py](Strategy322sgo.py/index.md) — 45 concepts

- [Strategy322sgo](Strategy322sgo/index.md) (45 concepts)

## Key Concepts

Highest-value concepts across all domains (Classes and Functions with rich descriptions).

| Concept | Type | Module | Description |
|---------|------|--------|-------------|
| [custom_stoploss](/Strategy322sgo/custom_stoploss.md) | Function | `Strategy322sgo.py` | long_timediff = ((current_time - timedelta(minutes=self.sell… |
| [bot_start](/Strategy322sgo/bot_start.md) | Function | `Strategy322sgo.py` | Load the HistoricalTrading policy and its exact training nor… |
| [order_filled](/Strategy322sgo/order_filled.md) | Function | `Strategy322sgo.py` | Callback triggered when any order is filled. |

## Usage with OpenCode

```bash
# Prime full context
RUN cat ./okf_bundle/SUMMARY.md

# Prime specific domain
RUN cat ./okf_bundle/Strategy322sgo.py/index.md

# Find a concept
RUN find ./okf_bundle -name '<ConceptName>.md' | xargs cat
```
