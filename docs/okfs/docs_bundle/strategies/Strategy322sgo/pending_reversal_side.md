---
concept_id: strategies/Strategy322sgo/pending_reversal_side
language: python
okf_version: '0.2'
resource: strategies/Strategy322sgo.py
tags:
- lang:python
- type:Function
- module:strategies
- domain:Strategy322sgo.py
- git:branch:main
- git:repo:askode
timestamp: '2026-07-10T05:38:37Z'
title: _pending_reversal_side
type: Function
---

# _pending_reversal_side

## Signature

```python
def _pending_reversal_side(self, pair: str) -> Optional[str]
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `pair` | `str` | `—` |

## Returns
`Optional[str]`

## Source
Lines 1248–1250 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| called_by | [_is_reversal_entry](/strategies/Strategy322sgo/is_reversal_entry.md) |
| called_by | [populate_entry_trend](/strategies/Strategy322sgo/populate_entry_trend.md) |
