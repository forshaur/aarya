import asyncio
import argparse
import json
import random
import re
import sys
from importlib.metadata import version, PackageNotFoundError

import httpx
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich import box
from rich.rule import Rule

import aarya.modules.shopping.flipkart as flipkart
import aarya.modules.shopping.amazon as amazon
import aarya.modules.learning.duolingo as duolingo
import aarya.modules.music.spotify as spotify
import aarya.modules.social.instagram as instagram
import aarya.modules.social.twitter as twitter
import aarya.modules.social.wattpad as wattpad
import aarya.modules.mail.gmail as gmail
import aarya.modules.mail.proton as proton

console = Console()

MODS = [amazon, flipkart, duolingo, spotify, instagram, twitter, wattpad, gmail, proton]

# ponytail: browser_cookie3 in gmail.py tries Brave first, Chrome fallback
SUPPORTED_BROWSER = "Brave (or Chrome)"

try:
    __version__ = version("aarya")
except PackageNotFoundError:
    __version__ = "dev"

LOGO = f"""[bold bright_cyan]
┏━┓┏━┓┏━┓╻ ╻┏━┓
┣━┫┣━┫┣┳┛┗┳┛┣━┫
╹ ╹╹ ╹╹┗╸ ╹ ╹ ╹[white][dim] | Email to digital footprint[/dim][white]
[/bold bright_cyan]
[white]GitHub: [link=https://github.com/forshaur]forshaur[/link][white] | X: @forshaur
Version: [bold bright_cyan]{__version__}[/bold bright_cyan]"""

TIPS = [
    f"Log into Google in {SUPPORTED_BROWSER} browser to let Aarya access your local cookies for deeper Google intelligence.",
    "Save results as JSON for further processing: aarya target@email.com -o output.json",
    "Hitting 'Rate Limit' on multiple services? Switch networks or use a VPN to get a fresh IP.",
    "People often reuse their email prefix as usernames. Try searching 'johndoe' from johndoe@email.com on username lookup tools.",
    f"Aarya reads cookies from {SUPPORTED_BROWSER}. Make sure you're logged into Google there for best results.",
    "A ProtonMail hit often indicates a privacy-conscious target. Check the intelligence report for PGP key metadata.",
]


def is_valid(email):
    return re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email) is not None


def parse_google_metadata(metadata_str):
    """Parses 'Key: Val | Key: Val' string into dict."""
    if not metadata_str:
        return {}
    data = {}
    for part in metadata_str.split(" | "):
        if ": " in part:
            k, v = part.split(": ", 1)
            data[k.strip()] = v.strip()
    return data


async def check_service(mod, email, client, progress, task_id, table, detailed_findings):
    try:
        d = await mod.site(email, client)
    except Exception:
        progress.update(task_id, advance=1)
        return None

    name = d.get("name", "Unknown").capitalize()
    exists = d.get("exists")
    rate_limit = d.get("rateLimit")
    others = d.get("others")

    if exists:
        style = "bold green"
        status = "FOUND"
        if name.lower() == "google":
            detailed_findings.append({"module": "Google", "data": others, "type": "google"})
            detail = "[bold white]See Intelligence Report ↓[/bold white]"
        elif name.lower() == "protonmail" and isinstance(others, dict):
            detailed_findings.append({"module": "ProtonMail", "data": others, "type": "dict"})
            detail = "[bold white]See Intelligence Report ↓[/bold white]"
        else:
            detail = str(others) if others else "-"
    elif rate_limit:
        style, status = "bold yellow", "RATE LIMIT"
        detail = "[yellow]Request throttled[/yellow]"
    elif others and ("Error" in str(others) or "Timeout" in str(others)):
        style, status = "bold red", "ERROR"
        detail = "[red]Module Error[/red]"
    else:
        style, status = "dim white", "NOT FOUND"
        detail = "-"
        # ponytail: gmail-specific hint — if target is @gmail but Google returned nothing, nudge the user
        if name.lower() == "google" and email.endswith("@gmail.com"):
            detail = f"[yellow]Login to Google in {SUPPORTED_BROWSER} for results[/yellow]"

    table.add_row(f"[{style}]{name}[/]", f"[{style}]{status}[/]", detail)
    progress.update(task_id, advance=1)
    return d


def print_intelligence_report(findings):
    if not findings:
        return
    console.print()
    console.print(Rule("[bold magenta]Intelligence Report[/bold magenta]"))
    console.print()
    for item in findings:
        module = item["module"]
        if item["type"] == "google":
            data = parse_google_metadata(item["data"])
            console.print(f"[bold bright_cyan]target@{module}[/bold bright_cyan]")
            console.print(f" ├─ [bold white]Full Name:[/bold white]  [bold yellow]{data.get('Name', 'Unknown')}[/bold yellow]")
            console.print(f" ├─ [bold white]Gaia ID:[/bold white]    [cyan]{data.get('ID', 'N/A')}[/cyan]")
            console.print(f" ├─ [bold white]Maps:[/bold white]       [link={data.get('Maps', 'N/A')}][u]View Contributions[/u][/link]")
            console.print(f" └─ [bold white]Image:[/bold white]      [link={data.get('Pic', 'N/A')}][u]View Profile Picture[/u][/link]")
            console.print()
        elif item["type"] == "dict":
            console.print(f"[bold bright_cyan]target@{module}[/bold bright_cyan]")
            keys = list(item["data"].keys())
            for i, key in enumerate(keys):
                prefix = " └─" if i == len(keys) - 1 else " ├─"
                console.print(f"{prefix} [bold white]{key}:[/bold white] [yellow]{item['data'][key]}[/yellow]")
            console.print()


async def check_for_update(current_version):
    """Non-blocking PyPI version check. Returns new version string or False."""
    if current_version == "dev":
        return False
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get("https://pypi.org/pypi/aarya/json")
            if resp.status_code == 200:
                latest = resp.json().get("info", {}).get("version")
                if latest and latest != current_version:
                    from packaging.version import parse
                    if parse(latest) > parse(current_version):
                        return latest
    except Exception:
        pass
    return False


async def perform_update():
    try:
        proc = await asyncio.create_subprocess_shell(
            "pip install --upgrade aarya",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()
    except Exception:
        pass


async def run_scan(email):
    update_task = asyncio.create_task(check_for_update(__version__))

    console.print(LOGO)
    console.print(f"\n[bold yellow]Tip:[/bold yellow] [italic]{random.choice(TIPS)}[/italic]")
    console.print(f"\n[bold white]Target:[/bold white] [bold cyan]{email}[/bold cyan]\n")

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold magenta", expand=True)
    table.add_column("Service", style="bold cyan", width=15)
    table.add_column("Status", width=12)
    table.add_column("Quick Info", style="white")

    results = []
    detailed_findings = []

    async with httpx.AsyncClient(timeout=30.0) as cl:
        with Progress(
            SpinnerColumn(style="bold cyan"),
            TextColumn("[bold cyan]{task.description}[/bold cyan]"),
            BarColumn(bar_width=None, complete_style="magenta", finished_style="green"),
            TimeElapsedColumn(),
            transient=True,
        ) as progress:
            task = progress.add_task("Scanning...", total=len(MODS))
            coros = [check_service(m, email, cl, progress, task, table, detailed_findings) for m in MODS]
            res = await asyncio.gather(*coros)
            results = [r for r in res if r]

    console.print(table)
    print_intelligence_report(detailed_findings)

    # ponytail: autoupdate runs in background, resolved here so it never blocks the scan
    try:
        new_version = await update_task
        if new_version:
            console.print(f"\n[bold white]A new version of Aarya ([cyan]v{new_version}[/cyan]) is available.[/bold white]")
            with Progress(SpinnerColumn(style="bold green"), TextColumn("[bold green]Updating...[/bold green]"), transient=True) as p:
                p.add_task("", total=None)
                await perform_update()
            console.print(f"[bold green]Aarya updated to v{new_version}. Changes take effect on next run.[/bold green]\n")
    except Exception:
        pass

    return results


def _extract_found(results):
    """Returns set of service names that returned exists=True."""
    return {r["name"] for r in results if r and r.get("exists")}


async def _notify(title, body):
    """Desktop notification via notify-send. ponytail: no deps, Linux-native."""
    try:
        await asyncio.create_subprocess_exec(
            "notify-send", "-u", "critical", "-a", "Aarya", title, body,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
    except FileNotFoundError:
        # ponytail: notify-send missing, fall back to console-only
        pass


async def run_watch(email, interval_min):
    console.print(f"[bold bright_cyan]Watchdog active.[/bold bright_cyan] Scanning [cyan]{email}[/cyan] every [yellow]{interval_min}m[/yellow]. Press Ctrl+C to stop.\n")

    previous = set()
    cycle = 0

    while True:
        cycle += 1
        console.print(Rule(f"[dim]Scan #{cycle} — {email}[/dim]"))
        results = await run_scan(email)
        current = _extract_found(results)

        if cycle == 1:
            previous = current
            if current:
                console.print(f"\n[bold white]Baseline:[/bold white] {', '.join(sorted(current))}\n")
            else:
                console.print(f"\n[dim]No accounts found yet. Watching...[/dim]\n")
        else:
            new = current - previous
            if new:
                names = ", ".join(sorted(n.capitalize() for n in new))
                msg = f"New account(s) detected for {email}: {names}"
                console.print(f"\n[bold green][!] {msg}[/bold green]\n")
                await _notify("Aarya — New Account Detected", msg)
            else:
                console.print(f"\n[dim]No new accounts since last scan.[/dim]\n")
            previous = current

        console.print(f"[dim]Next scan in {interval_min} minute(s)...[/dim]\n")
        await asyncio.sleep(interval_min * 60)


def main():
    parser = argparse.ArgumentParser(description="Aarya: OSINT Email Scanner")
    parser.add_argument("email", help="The target email address to scan")
    parser.add_argument("-o", "--output", help="Path to save JSON output")
    parser.add_argument(
        "-w", "--watch",
        nargs="?",
        const=30,
        type=int,
        metavar="MIN",
        help="Watchdog mode: re-scan every MIN minutes (default: 30) and alert on new accounts",
    )
    args = parser.parse_args()

    if not is_valid(args.email):
        console.print("[bold red][!] Invalid email address format.[/bold red]")
        sys.exit(1)

    if args.watch:
        try:
            asyncio.run(run_watch(args.email, args.watch))
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Watchdog stopped.[/bold yellow]")
        sys.exit(0)

    final_list = asyncio.run(run_scan(args.email))

    if args.output:
        try:
            with open(args.output, "w") as f:
                json.dump(final_list, f, indent=4)
            console.print(f"\n[bold green][+] Data saved to {args.output}[/bold green]")
        except Exception as e:
            console.print(f"\n[bold red][!] Failed to save file: {e}[/bold red]")


if __name__ == "__main__":
    main()
