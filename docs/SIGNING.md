# Signing with SignPath

The workflow `.github/workflows/release.yml` signs `Sayvant.exe` and the installer through the [SignPath Foundation](https://signpath.org/) once the credentials are configured. Until then it builds unsigned releases.

Status: the application to the SignPath Foundation is pending, releases are unsigned for now.

## One-time setup

1. The repository is public on GitHub, with the MIT license and `CODE_SIGNING_POLICY.md`.
2. Apply at the SignPath Foundation: https://signpath.org/apply.html
3. After approval, create in the SignPath account:
   - A project with the slug `sayvant`, linked to this GitHub repository as a trusted build source.
   - A signing policy `release-signing` (every request approved manually).
   - An artifact configuration `app`: ZIP archive, sign `Sayvant.exe` inside with Authenticode.
   - An artifact configuration `installer`: ZIP archive, sign `Sayvant-Setup-*.exe` inside with Authenticode.
4. In the GitHub repository under Settings, Secrets and variables, Actions:
   - Variable `SIGNPATH_ORGANIZATION_ID` with the organization ID from SignPath.
   - Secret `SIGNPATH_API_TOKEN` with an API token of a CI user from SignPath.

## Test run without a release

Before the first tag and after changes to dependencies or the workflow:

1. Push the changes to `main`.
2. On GitHub, open Actions, choose the "Release" workflow, click "Run workflow" on branch `main` and leave the "sign" option off.
3. When the run has finished (a few minutes), download the artifact `sayvant-<version>` from the run: installer and portable ZIP, unsigned. Install and try it.

With the "sign" option the run also signs through SignPath once that is set up. A test run never creates a release.

## Publishing a version

1. Raise the version in `sayvant/__init__.py` and commit.
2. Create and push a tag, for example `git tag v0.2.0` and `git push origin v0.2.0`.
3. The workflow builds, sends both files to SignPath and waits up to an hour per file for approval.
4. A draft release appears on GitHub. Review it and publish it.

## Dependency versions

`requirements.txt` lists the direct dependencies with fixed versions, `constraints.txt` the tested versions of all packages. Both are used locally (`install.ps1`, `packaging\build.ps1`) and in the workflow. To update, raise the packages in `.venv`, test, and copy `pip freeze` into `constraints.txt`.
