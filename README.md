# 🗿 VSCode Terminal Watchdog

**VSCode Terminal Watchdog** is a Python-based command monitor designed to wrap your terminal commands in Visual Studio Code. It logs output, notifies you upon completion (with a Windows toast), and flashes the taskbar to keep you in the loop, all while feeling like a native part of your workflow.

> ⚡ Perfect for lazy folks like me who don't want to keep checking the terminal every few minutes, just let it notify you when your script, compile, or install finishes in VS Code. Since other VSCode extensions requires payment for this kind of thing, I decided to create my own that does exactly what I need, cause why not?

---

## ✨ Features

- Windows toast notifications (using [winotify](https://pypi.org/project/winotify/))
- Custom success/failure icons and emoji titles
- Taskbar flashing to grab attention
- Logs output to `script_output.log`
- Only activates inside VS Code terminal
- Simple PowerShell profile integration

---

## 📦 Requirements

- Windows OS
- Python 3.8+
- PowerShell 5+
- Visual Studio Code

Python packages:

- [pywin32](https://pypi.org/project/pywin32/)
- [winotify](https://pypi.org/project/winotify/)

## 🔧 Setup Instructions

1. Clone Repository

```bash
git clone https://github.com/yourusername/vscode-terminal-watchdog.git
cd vscode-terminal-watchdog
```

2. Create a Virtual Environment (Optional but recommended)

```bash
python -m venv .venv
.venv\Scripts\activate

```

3. Install requirements

```bash
pip install -r requirements.txt
```

4. Add Custom Icons (Optional)
   Place `.ico` files in the same directory as `script.py`:

- `gigachad.ico` → for success
- `stare.ico` → for failure
  Or change filenames in `script.py` accordingly.

## ⚙️ PowerShell Profile Setup (Windows)

To enable automatic monitoring only inside VS Code, update your PowerShell profile:

1. Find your profile path (in powershell):

```powershell
$PROFILE
```

> if missing, create the profile file:
>
> ```powershell
>   New-Item -Path $PROFILE -ItemType File -Force
> ```
>
> 2. Open and edit the file:

```bash
notepad $PROFILE
```

3. Paste the following (update paths as needed):

```powershell
# Confirm profile loaded
Write-Host "VS Code PowerShell profile loaded"

# Path to your global Python (not the one in .venv or .env)
$systemPython = "C:\Users\YourName\AppData\Local\Programs\Python\Python312\python.exe"
$monitor = "C:\Users\YourName\Path\To\vscode-terminal-watchdog\script.py"

function Is-InVSCode {
    return ($env:TERM_PROGRAM -eq "vscode")
}

# Only override commands if running inside VS Code and not already in monitor
if (-not $env:CODE_MONITOR_ACTIVE -and (Is-InVSCode)) {
    function python {
        & $systemPython $monitor python @args
    }
    function pip {
        & $systemPython $monitor pip @args
    }
    function npm {
        & $systemPython $monitor npm @args
    }
    function node {
        & $systemPython $monitor node @args
    }
    function git {
        & $systemPython $monitor git @args
    }
}
```

> 🔁 Replace `$systemPython` and `$monitor` with the absolute paths to your global Python and `script.py`.

> ⚠️ **Note:** The monitor script will always run with your global Python (where you install `winotify`, `pywin32`, etc.), but the commands you run (like `python app.py`) will use the current environment (including virtualenvs). You do **not** need to install monitor dependencies in every virtual environment—just globally.

## 🧪 How It Works

When you type a command like:

```bash
python test.py
```

...VSCode Terminal Watchdog intercepts it, runs it through the monitor script, logs the output, and notifies you on completion.

📋 Output Example

- Notification title: ✅ Completed or ❌ Failed

- Body: python test.py — Finished in 3.42 seconds.

- Audio: Windows default chime

- Icon: Custom .ico based on success/failure

- Log: Saved to script_output.log

## 📁 Project Structure

```bash
vscode-terminal-watchdog/
│
├── /icons
   │
   ├── gigachad.ico         # Optional icon (success)
   ├── stare.ico            # Optional icon (failure)
├── script.py               # Core monitor script
├── script_output.log       # Auto-generated log file
├── requirements.txt        # Dependencies
└── README.md               # This file

```

## 🧼 Uninstallation

To remove:

- Delete PowerShell profile entries or remove the `if (Is-InVSCode)` block.
- Delete the project folder.
- Deactivate and remove the virtual environment.

---

## 📜 License

MIT License — 🛠️ I made this for personal use. Feel free to do whatever you want with it 😄

## 🙌 Credits

- [winotify](https://pypi.org/project/winotify/)
- [pywin32](https://pypi.org/project/pywin32/)
- You, for using it.
