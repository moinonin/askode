---
concept_id: okfs/docs_bundle/strategies/Strategy322sgo/is_reversal_entry
description: 'def _is_reversal_entry(self, pair: str, entry_tag: str | None, side:
  str) -> bool'
git_branch: main
git_repo: askode
language: python
okf_version: '0.2'
resource: github.com/your/repo/blob/main//Users/nickrotich/Desktop/portfolio/projects/python/askode/docs/okfs/docs_bundle/strategies/Strategy322sgo/is_reversal_entry.md
tags:
- sgo
- ext:md
- strategy
- domain:okfs
timestamp: '2026-07-16T03:50:26.926687Z'
title: _is_reversal_entry
type: Document
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
Lines 1252–1256 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_pending_reversal_side](/strategies/Strategy322sgo/pending_reversal_side.md) |
| called_by | [confirm_trade_entry](/strategies/Strategy322sgo/confirm_trade_entry.md) |
