#!/usr/bin/env python3
"""
BuildWatchDog - AWS CodeBuild Monitor
A cross-platform CLI utility to monitor AWS CodeBuild jobs
"""

import subprocess
import json
import sys
import argparse
import time
from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.layout import Layout
from rich.text import Text
from rich import box

console = Console()


class BuildStatus(Enum):
    """AWS CodeBuild status values"""
    IN_PROGRESS = "IN_PROGRESS"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    STOPPED = "STOPPED"
    FAULT = "FAULT"
    TIMED_OUT = "TIMED_OUT"


@dataclass
class BuildEvent:
    """Represents a build status event"""
    timestamp: datetime
    status: str
    message: str


class AWSCLIWrapper:
    """Handles all AWS CLI interactions via subprocess"""
    
    def __init__(self, profile: Optional[str] = None):
        self.profile = profile
        self.base_cmd = ["aws", "codebuild"]
        if profile:
            self.base_cmd.extend(["--profile", profile])
    
    def get_build_info(self, build_id: str) -> Optional[Dict]:
        """Fetch build information from AWS CodeBuild"""
        try:
            cmd = self.base_cmd + ["batch-get-builds", "--ids", build_id]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip()
                if "could not be found" in error_msg.lower():
                    console.print(f"[red]Error: AWS CLI not found. Please install AWS CLI.[/red]")
                elif "credentials" in error_msg.lower():
                    console.print(f"[red]Error: Invalid AWS credentials. Please configure AWS CLI.[/red]")
                elif "expired" in error_msg.lower():
                    console.print(f"[red]Error: AWS credentials expired. Please refresh your credentials.[/red]")
                else:
                    console.print(f"[red]AWS CLI Error: {error_msg}[/red]")
                return None
            
            data = json.loads(result.stdout)
            if not data.get("builds"):
                console.print(f"[yellow]Warning: Build ID '{build_id}' not found.[/yellow]")
                return None
                
            return data["builds"][0]
            
        except subprocess.TimeoutExpired:
            console.print("[red]Error: AWS CLI request timed out. Check your network connection.[/red]")
            return None
        except json.JSONDecodeError:
            console.print("[red]Error: Invalid response from AWS CLI.[/red]")
            return None
        except FileNotFoundError:
            console.print("[red]Error: AWS CLI not installed. Please install it first.[/red]")
            return None
        except Exception as e:
            console.print(f"[red]Unexpected error: {str(e)}[/red]")
            return None


class NotificationManager:
    """Handles cross-platform desktop notifications"""
    
    @staticmethod
    def send(title: str, message: str):
        """Send a desktop notification"""
        try:
            if sys.platform == "darwin":  # macOS
                subprocess.run([
                    "osascript", "-e",
                    f'display notification "{message}" with title "{title}"'
                ], check=False)
            elif sys.platform.startswith("linux"):  # Linux
                subprocess.run([
                    "notify-send", title, message
                ], check=False)
        except Exception:
            pass  # Silently fail if notifications aren't available


class BuildWatchDog:
    """Main application class"""
    
    def __init__(self, build_id: str, interval: int = 10, 
                 notify_mode: str = "both", profile: Optional[str] = None):
        self.build_id = build_id
        self.interval = interval
        self.notify_mode = notify_mode
        self.aws = AWSCLIWrapper(profile)
        self.notifier = NotificationManager()
        self.events: List[BuildEvent] = []
        self.last_status = None
        self.project_name = ""
        
    def create_display(self, build_info: Dict) -> Panel:
        """Create the TUI display layout"""
        from rich.console import Group
        
        # Parse build information
        status = build_info.get("buildStatus", "UNKNOWN")
        phases = build_info.get("phases", [])
        current_phase = build_info.get("currentPhase", "")
        
        # Status emoji mapping
        status_emoji = {
            "IN_PROGRESS": "🟡",
            "SUCCEEDED": "🟢",
            "FAILED": "🔴",
            "STOPPED": "🟠",
            "FAULT": "🔴",
            "TIMED_OUT": "🔴"
        }
        
        # Header section
        header_text = Text()
        header_text.append("BuildWatchDog", style="bold cyan")
        header_text.append(" | Build: ", style="white")
        header_text.append(f"{self.build_id[:20]}...", style="dim")
        header_text.append(" | Project: ", style="white")
        header_text.append(self.project_name, style="bold yellow")
        
        status_text = Text()
        status_text.append("Status: ", style="white")
        status_text.append(f"{status_emoji.get(status, '⚪')} ", style="white")
        status_text.append(status, style="bold green" if status == "SUCCEEDED" else "bold yellow" if status == "IN_PROGRESS" else "bold red")
        
        # Timeline/Progress table
        timeline = Table(show_header=False, box=box.ROUNDED, padding=(0, 1), expand=False)
        timeline.add_column("Phase", style="cyan", no_wrap=True)
        timeline.add_column("Status", style="green")
        
        if phases:
            for phase in phases:
                phase_name = phase.get("phaseType", "Unknown")
                phase_status = phase.get("phaseStatus")
                
                # Handle None or empty status
                if not phase_status:
                    # If overall build succeeded and this is COMPLETED phase, mark it succeeded
                    if phase_name == "COMPLETED" and status == "SUCCEEDED":
                        phase_status = "SUCCEEDED"
                    else:
                        phase_status = "PENDING"
                
                if phase_status == "SUCCEEDED":
                    icon = "[green]✓[/green]"
                    status_style = "green"
                elif phase_status == "IN_PROGRESS":
                    icon = "[yellow]⏳[/yellow]"
                    status_style = "yellow"
                elif phase_status == "FAILED":
                    icon = "[red]✗[/red]"
                    status_style = "red"
                elif phase_status == "STOPPED":
                    icon = "[yellow]⏸[/yellow]"
                    status_style = "yellow"
                elif phase_status == "FAULT" or phase_status == "TIMED_OUT":
                    icon = "[red]✗[/red]"
                    status_style = "red"
                else:
                    icon = "[dim]○[/dim]"
                    status_style = "dim"
                
                timeline.add_row(
                    f"{icon} {phase_name}",
                    Text(phase_status, style=status_style)
                )
        else:
            timeline.add_row("[dim]No phase information available[/dim]", "")
        
        # Event history table
        event_table = Table(show_header=True, box=box.ROUNDED, padding=(0, 1), expand=False)
        event_table.add_column("Time", style="dim cyan", no_wrap=True)
        event_table.add_column("Event", style="white")
        
        if self.events:
            for event in self.events[-8:]:  # Last 8 events
                event_table.add_row(
                    event.timestamp.strftime("%H:%M:%S"),
                    event.message
                )
        else:
            event_table.add_row("[dim]No events yet[/dim]", "")
        
        # Build the panel content using Group
        content = Group(
            header_text,
            status_text,
            Text(""),  # Empty line
            Text("Build Phases:", style="bold white"),
            timeline,
            Text(""),  # Empty line
            Text("Recent Events:", style="bold white"),
            event_table
        )
        
        # Build the main panel
        main_panel = Panel(
            content,
            title="[bold cyan]BuildWatchDog[/bold cyan]",
            border_style="cyan",
            subtitle=f"[dim]Press Ctrl+C to quit | Interval: {self.interval}s[/dim]"
        )
        
        return main_panel
    
    def add_event(self, status: str, message: str):
        """Add a new event to the history"""
        event = BuildEvent(
            timestamp=datetime.now(),
            status=status,
            message=message
        )
        self.events.append(event)
        
        # Send notification if status changed
        if status != self.last_status and self.last_status is not None:
            if self.notify_mode in ["desktop", "both"]:
                self.notifier.send("BuildWatchDog", message)
            self.last_status = status
    
    def run(self):
        """Main monitoring loop"""
        console.print(f"[cyan]Starting BuildWatchDog...[/cyan]")
        console.print(f"[dim]Monitoring build: {self.build_id}[/dim]\n")
        
        # Initial fetch
        build_info = self.aws.get_build_info(self.build_id)
        if not build_info:
            sys.exit(1)
        
        self.project_name = build_info.get("projectName", "Unknown")
        initial_status = build_info.get("buildStatus", "UNKNOWN")
        self.last_status = initial_status
        self.add_event(initial_status, f"Started monitoring - {initial_status}")
        
        try:
            with Live(self.create_display(build_info), refresh_per_second=1) as live:
                while True:
                    build_info = self.aws.get_build_info(self.build_id)
                    
                    if not build_info:
                        self.add_event("ERROR", "Failed to fetch build info")
                        live.update(self.create_display(build_info or {}))
                        time.sleep(self.interval)
                        continue
                    
                    current_status = build_info.get("buildStatus", "UNKNOWN")
                    
                    # Check for status change
                    if current_status != self.last_status:
                        self.add_event(current_status, f"Status changed to {current_status}")
                    
                    live.update(self.create_display(build_info))
                    
                    # Exit if build is complete
                    if current_status in ["SUCCEEDED", "FAILED", "STOPPED", "FAULT", "TIMED_OUT"]:
                        # Do one final fetch to ensure we have the complete phase information
                        time.sleep(3)  # Longer pause to let AWS finalize
                        final_build_info = self.aws.get_build_info(self.build_id)
                        if final_build_info:
                            live.update(self.create_display(final_build_info))
                        
                        # Debug: uncomment to see raw phase data
                        # console.print("\n[dim]Debug - Final phases:[/dim]")
                        # console.print(final_build_info.get("phases", []))
                        
                        console.print(f"\n[bold]Build {current_status}![/bold]")
                        break
                    
                    time.sleep(self.interval)
                    
        except KeyboardInterrupt:
            console.print("\n[yellow]Monitoring stopped by user.[/yellow]")
            sys.exit(0)


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="BuildWatchDog - Monitor AWS CodeBuild jobs from the command line",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--build-id",
        required=True,
        help="AWS CodeBuild Build ID to monitor"
    )
    
    parser.add_argument(
        "--interval",
        type=int,
        default=10,
        help="Polling interval in seconds (default: 10)"
    )
    
    parser.add_argument(
        "--notify",
        choices=["terminal", "desktop", "both"],
        default="both",
        help="Notification method (default: both)"
    )
    
    parser.add_argument(
        "--profile",
        help="AWS CLI profile to use"
    )
    
    args = parser.parse_args()
    
    # Validate interval
    if args.interval < 5:
        console.print("[yellow]Warning: Interval less than 5 seconds may cause rate limiting.[/yellow]")
    
    # Create and run the watchdog
    watchdog = BuildWatchDog(
        build_id=args.build_id,
        interval=args.interval,
        notify_mode=args.notify,
        profile=args.profile
    )
    
    watchdog.run()


if __name__ == "__main__":
    main()