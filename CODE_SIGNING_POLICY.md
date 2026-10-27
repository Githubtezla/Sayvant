# Code signing policy

Free code signing provided by [SignPath.io](https://about.signpath.io/), certificate by [SignPath Foundation](https://signpath.org/).

> [!NOTE]
> **Status:** The application to the SignPath Foundation has been submitted and is pending. Until it is approved, release builds are unsigned. This policy describes how releases will be signed once it is in place.

## What is signed

Only release builds of Sayvant are signed: `Sayvant.exe` and the installer `Sayvant-Setup-<version>.exe` attached to a GitHub release of this repository.

Every signed file is built by the GitHub Actions workflow [`.github/workflows/release.yml`](.github/workflows/release.yml) directly from the tagged source code in this repository. Nothing is built or signed on a personal computer.

## Roles

| Role | Members |
|---|---|
| Committers and reviewers | [Githubtezla](https://github.com/Githubtezla) |
| Approvers (signing requests) | [Githubtezla](https://github.com/Githubtezla) |

Each signing request is approved manually by an approver.

## Privacy

Sayvant transcribes speech locally by default. Audio and text leave the computer only if the user configures an external API provider (for example OpenAI, Groq, OpenRouter or Anthropic) in the settings, and only to that provider. Sayvant itself sends no telemetry and contacts no other servers, except Hugging Face to download the speech model on first use.
