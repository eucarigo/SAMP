<h1 style="display: flex; align-items: center; gap: 12px;">
  <img src="samp.svg" alt="SAMP logo" style="height: 1em; margin-top: 0.2em;">
  SAMP
</h1>

**SAMP** (acronym for *Spotify Ad Muter Panel*) is a Windows application that automatically controls Spotify's volume based on whether it is playing a song or an ad.

It lets you adjust the volume level for songs and ads separately, and also integrates with the system volume.

**Current version**: 1.0


## ✨ Features

- 🎛️ **Independent controls** for song and ad volume.
- 🔊 **System volume** also adjustable from the same window.
- 🔄 **Automatic detection** of Spotify's state (song / ad) using the Windows Media Control API (SMTC).
- ⚡ **Instant volume switching** when Spotify changes from a song to an ad or vice versa.
- 🖥️ **Lightweight interface** with PyQt6 and a dark theme.
- 🎨 **Custom icons** for each mode.


## 📋 Requirements

- **Operating system:** Windows 10 / 11 (64-bit)
- **CPU:** 1 GHz or higher (any x86_64 processor from the last 10 years)
- **RAM:** 512 MB minimum, 1 GB or more recommended
- **Free space:** at least 65 MB (100 MB recommended)
- **Spotify:** desktop app installed and running
- **Python:** not required if using the executable (coming soon), but for development you need Python 3.8+ (3.12 recommended)

### Dependencies (only when running from source)

```bash
pip install pyqt6 qasync pycaw psutil winsdk comtypes
```


## 🚀 Installation

> Precompiled executables will be published soon. In the meantime, you can run from source code.


## 🕹️ Usage

1. Launch Spotify and play a song or an ad.

2. Adjust the sliders:

- `Sistema` (translated *System*): controls the Windows master volume.
- `Canción` (translated *Song*): automatically applied when Spotify plays a song.
- `Anuncios` (translated *Ads*): volume applied during audio ads.

3. SAMP automatically detects the playback state and changes the Spotify session volume to the value you have chosen for that state.

> 💡 Note: If you manually change Spotify's volume using the slider for a song or an ad while in that state, the change is applied immediately and saved as the new preferred value for that state.


## ⚙️ How it works

- Uses the Windows `GlobalSystemMediaTransportControlsSessionManager` API (winsdk) to obtain Spotify's media session.
- Detects whether the next button is enabled: in Spotify, the next button is active during songs, but disabled during ads – that is the heuristic used.
- Uses `pycaw` to get the volume control of the `Spotify.exe` audio session and adjusts it according to the current state.
- An asynchronous thread periodically monitors the state and external volume changes (e.g., the user changes volume from the Windows mixer) and synchronises the sliders.


## ⚠️ Summary of Legal Notice

Use of SAMP is at your own risk. Read the [full legal notice](DISCLAIMER.md) to understand the terms regarding compliance with Spotify's Terms of Service, limitation of liability, and license.

In summary:

- SAMP does not block ads, it only lowers their volume.
- It does not modify the Spotify client or interact with its servers.
- The developer is not responsible for any suspension of your Spotify account based on the company's interpretation of the use of this tool.

### IMPORTANT

> The text above **does not invalidate or replace** the [full legal notice](DISCLAIMER.md); it merely summarises it to make the official notice easier to understand for non‑specialist readers.

## 📄 License

This project is distributed under the GNU General Public License v3.0 (GPLv3), without warranties. See the `LICENSE` file for details or visit the [official GPLv3 page](https://www.gnu.org/licenses/gpl-3.0.txt).


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
