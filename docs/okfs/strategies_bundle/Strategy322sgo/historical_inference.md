---
concept_id: Strategy322sgo/historical_inference
language: python
okf_version: '0.2'
resource: Strategy322sgo.py
tags:
- lang:python
- type:Function
- module:Strategy322sgo.py
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
Lines 517–557 in `Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/Strategy322sgo/Strategy322sgo.md) |
| calls | [_historical_required_margin](/Strategy322sgo/historical_required_margin.md) |
| calls | [_load_historical_policy](/Strategy322sgo/load_historical_policy.md) |
| called_by | [populate_indicators](/Strategy322sgo/populate_indicators.md) |
