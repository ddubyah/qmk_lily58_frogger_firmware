"""
Enhanced QMK Trainer CLI that works with key-based firmware controls.
This CLI guides you through using the trainer mode on your keyboard.
"""

import time
import sys
from typing import List, Dict
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

app = typer.Typer(help="QMK Trainer CLI - One-handed keyboard training assistant")
console = Console()

# Predefined training patterns available in firmware
PATTERNS = {
    0: {"name": "Home Row (ASDF)", "keys": ["A", "S", "D", "F"], "color": "red"},
    1: {"name": "QWER Row", "keys": ["Q", "W", "E", "R"], "color": "green"},
    2: {"name": "Numbers (1234)", "keys": ["1", "2", "3", "4"], "color": "blue"},
    3: {"name": "Common Word (THE)", "keys": ["T", "H", "E"], "color": "yellow"},
}

def show_key_commands():
    """Display available keyboard commands."""
    table = Table(title="🎹 Keyboard Commands (Layer 1 + Function Keys)")
    table.add_column("Key Combo", style="cyan")
    table.add_column("Function", style="green")
    table.add_column("Description", style="white")

    table.add_row("Layer1 + F1", "Test LEDs", "All LEDs blue for 5 seconds")
    table.add_row("Layer1 + F2", "Start Trainer", "Sets white backdrop mode")
    table.add_row("Layer1 + F3", "End Trainer", "Restores normal RGB")
    table.add_row("Layer1 + F4", "Pattern 0", "Home row (ASDF) - Red")
    table.add_row("Layer1 + F5", "Pattern 1", "QWER row - Green")
    table.add_row("Layer1 + F6", "Pattern 2", "Numbers (1234) - Blue")
    table.add_row("Layer1 + F7", "Pattern 3", "THE keys - Yellow")
    table.add_row("Layer1 + F8", "OLED Test", "Show trainer text on display")
    table.add_row("Encoder Button", "Quick Test", "First 5 LEDs red")

    console.print(table)

@app.command()
def info():
    """Show trainer firmware information and available commands."""
    console.print(Panel.fit(
        "🚀 QMK Trainer - Enhanced Firmware Mode\n\n"
        "This firmware includes built-in trainer controls!\n"
        "Use key combinations to activate LED patterns and OLED text.\n\n"
        "✅ VIA remains enabled for keymap configuration\n"
        "✅ RGB highlighting works directly on keyboard\n"
        "✅ No external communication needed",
        title="Trainer Info"
    ))

    show_key_commands()

@app.command()
def start():
    """Guide you through starting a training session."""
    console.print("🎯 Starting Trainer Session", style="bold green")
    console.print()

    console.print("Step 1: Test your setup")
    console.print("  → Press [cyan]Layer1 + F1[/cyan] to test LEDs (should show blue)")
    console.print()

    console.print("Step 2: Start trainer mode")
    console.print("  → Press [cyan]Layer1 + F2[/cyan] to activate trainer mode")
    console.print("  → This sets a white backdrop for training")
    console.print()

    console.print("Step 3: Try pattern highlighting")
    console.print("  → Press [cyan]Layer1 + F4[/cyan] for home row (ASDF) in red")
    console.print("  → Press [cyan]Layer1 + F5[/cyan] for QWER in green")
    console.print()

    console.print("Step 4: Test OLED display")
    console.print("  → Press [cyan]Layer1 + F8[/cyan] to show trainer text")
    console.print()

    console.print("Step 5: End session")
    console.print("  → Press [cyan]Layer1 + F3[/cyan] to end trainer mode")

@app.command()
def patterns():
    """Show available highlighting patterns."""
    console.print("🎨 Available LED Patterns", style="bold magenta")
    console.print()

    table = Table()
    table.add_column("Pattern", style="cyan")
    table.add_column("Key Combo", style="yellow")
    table.add_column("Keys Highlighted", style="white")
    table.add_column("Color", style="green")

    for idx, pattern in PATTERNS.items():
        keys_str = " ".join(pattern["keys"])
        table.add_row(
            pattern["name"],
            f"Layer1 + F{idx + 4}",
            keys_str,
            pattern["color"]
        )

    console.print(table)
    console.print()
    console.print("💡 [italic]Each pattern highlights for 3 seconds[/italic]")

@app.command()
def drill(
    pattern: int = typer.Option(0, help="Pattern number (0-3)"),
    duration: int = typer.Option(30, help="Duration in seconds"),
):
    """Guide you through a drilling exercise with a specific pattern."""
    if pattern not in PATTERNS:
        console.print(f"❌ Invalid pattern: {pattern}. Use 0-3.", style="red")
        return

    pattern_info = PATTERNS[pattern]
    console.print(f"🎯 Drilling Pattern: {pattern_info['name']}", style="bold green")
    console.print(f"Keys: {' '.join(pattern_info['keys'])}")
    console.print(f"Color: {pattern_info['color']}")
    console.print()

    console.print("Setup:")
    console.print(f"1. Press [cyan]Layer1 + F2[/cyan] to start trainer mode")
    console.print(f"2. Press [cyan]Layer1 + F{pattern + 4}[/cyan] to highlight pattern")
    console.print()

    console.print(f"🕐 Drill for {duration} seconds:")
    console.print(f"  → Type the keys: [bold]{' '.join(pattern_info['keys'])}[/bold]")
    console.print(f"  → Pattern will re-highlight every 3 seconds")
    console.print(f"  → Press [cyan]Layer1 + F{pattern + 4}[/cyan] to refresh highlighting")

    if typer.confirm("\nStart drill timer?"):
        for remaining in range(duration, 0, -1):
            console.print(f"\r⏰ Time remaining: {remaining:02d}s", end="")
            time.sleep(1)

        console.print("\n🎉 Drill complete!")
        console.print("Press [cyan]Layer1 + F3[/cyan] to end trainer mode")

@app.command()
def oled():
    """Test OLED display functionality."""
    console.print("📺 OLED Display Test", style="bold blue")
    console.print()
    console.print("Available OLED commands:")
    console.print("  → Press [cyan]Layer1 + F8[/cyan] to show trainer text")
    console.print("  → Text should appear: 'Trainer\\nActive!\\nF4-F7 patterns'")
    console.print()
    console.print("To clear OLED:")
    console.print("  → Press [cyan]Layer1 + F3[/cyan] to end trainer mode")

@app.command()
def guide():
    """Complete usage guide for the trainer system."""
    console.print(Panel.fit(
        "🎓 Complete QMK Trainer Guide\n\n"
        "This firmware has built-in trainer controls that work\n"
        "directly on your keyboard without needing external tools!",
        title="Trainer Guide"
    ))

    console.print()
    console.print("📋 [bold]Quick Start:[/bold]")
    console.print("1. Flash the latest firmware")
    console.print("2. Press Layer1 + F1 to test (blue LEDs)")
    console.print("3. Press Layer1 + F2 to start training")
    console.print("4. Press Layer1 + F4-F7 for patterns")
    console.print("5. Press Layer1 + F3 to end")

    console.print()
    show_key_commands()

    console.print()
    console.print("🎯 [bold]Training Workflow:[/bold]")
    console.print("• Start with pattern 0 (home row)")
    console.print("• Practice typing highlighted keys")
    console.print("• Move to pattern 1 (QWER)")
    console.print("• Use pattern 2 for numbers")
    console.print("• Pattern 3 for common words")

if __name__ == "__main__":
    app()