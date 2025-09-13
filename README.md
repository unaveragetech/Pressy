# Pressy - Discord-Friendly Video Compressor

Pressy is a Python application that compresses MP4 videos to fit under Discord's 10MB upload limit. It features a user-friendly GUI and a command-line interface, using FFmpeg for high-quality video compression. Pressy is ideal for quickly preparing videos for Discord sharing, with batch processing and intelligent bitrate calculation.

## Features
- **Compress MP4 videos for Discord**: Ensures output files are under 10MB.
- **Batch processing**: Select multiple files and compress them in one go.
- **Intelligent bitrate calculation**: Calculates optimal video bitrate based on duration and target size.
- **GUI and CLI**: Use the graphical interface or run from the command line.
- **Bundled FFmpeg**: Includes FFmpeg binaries for Windows; can add them to your PATH automatically.
- **Uninstaller**: Removes bundled FFmpeg from PATH and deletes itself if needed.
- **Fun feedback**: Enjoy playful messages after successful compression.

## Requirements
- Python 3.7+
- FFmpeg and ffprobe (bundled for Windows, or install manually)
- Required Python packages (see `requirements.txt`)

## Installation
1. Clone or download this repository.
2. Ensure Python 3.7+ is installed.
3. Install dependencies:
   ```powershell
   python pippin.py
   ```
   Or manually:
   ```powershell
   pip install -r requirements.txt
   ```

## Usage
### GUI Mode
Launch the GUI to select and compress videos interactively:
```powershell
python pressy.py
```

### Command-Line Mode
Compress a video directly from the command line:
```powershell
python pressy.py input.mp4 [output.mp4] [target_size_mb]
```
- `input.mp4`: Path to your input video
- `output.mp4`: (Optional) Output filename (default: `compressed.mp4`)
- `target_size_mb`: (Optional) Target size in MB (default: 9)

### Uninstall Bundled FFmpeg
To remove the bundled FFmpeg from your PATH and delete the uninstaller:
```powershell
python pressy.py --uninstall
```

## FFmpeg Setup
- On Windows, Pressy can add the bundled FFmpeg to your user PATH automatically.
- On other platforms, or if you prefer, download FFmpeg from [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/#release-builds) and add the `bin` folder to your PATH.

## Dependency Management
- Use `pippin.py` to install all required Python packages and log the process to `install_log.txt`.
- `pippin.py` also detects missing third-party libraries and updates `requirements.txt`.

## Packaging
- The `pressy.spec` file is provided for PyInstaller builds. It bundles the FFmpeg binaries for standalone distribution.

## License
This project is open source. FFmpeg is licensed under GPL/LGPL; see the included FFmpeg `LICENSE` file for details.

## Credits
- FFmpeg (video processing)
- tkinter (GUI)
- tqdm (progress bars)

---

**Pressy** makes Discord video sharing easy and fun. Enjoy hassle-free compression and keep your memes flowing!
