# Git Release Commands for v3.5.0

## Core Commands

```bash
git status
git add .
git commit -m "Release v3.5.0: final release engineering and archival metadata"
git tag -a v3.5.0 -m "SynAptIp Nyquist Analyzer v3.5.0"
git push origin main
git push origin v3.5.0
```

## Manual GitHub Release Draft Steps

1. Open GitHub repository Releases page.
2. Click Draft a new release.
3. Select existing tag v3.5.0.
4. Title: SynAptIp Nyquist Analyzer v3.5.0.
5. Paste notes from docs/releases/github_release_notes_v3_5_0.md.
6. Attach release assets (see below).
7. Save draft for review or publish immediately.

## Recommended Release Assets to Upload

- release_v3_5/SynAptIp_Nyquist_Analyzer_V3_5.exe
- release_v3_5/README_release.md
- release_v3_5/CHANGELOG.md
- release_v3_5/LICENSE.txt
- release_v3_5/ASSET_MANIFEST_v3_5_0.md
