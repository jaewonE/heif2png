# HEIC Converter

[ [English](README.md) | [한국어](README.ko.md) ]

**Batch-convert HEIC/HEIF images to PNG, JPEG or WEBP with a single drag-and-drop.**

![Demo](https://github.com/jaewonE/heif2png/blob/main/assets/demo.gif?raw=true)

---

## Table of Contents

1. [Features](#features)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Building Stand-alone Binaries](#building-stand-alone-binaries)
6. [Roadmap](#roadmap)
7. [Contributing](#contributing)
8. [License](#license)

---

## Features

- **Drag & drop interface** – drop individual files or whole folders; sub-folders are scanned automatically :contentReference[oaicite:0]{index=0}:contentReference[oaicite:1]{index=1}.
- **Batch conversion** to **PNG, JPEG or WEBP** with per-format optimisations (alpha-channel handling, quality settings) :contentReference[oaicite:2]{index=2}.
- **Metadata preservation** – optional retention of EXIF and ICC colour profiles :contentReference[oaicite:3]{index=3}:contentReference[oaicite:4]{index=4}.
- **Overwrite-in-place or “Converted Files” output folder** – keep originals safe or replace them in one click :contentReference[oaicite:5]{index=5}:contentReference[oaicite:6]{index=6}.
- **Live preview & progress bar** – see a thumbnail of the selected image and real-time progress updates :contentReference[oaicite:7]{index=7}.
- **Persistent preferences** – chosen options are remembered between sessions (via Qt `QSettings`) :contentReference[oaicite:8]{index=8}:contentReference[oaicite:9]{index=9}.
- **Pure-Python, cross-platform GUI** built with PyQt 6 – runs on Windows, macOS and Linux.

---

## Quick Start

```bash
# 1.  Install dependencies
uv venv --python=3.11.10
uv sync

# 2.  Launch the GUI
uv run app.py
```

---

## Installation

### Prerequisites

| Software            | Version                         |
| ------------------- | ------------------------------- |
| **Python**          | 3.11 recommended                |
| **pip**             | latest recommended              |
| **libheif** (Linux) | Optional – improves performance |

### Dependencies

```
PyQt6
pillow-heif    # HEIC/HEIF decoder plug-in for Pillow
pyinstaller    # for building stand-alone binaries
```

Install them manually or use the provided **`pyproject.toml`**.

---

## Usage

1. **Run the application** (`python app.py` or the packaged binary).
2. **Drag** one or more _.heic_ / _.heif_ files (or a folder) into the drop zone.
3. Choose:

   - **Output format**: PNG / JPEG / WEBP
   - **Overwrite original files** – unchecked = save to _Converted Files_ sub-folder
   - **Maintain metadata** – keep EXIF / ICC information

4. Click **Start Conversion**.
5. When the progress bar completes, a summary dialog lists successes, failures and output locations.

---

## Building Stand-alone Binaries

The project works out-of-the-box with **PyInstaller**.

<details>
<summary><strong>Windows (x64)</strong></summary>

```cmd
pyinstaller ^
  --noconsole --onefile ^
  --name "HeicConverter" ^
  --icon "assets\heic_converter.ico" ^
  --collect-all pillow_heif ^
  app.py
```

</details>

<details>
<summary><strong>macOS (Apple Silicon)</strong></summary>

```bash
pyinstaller \
  --onefile --windowed \
  --target-architecture arm64 \
  --name "HeicConverter" \
  --icon "assets/heic_converter.icns" \
  --collect-all pillow_heif \
  app.py
```

</details>

The generated executable is fully self-contained—no Python installation required for end-users.

---

## Roadmap

- CLI mode for headless batch processing
- Additional export formats (TIFF, AVIF)
- Dark-theme toggle
- Installer scripts (.msi, .dmg, .deb)

Got an idea? [Open an issue](../../issues) or send a PR!

---

## Contributing

1. Fork the repository and create your branch: `git checkout -b feature/awesome-idea`
2. Commit your changes with clear messages.
3. Push to the branch and open a pull request.

Please make sure your code follows **PEP 8** and is covered by sensible tests where possible.

---

## License

Released under the **GNU General Public License v3.0**.
See [`LICENSE`](LICENSE) for the full text.

Enjoy lightning-fast HEIC conversion! If this project saves you time, a ⭐ is always appreciated.
