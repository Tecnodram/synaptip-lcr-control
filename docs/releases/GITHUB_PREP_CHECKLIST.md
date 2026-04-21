# GitHub Prep Checklist

Use this checklist before publishing the repository.

## Keep in repository

- `src_v4_1/`
- `src_v4/`
- `src_v3_6/`
- `src_v3/`
- `src_v3_5/`
- `docs/`
- build scripts and spec files
- public assets required by the app

## Do not publish

- `licenses/`
- `*.lic`
- private signing or license generation tools
- local virtual environments
- `dist/`
- `build/`
- local logs and scratch exports

## Recommended first push target

- Treat V4.1 as the current release branch baseline.
- Tag or document it as the first stable UI-integrated logarithmic sweep version.

## Suggested next cleanup before GitHub

- Review README wording for V4.1.
- Confirm no private customer data exists in `example_outputs/` or exports.
- Confirm no machine-specific logs remain outside `.gitignore`.
- Remove any obsolete experimental files that are not part of V4.1 delivery or historical source versions you want to preserve.

