import subprocess
import sys
import time
import logging
import ctypes
import win32gui
import win32con
import os
from winotify import Notification, audio
import threading

def setup_logging():
    # Configure logging to save terminal output to a file
    logging.basicConfig(
        filename='script_output.log',
        level=logging.INFO,
        format='%(asctime)s - %(message)s'
    )

def flash_taskbar(hwnd):
    # Use FlashWindowEx for reliable flashing
    class FLASHWINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", ctypes.c_uint),
            ("hwnd", ctypes.c_void_p),
            ("dwFlags", ctypes.c_uint),
            ("uCount", ctypes.c_uint),
            ("dwTimeout", ctypes.c_uint)
        ]

    FLASHW_ALL = 3
    flash_info = FLASHWINFO()
    flash_info.cbSize = ctypes.sizeof(FLASHWINFO)
    flash_info.hwnd = hwnd
    flash_info.dwFlags = FLASHW_ALL
    flash_info.uCount = 5
    flash_info.dwTimeout = 500
    try:
        ctypes.windll.user32.FlashWindowEx(ctypes.byref(flash_info))
        print(f"Flashed window handle: {hwnd}")
    except Exception as e:
        print(f"Warning: Failed to flash taskbar: {str(e)}")

def find_vscode_window():
    # Find VS Code window by partial title match
    def enum_windows_callback(hwnd, results):
        title = win32gui.GetWindowText(hwnd)
        if "Visual Studio Code" in title and win32gui.IsWindowVisible(hwnd):
            results.append((hwnd, title))
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    if windows:
        hwnd, title = windows[0]
        print(f"Found VS Code window handle: {hwnd}, title: {title}")
        return hwnd
    print("No VS Code window found, falling back to console.")
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        print(f"Found console window handle: {hwnd}")
    else:
        print("Warning: No valid window handle found for flashing.")
    return hwnd

def notify_completion(command_desc, duration, success=True):
    # Send desktop notification using winotify
    status = "✅ Completed" if success else "❌ Failed"
    icon_file = "icons/gigachad.ico" if success else "icons/stare.ico"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, icon_file)

    try:
        toast = Notification(
            app_id="VSCode Terminal Watchdog",
            title=status,
            msg=f"{command_desc}\nFinished in {duration:.2f} seconds.",
            icon=icon_path if os.path.exists(icon_path) else None,
            duration="short"
        )
        toast.set_audio(audio.Default, loop=False)
        toast.show()
    except Exception as e:
        print(f"Warning: Failed to show notification: {str(e)}")

    # Flash VS Code or console window
    hwnd = find_vscode_window()
    if hwnd:
        flash_taskbar(hwnd)
    else:
        print("No window to flash.")

def monitor_command(command_list):
    setup_logging()
    command_desc = ' '.join(command_list)
    start_time = time.time()

    def stream_reader(stream, log_func, print_prefix=None):
        for line in iter(stream.readline, ''):
            line = line.rstrip('\n')
            if print_prefix:
                print(f"{print_prefix}{line}")
            else:
                print(line)
            sys.stdout.flush()
            log_func(line)
        stream.close()

    try:
        env = {**os.environ, "PYTHONUNBUFFERED": "1", "CODE_MONITOR_ACTIVE": "1"}
        process = subprocess.Popen(
            command_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            env=env
        )

        stdout_thread = threading.Thread(target=stream_reader, args=(process.stdout, logging.info))
        stderr_thread = threading.Thread(target=stream_reader, args=(process.stderr, logging.error, '[stderr] '))
        stdout_thread.start()
        stderr_thread.start()

        stdout_thread.join()
        stderr_thread.join()
        return_code = process.wait()
        duration = time.time() - start_time

        notify_completion(command_desc, duration, success=(return_code == 0))
        if return_code != 0:
            raise subprocess.CalledProcessError(return_code, command_list)

    except Exception as e:
        duration = time.time() - start_time
        notify_completion(command_desc, duration, success=False)
        logging.error(f"Error: {str(e)}")
        raise
    finally:
        print("Cleaning up process resources.")
        sys.stdout.flush()
        if 'process' in locals() and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                process.kill()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python monitor_script.py <command> [args...]")
        sys.exit(1)

    command_to_run = sys.argv[1:]
    try:
        monitor_command(command_to_run)
        print(f"Command {' '.join(command_to_run)} completed successfully.")
        sys.stdout.flush()
    except Exception as e:
        print(f"Command {' '.join(command_to_run)} failed: {str(e)}")
        sys.exit(1)
    finally:
        print("Script execution complete, exiting.")
        sys.stdout.flush()
        sys.exit(0)