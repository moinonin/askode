---
concept_id: docs/strategies/Strategy322sgo/is_reversal_entry
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
title: _is_reversal_entry
type: Function
---

# _is_reversal_entry

## Signature

```python
def _is_reversal_entry(self, pair: str, entry_tag: str | None, side: str) -> bool
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `pair` | `str` | `—` |

| `entry_tag` | `str | None` | `—` |

| `side` | `str` | `—` |

## Returns
`bool`

## Source
Lines 1252–1256 in `docs/strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/docs/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_pending_reversal_side](/docs/strategies/Strategy322sgo/pending_reversal_side.md) |
| called_by | [confirm_trade_entry](/docs/strategies/Strategy322sgo/confirm_trade_entry.md) |
