import subprocess
import sys
import time
import logging
import ctypes
import win32gui
import os
from winotify import Notification, audio  

def setup_logging():
    logging.basicConfig(
        filename='script_output.log',
        level=logging.INFO,
        format='%(asctime)s - %(message)s'
    )

def flash_taskbar(hwnd):
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
    except Exception as e:
        print(f"Warning: Failed to flash taskbar: {str(e)}")

def find_vscode_window():
    def enum_windows_callback(hwnd, results):
        title = win32gui.GetWindowText(hwnd)
        if "Visual Studio Code" in title and win32gui.IsWindowVisible(hwnd):
            results.append((hwnd, title))
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    if windows:
        hwnd, _ = windows[0]
        return hwnd
    return ctypes.windll.kernel32.GetConsoleWindow()

def notify_completion(command_desc, duration, success=True):
    status = "✅ Completed" if success else "❌ Failed"
    icon_file = "gigachad.ico" if success else "stare.ico"
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

    hwnd = find_vscode_window()
    if hwnd:
        flash_taskbar(hwnd)

def monitor_command(command_list):
    setup_logging()
    command_desc = ' '.join(command_list)
    start_time = time.time()

    try:
        process = subprocess.Popen(
            command_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                logging.info(output.strip())

        stderr = process.stderr.read()
        if stderr:
            print(stderr.strip())
            logging.error(stderr.strip())

        return_code = process.poll()
        duration = time.time() - start_time

        notify_completion(command_desc, duration, success=(return_code == 0))
        if return_code != 0:
            raise subprocess.CalledProcessError(return_code, command_list, stderr)

    except Exception as e:
        duration = time.time() - start_time
        notify_completion(command_desc, duration, success=False)
        logging.error(f"Error: {str(e)}")
        raise
    finally:
        print("Cleaning up process resources.")
        if 'process' in locals() and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                process.kill()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python monitor_command.py <command> [args...]")
        sys.exit(1)

    command_to_run = sys.argv[1:]
    try:
        monitor_command(command_to_run)
        print(f"Command {' '.join(command_to_run)} completed successfully.")
    except Exception as e:
        print(f"Command {' '.join(command_to_run)} failed: {str(e)}")
        sys.exit(1)
