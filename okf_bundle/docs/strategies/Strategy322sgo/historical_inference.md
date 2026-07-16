---
concept_id: docs/strategies/Strategy322sgo/historical_inference
language: python
okf_version: '0.2'
resource: docs/strategies/Strategy322sgo.py
tags:
- lang:python
- type:Function
- module:docs
- domain:strategies
- git:branch:main
- git:repo:askode
timestamp: '2026-07-10T05:38:37Z'
title: _historical_inference
type: Function
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
Lines 517–557 in `docs/strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/docs/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_historical_required_margin](/docs/strategies/Strategy322sgo/historical_required_margin.md) |
| calls | [_load_historical_policy](/docs/strategies/Strategy322sgo/load_historical_policy.md) |
| called_by | [populate_indicators](/docs/strategies/Strategy322sgo/populate_indicators.md) |
