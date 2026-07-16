---
concept_id: okfs/docs_bundle/strategies/Strategy322sgo/historical_inference
description: 'def _historical_inference(self, ask: float, bid: float, sma_compare:
  float, candidate_is_short: int) -> tuple[Optional[str], Optional[list[float]], Optional[float]]'
git_branch: main
git_repo: askode
language: python
okf_version: '0.2'
resource: github.com/your/repo/blob/main//Users/nickrotich/Desktop/portfolio/projects/python/askode/docs/okfs/docs_bundle/strategies/Strategy322sgo/historical_inference.md
tags:
- ext:md
- policy
- inference
- strategy
- domain:okfs
- sgo
timestamp: '2026-07-16T03:50:26.910543Z'
title: _historical_inference
type: Document
---

# _historical_inference

## Signature

```python
def _historical_inference(self, ask: float, bid: float, sma_compare: float, candidate_is_short: int) -> tuple[Optional[str], Optional[list[float]], Optional[float]]
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `ask` | `float` | `—` |

| `bid` | `float` | `—` |

| `sma_compare` | `float` | `—` |

| `candidate_is_short` | `int` | `—` |

## Returns
`tuple[Optional[str], Optional[list[float]], Optional[float]]`

## Source
Lines 517–557 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_historical_required_margin](/strategies/Strategy322sgo/historical_required_margin.md) |
| calls | [_load_historical_policy](/strategies/Strategy322sgo/load_historical_policy.md) |
| called_by | [populate_indicators](/strategies/Strategy322sgo/populate_indicators.md) |
