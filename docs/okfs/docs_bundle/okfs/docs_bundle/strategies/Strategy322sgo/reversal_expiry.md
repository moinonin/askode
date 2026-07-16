---
concept_id: okfs/docs_bundle/strategies/Strategy322sgo/reversal_expiry
description: 'def _reversal_expiry(self, created_at: datetime) -> datetime'
git_branch: main
git_repo: askode
language: python
okf_version: '0.2'
resource: github.com/your/repo/blob/main//Users/nickrotich/Desktop/portfolio/projects/python/askode/docs/okfs/docs_bundle/strategies/Strategy322sgo/reversal_expiry.md
tags:
- sgo
- ext:md
- strategy
- domain:okfs
timestamp: '2026-07-16T03:50:26.928606Z'
title: _reversal_expiry
type: Document
---

# _reversal_expiry

## Signature

```python
def _reversal_expiry(self, created_at: datetime) -> datetime
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `created_at` | `datetime` | `—` |

## Returns
`datetime`

## Source
Lines 1199–1200 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_normalize_reversal_time](/strategies/Strategy322sgo/normalize_reversal_time.md) |
| called_by | [_expire_pending_reversals](/strategies/Strategy322sgo/expire_pending_reversals.md) |
| called_by | [order_filled](/strategies/Strategy322sgo/order_filled.md) |
