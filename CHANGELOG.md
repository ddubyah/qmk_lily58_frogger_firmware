# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.1] - 2025-01-27

### Added
- QMK Trainer CLI application for one-handed keyboard training
- VIA custom command protocol implementation (`CMD_GET_LED_MAP`, `CMD_HIGHLIGHT_LEDS`, `CMD_TRAINER_BEGIN/END`, `CMD_OLED_TEXT`, `CMD_GET_FIRMWARE_INFO`)
- RGB Matrix LED highlighting system with timer-based control
- OLED text display integration for training feedback
- Python CLI with commands: `highlight`, `train`, `drill`, `test`, `oled`, `info`
- Enhanced keyboard firmware with trainer communication protocols
- Raw HID communication infrastructure
- 7-layer VIA support (increased from 5 layers)

### Changed
- OLED display branding updated to "Frogger58"
- Layer count expanded to 7 for enhanced VIA compatibility
- Removed all on-board test routines (F1-F8 function key tests, encoder button tests)
- Simplified `process_record_user()` function

### Technical Decisions Made

#### VIA Compatibility vs Custom Features
- **Decision**: Prioritized VIA compatibility over custom trainer integration
- **Rationale**: VIA's keymap configurator is essential for one-handed FrogPad layout customization
- **Impact**: Limited to VIA-compatible communication methods

#### PID Management for VIA Recognition
- **Attempted**: Changed PID from `0x0002` to `0x5866` to display "Frogger58" in VIA
- **Reverted**: Rolled back to original PID `0x0002`
- **Reason**: Custom PID breaks VIA's database layout recognition
- **Trade-off**: Accept "Lily58 Pro" display name to maintain layout compatibility

#### Communication Protocol Challenges
- **VIA Custom Commands**: Implemented but discovered unreliable in modern QMK/VIA versions
- **Raw HID**: Attempted but conflicts with VIA's HID usage
- **Result**: No reliable firmware-to-CLI communication path while maintaining VIA compatibility

### Deprecated
- **QMK Trainer CLI communication approach** - Cannot reliably communicate with firmware while maintaining VIA compatibility
- **Firmware-based trainer controls** - Removed all on-board test routines

### Lessons Learned

#### 1. VIA Database Dependencies
- VIA uses VID/PID combinations to identify keyboards from its internal database
- Changing PID breaks layout recognition even if it fixes display names
- VIA compatibility requires using exact database entries

#### 2. Modern QMK/VIA Communication Limitations
- VIA custom commands (`via_custom_value_command_kb`) are unreliable in current versions
- Raw HID conflicts with VIA's HID usage patterns
- No clean way to extend VIA protocol without breaking compatibility

#### 3. Firmware Design Constraints
- Maintaining VIA compatibility severely limits custom communication options
- Feature toggles between VIA and custom modes may be necessary for advanced features
- On-board test routines consume valuable key combinations

#### 4. Development Architecture
- Clean separation between firmware and external tools is difficult with VIA constraints
- Terminal-only solutions may be more reliable than firmware integration
- Hardware capabilities (RGB, OLED) work well but external control is problematic

### Next Steps
- Pivot to terminal-only trainer implementation
- Design training system that doesn't require firmware communication
- Explore alternative approaches for one-handed keyboard training

## [1.0.0] - 2025-01-26

### Added
- Initial Lily58 "Frogger" variant firmware
- VIA-compatible keymap with RGB matrix support
- 5-layer keymap configuration
- RP2040 controller support with UF2 output
- Custom build system with automated scripts