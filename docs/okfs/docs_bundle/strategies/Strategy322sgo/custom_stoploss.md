---
concept_id: strategies/Strategy322sgo/custom_stoploss
description: long_timediff = ((current_time - timedelta(minutes=self.sell_long_tmax.value))
  - trade.open_date_utc).total_seconds()/60
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
title: custom_stoploss
type: Function
---

# custom_stoploss

long_timediff = ((current_time - timedelta(minutes=self.sell_long_tmax.value)) - trade.open_date_utc).total_seconds()/60

## Signature

```python
def custom_stoploss(self, pair: str, trade: Trade, current_time: datetime, current_rate: float, current_profit: float, after_fill: bool = False) -> Optional[float]
```

## Docstring

long_timediff = ((current_time - timedelta(minutes=self.sell_long_tmax.value)) - trade.open_date_utc).total_seconds()/60
short_timediff = ((current_time - timedelta(minutes=self.sell_short_tmax.value)) - trade.open_date_utc).total_seconds()/60

long_disc_time = self.interval * (long_timediff // self.interval)
short_disc_time = self.interval * (short_timediff // self.interval)

long_sl0 = self.sell_long_custom_sl.value # * trade.initial_stop_loss_pct
short_sl0 = self.sell_short_custom_sl.value #* trade.initial_stop_loss_pct

short_stop = self.stop_loss_decay(self.sell_short_final_fraction.value, self.sell_Tmax_short.value, t=short_disc_time, SL_0=short_sl0)
long_stop = self.stop_loss_decay(self.sell_long_final_fraction.value, self.sell_Tmax_long.value, t=long_disc_time, SL_0=long_sl0)


if trade.is_short:
    min_profit = self.sell_short_loss_factor_two.value - 1
else:
    min_profit = 1 - self.sell_long_loss_factor_two.value

can_set_absolute_sl = current_profit > min_profit

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `pair` | `str` | `—` |

| `trade` | `Trade` | `—` |

| `current_time` | `datetime` | `—` |

| `current_rate` | `float` | `—` |

| `current_profit` | `float` | `—` |

| `after_fill` | `bool` | `False` |

## Returns
`Optional[float]`

## Source
Lines 1017–1072 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
