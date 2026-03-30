# USING JSHORTCUTS ON WINDOWS

`jshortcuts` provides seamless integration for Windows desktops, natively supporting Command Prompt and PowerShell, as well as installing a convenient Graphical Desktop icon.

## Installation

Because the framework natively manages your Windows directories, you can install the system globally with minimal effort:

1. Download or "Clone" this repository as a `.zip` file into your Downloads folder.
2. Extract the folder.
3. Open the extracted folder until you see the `install.bat` file.
4. **Double-click `install.bat`** to run the Windows installer!

> [!IMPORTANT]
> A small command window will pop up. It will attempt to automatically bind the `jshortcuts` command to your environment variables. **You must have Python 3 installed** on your system. If you do not, the prompt will halt and instruct you to download Python from [python.org](https://python.org).

### What the installer does behind the scenes:
- Copies the core executable files into your local user folder at `%LOCALAPPDATA%\jshortcuts`.
- Generates a Windows `jshortcuts.bat` file which reroutes system terminal requests straight into Python dynamically.
- Drops a Graphical UI launcher natively onto your Desktop called **jshortcuts**.
- Inserts `%LOCALAPPDATA%\jshortcuts` directly into your user's system `PATH`.

## How to execute After Installation

You have two primary options:

#### 1. The Graphical User Interface (GUI)
Simply locate your Desktop, and **double-click** the newly generated `jshortcuts` shortcut icon. The desktop interface functions exactly identically to its Linux counterpart.

#### 2. The Terminal Command-Line Interface (CLI)
Open **PowerShell**, **Windows Terminal**, or **Command Prompt**, and try typing:

```bat
jshortcuts help
```

It should return the system-global help interface featuring rich, native ANSI colors directly in the Windows environment shell.

## Uninstalling your Environment

If you ever wish to completely purge `jshortcuts` from your Windows machine:
1. Re-open the downloaded repository folder from when you initially installed it.
2. Double-click `uninstall.bat`.

The installation script cleanly deletes the `%LOCALAPPDATA%` copy and gracefully severs all desktop shortcuts. It will then ask you if you want to completely destroy your local database files and your local tracked Github synchronization `.jshortcuts-sync` clone (useful if you are fully resetting!).

> [!WARNING]
> Because safely parsing and mutating the Windows Environment `PATH` array using batch scripts is inherently risky, you must open your Start Menu, type "Environment Variables", and explicitly select and delete `%LOCALAPPDATA%\jshortcuts` from your PATH list to completely stop the command binding.
