<div align="center">

<img src="docs/images/pill-demo.png" alt="Sayvant recording indicator" width="300">

# Sayvant

**Push-to-talk dictation for Windows.** Hold a key, speak, let go, and your words appear wherever the cursor is, in any app.
Speech recognition runs locally on your PC by default. No account, no subscription, no telemetry.

[Download](https://github.com/Githubtezla/Sayvant/releases) · [Deutsche Anleitung](README.de.md) · [Code signing policy](CODE_SIGNING_POLICY.md)

![License: MIT](https://img.shields.io/badge/license-MIT-2f7d6d) ![Windows 10 and 11](https://img.shields.io/badge/Windows-10%20%7C%2011-3b6fb6) ![Offline by default](https://img.shields.io/badge/recognition-offline%20by%20default-d97757)

</div>

![Sayvant overview](docs/images/window-home.png)

## Contents

- [How it works](#how-it-works)
- [Features](#features)
- [Installation](#installation)
- [Getting started](#getting-started)
- [Speech recognition](#speech-recognition)
- [Cleanup with a language model](#cleanup-with-a-language-model)
- [Shortcuts](#shortcuts)
- [Dictionary and snippets](#dictionary-and-snippets)
- [Overview and history](#overview-and-history)
- [The recording indicator](#the-recording-indicator)
- [Designs](#designs)
- [More settings](#more-settings)
- [Privacy](#privacy)
- [Tips and troubleshooting](#tips-and-troubleshooting)
- [Uninstalling](#uninstalling)
- [Building from source](#building-from-source)
- [Credits and license](#credits-and-license)

## How it works

1. Put the cursor in any text field: an email, a chat, a document, a code editor, a browser form.
2. Hold **Right Ctrl** (or mouse button 5) and speak.
3. Let go. Sayvant transcribes what you said and pastes it at the cursor.

That is all. Sayvant sits in the notification area and stays out of the way until you hold the key. A small indicator at the bottom of the screen shows that it is listening and how loud you are.

## Features

| Feature | What you get |
|---|---|
| **Local and private** | Parakeet v3 runs on your CPU, needs no internet after the first download, understands 25 languages and sets punctuation itself. Canary and Whisper are available as alternatives. |
| **Works everywhere** | Text is pasted wherever the cursor is, in any Windows program. |
| **API providers if you want them** | OpenAI, Groq, OpenRouter (Gemini, GPT audio, Voxtral) or your own Whisper server, with automatic fallback to local recognition. |
| **Optional cleanup** | A language model removes filler words, fixes punctuation and grammar, resolves self-corrections and can change the tone. Anthropic (Claude), OpenAI, OpenRouter or a local model via Ollama or LM Studio. |
| **Keyboard and mouse** | Hold to talk, add Space for hands-free, Esc to cancel, an optional toggle key, and a mouse button that works the same way. |
| **Dictionary and snippets** | Teach it names and terms, fix words it keeps getting wrong, and insert longer texts by saying a short trigger. |
| **Overview and history** | Words per day, time saved, speaking pace, a searchable history and a test dictation that does not paste anything. |
| **Clipboard friendly** | The dictation stays in the clipboard for pasting again, but is kept out of the Win+V history. |
| **Looks at home** | Three designs, each in light and dark, interface in English or German. |
| **Lightweight to install** | Per-user installer without admin rights, or a portable ZIP. |

## Installation

1. Download `Sayvant-Setup-<version>.exe` from the [releases page](https://github.com/Githubtezla/Sayvant/releases).
2. Run it. It installs for the current user only and does not need administrator rights.
3. Optionally create a desktop icon, then launch Sayvant. To start it with Windows, turn on **Start with Windows** in the settings.

Prefer no installer? Download `Sayvant-<version>-portable.zip`, extract it anywhere and run `Sayvant.exe`.

**Requirements:** Windows 10 or 11, 64-bit, with the Microsoft Edge WebView2 runtime (preinstalled on Windows 11 and on current Windows 10). About 1 GB of free memory while the local model is loaded.

**First start:** Sayvant downloads the speech model once (Parakeet v3, about 640 MB) from Hugging Face. A notification tells you when it starts and when it is ready. After that, local recognition works offline.

> [!NOTE]
> **Code signing has been requested** from the [SignPath Foundation](https://signpath.org/) and is not in place yet, so current builds are unsigned. Windows SmartScreen will show "Windows protected your PC": click **More info** and then **Run anyway**. Once signing is approved, releases will be signed as described in the [code signing policy](CODE_SIGNING_POLICY.md). Even signed builds can trigger SmartScreen until a new version has built up a reputation.

## Getting started

After the first start the settings window opens on the overview page. Try the **test dictation** there: it shows exactly what Sayvant understood and what the cleanup made of it, without pasting anything.

Then dictate for real:

- Click into a text field, hold **Right Ctrl**, speak, release.
- For longer texts, press **Space** while holding Right Ctrl. Recording continues hands-free until you press Right Ctrl again or click the indicator.
- Changed your mind? Press **Esc** while recording.

You can open the settings at any time with a click on the Sayvant icon in the notification area. A right-click opens the menu with quick switches for recognition and cleanup, "Paste last dictation again", the history, the log and a link to this page.

## Speech recognition

![Recognition settings](docs/images/window-engine.png)

### Local (default)

Runs entirely on your PC with [onnx-asr](https://github.com/istupakov/onnx-asr). The model is downloaded once on first use and then works offline.

| Model | Strengths |
|---|---|
| **Parakeet v3** (default) | Fast on the CPU, 25 European languages with automatic language detection, punctuation and capitalization built in. |
| **Canary 1B v2** | More accurate, but needs a fixed dictation language (set it under General). |
| **Whisper large-v3-turbo** | 99 languages, noticeably slower on the CPU. |

Options: **int8** precision (smaller and faster, barely any difference) or full precision, and processor or graphics card. The graphics card option uses DirectML (AMD, Intel, NVIDIA) and is available when Sayvant runs from source with `.\install.ps1 -DirectML`. Recordings longer than a minute are split at natural pauses automatically.

### API providers

Instead of the local model you can send the recording to a service of your choice. Preconfigured profiles:

| Profile | Endpoint | Default model |
|---|---|---|
| OpenAI | `/v1/audio/transcriptions` | `gpt-4o-mini-transcribe` |
| Groq | `/v1/audio/transcriptions` | `whisper-large-v3-turbo` |
| OpenRouter | chat with audio input | `google/gemini-3.5-flash-lite` |
| Your own server | `/v1/audio/transcriptions` | `Systran/faster-whisper-large-v3` (e.g. [speaches](https://github.com/speaches-ai/speaches)) |

You can add, rename and edit profiles, and every profile has a **Test connection** button. If an API call fails, Sayvant can fall back to local recognition so a dictation is never lost (on by default). Names and terms from the dictionary are passed along as a hint.

## Cleanup with a language model

![Cleanup settings](docs/images/window-cleanup.png)

Optional. After recognition, a language model polishes the text before it is pasted.

| Provider | Default model |
|---|---|
| Anthropic | `claude-haiku-5-5` |
| OpenAI | `gpt-6-luna` |
| OpenRouter | `anthropic/claude-haiku-5.5` (any chat model works) |
| Custom endpoint | any OpenAI-compatible server, e.g. Ollama (`qwen3:4b`) or LM Studio |

**Level**
- **Light:** removes filler words (um, uh), stutters and repetitions and fixes punctuation. The wording stays as spoken.
- **Medium:** additionally smooths grammar and awkward sentences, resolves self-corrections ("at three, no, at four" becomes "at four") and turns spoken enumerations into lists.

**Style:** none, formal, casual, all lowercase or excited.

**More:** Spoken commands like "comma", "period" or "new paragraph" become punctuation and line breaks. Optionally the title of the target window is sent along as a hint for names and tone. You can replace the built-in instructions completely with your own text file (**Custom rules**).

The cleanup is built to be safe: the dictation is treated as content, not as instructions, so a dictated question is never answered. If the result does not look like a cleaned version of what you said, or the provider is unreachable, Sayvant pastes the raw text instead and tells you why.

## Shortcuts

![Shortcut settings](docs/images/window-hotkeys.png)

| Action | Default | Notes |
|---|---|---|
| Hold to talk | **Right Ctrl** | Short taps and normal combinations like Ctrl+C do not trigger a recording. |
| Continue hands-free | **Space** while holding | Stop with the hold key again or a click on the indicator. |
| Toggle recording | not assigned | Starts and stops hands-free recording, e.g. F9. |
| Cancel | **Esc** | Discards the current recording. |
| Mouse | **Mouse button 5** (Forward) | Hold to talk, short click for hands-free. Alternatives: button 4, middle button, or off. Modes: hold or click, hold only, click on/off. |

Every shortcut can be changed by pressing the new key combination. The minimum hold time (300 ms by default) decides what counts as a dictation and what is normal typing.

## Dictionary and snippets

![Dictionary](docs/images/window-dictionary.png)

- **Names and terms:** spelled exactly the way you want them. Used as a hint for API recognition and cleanup.
- **Replacements:** words or phrases that are always replaced, as whole words and regardless of case. Handy for things a model keeps mishearing.
- **Snippets:** if a dictation consists only of a trigger phrase such as "my address", Sayvant pastes the stored text instead. Snippets can span several lines.

## Overview and history

![History](docs/images/window-history.png)

The overview shows words today and in total, the time saved compared to typing, your speaking pace and a chart of the last seven days. The history lists every dictation with time, duration, recognition engine, target window and whether it was cleaned up. Click an entry to see the raw recognition next to the final text, copy either one, or delete it. History is stored only on your PC, kept for 30 days by default and can be switched off.

## The recording indicator

<img src="docs/images/pill-demo.png" alt="Indicator animation" width="300">

A small pill at the bottom of the screen shows what Sayvant is doing. It never takes the focus away from your app.

| State | Indicator |
|---|---|
| Recording (holding the key) | <img src="docs/images/pill-record.png" alt="Recording" height="90"> |
| Hands-free (click to stop) | <img src="docs/images/pill-handsfree.png" alt="Hands-free" height="90"> |
| Processing | <img src="docs/images/pill-busy.png" alt="Processing" height="90"> |
| Short notice | <img src="docs/images/pill-message.png" alt="Notice" height="90"> |
| Error | <img src="docs/images/pill-error.png" alt="Error" height="90"> |

The indicator follows the chosen design and can be switched off.

## Designs

![Three designs in light and dark](docs/images/designs.png)

**Cream** (warm, serif), **Modern** (Windows 11, indigo) and **Graphite** (black and white). Each comes in light and dark, or follows the Windows setting. The design also changes the indicator and the notification area icon.

## More settings

![General settings](docs/images/window-general.png)

- **Dictation language:** automatic, or fixed to English, German, Spanish, French, Italian, Dutch, Polish or Portuguese.
- **Microphone:** Windows default or a specific device, with a live level meter. The microphone is only opened while you dictate.
- **Sounds:** a short tone when recording starts and stops.
- **Pasting:** via the clipboard and Ctrl+V (fast and reliable) or by typing character by character. Keep the dictation in the clipboard, restore what was there before, keep it out of the Win+V history, add a trailing space.
- **Start with Windows**, show or hide the indicator, history on or off and how long to keep it.
- **Display language:** English or German, following Windows by default.

## Privacy

- With local recognition **nothing leaves your PC.** The only network access is the one-time model download from Hugging Face.
- Audio or text is sent only to providers **you** configure, and only for the features you turn on.
- API keys are stored in the **Windows Credential Manager** (service `Sayvant`), never in the settings file or the log.
- **No telemetry**, no account, no update pings.

| What | Where |
|---|---|
| Settings | `%APPDATA%\Sayvant\settings.json` |
| History | `%APPDATA%\Sayvant\history.db` |
| Log | `%APPDATA%\Sayvant\sayvant.log` |
| Custom cleanup rules | `%APPDATA%\Sayvant\cleanup_prompt.txt` |
| Speech models | `%USERPROFILE%\.cache\huggingface` |
| API keys | Windows Credential Manager, service `Sayvant` |

## Tips and troubleshooting

- **Nothing is pasted into a program that runs as administrator.** Windows does not let a normally started program send keystrokes to elevated programs. Run Sayvant as administrator too, or dictate elsewhere.
- **"Nothing heard":** check the microphone on the General page with **Check level**. The bars should move while you speak.
- **The text appears in the wrong place:** Sayvant pastes into the window that has the focus when recognition finishes. Keep the cursor where the text should go.
- **Chats send the message too early:** with the "Type" paste method, line breaks act like Enter. Use the clipboard method.
- **Do not use AltGr as the hold key** on German and many other keyboards, it is needed for @, € and brackets.
- **Mouse button 5 no longer goes forward in the browser:** the chosen mouse button is reserved for dictation. Pick another one or switch it off under Shortcuts.
- **Something else is wrong:** right-click the icon and choose **Open log**, or open the data folder from the settings window.

## Uninstalling

Uninstall Sayvant from Windows Settings, Apps. The installer removes the program and the autostart entry. Your settings, history, the downloaded model and stored API keys stay in place so a reinstall picks up where you left off. To remove them as well, delete `%APPDATA%\Sayvant`, the model folders in `%USERPROFILE%\.cache\huggingface` and the `Sayvant` entries in the Credential Manager.

## Building from source

Requirements: Windows, Python 3.12, and [Inno Setup 6](https://jrsoftware.org/isinfo.php) for the installer.

```powershell
.\install.ps1                  # virtual environment and pinned dependencies
.\install.ps1 -DirectML        # additionally recognition on the graphics card
.\Sayvant debug.cmd            # run from source with a console
.\packaging\build.ps1          # dist\Sayvant\Sayvant.exe and the installer
```

`requirements.txt` lists the direct dependencies, `constraints.txt` the tested versions of all packages. Releases are built by GitHub Actions from version tags (`v0.2.0`). Signing through SignPath is prepared in the workflow and will be switched on once the application is approved, see [docs/SIGNING.md](docs/SIGNING.md) and the [code signing policy](CODE_SIGNING_POLICY.md).

The app consists of two processes: the tray app (hooks, recording, recognition, pasting, indicator) and the settings window (pywebview with WebView2), connected through a token-protected local connection.

## Credits and license

Inspired by [Diction](https://github.com/bendrape1-byte/Diction) for macOS. Local recognition uses [onnx-asr](https://github.com/istupakov/onnx-asr) with ONNX versions of NVIDIA Parakeet and Canary and OpenAI Whisper, downloaded from Hugging Face under their own licenses. The settings window is built with [pywebview](https://pywebview.flowrl.com/).

Sayvant is released under the [MIT License](LICENSE). Free code signing has been requested from [SignPath.io](https://about.signpath.io/) and the [SignPath Foundation](https://signpath.org/).
