<h1 style="display: flex; align-items: baseline; gap: 12px;">
  <img src="samp.svg" alt="SAMP logo" style="height: 0.9em;">
  SAMP
</h1>

**SAMP** (*Spotify Ad Muter Panel*) is a Windows application that automatically controls Spotify's volume based on whether it is playing a song or an ad.
**Current version**: 1.3.0

## ✨ Features
* 🎛️ **Independent controls**: Adjust song and ad volume levels separately.
* 🔊 **System volume**: Manage Windows master volume directly from the main window.
* 🔄 **Automatic state detection**: Detects Spotify playback state (song vs. ad) using the Windows Media Control API (GSMTC/SMTC).
* ⚡ **Instant volume switching**: Adjusts Spotify's audio session volume via WASAPI (`pycaw`) immediately upon state transition.
* 🖥️ **Lightweight interface**: Modern GUI built with PyQt6 and integrated with `qasync`.
* 🎨 **Custom vector icons**: Built-in SVG icons for controls and playback states.
* 🌍 **Multi-language support**: English, Spanish, German, and French — switchable at runtime.
* 🎨 **Multiple visual themes**: Dark, Light, and Forest themes — switchable at runtime.
* ⏱️ **Configurable check interval**: Fine-tune state polling frequency (in tenths of a second).
* 🔁 **Start with Spotify**: Persistent background watcher launches SAMP automatically whenever Spotify starts during the session.
* 🔒 **Single-instance enforcement**: Uses `QLocalServer`/`QLocalSocket` to bring existing instances to focus rather than launching duplicates.
* ℹ️ **In-app documentation**: Integrated About dialog covering usage tutorials, architecture notes, and legal details.

## 📋 Requirements
* **Operating System:** Windows 10 / 11 (64-bit, build 17763 or higher).
* **CPU:** 1 GHz or higher (x86_64 architecture).
* **RAM:** 512 MB minimum, 1 GB recommended.
* **Free Space:** 52 MB minimum, 60 MB recommended.
* **Spotify:** Desktop app installed and running.
* **Python:** 3.8+ (3.12 recommended) — only required when running from source code.

## 🚀 Installation

### 💿 Executable Installer (Recommended)
Download and run `SAMP_Setup_1.3.0.exe` generated with Inno Setup. The setup wizard supports Express and Custom installations, desktop/Start Menu shortcut creation, and optional configuration of the *Start with Spotify* background task.

### 📦 Portable version (ZIP)
1. Download ´SAMP_1.3.0_portable.zip´ from the latest release. 
2. Extract the contents of the ZIP file to any folder or portable drive.
3. Run ´SAMP.exe´ directly — no installation or admin. privileges required.

### 🛠️ Running from Source
1. Clone the repository.
2. Install dependencies:
```bash
pip install PyQt6 qasync winsdk pycaw psutil comtypes
```
3. Run the application:
```bash
python main.py
```


## 🕹️ Usage

1. Launch Spotify and SAMP (or let it start automatically).
2. Adjust the sliders:
* **System**: Master Windows volume.
* **Song**: Target volume for music playback.
* **Ads**: Target volume for audio ads (set to 0% to mute completely).
3. Manual slider adjustments during any state automatically save the new target volume for that state.

### ⚙️ Settings (`Ctrl+,`)

* Change application language (English, Spanish, German, French).
* Change visual theme (Dark, Light, Forest).
* Adjust check interval (default: 0.5 seconds).
* Enable or disable **Start with Spotify** integration.

### 🔁 Start with Spotify - Details

* Registers or removes the `SAMP_StartWithSpotify` task in Windows Task Scheduler.
* A persistent background PowerShell watcher script listens for `Spotify.exe` launch events and triggers SAMP after a 2-second buffer.
* Synchronous UAC elevation verifies Administrator approval and reports real execution status.
* The scheduled task runs under normal user privileges without requiring elevated rights for daily operation.
* Restarting the current Windows session is recommended after enabling/disabling for changes to take full effect.

## ⚙️ How It Works

* Queries Spotify media transport controls via `winsdk` (`GSMTCM`).
* Uses the availability heuristic of the "Next Track" media button to differentiate songs from unskippable ads.
* Adjusts Spotify's audio session output volume via `pycaw` (WASAPI).
* Runs an asynchronous polling loop (`qasync` + `asyncio`) to monitor state changes and synchronize GUI sliders.
* Employs an IPC server (`QLocalServer` named `SAMP_SingleInstance`) to enforce single-instance operation.

#### 🔒 Privacy & Legal Notice

* **Privacy:** SAMP operates 100% locally, includes no telemetry or analytics, and makes no network requests.
* **Legal:** SAMP does not block ads, alter binary files, or modify Spotify's client; it solely controls system session audio output. See [DISCLAIMER.md](DISCLAIMER.md) for full terms.


## 🤝 Contributions

Contributions are welcome. Please open an issue or a pull request to propose changes or improvements.


## 🙏 Acknowledgements

The icons used in SAMP are drawn with SVG.

- The main icon (framed quarter rest, coloured #CC7722) is based on the [Quarter Rest icon from SVG Repo](https://www.svgrepo.com/svg/480283/quarter-rest), used under the terms of the [SVGRepo license](https://www.svgrepo.com/page/licensing/). The final composition and colouring are original work by the developer.

- The other icons (speaker, Spotify icon, and ad icon) are taken from the [tabler-icons](https://github.com/tabler/tabler-icons) repository ([MIT license](https://opensource.org/licenses/MIT)).

> Remember to support those projects by visiting the provided links.


## 📧 Contact

Developer: contact@eucarigo.com
Legal notice: `DISCLAIMER.md`

---

⭐ If you find it useful, please give the repository a star.

*Free software, without ads & login, open source and libre licensed.*
