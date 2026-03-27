# Zenodo Workflow for v3.5.0

## Authoritative Metadata Source

The authoritative archival metadata source for this release is:

- .zenodo.json

## Workflow

1. Sign in to Zenodo and enable GitHub integration for this repository.
2. Ensure .zenodo.json is committed on the release branch baseline.
3. Publish the GitHub Release for tag v3.5.0.
4. Wait for Zenodo ingestion and record creation.
5. Record assigned identifiers:
   - Concept DOI: CONCEPT_DOI_PENDING
   - Version DOI: VERSION_DOI_PENDING
6. Update README badge and citation files after DOI assignment.

## Required Follow-Up

- Update CITATION.cff with final DOI and release date.
- Update docs/releases/v3_5_0_release_record.md with DOI links.
- Keep V3.5.0 immutable as the stable baseline before V4 work.
