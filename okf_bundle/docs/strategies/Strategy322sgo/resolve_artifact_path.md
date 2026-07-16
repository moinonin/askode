---
concept_id: docs/strategies/Strategy322sgo/resolve_artifact_path
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
title: _resolve_artifact_path
type: Function
---

# _resolve_artifact_path

## Signature

```python
def _resolve_artifact_path(configured_path: str) -> Optional[Path]
```

## Decorators

- `staticmethod`

## Parameters

| Name | Type | Default |
|------|------|---------|
| `configured_path` | `str` | `—` |

## Returns
`Optional[Path]`

## Source
Lines 248–285 in `docs/strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/docs/strategies/Strategy322sgo/Strategy322sgo.md) |
| called_by | [_load_historical_policy](/docs/strategies/Strategy322sgo/load_historical_policy.md) |
