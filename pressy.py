def uninstall_ffmpeg_from_path_and_self():
    import os, sys
    import tkinter as tk
    from tkinter import messagebox
    if os.name != 'nt':
        print("Uninstaller only supports Windows.")
        return
    bundled_bin = os.path.abspath(os.path.join(os.path.dirname(__file__), 'ffmpeg-8.0-essentials_build', 'ffmpeg-8.0-essentials_build', 'bin'))
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_READ) as key:
            current_path, _ = winreg.QueryValueEx(key, 'PATH')
    except FileNotFoundError:
        current_path = ''
    if bundled_bin in current_path:
        new_path = ';'.join([p for p in current_path.split(';') if os.path.abspath(p) != bundled_bin])
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, new_path)
        msg = f"The Pressy uninstaller has removed the bundled ffmpeg from your user PATH.\n\nYou may need to restart your terminal or log out/in for the change to take effect.\n\nPath removed: {bundled_bin}"
    else:
        msg = "The Pressy uninstaller did not find the bundled ffmpeg path in your user PATH. No changes were made."
    # Show popup
    root = tk.Tk(); root.withdraw()
    messagebox.showinfo("Pressy Uninstaller", msg)
    root.destroy()
    # Delete self (main file)
    main_file = os.path.abspath(__file__)
    try:
        os.remove(main_file)
    except Exception as e:
        # If running as .exe, schedule for deletion on exit
        import ctypes
        try:
            ctypes.windll.kernel32.MoveFileExW(main_file, None, 4)  # MOVEFILE_DELAY_UNTIL_REBOOT
        except Exception:
            pass
    sys.exit(0)
#!/usr/bin/env python3
"""
Pressy - A Discord-Friendly Video Compressor

Compresses MP4 videos to meet Discord's 10MB file size limit using FFmpeg.
Uses intelligent bitrate calculation based on video duration and target size.
Provides a GUI for batch processing or accepts command-line arguments.

Requirements:
- Python 3.7+
- ffmpeg and ffprobe in system PATH
- windows-curses (only needed if using curses; removed in this version)

Usage:
    python pressy.py                          # Launch GUI
    python pressy.py input.mp4 [output.mp4] [target_size_mb]
"""

import os
import sys
import time
import random
import subprocess
import tkinter as tk
from tkinter import (
    filedialog,
    simpledialog,
    messagebox,
    scrolledtext,
    ttk
)
from typing import List, Dict, Optional
import shutil


# -------------------------------
# CONFIGURATION
# -------------------------------

TARGET_SIZE_DEFAULT_MB = 9
DISCORD_LIMIT_MB = 10
AUDIO_BITRATE_KBPS = 128  # kbps reserved for audio
FUN_MESSAGES = [
    "🎉 Success! '{name}' is now just {size:.2f}MB. Ready for Discord uploads!",
    "🚀 All done! '{name}' was compressed from {orig:.2f}MB to {size:.2f}MB. Share away!",
    "🙌 Woohoo! '{name}' fits under Discord's 10MB limit at {size:.2f}MB. No more upload errors!",
    "✨ Magic! '{name}' is now {size:.2f}MB. You can upload it to Discord with no worries.",
    "😎 Nailed it! '{name}' went from {orig:.2f}MB to {size:.2f}MB. Discord will love this!",
    "🥳 Compression complete! '{name}' is a lean {size:.2f}MB. Time to flex those uploads!",
    "💾 Done! '{name}' is now {size:.2f}MB. Enjoy hassle-free Discord sharing!",
    "🎬 '{name}' is now {size:.2f}MB. You’re all set for Discord. Keep those memes coming!",
    "🔥 '{name}' was squished down to {size:.2f}MB. Discord won’t know what hit it!"
]


# -------------------------------
# UTILITY FUNCTIONS
# -------------------------------

def check_ffmpeg_installed() -> bool:
    """
    Check if ffmpeg and ffprobe are available in PATH.
    Returns True if both are found, False otherwise.
    """
    found = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None
    if not found and os.name == 'nt':
        # Try to add bundled ffmpeg to PATH
        bundled_bin = os.path.abspath(os.path.join(os.path.dirname(__file__), 'ffmpeg-8.0-essentials_build', 'ffmpeg-8.0-essentials_build', 'bin'))
        if os.path.exists(os.path.join(bundled_bin, 'ffmpeg.exe')):
            import winreg
            try:
                # Read current user PATH
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_READ) as key:
                    current_path, _ = winreg.QueryValueEx(key, 'PATH')
            except FileNotFoundError:
                current_path = ''
            # Only add if not already present
            if bundled_bin not in current_path:
                new_path = current_path + (';' if current_path else '') + bundled_bin
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, new_path)
                # Inform user
                root = tk.Tk(); root.withdraw()
                messagebox.showinfo(
                    "PATH Updated",
                    f"The bundled ffmpeg was added to your user PATH.\n\nYou must restart your computer before continuing.\n\nPath added: {bundled_bin}"
                )
                root.destroy()
                # After adding to PATH, user must restart for changes to take effect
                return False
            # Re-check
            found = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None
            if not found:
                # PATH was already set, but not visible to this process
                root = tk.Tk(); root.withdraw()
                messagebox.showwarning(
                    "Restart Required",
                    f"FFmpeg was found in your PATH, but is not accessible to this program. Please restart your computer before continuing."
                )
                root.destroy()
                return False
    return found


def print_ffmpeg_instructions() -> None:
    """
    Display instructions for installing FFmpeg in a message box.
    """
    msg = (
        "FFmpeg and ffprobe are required for this script to work.\n\n"
        "1. Download the latest FFmpeg release build from:\n"
        "   https://www.gyan.dev/ffmpeg/builds/#release-builds\n\n"
        "2. Extract the downloaded ZIP file to a folder, e.g., your Desktop.\n"
        "3. Open the extracted folder, then open the 'bin' subfolder. It should contain ffmpeg.exe and ffprobe.exe.\n"
        "4. Copy the full path to the 'bin' folder. Example:\n"
        "   C:\\Users\\YOURNAME\\Desktop\\ffmpeg-8.0-essentials_build\\ffmpeg-8.0-essentials_build\\bin\n\n"
        "5. Add this path to your System or User PATH environment variable:\n"
        "   - Press Win+S, search 'environment variables', and open 'Edit the system environment variables'.\n"
        "   - Click 'Environment Variables...'.\n"
        "   - Under 'User variables' or 'System variables', select 'Path' and click 'Edit'.\n"
        "   - Click 'New', paste the bin path, and click OK on all windows.\n\n"
        "6. Close ALL terminal windows and open a new one.\n"
        "7. Test by running: ffprobe -version\n\n"
        "After completing these steps, restart this script."
    )
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("FFmpeg Not Found", msg)
    root.destroy()


def pick_files(title: str, filetypes: List[tuple]) -> List[str]:
    """
    Open file dialog to select multiple files.
    Returns list of selected file paths.
    """
    root = tk.Tk()
    root.withdraw()
    files = filedialog.askopenfilenames(title=title, filetypes=filetypes)
    root.destroy()
    return list(files)


def pick_output_folder(title: str) -> Optional[str]:
    """
    Open folder dialog to select output directory.
    Returns selected folder path or None if cancelled.
    """
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title=title)
    root.destroy()
    return folder


def ask_target_size(default: float = TARGET_SIZE_DEFAULT_MB) -> Optional[float]:
    """
    Prompt user for target size in MB.
    Returns float value or None if cancelled.
    """
    root = tk.Tk()
    root.withdraw()
    size = simpledialog.askfloat(
        "Target Size",
        f"Enter target output size in MB (e.g. {default}):",
        initialvalue=default,
        minvalue=1,
        maxvalue=1000
    )
    root.destroy()
    return size


def show_summary_window(stats_list: List[Dict], output_folder: str) -> None:
    """
    Display a scrollable summary window with compression results.
    """
    popup = tk.Toplevel()
    popup.title("Compression Summary")
    popup.geometry("1000x600")

    # Text widget for summary
    st = scrolledtext.ScrolledText(popup, wrap=tk.WORD, font=("Consolas", 10))
    st.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Header
    summary = f"All done! Compressed files saved to: {output_folder}\n\n"
    summary += f"{'Original Name':<25} {'Input Size (MB)':>15} {'Output Name':<25} {'Output Size (MB)':>17} {'Saved (MB)':>12} {'Time (s)':>10} {'Status':>10}\n"
    summary += "-" * 115 + "\n"

    # Rows
    for s in stats_list:
        status = "✅" if s['under_target'] else "⚠️"
        summary += f"{s['original_name']:<25} {s['input_size']:>15.2f} {s['output_name']:<25} {s['output_size']:>17.2f} {s['saved']:>12.2f} {s['conversion_time']:>10.2f} {status:>10}\n"

    st.insert(tk.END, summary)
    st.config(state=tk.DISABLED)

    # Button frame
    btn_frame = tk.Frame(popup)
    btn_frame.pack(pady=10)

    def on_ok():
        popup.destroy()

    def on_another():
        popup.destroy()
        # Set a global flag to indicate another compression
        global COMPRESS_ANOTHER
        COMPRESS_ANOTHER = True

    ok_btn = tk.Button(btn_frame, text="OK", width=12, command=on_ok)
    ok_btn.pack(side="left", padx=8)
    another_btn = tk.Button(btn_frame, text="Compress Another", width=18, command=on_another)
    another_btn.pack(side="left", padx=8)

    popup.transient()  # Keep on top of main window
    popup.grab_set()   # Modal
    popup.wait_window()


# -------------------------------
# CORE COMPRESSION LOGIC
# -------------------------------

def compress_for_discord(input_file: str, output_file: str, target_size_mb: float) -> Dict:
    """
    Compress an MP4 video to fit within target_size_mb for Discord.

    Uses ffprobe to get duration, calculates optimal video bitrate,
    and uses ffmpeg to perform compression.

    Args:
        input_file: Path to input video file
        output_file: Path to output video file
        target_size_mb: Target file size in MB

    Returns:
        Dictionary with stats: original_name, output_name, input_size, output_size, conversion_time, under_target, saved
    """
    start_time = time.time()

    # Validate input file
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file does not exist: {input_file}")

    # Get video duration using ffprobe
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_file],
            capture_output=True,
            text=True,
            check=True,
            stdin=subprocess.DEVNULL
        )
        duration = float(result.stdout.strip())
    except (ValueError, subprocess.CalledProcessError) as e:
        raise RuntimeError(f"Failed to read video duration: {e}")

    if duration <= 0:
        raise ValueError("Video duration is zero or invalid.")

    # Convert target size from MB to bits
    target_size_bits = target_size_mb * 1024 * 1024 * 8
    audio_bitrate_bits = AUDIO_BITRATE_KBPS * 1000  # 128 kbps

    # Calculate video bitrate: total - audio
    video_bitrate_bits = int((target_size_bits / duration) - audio_bitrate_bits)

    if video_bitrate_bits <= 0:
        raise ValueError(
            f"Target size ({target_size_mb} MB) is too small for video of {duration:.2f}s "
            f"with {AUDIO_BITRATE_KBPS} kbps audio. Try increasing target size."
        )

    # Get input file size
    input_size_mb = os.path.getsize(input_file) / (1024 * 1024)

    # Log progress
    print(f"Compressing: {os.path.basename(input_file)}")
    print(f"Duration: {duration:.2f}s | Target: {target_size_mb}MB | Video Bitrate: {video_bitrate_bits / 1000:.2f} kbps")

    # Run ffmpeg
    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-b:v", str(video_bitrate_bits),
        "-b:a", str(audio_bitrate_bits),
        "-y",  # Overwrite output
        output_file
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg failed: {e}")

    # Get final output size
    final_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    elapsed = time.time() - start_time
    saved_mb = input_size_mb - final_size_mb
    under_target = final_size_mb <= target_size_mb

    # Generate fun message
    if under_target:
        msg = random.choice(FUN_MESSAGES).format(
            name=os.path.basename(output_file),
            size=final_size_mb,
            orig=input_size_mb
        )
        print(msg)
    else:
        print(f"⚠️ Warning: Could not compress under target size. Output is {final_size_mb:.2f}MB.")

    # Return stats
    return {
        "original_name": os.path.basename(input_file),
        "output_name": os.path.basename(output_file),
        "input_size": input_size_mb,
        "output_size": final_size_mb,
        "conversion_time": elapsed,
        "under_target": under_target,
        "saved": saved_mb
    }


# -------------------------------
# GUI MAIN APPLICATION
# -------------------------------

class PressyApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Pressy - Discord Video Compressor")
        self.root.geometry("700x500")
        self.root.resizable(True, True)

        # Style
        style = ttk.Style()
        style.theme_use('clam')

        # UI Components
        self.create_widgets()

    def create_widgets(self):
        # Title
        title_label = tk.Label(self.root, text="🎥 Pressy - Compress Videos for Discord", font=("Arial", 16, "bold"))
        title_label.pack(pady=(20, 10))

        # Instructions
        instr = tk.Label(
            self.root,
            text="Select input files and an output folder. Pressy will compress them to fit Discord's 10MB limit.",
            wraplength=650,
            justify="center",
            fg="#555"
        )
        instr.pack(pady=(0, 20))

        # Buttons Frame
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.select_files_btn = tk.Button(btn_frame, text="Select Input Files", command=self.select_input_files, width=20)
        self.select_files_btn.grid(row=0, column=0, padx=10)

        self.select_output_btn = tk.Button(btn_frame, text="Select Output Folder", command=self.select_output_folder, width=20)
        self.select_output_btn.grid(row=0, column=1, padx=10)

        self.target_size_btn = tk.Button(btn_frame, text="Set Target Size (MB)", command=self.set_target_size, width=20)
        self.target_size_btn.grid(row=0, column=2, padx=10)

        # Status display
        self.status_var = tk.StringVar(value="Ready. Select files to begin.")
        status_label = tk.Label(self.root, textvariable=self.status_var, fg="blue", font=("Arial", 10))
        status_label.pack(pady=10)

        # Progress area
        self.progress_text = scrolledtext.ScrolledText(self.root, height=12, state='disabled', font=("Consolas", 9))
        self.progress_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Start Button
        self.start_btn = tk.Button(self.root, text="Start Compression", command=self.start_compression, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
        self.start_btn.pack(pady=10)

        # Initialize state
        self.input_files: List[str] = []
        self.output_folder: Optional[str] = None
        self.target_size: float = TARGET_SIZE_DEFAULT_MB

    def log(self, message: str):
        """Append message to progress log."""
        self.progress_text.config(state='normal')
        self.progress_text.insert(tk.END, message + "\n")
        self.progress_text.see(tk.END)
        self.progress_text.config(state='disabled')

    def select_input_files(self):
        files = pick_files("Select MP4 Files", [("MP4 files", "*.mp4"), ("All files", "*.*")])
        if files:
            self.input_files = files
            self.status_var.set(f"Selected {len(files)} file(s).")
            self.log(f"✅ Selected {len(files)} input file(s).")
        else:
            self.log("❌ No files selected.")

    def select_output_folder(self):
        folder = pick_output_folder("Select Output Folder")
        if folder:
            self.output_folder = folder
            self.status_var.set(f"Output folder: {os.path.basename(folder)}")
            self.log(f"📁 Output folder set to: {folder}")
        else:
            self.log("❌ No output folder selected.")

    def set_target_size(self):
        size = ask_target_size(self.target_size)
        if size is not None:
            self.target_size = size
            self.status_var.set(f"Target size: {size} MB")
            self.log(f"🎯 Target size set to {size} MB")

    def start_compression(self):
        if not self.input_files:
            messagebox.showwarning("No Files", "Please select input files first.")
            return

        if not self.output_folder:
            messagebox.showwarning("No Folder", "Please select an output folder first.")
            return

        # Disable buttons during processing
        self.start_btn.config(state='disabled')
        self.select_files_btn.config(state='disabled')
        self.select_output_btn.config(state='disabled')
        self.target_size_btn.config(state='disabled')

        self.log(f"▶️ Starting compression of {len(self.input_files)} files...")
        self.root.update()

        stats_list = []
        total = len(self.input_files)

        try:
            for idx, input_file in enumerate(self.input_files):
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                custom_name = simpledialog.askstring(
                    "Output Name",
                    f"Enter output name for '{base_name}' (without extension):",
                    initialvalue=f"{base_name}_compressed"
                )

                output_name = f"{custom_name}.mp4" if custom_name else f"{base_name}_compressed.mp4"
                output_path = os.path.join(self.output_folder, output_name)

                self.log(f"[{idx+1}/{total}] Processing: {os.path.basename(input_file)} → {output_name}")

                # Perform compression
                try:
                    stats = compress_for_discord(input_file, output_path, self.target_size)
                    stats_list.append(stats)
                    self.log(f"✅ {output_name} ({stats['output_size']:.2f}MB)")
                except Exception as e:
                    self.log(f"❌ Error compressing {os.path.basename(input_file)}: {str(e)}")

            # Show summary
            global COMPRESS_ANOTHER
            COMPRESS_ANOTHER = False
            if stats_list:
                self.log("\n" + "="*60)
                self.log("🎉 COMPRESSION COMPLETE!")
                show_summary_window(stats_list, self.output_folder)
                if COMPRESS_ANOTHER:
                    # Reset state and restart workflow
                    self.input_files = []
                    self.output_folder = None
                    self.status_var.set("Ready. Select files to begin.")
                    self.progress_text.config(state='normal')
                    self.progress_text.delete('1.0', tk.END)
                    self.progress_text.config(state='disabled')
                    # Re-enable all buttons
                    self.start_btn.config(state='normal')
                    self.select_files_btn.config(state='normal')
                    self.select_output_btn.config(state='normal')
                    self.target_size_btn.config(state='normal')
                    self.select_input_files()
            else:
                messagebox.showinfo("No Success", "No files were successfully compressed.")

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{str(e)}")
            self.log(f"❗ Fatal error: {e}")

        finally:
            # Re-enable buttons
            self.start_btn.config(state='normal')
            self.select_files_btn.config(state='normal')
            self.select_output_btn.config(state='normal')
            self.target_size_btn.config(state='normal')


# -------------------------------
# COMMAND-LINE ENTRY POINT
# -------------------------------

def main_cli(input_file: str, output_file: str = "compressed.mp4", target_size_mb: float = TARGET_SIZE_DEFAULT_MB):
    """Command-line interface mode."""
    try:
        stats = compress_for_discord(input_file, output_file, target_size_mb)
        print("\n--- Conversion Stats ---")
        print(f"Original Name: {stats['original_name']}")
        print(f"Original Size: {stats['input_size']:.2f} MB")
        print(f"Output Name:   {stats['output_name']}")
        print(f"Output Size:   {stats['output_size']:.2f} MB")
        print(f"Saved:         {stats['saved']:.2f} MB")
        print(f"Time Taken:    {stats['conversion_time']:.2f} seconds")
        print(f"Done! Final size: {stats['output_size']:.2f} MB")
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


# -------------------------------
# ENTRY POINT
# -------------------------------

def show_startup_popup() -> bool:
    import shutil
    root = tk.Tk()
    root.title("Welcome to Pressy!")
    root.geometry("600x480")
    root.resizable(False, False)

    info = (
        "Pressy - Discord-Friendly Video Compressor\n\n"
        "This app compresses MP4 videos to fit under Discord's 10MB upload limit. "
        "It uses FFmpeg (open source) for video processing.\n\n"
        "What this app does:\n"
        "- Lets you select and compress videos via a simple GUI or command line.\n"
        "- Uses FFmpeg and ffprobe for all video/audio processing.\n"
        "- Bundles FFmpeg binaries for your convenience (no download needed).\n\n"
        "Permissions and Environment:\n"
        "- If FFmpeg is not found in your PATH, Pressy can add the bundled FFmpeg to your user PATH.\n"
        "- This makes FFmpeg available to other apps and the command line.\n"
        "- No files are downloaded from the internet.\n"
        "- No changes will be made to your PATH or system unless you explicitly allow it.\n\n"
    )

    import os
    import shutil
    import winreg
    root = tk.Tk()
    root.title("Welcome to Pressy!")
    root.geometry("600x480")
    root.resizable(False, False)

    info = (
        "Pressy - Discord-Friendly Video Compressor\n\n"
        "This app compresses MP4 videos to fit under Discord's 10MB upload limit. "
        "It uses FFmpeg (open source) for video processing.\n\n"
        "What this app does:\n"
        "- Lets you select and compress videos via a simple GUI or command line.\n"
        "- Uses FFmpeg and ffprobe for all video/audio processing.\n"
        "- Bundles FFmpeg binaries for your convenience (no download needed).\n\n"
        "Permissions and Environment:\n"
        "- If FFmpeg is not found in your PATH, Pressy can add the bundled FFmpeg to your user PATH.\n"
        "- This makes FFmpeg available to other apps and the command line.\n"
        "- No files are downloaded from the internet.\n"
        "- No changes will be made to your PATH or system unless you explicitly allow it.\n\n"
    )

    def check_in_env_paths(exe):
        if os.name != 'nt':
            return False
        paths = []
        # User PATH
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_READ) as key:
                user_path, _ = winreg.QueryValueEx(key, 'PATH')
                paths.extend(user_path.split(';'))
        except Exception:
            pass
        # System PATH
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment', 0, winreg.KEY_READ) as key:
                sys_path, _ = winreg.QueryValueEx(key, 'PATH')
                paths.extend(sys_path.split(';'))
        except Exception:
            pass
        for p in paths:
            exe_path = os.path.join(p.strip(), exe)
            if os.path.exists(exe_path):
                return True
        return False

    ffmpeg_found = shutil.which("ffmpeg") is not None or check_in_env_paths('ffmpeg.exe')
    ffprobe_found = shutil.which("ffprobe") is not None or check_in_env_paths('ffprobe.exe')
    all_found = ffmpeg_found and ffprobe_found

    status_text = "\nFFmpeg: {}\nffprobe: {}".format(
        "✅ Found" if ffmpeg_found else "❌ Not found",
        "✅ Found" if ffprobe_found else "❌ Not found"
    )

    label = tk.Label(root, text=info + status_text, justify="left", wraplength=480, font=("Arial", 10))
    label.pack(padx=20, pady=(20,10))

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=20)

    result = {'allow': False}

    def allow():
        result['allow'] = True
        root.destroy()

    def deny():
        result['allow'] = False
        root.destroy()

    install_btn = tk.Button(btn_frame, text="Install Bundled FFmpeg", width=22, command=allow, state=("disabled" if all_found else "normal"))
    install_btn.grid(row=0, column=0, padx=10)

    continue_btn = tk.Button(btn_frame, text="Continue", width=14, command=deny, state=("normal" if all_found else "disabled"))
    continue_btn.grid(row=0, column=1, padx=10)

    root.protocol("WM_DELETE_WINDOW", deny)

    root.mainloop()
    return result['allow']

def main():
    # Check for bundled FFmpeg if needed
    if not check_ffmpeg_installed():
        allow_install = show_startup_popup()
        if allow_install:
            # The check_ffmpeg_installed function will handle the installation
            if not check_ffmpeg_installed():
                sys.exit(1)
        else:
            print_ffmpeg_instructions()
            sys.exit(1)
    
    # Uninstaller mode
    if len(sys.argv) > 1 and sys.argv[1] in ("--uninstall", "/uninstall", "-u"):
        uninstall_ffmpeg_from_path_and_self()

    # CLI Mode: If arguments provided (and not uninstall)
    if len(sys.argv) > 1:
        try:
            input_file = sys.argv[1]
            output_file = sys.argv[2] if len(sys.argv) > 2 else "compressed.mp4"
            target_size = float(sys.argv[3]) if len(sys.argv) > 3 else TARGET_SIZE_DEFAULT_MB
            main_cli(input_file, output_file, target_size)
        except ValueError:
            print("❌ Invalid target size. Use: python pressy.py <input.mp4> [output.mp4] [target_size_mb]")
            sys.exit(1)
        except FileNotFoundError as e:
            print(f"❌ File not found: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            sys.exit(1)

    # GUI Mode
    else:
        root = tk.Tk()
        app = PressyApp(root)
        root.mainloop()

if __name__ == '__main__':
    main()