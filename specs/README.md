# Specifications Directory (`specs/`)

This directory houses all formal system requirements written in **Easy Approach to Requirements Syntax (EARS)**.

## EARS Format Syntax Reference
Every requirement must follow one of the 5 standard EARS patterns:
1. **Ubiquitous**: The system shall [system response].
2. **Event-driven**: When [trigger], the system shall [system response].
3. **State-driven**: While [specific system state], the system shall [system response].
4. **Unwanted behaviour**: If [error condition / edge case], then the system shall [system response].
5. **Optional feature**: Where [feature flag or setting enabled], the system shall [system response].

## Requirement Structure & `[PLANNED]` Lifecycle
```markdown
## [MODULE]-[NUMBER]: [Descriptive Title]

[EARS Statement]

Acceptance Criteria:
- AC-[MODULE]-[NUMBER].1: [Criterion 1]
- AC-[MODULE]-[NUMBER].2: [Criterion 2]
```

To author roadmap specs upfront for incremental implementation, append `[PLANNED]` to the heading:
```markdown
## [MODULE]-[NUMBER]: [Future Feature Title] [PLANNED]
```
- **Active Specs (No `[PLANNED]` tag)**: Must be implemented in `src/` and 100% verified in `tests/`.
- **Planned Specs (`[PLANNED]`)**: Deferred for future steps; `guardian.py --strict` will fail if AI implements them prematurely before `[PLANNED]` is removed.

## Bi-Directional Traceability & Semantic Anti-Mirage Rules
- **Normalized Block Hashing**: Each requirement block from `## [REQ-ID]:` to the next `##` or EOF is normalized and fingerprinted via SHA-256.
- **Forward & Reverse Code Binding**: Every public function/class in `src/` must carry `# [spec: REQ-ID]`.
- **1-Test-to-1-AC Binding**: Every `def test_*` in `tests/` must carry exactly one `# [verifies: REQ-ID/AC-ID]` tag, reference a symbol/module bound to `REQ-ID`, and execute deterministic anti-mirage assertions.
- **Traceability Manifest**: `specs/traceability.json` is auto-compiled and verified by Spec Guardian.
