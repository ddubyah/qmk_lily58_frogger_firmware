"""
Training session management for one-handed keyboard training.
Handles sequential training, progress tracking, and user interaction.
"""

from typing import Dict, List, Tuple, Any
import time
from rich.console import Console
from rich.progress import Progress, TextColumn, BarColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.text import Text

from .hid_comm import highlight_leds_with_color, send_oled_text
from .chord_mapper import ChordMapper
from .config import get_layer_color

console = Console()

class TrainingSession:
    """Manages a training session with LED highlighting and progress tracking."""
    
    def __init__(self, device, matrix_to_led_map: Dict[Tuple[int, int], int], config: Dict[str, Any]):
        self.device = device
        self.matrix_to_led_map = matrix_to_led_map
        self.config = config
        self.chord_mapper = ChordMapper(device)
        self.chord_mapper.matrix_to_led_map = matrix_to_led_map
        
        # Load keymap from device
        console.print("[blue]→[/blue] Loading keymap from device...")
        self.chord_mapper.load_from_device(device)
        
        # Build layer colors mapping
        self.layer_colors = {}
        for layer in range(5):  # Support up to 5 layers
            self.layer_colors[layer] = get_layer_color(config, layer)
    
    def train_sequence(self, text: str, duration: int = None) -> None:
        """Train typing a sequence of characters with LED highlighting."""
        if duration is None:
            duration = self.config.get('training', {}).get('default_duration', 2000)
        
        show_progress = self.config.get('training', {}).get('show_progress', True)
        prompt_delay = self.config.get('training', {}).get('prompt_delay', 500)
        
        console.print(f"[green]→[/green] Starting training session for: '[cyan]{text}[/cyan]'")
        console.print(f"[blue]→[/blue] LED highlight duration: {duration}ms")
        
        if show_progress:
            self._train_with_progress(text, duration, prompt_delay)
        else:
            self._train_simple(text, duration, prompt_delay)
    
    def _train_with_progress(self, text: str, duration: int, prompt_delay: int) -> None:
        """Train with rich progress bar."""
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task("Training Progress", total=len(text))
            
            for i, char in enumerate(text):
                # Update progress
                progress.update(task, description=f"Character: '{char}' ({i+1}/{len(text)})")
                
                # Train character
                self._train_character(char, duration, prompt_delay)
                
                # Update progress
                progress.advance(task)
    
    def _train_simple(self, text: str, duration: int, prompt_delay: int) -> None:
        """Train without progress bar."""
        for i, char in enumerate(text):
            console.print(f"[cyan]Character {i+1}/{len(text)}: '{char}'[/cyan]")
            self._train_character(char, duration, prompt_delay)
    
    def _train_character(self, char: str, duration: int, prompt_delay: int) -> None:
        """Train a single character with LED highlighting and OLED prompt."""
        # Get LED positions and colors for this character
        led_info = self.chord_mapper.char_to_leds_with_layers(char, self.layer_colors)
        
        if not led_info:
            console.print(f"[yellow]⚠[/yellow] No mapping found for character '{char}' - skipping")
            return
        
        # Send OLED prompt
        if char == ' ':
            oled_text = "Press: SPACE"
        elif char == '\n':
            oled_text = "Press: ENTER" 
        elif char == '\t':
            oled_text = "Press: TAB"
        else:
            oled_text = f"Press: {char}"
        
        send_oled_text(self.device, oled_text)
        
        # Group LEDs by color for efficient highlighting
        color_groups = {}
        for led_idx, color in led_info:
            if color not in color_groups:
                color_groups[color] = []
            color_groups[color].append(led_idx)
        
        # Highlight each color group
        for color, led_indexes in color_groups.items():
            highlight_leds_with_color(self.device, led_indexes, color, duration)
        
        # Display character info to user
        positions = self.chord_mapper.get_positions_for_char(char)
        if len(positions) == 1:
            layer, row, col = positions[0]
            console.print(f"[green]→[/green] '{char}': Layer {layer}, Position ({row},{col})")
        else:
            layers = list(set(pos[0] for pos in positions))
            console.print(f"[green]→[/green] '{char}': {len(positions)} positions on layers {layers}")
        
        # Wait for character duration plus prompt delay
        time.sleep(duration / 1000.0 + prompt_delay / 1000.0)
    
    def drill_mode(self, word_list: List[str] = None) -> None:
        """Interactive drill mode with feedback."""
        if word_list is None:
            word_list = ["hello", "world", "test", "qmk", "keyboard", "frog", "pad"]
        
        console.print("[green]→[/green] Starting drill mode")
        console.print("[blue]→[/blue] Press Ctrl+C to exit")
        
        try:
            while True:
                # Pick a random word
                import random
                word = random.choice(word_list)
                
                console.print(Panel(f"Type: [cyan]{word}[/cyan]", title="Drill"))
                
                # Show the word sequence
                self.train_sequence(word)
                
                # Simple pause between words
                console.print("[dim]Press Enter to continue or Ctrl+C to exit...[/dim]")
                input()
                
        except KeyboardInterrupt:
            console.print("\n[green]✓[/green] Drill mode ended")
    
    def validate_setup(self) -> bool:
        """Validate that the training setup is working correctly."""
        console.print("[blue]→[/blue] Validating training setup...")
        
        # Check device connection
        if not self.device:
            console.print("[red]✗[/red] No device connected")
            return False
        
        # Check LED mapping
        if not self.matrix_to_led_map:
            console.print("[red]✗[/red] No LED mapping available")
            return False
        
        console.print(f"[green]✓[/green] LED mapping loaded: {len(self.matrix_to_led_map)} positions")
        
        # Check keymap
        if not self.chord_mapper.keymap:
            console.print("[red]✗[/red] No keymap loaded from device")
            return False
        
        total_keys = sum(len(layer_map) for layer_map in self.chord_mapper.keymap.values())
        console.print(f"[green]✓[/green] Keymap loaded: {total_keys} keys across {len(self.chord_mapper.keymap)} layers")
        
        # Check character mappings
        available_chars = self.chord_mapper.get_available_characters()
        if len(available_chars) < 26:  # At least the alphabet
            console.print(f"[yellow]⚠[/yellow] Only {len(available_chars)} characters mapped")
        else:
            console.print(f"[green]✓[/green] Character mapping: {len(available_chars)} characters available")
        
        # Test a simple character
        test_char = 'a'
        led_info = self.chord_mapper.char_to_leds_with_layers(test_char, self.layer_colors)
        if led_info:
            console.print(f"[green]✓[/green] Test mapping for '{test_char}': {len(led_info)} LEDs")
        else:
            console.print(f"[yellow]⚠[/yellow] Test mapping for '{test_char}' failed")
        
        return True
    
    def print_character_summary(self) -> None:
        """Print summary of available characters and their mappings."""
        available_chars = sorted(self.chord_mapper.get_available_characters())
        
        # Group by type
        letters = [c for c in available_chars if c.isalpha()]
        numbers = [c for c in available_chars if c.isdigit()]
        symbols = [c for c in available_chars if not c.isalnum() and c.isprintable()]
        
        console.print("\n[bold]Available Characters:[/bold]")
        
        if letters:
            console.print(f"[green]Letters ({len(letters)}):[/green] {''.join(letters[:26])}")
            if len(letters) > 26:
                console.print(f"[green]More:[/green] {''.join(letters[26:])}")
        
        if numbers:
            console.print(f"[blue]Numbers ({len(numbers)}):[/blue] {''.join(numbers)}")
        
        if symbols:
            console.print(f"[yellow]Symbols ({len(symbols)}):[/yellow] {''.join(symbols[:20])}")
    
    def test_highlight(self, char: str, duration: int = 2000) -> bool:
        """Test LED highlighting for a specific character."""
        console.print(f"[blue]→[/blue] Testing LED highlight for character: '{char}'")
        
        led_info = self.chord_mapper.char_to_leds_with_layers(char, self.layer_colors)
        
        if not led_info:
            console.print(f"[red]✗[/red] No LED mapping found for '{char}'")
            return False
        
        console.print(f"[green]→[/green] Highlighting {len(led_info)} LEDs...")
        
        # Group by color and highlight
        color_groups = {}
        for led_idx, color in led_info:
            if color not in color_groups:
                color_groups[color] = []
            color_groups[color].append(led_idx)
        
        for color, led_indexes in color_groups.items():
            highlight_leds_with_color(self.device, led_indexes, color, duration)
            console.print(f"[cyan]→[/cyan] Color {color}: LEDs {led_indexes}")
        
        return True