import asyncio
import argparse
import json
import re
import sys
from importlib.metadata import version, PackageNotFoundError

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich import box
from rich.rule import Rule
from rich.panel import Panel

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

MODS = [
    amazon, flipkart, duolingo, spotify,
    instagram, twitter, wattpad, gmail, proton
]

try:
    __version__ = version("aarya")
except PackageNotFoundError:
    # if we run the script locally
    __version__ = "dev"

LOGO = f"""[bold bright_cyan]
┏━┓┏━┓┏━┓╻ ╻┏━┓
┣━┫┣━┫┣┳┛┗┳┛┣━┫
╹ ╹╹ ╹╹┗╸ ╹ ╹ ╹[white][dim] | The Advanced OSINT Email Scanner[/dim][white]
[/bold bright_cyan]
[white]GitHub: [link=https://github.com/forshaur]forshaur[/link][white] | X: @forshaur
Version: [bold bright_cyan]{__version__}[/bold bright_cyan]"""

def is_valid(email):
    pat = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pat, email) is not None

def parse_google_metadata(metadata_str):
    """Parses Google string into a clean dict."""
    if not metadata_str: return {}
    data = {}
    parts = metadata_str.split(" | ")
    for part in parts:
        if ": " in part:
            key, val = part.split(": ", 1)
            data[key.strip()] = val.strip()
    return data

async def check_service(mod, email, client, progress, task_id, table, detailed_findings):
    try:
        d = await mod.site(email, client)
        
        name = d.get("name", "Unknown").capitalize()
        exists = d.get("exists")
        rate_limit = d.get("rateLimit")
        others = d.get("others")

        status_text = ""
        status_style = ""
        table_details = "-"

        if exists:
            status_text = "FOUND"
            status_style = "bold green" 
            
            if name.lower() == "google":
                detailed_findings.append({"module": "Google", "data": others, "type": "google"})
                table_details = "[bold white]See Intelligence Report ↓[/bold white]"
            
            elif name.lower() == "protonmail" and isinstance(others, dict):
                 detailed_findings.append({"module": "ProtonMail", "data": others, "type": "dict"})
                 table_details = "[bold white]See Intelligence Report ↓[/bold white]"
            
            else:
                table_details = str(others) if others else "-"

        elif rate_limit:
            status_text = "RATE LIMIT"
            status_style = "bold yellow" 
            table_details = "[yellow]Request throttled[/yellow]"
        elif others and ("Error" in str(others) or "Timeout" in str(others)):
            status_text = "ERROR"
            status_style = "bold red"    
            table_details = "[red]Module Error[/red]"
        else:
            status_text = "NOT FOUND"
            status_style = "dim white"

        table.add_row(
            f"[{status_style}]{name}[/]", 
            f"[{status_style}]{status_text}[/]", 
            table_details
        )
        progress.update(task_id, advance=1)
        return d

    except Exception as e:
        progress.update(task_id, advance=1)
        return None

def print_intelligence_report(findings):
    """Prints the detailed data at the end of the scan."""
    if not findings:
        return

    console.print()
    console.print(Rule("[bold magenta]Intelligence Report[/bold magenta]"))
    console.print()

    for item in findings:
        module = item['module']
        
        if item['type'] == 'google':
            data = parse_google_metadata(item['data'])
            name = data.get("Name", "Unknown")
            gaia_id = data.get("ID", "N/A")
            maps_url = data.get("Maps", "N/A")
            pic_url = data.get("Pic", "N/A")

            console.print(f"[bold bright_cyan]target@{module}[/bold bright_cyan]")
            console.print(f" ├─ [bold white]Full Name:[/bold white]  [bold yellow]{name}[/bold yellow]")
            console.print(f" ├─ [bold white]Gaia ID:[/bold white]    [cyan]{gaia_id}[/cyan]")
            console.print(f" ├─ [bold white]Maps:[/bold white]       [link={maps_url}][u]View Contributions[/u][/link]")
            console.print(f" └─ [bold white]Image:[/bold white]      [link={pic_url}][u]View Profile Picture[/u][/link]")
            console.print()

        elif item['type'] == 'dict':
            console.print(f"[bold bright_cyan]target@{module}[/bold bright_cyan]")
            data = item['data']
            keys = list(data.keys())
            for i, key in enumerate(keys):
                is_last = (i == len(keys) - 1)
                prefix = " └─" if is_last else " ├─"
                console.print(f"{prefix} [bold white]{key}:[/bold white] [yellow]{data[key]}[/yellow]")
            console.print()

async def run_scan(email):
    console.print(LOGO)
    console.print(f"\n[bold white]Target:[/bold white] [bold cyan]{email}[/bold cyan]\n")

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold magenta", expand=True)
    table.add_column("Service", style="bold cyan", width=15)
    table.add_column("Status", width=12)
    table.add_column("Quick Info", style="white") 

    results = []
    detailed_findings = []
    
    import httpx
    async with httpx.AsyncClient(timeout=30.0) as cl:
        with Progress(
            SpinnerColumn(style="bold cyan"),   
            TextColumn("[bold cyan]{task.description}[/bold cyan]"),
            BarColumn(bar_width=None, complete_style="magenta", finished_style="green"), 
            TimeElapsedColumn(),
            transient=True
        ) as progress:
            
            task = progress.add_task(f"Scanning...", total=len(MODS))
            
            tasks = [check_service(m, email, cl, progress, task, table, detailed_findings) for m in MODS]
            res = await asyncio.gather(*tasks)
            results = [r for r in res if r]

    console.print(table)
    print_intelligence_report(detailed_findings)

    return results

def main():
    parser = argparse.ArgumentParser(description="Aarya: OSINT Email Scanner")
    parser.add_argument("email", help="The target email address to scan")
    parser.add_argument("-o", "--output", help="Path to save JSON output (optional)")
    
    args = parser.parse_args()
    
    if not is_valid(args.email):
        console.print(f"[bold red][!] Invalid email address format.[/bold red]")
        sys.exit(1)

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