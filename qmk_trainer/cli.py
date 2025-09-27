#!/usr/bin/env python3
"""
QMK Trainer CLI - One-handed keyboard training with LED highlighting and OLED feedback.
"""

import typer
from rich.console import Console
from rich.table import Table
from typing import List, Optional

from qmk_trainer import __version__
from .config import load_config, install_default_config
from .hid_comm import VIADevice
from .trainer import TrainingSession

app = typer.Typer(
    name="qmk_trainer",
    help="One-handed keyboard training CLI with LED highlighting and OLED feedback",
    add_completion=False,
)
console = Console()

@app.command()
def highlight(
    keys: str = typer.Option(..., "--keys", "-k", help="Comma-separated LED indexes to highlight"),
    duration: int = typer.Option(2000, "--duration", "-d", help="Duration in milliseconds"),
    color: str = typer.Option("255,0,0", "--color", "-c", help="RGB color as 'r,g,b'"),
) -> None:
    """Debug LED highlighting by specifying LED indexes directly."""
    try:
        # Parse inputs
        led_indexes = [int(x.strip()) for x in keys.split(",")]
        r, g, b = [int(x.strip()) for x in color.split(",")]
        
        # Connect to device using context manager
        with VIADevice() as via:
            console.print(f"[green]✓[/green] Connected to VIA device")
            
            # Send highlight command directly to specified LED indexes
            from .hid_comm import highlight_leds_with_color
            highlight_leds_with_color(via.device, led_indexes, (r, g, b), duration)
            console.print(f"[blue]→[/blue] Highlighting LEDs {led_indexes} with color RGB({r},{g},{b}) for {duration}ms")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")
        raise typer.Exit(1)

@app.command()
def train(
    text: str = typer.Argument(..., help="Text to train typing"),
    duration: int = typer.Option(2000, "--duration", "-d", help="LED highlight duration per character"),
    validate: bool = typer.Option(False, "--validate", help="Validate setup before training"),
) -> None:
    """Sequential training mode - highlights keys for each character in sequence."""
    try:
        config = load_config()
        
        with VIADevice() as via:
            console.print(f"[green]✓[/green] Connected to VIA device")
            
            # Load mappings from device (this reads the keymap automatically)
            console.print(f"[blue]→[/blue] Loading keymap and LED mapping from device...")
            via.load_mappings()
            
            # Start training session
            session = TrainingSession(via.device, via.matrix_to_led_map, config)
            
            if validate:
                console.print(f"[blue]→[/blue] Validating training setup...")
                if not session.validate_setup():
                    console.print(f"[red]✗[/red] Setup validation failed")
                    raise typer.Exit(1)
                console.print(f"[green]✓[/green] Setup validation passed")
            
            # Show available characters
            session.print_character_summary()
            
            # Start training
            session.train_sequence(text, duration)
            console.print(f"[green]✓[/green] Training complete")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")
        raise typer.Exit(1)

@app.command()
def drill(
    words: Optional[str] = typer.Option(None, "--words", "-w", help="Comma-separated list of words to practice"),
    duration: int = typer.Option(1500, "--duration", "-d", help="LED highlight duration per character"),
) -> None:
    """Practice mode with feedback - interactive training with prompts."""
    try:
        config = load_config()
        
        # Parse word list
        if words:
            word_list = [w.strip() for w in words.split(",")]
        else:
            word_list = ["hello", "world", "test", "qmk", "keyboard", "frog", "pad", "via", "lily", "train"]
        
        with VIADevice() as via:
            console.print(f"[green]✓[/green] Connected to VIA device")
            via.load_mappings()
            
            session = TrainingSession(via.device, via.matrix_to_led_map, config)
            session.drill_mode(word_list)
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")
        raise typer.Exit(1)
    
@app.command()
def test(
    char: str = typer.Argument(..., help="Character to test LED highlighting for"),
    duration: int = typer.Option(3000, "--duration", "-d", help="LED highlight duration in milliseconds"),
) -> None:
    """Test LED highlighting for a specific character."""
    try:
        config = load_config()
        
        with VIADevice() as via:
            console.print(f"[green]✓[/green] Connected to VIA device")
            via.load_mappings()
            
            session = TrainingSession(via.device, via.matrix_to_led_map, config)
            
            if session.test_highlight(char, duration):
                console.print(f"[green]✓[/green] Test completed for character: '{char}'")
            else:
                console.print(f"[red]✗[/red] Test failed for character: '{char}'")
                raise typer.Exit(1)
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")
        raise typer.Exit(1)

@app.command()  
def config(
    show: bool = typer.Option(False, "--show", "-s", help="Show current configuration"),
    edit: bool = typer.Option(False, "--edit", "-e", help="Edit configuration file"),
) -> None:
    """View or edit configuration settings."""
    try:
        config_data = load_config()
        
        if show:
            table = Table(title="QMK Trainer Configuration")
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="green")
            
            # Layer colors
            for layer, color in config_data.get("layer_colors", {}).items():
                table.add_row(f"Layer {layer} Color", f"RGB{tuple(color)}")
            
            # Training settings
            training = config_data.get("training", {})
            table.add_row("Default Duration", f"{training.get('default_duration', 2000)}ms")
            table.add_row("Show Progress", str(training.get('show_progress', True)))
            
            # Device settings
            device = config_data.get("device", {})
            table.add_row("Vendor ID", f"0x{device.get('vendor_id', 0x7171):04X}")
            table.add_row("Product ID", f"0x{device.get('product_id', 0x0002):04X}")
            
            console.print(table)
        
        if edit:
            import os
            from pathlib import Path
            config_path = Path.home() / ".config" / "qmk_trainer" / "config.toml"
            os.system(f"${os.environ.get('EDITOR', 'nano')} {config_path}")
            
        if not show and not edit:
            console.print("[yellow]Use --show to view config or --edit to modify it[/yellow]")
            
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")
        raise typer.Exit(1)

@app.command()
def info() -> None:
    """Show device information and connection status."""
    try:
        with VIADevice() as via:
            from .hid_comm import get_device_info
            
            console.print(f"[green]✓[/green] Connected to VIA device")
            
            # Get device info
            device_info = get_device_info(via.device)
            
            table = Table(title="Device Information")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in device_info.items():
                table.add_row(key.replace("_", " ").title(), str(value))
            
            console.print(table)
            
            # Load and show mapping info
            via.load_mappings()
            
            console.print("[blue]Device Capabilities:[/blue]")
            console.print(f"  LED Positions: {len(via.matrix_to_led_map)}")
            console.print(f"  Keymap Layers: {len(via.keymap)}")
            
            total_keys = sum(len(layer_map) for layer_map in via.keymap.values())
            console.print(f"  Total Key Positions: {total_keys}")
            
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")
        raise typer.Exit(1)

@app.callback()
def main(
    version: bool = typer.Option(False, "--version", help="Show version information"),
) -> None:
    """QMK Trainer CLI for one-handed keyboard training."""
    if version:
        console.print(f"qmk_trainer version {__version__}")
        raise typer.Exit()

if __name__ == "__main__":
    app()