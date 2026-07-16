---
concept_id: okfs/docs_bundle/strategies/Strategy322sgo/expire_pending_reversals
description: 'def _expire_pending_reversals(self, now: datetime) -> None'
git_branch: main
git_repo: askode
language: python
okf_version: '0.2'
resource: github.com/your/repo/blob/main//Users/nickrotich/Desktop/portfolio/projects/python/askode/docs/okfs/docs_bundle/strategies/Strategy322sgo/expire_pending_reversals.md
tags:
- sgo
- ext:md
- strategy
- domain:okfs
timestamp: '2026-07-16T03:50:26.949846Z'
title: _expire_pending_reversals
type: Document
---

# _expire_pending_reversals

## Signature

```python
def _expire_pending_reversals(self, now: datetime) -> None
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `now` | `datetime` | `—` |

## Returns
`None`

## Source
Lines 1202–1210 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_normalize_reversal_time](/strategies/Strategy322sgo/normalize_reversal_time.md) |
| calls | [_reversal_expiry](/strategies/Strategy322sgo/reversal_expiry.md) |
| called_by | [confirm_trade_entry](/strategies/Strategy322sgo/confirm_trade_entry.md) |
| called_by | [populate_entry_trend](/strategies/Strategy322sgo/populate_entry_trend.md) |
