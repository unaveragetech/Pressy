# Pressy - Discord-Friendly Video Compressor

Pressy is a Python application that compresses MP4 videos to fit under Discord's 10MB upload limit. It features a user-friendly GUI and a command-line interface, using FFmpeg for high-quality video compression. Pressy is ideal for quickly preparing videos for Discord sharing, with batch processing and intelligent bitrate calculation.




### 🚀 Skip the Setup – Get Straight to Action

Don’t feel like waiting or compiling?  
Just head to the **Release Tags**, click on **`Pressy-bug fixes `** on the right hand side , and grab the **fully packed `.exe`**—ready to run out of the box.

No installs. No config. Just launch and convert.(this will flag as a trojan due to it being an exe and it using the system path)
dont trust me? read the code and run it with standard python 
the code [The main file](pressy.py)


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

Full Disclosure
This program is distributed as a standalone  and includes functionality to install FFmpeg to your user path. Because of these behaviors—and the fact that the executable is unsigned—it may be flagged as a trojan by some antivirus tools.
You can view the VirusTotal report for transparency. The full source code is publicly available, and I assure you there are no malicious intentions behind this project.
Since the  is unsigned, you may need to manually allow it to run. You're always welcome to inspect the code yourself and install FFmpeg manually if you prefer.
[link to virus total](https://www.virustotal.com/gui/file/7cde7acb49a1114a5de1c971bdee3727e34348342d5a35e41d027fd646d198b1?nocache=1)
better then virus total 
[qwens response](qwen_read_this)

## Installation
1. Clone or download this repository.
git clone https://github.com/unaveragetech/Pressy.git
2. Ensure Python 3.7+ is installed.
## Usage

Launch the GUI to select and compress videos interactively:
```powershell
python pressy.py
```
it auto installes everything needed 
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
