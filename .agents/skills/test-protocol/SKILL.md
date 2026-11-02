---
name: SunrahaHu-test-protocol
description: >-
  Defines the testing methodology, runner commands, test tiering, and isolation rules
  for SunrahaHu. Enforced during [Gate 4] Test Suite Execution in release management.
---

# Test Protocol: SunrahaHu

This skill defines the official testing process for **SunrahaHu**.

## 1. Test Command & Execution
Execute tests via:
`uv run pytest`

```bash
uv run pytest
```

## 2. Test Execution Tiers
- **Fast Unit Tests**: Deterministic fast tests validating pure logic, schemas, and math. Must run in `< 5s`.
- **Integration Tests**: Tests database, file I/O, or local service boundaries.
- **Heavy / Live Inference (Opt-In)**: Heavy multi-model or network tests isolated from standard pre-commit runs.

## 3. Anti-Mirage Assertion Rules
- All test assertions must verify deterministic outputs and exact numeric/factual anchors.
- Vacuous assertions (`assert result is not None`, `assert len(items) > 0`) are strictly forbidden.
