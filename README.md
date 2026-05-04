# pkgme

A beginner-friendly CLI tool for managing packages on Linux. pkgme automatically detects which package managers are installed on your system and provides a single, consistent interface, reducing the need to remember distro-specific commands.

---

## Features

- Auto-detects installed package managers (apt, dnf, yum, pacman, yay, zypper, apk, snap, flatpak)
- Install, uninstall, search, and update packages through a guided interactive menu
- Upgrade all packages across every detected package manager in one command
- Lazy package manager selection: only asks when an action actually needs it
- Distro-aware dependency hints: if `rich` is missing, tells you the right install command for your distro
- Clean, colour-coded terminal output via the [Rich](https://github.com/Textualize/rich) library

---

## Supported Package Managers

| Manager   | Distro / Type             |
|-----------|---------------------------|
| apt       | Debian / Ubuntu / Mint    |
| dnf       | Fedora / RHEL 8+          |
| yum       | CentOS / older RHEL       |
| pacman    | Arch / Manjaro            |
| yay       | Arch AUR helper           |
| zypper    | openSUSE                  |
| apk       | Alpine Linux              |
| snap      | Universal packages        |
| flatpak   | Universal packages        |

---

## Requirements

- Python 3.6+
- [rich](https://github.com/Textualize/rich). Install via your package manager:

| Distro          | Command                        |
|-----------------|--------------------------------|
| Arch / Manjaro  | `sudo pacman -S python-rich`   |
| Debian / Ubuntu | `sudo apt install python3-rich` |
| Fedora          | `sudo dnf install python3-rich` |
| Alpine          | `sudo apk add py3-rich`        |
| Others          | `pip install rich`             |

---

## Installation

```bash
git clone https://github.com/SarthakParab/pkgme.git
cd pkgme
chmod +x pkgme.py
sudo mv pkgme.py /usr/local/bin/pkgme   # optional: makes 'pkgme' available system-wide
```

---

## Usage

### Interactive mode (recommended for beginners)
```bash
pkgme
```
Launches a guided menu — just pick a number and follow the prompts.

### Direct commands
```bash
pkgme install <package>          # Install one or more packages
pkgme uninstall <package>        # Remove one or more packages
pkgme search <term>              # Search for a package
pkgme update                     # Refresh package lists
pkgme upgrade-all                # Upgrade all packages across all managers
pkgme info                       # Show detected package managers
pkgme help                       # Show help
```

### Examples
```bash
pkgme install vlc
pkgme install git curl wget
pkgme uninstall vlc
pkgme search "video editor"
pkgme upgrade-all
```

---

## How It Works

1. On launch, pkgme scans your system for supported package managers using `shutil.which`.
2. In interactive mode, the action menu appears first. A package manager is only selected when the chosen action requires one (install, uninstall, search, update).
3. If multiple managers are detected, pkgme presents a table and lets you pick.
4. `upgrade-all` skips selection entirely and runs the upgrade command for every detected manager, then prints a summary table of results.

---
