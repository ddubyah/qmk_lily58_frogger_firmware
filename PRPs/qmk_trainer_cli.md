# PRP: QMK Trainer CLI Implementation

**Project:** Lily58 + VIA + Python CLI trainer  
**Feature:** One-Handed Keyboard Training Helper  
**Owner:** DDubyah  
**Confidence Score:** 8/10  

## Overview

Implement a one-handed keyboard training system with LED highlighting and OLED display feedback, extending the existing Lily58 VIA-enabled firmware with minimal modifications to maintain full VIA compatibility.

## Core Design Principles

### KISS (Keep It Simple, Stupid)
- Use existing VIA custom command infrastructure 
- Minimal firmware changes (3 hook functions only)
- Straightforward Python CLI with proven libraries

### YAGNI (You Aren't Gonna Need It)
- No GUI - CLI only as specified
- No right-half support - left-only as required
- No complex state machines - simple command/response

### Open/Closed Principle
- Firmware remains VIA-compatible
- Python CLI extensible for new chord sets
- Training modes can be added without core changes

## Implementation Context

### Current Codebase State
- **Firmware Location:** `lily58_pro/keymaps/frogger_rgb_via/`
- **Current Features:** VIA enabled, RGB Matrix (74 LEDs), OLED support
- **RGB Configuration:** 37 LEDs per side, max brightness 120
- **Build System:** Uses `./build.sh frogger_rgb_via` → `.build/*.uf2`

### Key Files to Modify
```
lily58_pro/keymaps/frogger_rgb_via/
├── keymap.c          # Add VIA handlers + RGB/OLED hooks
├── rules.mk          # Already has VIA_ENABLE = yes
└── config.h          # Add trainer-specific defines
```

## Technical Architecture

### Firmware Extensions (QMK)

**VIA Custom Commands** (via `via_custom_value_command_kb()`):
```c
// Command definitions
#define CMD_GET_LED_MAP    0x01  // Return matrix_co mapping
#define CMD_HIGHLIGHT_LEDS 0x02  // Highlight given LED indexes with layer colors
#define CMD_TRAINER_BEGIN  0x03  // Save RGB mode, set backdrop
#define CMD_TRAINER_END    0x04  // Restore RGB mode
#define CMD_OLED_TEXT      0x10  // Display text on OLED
```

**RGB Matrix Indicators** (via `rgb_matrix_indicators_advanced_user()`):
- Timer-based LED highlighting with duration control
- Layer-specific color coding for chord visualization
- Configurable colors via Python CLI config system
- Non-destructive - preserves normal RGB animations

**OLED Display** (via `oled_task_user()`):
- 63-byte text buffer for host messages
- Simple text display for training prompts
- Memory-conscious implementation

### Python CLI Application

**Project Structure:**
```
qmk_trainer/
├── pyproject.toml    # uv project configuration with tool install
├── cli.py            # Typer CLI interface
├── hid_comm.py       # VIA HID communication
├── chord_mapper.py   # FrogPad chord definitions
├── trainer.py        # Training session logic
├── config.py         # Configuration management
├── default_config.toml # Default configuration file
└── tests/            # Unit and integration tests
```

**Dependencies:**
- `typer` - CLI framework
- `rich` - Console UI and progress display  
- `hidapi` - USB HID communication
- `tomli` / `tomllib` - TOML configuration parsing
- `pytest` - Testing framework

**CLI Commands:**
```bash
qmk_trainer highlight --keys 1,2,3 --duration 1000  # Debug LED highlighting
qmk_trainer train "hello"                            # Sequential training
qmk_trainer drill                                    # Practice mode with feedback
qmk_trainer config                                   # View/edit configuration
```

## Implementation Details

### Firmware Code Patterns

**VIA Command Handler:**
```c
void via_custom_value_command_kb(uint8_t *data, uint8_t length) {
    switch (data[0]) {
    case CMD_GET_LED_MAP:
        // Send g_led_config.matrix_co mapping back via raw_hid_send
        for (uint8_t row = 0; row < MATRIX_ROWS; row++) {
            for (uint8_t col = 0; col < MATRIX_COLS; col++) {
                // Pack row,col -> LED index mapping
            }
        }
        raw_hid_send(response, 32);
        break;
    case CMD_HIGHLIGHT_LEDS:
        hilite_count = data[1];
        memcpy(hilite_leds, &data[2], hilite_count);
        // Extract RGB color values (3 bytes after LED indexes)
        hilite_r = data[2 + hilite_count];
        hilite_g = data[2 + hilite_count + 1]; 
        hilite_b = data[2 + hilite_count + 2];
        hilite_duration = (data[length-2] | (data[length-1] << 8));
        hilite_started = timer_read32();
        break;
    }
}
```

**RGB Highlighting:**
```c
bool rgb_matrix_indicators_advanced_user(uint8_t led_min, uint8_t led_max) {
    if (timer_elapsed32(hilite_started) < hilite_duration) {
        for (uint8_t i = 0; i < hilite_count; i++) {
            uint8_t idx = hilite_leds[i];
            if (idx >= led_min && idx < led_max) {
                RGB_MATRIX_INDICATOR_SET_COLOR(idx, hilite_r, hilite_g, hilite_b);
            }
        }
    }
    return false;
}
```

### Python Communication Pattern

**HID Device Detection:**
```python
def get_via_device():
    devices = hid.enumerate(0x7171, 0x0002)  # Lily58 VID/PID
    via_devices = [d for d in devices if d['usage_page'] == 0xFF60]
    if not via_devices:
        raise RuntimeError("No VIA device found")
    return hid.Device(path=via_devices[0]['path'])
```

**Command Sending:**
```python
def send_via_command(device, cmd, payload=b""):
    report = [0x00] * 33  # Report ID + 32 bytes
    report[1] = cmd
    report[2:2+len(payload)] = payload[:30]  # Max 30 bytes payload
    device.write(bytes(report))

def highlight_leds_with_color(device, led_indexes, color_rgb, duration_ms):
    """Send highlight command with layer-specific color."""
    payload = [len(led_indexes)] + led_indexes + list(color_rgb)
    payload += [(duration_ms & 0xFF), (duration_ms >> 8) & 0xFF]
    send_via_command(device, CMD_HIGHLIGHT_LEDS, bytes(payload))
```

### Chord Mapping System

**FrogPad Chord Definitions:**
```python
FROGPAD_CHORDS = {
    'a': [(2, 1, 0)],              # Single key on layer 0
    'b': [(3, 1, 0), (3, 2, 0)],   # Two key chord on layer 0
    'c': [(3, 2, 0)],              # Single key on layer 0
    'A': [(2, 1, 1)],              # Uppercase on layer 1
    # ... complete FrogPad mapping with layer info
}

def char_to_leds_with_layers(char, matrix_to_led_map, layer_colors):
    chord = FROGPAD_CHORDS.get(char)
    if not chord:
        return []
    
    led_info = []
    for row, col, layer in chord:
        led_idx = matrix_to_led_map[row][col]
        color = layer_colors.get(layer, (255, 255, 255))  # Default white
        led_info.append((led_idx, color))
    return led_info

## Configuration System

**Default Configuration** (`~/.config/qmk_trainer/config.toml`):
```toml
[layer_colors]
# RGB values (0-255) for each layer
0 = [0, 255, 0]      # Layer 0: Green
1 = [255, 165, 0]    # Layer 1: Orange  
2 = [255, 0, 0]      # Layer 2: Red
3 = [0, 0, 255]      # Layer 3: Blue
4 = [255, 0, 255]    # Layer 4: Magenta

[training]
default_duration = 2000  # Default highlight duration in ms
show_progress = true     # Show training progress bar

[device]
# USB VID/PID for device detection
vendor_id = 0x7171
product_id = 0x0002
```

**Configuration Management:**
```python
import tomli
from pathlib import Path
import shutil

def get_config_path():
    return Path.home() / ".config" / "qmk_trainer" / "config.toml"

def install_default_config():
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    if not config_path.exists():
        # Copy from package default_config.toml
        default_config = Path(__file__).parent / "default_config.toml"
        shutil.copy2(default_config, config_path)

def load_config():
    config_path = get_config_path()
    if not config_path.exists():
        install_default_config()
    with open(config_path, 'rb') as f:
        return tomli.load(f)
```
```

## Implementation Sequence

### Phase 1: Firmware Foundation
1. **Add VIA command handler to `keymap.c`**
   - Implement `via_custom_value_command_kb()` with command switching
   - Add static variables for highlight state, RGB color values, and OLED buffer

2. **Implement RGB indicators**
   - Add `rgb_matrix_indicators_advanced_user()` function
   - Use timer-based highlighting with configurable duration
   - Support layer-specific RGB color values from CLI

3. **Add OLED support**
   - Implement `oled_task_user()` for text display
   - Handle memory constraints vs VIA compatibility

4. **Build and test firmware**
   - Compile with `./build.sh frogger_rgb_via`
   - Flash to hardware and verify VIA still works

### Phase 2: Python CLI Development
1. **Initialize project structure**
   ```bash
   mkdir qmk_trainer && cd qmk_trainer
   uv init --name qmk_trainer --app
   uv add typer rich hidapi tomli pytest
   ```

2. **Create HID communication layer**
   - Implement VIA device detection and connection
   - Create command sending/receiving functions
   - Test basic communication with firmware

3. **Build chord mapping system**
   - Define FrogPad chord mappings
   - Request LED mapping from firmware (cmd 0x01)
   - Create character → LED index translation

4. **Implement CLI interface**
   - Create Typer app with subcommands
   - Add Rich console output for progress and status
   - Implement training session management
   
5. **Create configuration system**
   - Create default config file with layer color mappings
   - Implement config file installation to `~/.config/qmk_trainer/`
   - Add config command for viewing/editing settings

### Phase 3: Integration and Testing
1. **Create integration tests**
   - Test LED highlighting accuracy
   - Verify OLED message display
   - Validate RGB restoration after training

2. **Add comprehensive error handling**
   - Handle device disconnection gracefully
   - Validate chord definitions
   - Provide helpful error messages

3. **Performance optimization**
   - Minimize HID communication overhead
   - Efficient LED index caching
   - Responsive CLI interface

## Validation Gates

### Firmware Validation
```bash
# Build check
./build.sh frogger_rgb_via
ls -la .build/lily58_frogger_frogger_rgb_via.uf2

# Flash and verify VIA compatibility
# Manual test: Open VIA, verify all functions work
# Manual test: RGB animations function normally
```

### Python Validation  
```bash
# Environment setup and installation
cd qmk_trainer
uv sync

# Install as global tool
uv tool install --editable .

# Code quality
uv run ruff check --fix .
uv run mypy . --ignore-missing-imports

# Unit tests
uv run pytest tests/ -v --cov=.

# Integration tests
qmk_trainer highlight --keys 0,1,2 --duration 2000
qmk_trainer train "a"
```

### Success Criteria Validation
- [ ] Command `qmk_trainer train "cat"` highlights correct chord sequence with layer colors
- [ ] OLED displays training prompts ("Press: c", "Press: a", "Press: t")  
- [ ] RGB animations restore to normal after training session ends
- [ ] VIA editor opens and functions normally (keymap editing, RGB control)
- [ ] System works with only left half connected (MASTER_LEFT)
- [ ] Configuration file created at `~/.config/qmk_trainer/config.toml` on first run
- [ ] Layer colors are configurable and applied correctly during training

## Risk Mitigation

### Flash Memory Constraints
**Issue:** ATmega32u4 limited flash space with VIA + RGB + OLED
**Mitigation:** 
- Use `LTO_ENABLE = yes` (already enabled)
- Conditional OLED compilation based on available space
- Minimal code footprint for VIA handlers

### HID Communication Conflicts
**Issue:** Multiple applications accessing VIA interface
**Mitigation:**
- Use standard VIA custom command channel only
- Graceful device detection and connection handling
- Clear error messages for connection issues

### Chord Definition Accuracy
**Issue:** Incorrect FrogPad mappings leading to wrong training
**Mitigation:**
- Reference authentic FrogPad documentation
- Implement chord validation against known patterns
- Provide debug mode for chord verification

### Split Keyboard Sync Issues  
**Issue:** LED/OLED sync between keyboard halves
**Mitigation:**
- Use `MASTER_LEFT` configuration (already set)
- Design for left-half-only operation as specified
- No right-half dependencies in implementation

## Documentation References

### QMK Documentation
- **VIA Custom Commands:** https://docs.qmk.fm/features/via#custom-value-commands
- **RGB Matrix Indicators:** https://docs.qmk.fm/features/rgb_matrix#indicator-examples
- **OLED Driver:** https://docs.qmk.fm/features/oled_driver
- **Raw HID:** https://docs.qmk.fm/features/rawhid

### Python Libraries
- **hidapi Documentation:** https://pypi.org/project/hid/
- **Typer Documentation:** https://typer.tiangolo.com/
- **Rich Documentation:** https://rich.readthedocs.io/

### Hardware References
- **Lily58 RGB Matrix Config:** See `lily58_pro/keyboard.json` (74 LEDs, 37 per side)
- **VIA Protocol:** USB VID: 0x7171, PID: 0x0002, Usage Page: 0xFF60

## Expected Deliverables

### Firmware Changes
- Extended `keymap.c` with 3 hook functions (~100 lines of code)
- Optional `config.h` additions for trainer-specific defines
- Maintains 100% VIA compatibility

### Python CLI Application
- Complete training CLI with 4 commands (highlight, train, drill, config)
- Installable as global tool via `uv tool install`
- Configuration system with layer color customization
- Rich console interface with progress indication
- Comprehensive test suite with >80% coverage
- Documentation and usage examples

### Integration Package
- Build scripts for firmware compilation
- Python CLI tool installable globally via `uv tool install`
- Default configuration installation to `~/.config/qmk_trainer/`
- End-to-end testing procedures
- User guide for training workflow and layer color customization

**Final Confidence Assessment: 8/10**
- ✅ Clear technical requirements with proven patterns
- ✅ Existing VIA infrastructure provides solid foundation  
- ✅ Well-defined API boundary between firmware and CLI
- ✅ Minimal firmware changes reduce flash memory risk
- ⚠️ FrogPad chord definitions need careful verification
- ⚠️ OLED vs VIA memory trade-off may require conditional compilation