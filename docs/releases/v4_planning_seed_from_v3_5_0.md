# V4 Planning Seed from V3.5.0 Baseline

## Stable Baseline Inherited from V3.5.0

- Validated V3.5.0 analysis pipeline and export structure.
- Frozen release tag v3.5.0 with reproducibility artifacts.
- Startup-robust packaged executable behavior.

## What Must Remain Untouched

- V3.5.0 release logic and validated behaviors.
- V3 compatibility dependencies currently required by V3.5.0.
- V3.5.0 archival metadata and citation references.

## Candidate V4 Directions (High Level Only)

- circuit fitting
- KK validation
- advanced interpretation
- UI upgrades

## Branching Rule

V4 must branch from the frozen V3.5.0 baseline.

## Do not rewrite V3.5.0 during V4 development

Treat V3.5.0 as immutable release history. Any V4 changes must be developed in a separate branch/line and must not retroactively alter validated V3.5.0 release behavior.
