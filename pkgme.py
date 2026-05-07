#!/usr/bin/env python3
"""
pkgme - A beginner-friendly package installer for Linux
Automatically detects your package manager and installs software for you.
"""

import shutil
import subprocess
import sys

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.rule import Rule
    from rich import box
except ImportError:
    import shutil as _shutil

    # Give distro-appropriate advice instead of always saying "pip install"
    if _shutil.which("pacman"):
        cmd = "sudo pacman -S python-rich"
    elif _shutil.which("apt"):
        cmd = "sudo apt install python3-rich"
    elif _shutil.which("dnf"):
        cmd = "sudo dnf install python3-rich"
    elif _shutil.which("yum"):
        cmd = "sudo yum install python3-rich"
    elif _shutil.which("zypper"):
        cmd = "sudo zypper install python3-rich"
    elif _shutil.which("apk"):
        cmd = "sudo apk add py3-rich"
    else:
        cmd = "pip install rich"

    print(f"pkgme requires the 'rich' library. Install it with:  {cmd}")
    sys.exit(1)

console = Console()

# ──────────────────────────────────────────────────────────────────────────────
# Package manager definitions
# ──────────────────────────────────────────────────────────────────────────────
PACKAGE_MANAGERS = [
    {
        "name": "apt",
        "label": "APT",
        "distro": "Debian / Ubuntu / Mint",
        "install":   ["sudo", "apt", "install", "-y"],
        "uninstall": ["sudo", "apt", "remove", "-y"],
        "update":    ["sudo", "apt", "update"],
        "upgrade":   ["sudo", "apt", "upgrade", "-y"],
        "search":    ["apt-cache", "search"],
    },
    {
        "name": "dnf",
        "label": "DNF",
        "distro": "Fedora / RHEL 8+",
        "install":   ["sudo", "dnf", "install", "-y"],
        "uninstall": ["sudo", "dnf", "remove", "-y"],
        "update":    ["sudo", "dnf", "check-update"],
        "upgrade":   ["sudo", "dnf", "upgrade", "-y"],
        "search":    ["dnf", "search"],
    },
    {
        "name": "yum",
        "label": "YUM",
        "distro": "CentOS / older RHEL",
        "install":   ["sudo", "yum", "install", "-y"],
        "uninstall": ["sudo", "yum", "remove", "-y"],
        "update":    ["sudo", "yum", "check-update"],
        "upgrade":   ["sudo", "yum", "update", "-y"],
        "search":    ["yum", "search"],
    },
    {
        "name": "pacman",
        "label": "Pacman",
        "distro": "Arch / Manjaro",
        "install":   ["sudo", "pacman", "-S", "--noconfirm"],
        "uninstall": ["sudo", "pacman", "-R", "--noconfirm"],
        "update":    ["sudo", "pacman", "-Sy"],
        "upgrade":   ["sudo", "pacman", "-Syu", "--noconfirm"],
        "search":    ["pacman", "-Ss"],
    },
    {
        "name": "yay",
        "label": "Yay",
        "distro": "Arch AUR helper",
        "install":   ["yay", "-S", "--noconfirm"],
        "uninstall": ["yay", "-R", "--noconfirm"],
        "update":    ["yay", "-Sy"],
        "upgrade":   ["yay", "-Syu", "--noconfirm"],
        "search":    ["yay", "-Ss"],
    },
    {
        "name": "zypper",
        "label": "Zypper",
        "distro": "openSUSE",
        "install":   ["sudo", "zypper", "install", "-y"],
        "uninstall": ["sudo", "zypper", "remove", "-y"],
        "update":    ["sudo", "zypper", "refresh"],
        "upgrade":   ["sudo", "zypper", "update", "-y"],
        "search":    ["zypper", "search"],
    },
    {
        "name": "apk",
        "label": "APK",
        "distro": "Alpine Linux",
        "install":   ["sudo", "apk", "add"],
        "uninstall": ["sudo", "apk", "del"],
        "update":    ["sudo", "apk", "update"],
        "upgrade":   ["sudo", "apk", "upgrade"],
        "search":    ["apk", "search"],
    },
    {
        "name": "snap",
        "label": "Snap",
        "distro": "Universal packages",
        "install":   ["sudo", "snap", "install"],
        "uninstall": ["sudo", "snap", "remove"],
        "update":    ["sudo", "snap", "refresh"],
        "upgrade":   ["sudo", "snap", "refresh"],
        "search":    ["snap", "find"],
    },
    {
        "name": "flatpak",
        "label": "Flatpak",
        "distro": "Universal packages",
        "install":   ["flatpak", "install", "-y", "flathub"],
        "uninstall": ["flatpak", "uninstall", "-y"],
        "update":    ["flatpak", "update", "-y"],
        "upgrade":   ["flatpak", "update", "-y"],
        "search":    ["flatpak", "search"],
    },
]


# ──────────────────────────────────────────────────────────────────────────────
# Core helpers
# ──────────────────────────────────────────────────────────────────────────────
def detect_package_managers():
    """Return a list of package manager dicts available on this system."""
    return [pm for pm in PACKAGE_MANAGERS if shutil.which(pm["name"])]


def run(cmd):
    """Run a command, streaming output live. Returns exit code."""
    try:
        result = subprocess.run(cmd)
        return result.returncode
    except FileNotFoundError:
        console.print(f"  [red]✗ Command not found:[/red] {cmd[0]}")
        return 1


def ask_yn(prompt):
    """Ask a yes/no question. Returns bool."""
    try:
        return Confirm.ask(f"  [yellow]{prompt}[/yellow]")
    except (EOFError, KeyboardInterrupt):
        console.print()
        sys.exit(0)


def ask_input(prompt):
    """Ask for freeform text input."""
    try:
        return Prompt.ask(f"  [cyan]{prompt}[/cyan]").strip()
    except (EOFError, KeyboardInterrupt):
        console.print()
        sys.exit(0)


def pick_pm(available):
    """Let the user pick a package manager when multiple are available."""
    if len(available) == 1:
        return available[0]

    console.print()
    table = Table(
        title="[bold]Multiple package managers detected[/bold]",
        box=box.ROUNDED,
        border_style="cyan",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("#",             style="bold cyan", justify="right", width=4)
    table.add_column("Name",          style="bold white")
    table.add_column("Distro / Type", style="dim white")

    for i, pm in enumerate(available, 1):
        table.add_row(str(i), pm["label"], pm["distro"])

    console.print(table)
    console.print()

    choices = [str(i) for i in range(1, len(available) + 1)]
    while True:
        try:
            choice = Prompt.ask(
                f"  [cyan]Which one should I use?[/cyan] [dim](1–{len(available)})[/dim]"
            ).strip()
        except (EOFError, KeyboardInterrupt):
            console.print()
            sys.exit(0)
        if choice in choices:
            return available[int(choice) - 1]
        console.print(f"  [yellow]Please enter a number between 1 and {len(available)}.[/yellow]")


# ──────────────────────────────────────────────────────────────────────────────
# Actions
# ──────────────────────────────────────────────────────────────────────────────
def action_install(pm, packages):
    pkg_list = ", ".join(packages)
    console.print()
    console.print(Panel(
        f"[bold white]Installing:[/bold white] [green]{pkg_list}[/green]\n"
        f"[dim]Using: {pm['label']} ({pm['distro']})[/dim]",
        title="[bold][ Install ][/bold]",
        border_style="green",
        box=box.ROUNDED,
    ))

    if ask_yn("Update package lists first? (recommended)"):
        console.print()
        console.print("  [dim]→ Refreshing package lists…[/dim]")
        run(pm["update"])

    console.print()
    console.print(f"  [dim]→ Running: {' '.join(pm['install'] + packages)}[/dim]")
    console.print()
    code = run(pm["install"] + packages)
    console.print()

    if code == 0:
        console.print(f"  [bold green]✓ {pkg_list} installed successfully![/bold green]")
    else:
        console.print(f"  [bold red]✗ Installation failed (exit code {code}).[/bold red]")
        console.print("  [yellow]Tip: check the output above for clues.[/yellow]")


def action_uninstall(pm, packages):
    pkg_list = ", ".join(packages)
    console.print()
    console.print(Panel(
        f"[bold white]Removing:[/bold white] [red]{pkg_list}[/red]\n"
        f"[dim]Using: {pm['label']} ({pm['distro']})[/dim]",
        title="[bold][ Uninstall ][/bold]",
        border_style="red",
        box=box.ROUNDED,
    ))

    if not ask_yn(f"Are you sure you want to remove {pkg_list}?"):
        console.print("  [yellow]Cancelled.[/yellow]")
        return

    console.print()
    console.print(f"  [dim]→ Running: {' '.join(pm['uninstall'] + packages)}[/dim]")
    console.print()
    code = run(pm["uninstall"] + packages)
    console.print()

    if code == 0:
        console.print(f"  [bold green]✓ {pkg_list} removed successfully![/bold green]")
    else:
        console.print(f"  [bold red]✗ Uninstall failed (exit code {code}).[/bold red]")
        console.print("  [yellow]Tip: check the output above for clues.[/yellow]")


def action_search(pm, query):
    console.print()
    console.print(Panel(
        f"[bold white]Query:[/bold white] [cyan]{query}[/cyan]\n"
        f"[dim]Using: {pm['label']} ({pm['distro']})[/dim]",
        title="[bold][ Search ][/bold]",
        border_style="cyan",
        box=box.ROUNDED,
    ))
    console.print()
    run(pm["search"] + [query])


def action_update(pm):
    console.print()
    console.print(Panel(
        f"[dim]Using: {pm['label']} ({pm['distro']})[/dim]",
        title="[bold][ Update Package Lists ][/bold]",
        border_style="blue",
        box=box.ROUNDED,
    ))
    console.print()
    code = run(pm["update"])
    console.print()
    if code == 0:
        console.print("  [bold green]✓ Package lists updated.[/bold green]")
    else:
        console.print(f"  [bold red]✗ Update failed (exit code {code}).[/bold red]")


def action_upgrade_all(available):
    names = ", ".join(pm["label"] for pm in available)
    console.print()
    console.print(Panel(
        f"[bold white]Upgrading packages from:[/bold white] [cyan]{names}[/cyan]\n"
        f"[dim]This may take a while and will require your password.[/dim]",
        title="[bold][ Upgrade All Packages ][/bold]",
        border_style="magenta",
        box=box.ROUNDED,
    ))

    if not ask_yn("Continue?"):
        console.print("  [yellow]Cancelled.[/yellow]")
        return

    results = []

    for pm in available:
        console.print()
        console.print(Rule(f"[bold cyan]{pm['label']}[/bold cyan] [dim]({pm['distro']})[/dim]"))
        console.print()

        if pm["update"] != pm["upgrade"]:
            console.print("  [dim]→ Refreshing package lists…[/dim]")
            run(pm["update"])
            console.print()

        console.print("  [dim]→ Upgrading all packages…[/dim]")
        code = run(pm["upgrade"])
        results.append((pm["label"], pm["distro"], code))

    # ── Summary table ─────────────────────────────────────────────────────────
    console.print()
    console.print(Rule("[bold]Upgrade Summary[/bold]"))
    console.print()

    table = Table(box=box.ROUNDED, border_style="magenta", show_header=True, header_style="bold magenta")
    table.add_column("Package Manager", style="bold white")
    table.add_column("Distro / Type",   style="dim white")
    table.add_column("Result",          justify="center")

    all_ok = True
    for label, distro, code in results:
        if code == 0:
            table.add_row(label, distro, "[bold green]✓  OK[/bold green]")
        else:
            table.add_row(label, distro, f"[bold red]✗  Failed (code {code})[/bold red]")
            all_ok = False

    console.print(table)
    console.print()

    # ── Completion banner ─────────────────────────────────────────────────────
    status = (
        "[bold green]✓  All package managers upgraded successfully![/bold green]"
        if all_ok else
        "[bold yellow]⚠  Some errors occurred — check the output above.[/bold yellow]"
    )
    console.print(Panel(
        f"{status}\n\n"
        "[bold white]System upgrade complete![/bold white]\n"
        "[dim]You can safely close this terminal window.[/dim]",
        border_style="green" if all_ok else "yellow",
        box=box.DOUBLE,
        padding=(1, 4),
    ))
    console.print()


def action_info():
    """Show detected package managers in a table."""
    available = detect_package_managers()
    console.print()

    if not available:
        console.print(Panel(
            "[red]No supported package managers were found on this system.[/red]",
            border_style="red",
            box=box.ROUNDED,
        ))
        return

    table = Table(
        title="[bold]Detected Package Managers[/bold]",
        box=box.ROUNDED,
        border_style="green",
        header_style="bold green",
    )
    table.add_column("Name",          style="bold white")
    table.add_column("Distro / Type", style="dim white")
    table.add_column("Command",       style="cyan")

    for pm in available:
        table.add_row(pm["label"], pm["distro"], pm["name"])

    console.print(table)
    console.print()


# ──────────────────────────────────────────────────────────────────────────────
# Interactive mode
# ──────────────────────────────────────────────────────────────────────────────
MENU_ITEMS = [
    ("1", "+", "Install a package"),
    ("2", "-", "Uninstall a package"),
    ("3", "?", "Search for a package"),
    ("4", "~", "Update package lists"),
    ("5", "^", "Upgrade all packages [dim](all package managers)[/dim]"),
    ("q", "x", "Quit"),
]

def print_menu():
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    table.add_column(style="bold cyan",  justify="right", width=3)
    table.add_column(width=3)
    table.add_column(style="white")

    for key, icon, label in MENU_ITEMS:
        table.add_row(key, icon, label)

    console.print(Panel(
        table,
        title="[bold]What would you like to do?[/bold]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(0, 1),
    ))


def interactive(available):
    chosen_pm = None

    def get_pm():
        nonlocal chosen_pm
        if chosen_pm is None:
            chosen_pm = pick_pm(available)
            console.print(
                f"\n  [bold]Using:[/bold] [cyan]{chosen_pm['label']}[/cyan]"
                f" [dim]({chosen_pm['distro']})[/dim]"
            )
        return chosen_pm

    valid = {"1", "2", "3", "4", "5", "q"}

    while True:
        console.print()
        print_menu()
        console.print()

        while True:
            try:
                choice = Prompt.ask("  [cyan]Enter choice[/cyan]").strip().lower()
            except (EOFError, KeyboardInterrupt):
                console.print()
                sys.exit(0)
            if choice in valid:
                break
            console.print(f"  [yellow]Please enter one of: {', '.join(sorted(valid))}[/yellow]")

        if choice == "1":
            raw = ask_input("Package name(s) to install (space-separated)")
            if raw:
                action_install(get_pm(), raw.split())
        elif choice == "2":
            raw = ask_input("Package name(s) to uninstall (space-separated)")
            if raw:
                action_uninstall(get_pm(), raw.split())
        elif choice == "3":
            query = ask_input("Search term")
            if query:
                action_search(get_pm(), query)
        elif choice == "4":
            action_update(get_pm())
        elif choice == "5":
            action_upgrade_all(available)
        elif choice == "q":
            console.print()
            console.print(Panel(
                "[bold white]Goodbye![/bold white]",
                border_style="cyan",
                box=box.ROUNDED,
            ))
            console.print()
            sys.exit(0)


# ──────────────────────────────────────────────────────────────────────────────
# CLI entry point
# ──────────────────────────────────────────────────────────────────────────────
USAGE = """\
[bold cyan]pkgme[/bold cyan] — beginner-friendly Linux package installer

[bold]Usage:[/bold]
  pkgme                          Interactive mode (guided)
  pkgme install   <pkg> [pkg…]   Install one or more packages
  pkgme uninstall <pkg> [pkg…]   Remove one or more packages
  pkgme search    <term>         Search for a package
  pkgme update                   Update package lists (one manager)
  pkgme upgrade-all              Upgrade ALL packages across ALL managers
  pkgme info                     Show detected package managers
  pkgme help                     Show this help

[bold]Examples:[/bold]
  pkgme
  pkgme install vlc
  pkgme install git curl wget
  pkgme uninstall vlc
  pkgme search "video editor"
  pkgme upgrade-all
"""

def main():
    args = sys.argv[1:]

    # ── Banner ────────────────────────────────────────────────────────────────
    console.print()
    console.print(Panel(
        "[bold cyan]pkgme[/bold cyan]  [dim]—  beginner-friendly Linux package installer[/dim]",
        box=box.DOUBLE_EDGE,
        border_style="cyan",
        padding=(0, 4),
    ))
    console.print()

    if args and args[0] in ("help", "--help", "-h"):
        console.print(USAGE)
        sys.exit(0)

    if args and args[0] == "info":
        action_info()
        sys.exit(0)

    # ── Detect package managers ───────────────────────────────────────────────
    available = detect_package_managers()

    if not available:
        console.print(Panel(
            "[red]✗ No supported package managers found on this system.[/red]\n\n"
            "[dim]Supported:[/dim] " + ", ".join(pm["name"] for pm in PACKAGE_MANAGERS),
            border_style="red",
            box=box.ROUNDED,
        ))
        sys.exit(1)

    # Show detected managers inline
    names = "  ".join(
        f"[bold green]{pm['label']}[/bold green] [dim]({pm['distro']})[/dim]"
        for pm in available
    )
    console.print(f"  [bold green]✓ Detected:[/bold green]  {names}")
    console.print()

    # ── Dispatch ──────────────────────────────────────────────────────────────
    if not args:
        interactive(available)
        return

    command = args[0]
    rest    = args[1:]

    # upgrade-all doesn't need a single pm chosen
    if command in ("upgrade-all", "upgrade"):
        action_upgrade_all(available)
        return

    pm = pick_pm(available)

    if command == "install":
        if not rest:
            console.print("  [red]✗ Please provide at least one package name.[/red]")
            console.print("  [yellow]Example: pkgme install vlc[/yellow]")
            sys.exit(1)
        action_install(pm, rest)

    elif command in ("uninstall", "remove"):
        if not rest:
            console.print("  [red]✗ Please provide at least one package name.[/red]")
            console.print("  [yellow]Example: pkgme uninstall vlc[/yellow]")
            sys.exit(1)
        action_uninstall(pm, rest)

    elif command == "search":
        if not rest:
            console.print("  [red]✗ Please provide a search term.[/red]")
            console.print('  [yellow]Example: pkgme search vlc[/yellow]')
            sys.exit(1)
        action_search(pm, " ".join(rest))

    elif command == "update":
        action_update(pm)

    else:
        console.print(f"  [red]✗ Unknown command:[/red] '{command}'")
        console.print()
        console.print(USAGE)
        sys.exit(1)


if __name__ == "__main__":
    main()
