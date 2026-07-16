---
concept_id: okfs/docs_bundle/strategies/Strategy322sgo/custom_exit
description: 'def custom_exit(self, pair: str, trade: Trade, current_time: datetime,
  current_rate: float, current_profit: float) -> str | None'
git_branch: main
git_repo: askode
language: python
okf_version: '0.2'
resource: github.com/your/repo/blob/main//Users/nickrotich/Desktop/portfolio/projects/python/askode/docs/okfs/docs_bundle/strategies/Strategy322sgo/custom_exit.md
tags:
- ext:md
- strategy
- domain:okfs
- sgo
- karakana
timestamp: '2026-07-16T03:50:26.940455Z'
title: custom_exit
type: Document
---

# custom_exit

## Signature

```python
def custom_exit(self, pair: str, trade: Trade, current_time: datetime, current_rate: float, current_profit: float) -> str | None
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `pair` | `str` | `—` |

| `trade` | `Trade` | `—` |

| `current_time` | `datetime` | `—` |

| `current_rate` | `float` | `—` |

| `current_profit` | `float` | `—` |

## Returns
`str | None`

## Source
Lines 994–1015 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_evaluate_karakana_exit](/strategies/Strategy322sgo/evaluate_karakana_exit.md) |
