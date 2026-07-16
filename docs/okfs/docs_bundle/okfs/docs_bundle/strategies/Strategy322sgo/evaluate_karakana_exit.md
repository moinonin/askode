---
concept_id: okfs/docs_bundle/strategies/Strategy322sgo/evaluate_karakana_exit
description: 'def _evaluate_karakana_exit(self, trade: Trade, current_time: datetime,
  current_rate: float, pnl: float) -> str | None'
git_branch: main
git_repo: askode
language: python
okf_version: '0.2'
resource: github.com/your/repo/blob/main//Users/nickrotich/Desktop/portfolio/projects/python/askode/docs/okfs/docs_bundle/strategies/Strategy322sgo/evaluate_karakana_exit.md
tags:
- ext:md
- strategy
- domain:okfs
- sgo
- karakana
timestamp: '2026-07-16T03:50:26.943577Z'
title: _evaluate_karakana_exit
type: Document
---

# _evaluate_karakana_exit

## Signature

```python
def _evaluate_karakana_exit(self, trade: Trade, current_time: datetime, current_rate: float, pnl: float) -> str | None
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `trade` | `Trade` | `—` |

| `current_time` | `datetime` | `—` |

| `current_rate` | `float` | `—` |

| `pnl` | `float` | `—` |

## Returns
`str | None`

## Source
Lines 894–992 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| called_by | [confirm_trade_exit](/strategies/Strategy322sgo/confirm_trade_exit.md) |
| called_by | [custom_exit](/strategies/Strategy322sgo/custom_exit.md) |
