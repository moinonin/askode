---
concept_id: okfs/docs_bundle/strategies/Strategy322sgo/historical_required_margin
description: 'def _historical_required_margin(self, candidate_is_short: int) -> float'
git_branch: main
git_repo: askode
language: python
okf_version: '0.2'
resource: github.com/your/repo/blob/main//Users/nickrotich/Desktop/portfolio/projects/python/askode/docs/okfs/docs_bundle/strategies/Strategy322sgo/historical_required_margin.md
tags:
- ext:md
- inference
- strategy
- domain:okfs
- sgo
timestamp: '2026-07-16T03:50:26.924694Z'
title: _historical_required_margin
type: Document
---

# _historical_required_margin

## Signature

```python
def _historical_required_margin(self, candidate_is_short: int) -> float
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `candidate_is_short` | `int` | `—` |

## Returns
`float`

## Source
Lines 336–345 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_refresh_strategy_health_snapshot](/strategies/Strategy322sgo/refresh_strategy_health_snapshot.md) |
| called_by | [_historical_inference](/strategies/Strategy322sgo/historical_inference.md) |
| called_by | [populate_entry_trend](/strategies/Strategy322sgo/populate_entry_trend.md) |
