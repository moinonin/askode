---
concept_id: okfs/docs_bundle/strategies/Strategy322sgo/expire_blocked_reentries
description: 'def _expire_blocked_reentries(self, now: datetime) -> None'
git_branch: main
git_repo: askode
language: python
okf_version: '0.2'
resource: github.com/your/repo/blob/main//Users/nickrotich/Desktop/portfolio/projects/python/askode/docs/okfs/docs_bundle/strategies/Strategy322sgo/expire_blocked_reentries.md
tags:
- sgo
- ext:md
- strategy
- domain:okfs
timestamp: '2026-07-16T03:50:26.920132Z'
title: _expire_blocked_reentries
type: Document
---

# _expire_blocked_reentries

## Signature

```python
def _expire_blocked_reentries(self, now: datetime) -> None
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `now` | `datetime` | `—` |

## Returns
`None`

## Source
Lines 1235–1243 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_normalize_reversal_time](/strategies/Strategy322sgo/normalize_reversal_time.md) |
| called_by | [confirm_trade_entry](/strategies/Strategy322sgo/confirm_trade_entry.md) |
