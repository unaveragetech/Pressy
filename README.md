# Pressy

A fast and simple video compression tool powered by FFmpeg. Compress your videos quickly and efficiently with just a few commands.

## 📋 Overview

Pressy is a standalone command-line tool designed to make video compression easy and accessible. Whether you need to reduce file sizes for storage, sharing, or streaming, Pressy provides a simple interface to FFmpeg's powerful compression capabilities.

## ✨ Features

- **Fast Compression**: Leverage FFmpeg's optimized encoding for quick processing
- **Multiple Formats**: Support for popular video formats (MP4, AVI, MOV, MKV, and more)
- **Quality Control**: Choose from preset quality levels or customize compression settings
- **Batch Processing**: Compress multiple videos at once
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Lightweight**: Minimal resource usage with maximum efficiency

## 🚀 Quick Start

### Installation

1. Go to the [Releases](https://github.com/unaveragetech/Pressy/releases) tab
2. Download the latest release for your operating system
3. Extract the archive and run the executable

### Prerequisites

- **FFmpeg** must be installed on your system
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use `winget install FFmpeg`
  - macOS: Install via Homebrew: `brew install ffmpeg`
  - Linux: Install via package manager: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo yum install ffmpeg` (RedHat/CentOS)

### Basic Usage

```bash
# Compress a single video with default settings
pressy input.mp4

# Compress with custom output name
pressy input.mp4 -o compressed_video.mp4

# Compress with specific quality (1-5, where 1 is highest quality)
pressy input.mp4 --quality 3

# Compress multiple videos
pressy video1.mp4 video2.mp4 video3.mp4

# Compress all MP4 files in current directory
pressy *.mp4
```

## 🛠️ Command Options

```
Usage: pressy [OPTIONS] <input_files>...

Options:
  -o, --output <FILE>     Output filename (for single file compression)
  -q, --quality <LEVEL>   Compression quality level (1-5) [default: 3]
  -f, --format <FORMAT>   Output format (mp4, avi, mov, mkv) [default: mp4]
  --preset <PRESET>       FFmpeg preset (ultrafast, fast, medium, slow, veryslow) [default: medium]
  --bitrate <BITRATE>     Target bitrate (e.g., 1M, 500K)
  --resolution <RES>      Target resolution (e.g., 1920x1080, 1280x720)
  --batch-dir <DIR>       Process all videos in directory
  -h, --help              Show help message
  -v, --version           Show version information
```

## 📊 Quality Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| 1 | Highest quality, larger file | Archival, professional use |
| 2 | High quality | High-definition sharing |
| 3 | Balanced (default) | General use, good quality-size ratio |
| 4 | Good compression | Web uploads, faster processing |
| 5 | Maximum compression | Social media, minimal storage |

## 💡 Examples

```bash
# Compress for web sharing (720p, medium quality)
pressy vacation.mp4 --resolution 1280x720 --quality 3

# Quick compression with maximum speed
pressy large_video.mov --preset ultrafast --quality 4

# Compress for mobile with specific bitrate
pressy presentation.mp4 --bitrate 500K --format mp4

# Batch compress all videos in a folder
pressy --batch-dir ./videos --quality 3 --format mp4
```

## 🔧 Troubleshooting

### FFmpeg Not Found
If you see an error about FFmpeg not being found:
1. Ensure FFmpeg is installed and in your system PATH
2. Test FFmpeg installation: `ffmpeg -version`
3. On Windows, you may need to restart your terminal after installation

### Compression Taking Too Long
- Use `--preset ultrafast` for faster processing
- Reduce quality level (higher number = faster processing)
- Consider lowering resolution for very large videos

### Output Quality Issues
- Lower quality numbers (1-2) for better quality
- Use slower presets (`slow`, `veryslow`) for better compression efficiency
- Adjust bitrate manually for fine-tuned control

## 📈 Performance Tips

- **SSD Storage**: Process videos on SSD for faster I/O
- **CPU Cores**: FFmpeg will automatically use multiple cores
- **RAM**: Ensure sufficient RAM for large video files
- **Batch Processing**: Process multiple small files together for efficiency

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines and feel free to submit issues or pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [FFmpeg](https://ffmpeg.org/) - the leading multimedia framework
- Thanks to all contributors and users who help improve Pressy

---

**Need help?** Open an issue in our [GitHub Issues](https://github.com/unaveragetech/Pressy/issues) section.
