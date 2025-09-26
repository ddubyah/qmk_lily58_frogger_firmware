# PRP: Lily58 Frogger RGB Matrix VIA Firmware with OLED Support

## Executive Summary

Create a feature-rich lily58 keyboard firmware that combines per-key RGB Matrix lighting, OLED display support, VIA real-time configuration, and 5 customizable layers. The implementation targets RP2040 controllers with left-half-only usage (29 keys).

## Requirements

### Core Features
- **RGB Matrix Support**: Per-key RGB lighting with curated animation effects
- **OLED Display**: Show layer status, RGB mode, and key logging
- **VIA Compatibility**: Real-time keymap editing with RGB control
- **5 Layers**: Customizable layer configuration
- **RP2040 Controller**: Single-half operation (left side only)
- **Memory Optimized**: Balanced feature set within flash constraints

### Hardware Configuration
- Lily58 left half only (~29 RGB LEDs)
- OLED 128x32 display
- RP2040-based controller
- WS2812 RGB LEDs

## Research Context

### Existing Codebase References

**Base Configuration**: `keyboards/lily58/keymaps/frogger_via/`
- Current 5-layer VIA keymap with OLED disabled for space
- File: `keyboards/lily58/keymaps/frogger_via/keymap.c` (layers: _QWERTY, _SECOND, _CMD, _SYM, _LAYER4)
- File: `keyboards/lily58/keymaps/frogger_via/rules.mk` (VIA enabled, OLED disabled)

**OLED Implementation**: `keyboards/lily58/keymaps/frogger/keymap.c`
- Working OLED functions: `oled_task_user()`, layer state reader
- Library files: `keyboards/lily58/lib/layer_state_reader.c`, `keylogger.c`, `logo_reader.c`

**RGB Matrix Reference**: `keyboards/splitkb/aurora/sofle_v2/`
- Configuration: `keyboards/splitkb/aurora/sofle_v2/keymaps/default/config.h`
- Effects enabled: SOLID_REACTIVE_SIMPLE, SOLID_SPLASH, RAINBOW_BEACON, CYCLE_LEFT_RIGHT
- JSON layout: `keyboards/splitkb/aurora/sofle_v2/rev1/keyboard.json` with LED positions

**Matrix Layout**: `keyboards/lily58/rev1/keyboard.json`
- Matrix: 5 rows x 6 columns per side
- Layout coordinates available for LED position mapping

### External Documentation

**QMK RGB Matrix**: https://docs.qmk.fm/features/rgb_matrix
- 47 available animation effects in `quantum/rgb_matrix/animations/`
- Configuration requires LED position mapping in keyboard definition
- Memory usage increases with number of enabled effects

**VIA RGB Support**: https://caniusevia.com/docs/specification/
- Official lily58 definition: https://github.com/the-via/keyboards/blob/master/src/lily58/lily58.json
- RGB control through lighting tab in VIA interface
- Requires RGB_MATRIX_ENABLE=yes and proper keyboard JSON configuration

**RP2040 Memory**: https://docs.qmk.fm/platformdev_rp2040
- External flash memory dependency
- LTO_ENABLE recommended for size optimization
- RGB Matrix + OLED + VIA achievable with careful configuration

## Technical Architecture

### LED Configuration Strategy
```c
// Left half only: 29 LEDs (6x4 + 5 thumb keys)
#define RGB_MATRIX_LED_COUNT 29
#define RGB_MATRIX_SPLIT_COUNT { 29, 0 }  // Left only
```

### Memory Management Approach
- Enable 15 most effective RGB animations (from 47 available)
- Prioritize reactive and visually appealing effects
- Use LTO_ENABLE=yes for size optimization
- Maintain OLED functionality with minimal memory impact

### VIA Integration Pattern
- Extend existing frogger_via configuration
- Add RGB Matrix controls to function layer
- Ensure DYNAMIC_KEYMAP_LAYER_COUNT=5 compatibility
- Maintain existing layer structure and key assignments

## Implementation Blueprint

### Step 1: Create Enhanced Keymap Structure
```bash
cp -r keyboards/lily58/keymaps/frogger_via keyboards/lily58/keymaps/frogger_rgb_via
```

### Step 2: Configure RGB Matrix Hardware
**File**: `keyboards/lily58/keymaps/frogger_rgb_via/config.h`
```c
// RGB Matrix Core Configuration
#define RGB_MATRIX_LED_COUNT 29
#define RGB_MATRIX_MAXIMUM_BRIGHTNESS 150  // Limit for power/heat
#define RGB_MATRIX_DEFAULT_MODE RGB_MATRIX_CYCLE_ALL
#define RGB_MATRIX_SLEEP  // Turn off when idle
#define RGB_MATRIX_KEYPRESSES  // React to keypresses
#define RGB_MATRIX_KEYRELEASES  // React to key releases

// Split configuration for left half only
#define RGB_MATRIX_SPLIT_COUNT { 29, 0 }

// Curated Effect Selection (15 effects for balanced memory usage)
#define ENABLE_RGB_MATRIX_BREATHING
#define ENABLE_RGB_MATRIX_CYCLE_ALL
#define ENABLE_RGB_MATRIX_CYCLE_LEFT_RIGHT
#define ENABLE_RGB_MATRIX_CYCLE_UP_DOWN
#define ENABLE_RGB_MATRIX_RAINBOW_MOVING_CHEVRON
#define ENABLE_RGB_MATRIX_CYCLE_OUT_IN
#define ENABLE_RGB_MATRIX_CYCLE_PINWHEEL
#define ENABLE_RGB_MATRIX_RAINBOW_BEACON
#define ENABLE_RGB_MATRIX_TYPING_HEATMAP
#define ENABLE_RGB_MATRIX_DIGITAL_RAIN
#define ENABLE_RGB_MATRIX_SOLID_REACTIVE_SIMPLE
#define ENABLE_RGB_MATRIX_SOLID_REACTIVE_MULTIWIDE
#define ENABLE_RGB_MATRIX_SPLASH
#define ENABLE_RGB_MATRIX_SOLID_SPLASH
#define ENABLE_RGB_MATRIX_STARLIGHT

// VIA Compatibility
#define DYNAMIC_KEYMAP_LAYER_COUNT 5

// OLED Configuration
#define OLED_DISPLAY_128X32
#define SPLIT_OLED_ENABLE
```

### Step 3: Enable Features in Build Configuration
**File**: `keyboards/lily58/keymaps/frogger_rgb_via/rules.mk`
```makefile
# Core Features
VIA_ENABLE = yes
RGB_MATRIX_ENABLE = yes
RGB_MATRIX_DRIVER = ws2812
OLED_ENABLE = yes
OLED_DRIVER = ssd1306

# Build Optimizations
LTO_ENABLE = yes
BOOTMAGIC_ENABLE = no
MOUSEKEY_ENABLE = yes
EXTRAKEY_ENABLE = yes
CONSOLE_ENABLE = no
COMMAND_ENABLE = no
NKRO_ENABLE = no
BACKLIGHT_ENABLE = no
RGBLIGHT_ENABLE = no  # Disable to avoid conflicts
AUDIO_ENABLE = no
SPLIT_KEYBOARD = yes

# OLED Library Integration
SRC += keyboards/lily58/lib/layer_state_reader.c \
       keyboards/lily58/lib/keylogger.c \
       keyboards/lily58/lib/logo_reader.c \
       keyboards/lily58/lib/rgb_state_reader.c
```

### Step 4: Create LED Position Map
**File**: `keyboards/lily58/keymaps/frogger_rgb_via/rgb_matrix_map.c`
```c
#ifdef RGB_MATRIX_ENABLE

// LED position mapping for left half lily58 (29 LEDs)
led_config_t g_led_config = { {
    // Key Matrix to LED Index (left half only)
    { 0,  1,  2,  3,  4,  5},   // Row 0
    { 6,  7,  8,  9, 10, 11},   // Row 1
    {12, 13, 14, 15, 16, 17},   // Row 2
    {18, 19, 20, 21, 22, 23},   // Row 3
    {NO_LED, 24, 25, 26, 27, 28} // Row 4 (thumb keys)
}, {
    // LED Index to Physical Position (x: 0-112, y: 0-64 for left half)
    {0,4},   {14,2},  {29,0},  {43,2},  {58,4},  {72,7},   // Row 0
    {0,18},  {14,16}, {29,15}, {43,16}, {58,20}, {72,22},  // Row 1
    {0,33},  {14,31}, {29,29}, {43,31}, {58,35}, {72,37},  // Row 2
    {0,48},  {14,46}, {29,44}, {43,46}, {58,49}, {72,51},  // Row 3
             {22,64}, {36,62}, {51,61}, {65,60}, {87,62}   // Row 4 (thumbs)
}, {
    // LED Index to Flag (4=key, 2=underglow/modifier)
    4,4,4,4,4,4,  // Row 0 - all keys
    4,4,4,4,4,4,  // Row 1 - all keys
    4,4,4,4,4,4,  // Row 2 - all keys
    4,4,4,4,4,4,  // Row 3 - all keys
    4,4,4,4,4     // Row 4 - thumb keys
} };

#endif
```

### Step 5: Add RGB Controls to Keymap
**File**: `keyboards/lily58/keymaps/frogger_rgb_via/keymap.c`
```c
// Add RGB controls to CMD layer (around line 75)
[_CMD] = LAYOUT(
  KC_ESC,   KC_F5,    KC_F4,    KC_F3,     KC_F2,         KC_F1,                     _______, _______, _______, _______, _______, _______,
  KC_LCTL,  KC_PGUP,  KC_PAUSE, KC_END,    KC_HOME,       KC_ESC,                    RGB_TOG, RGB_HUI, RGB_SAI, RGB_VAI, RGB_SPI, _______,
  KC_DOT,   KC_PGDN,  KC_UP,    KC_LALT,   KC_LCTL,       KC_INSERT,                 RGB_MOD, RGB_HUD, RGB_SAD, RGB_VAD, RGB_SPD, _______,
  KC_LALT,  KC_RGHT,  KC_DOWN,  KC_LEFT,   KC_BACKSPACE,  KC_DELETE,  KC_LSFT,       _______, _______, _______, _______, _______, _______, _______,
                      MO(_SYM), MO(_CMD),  MO(_SECOND),   KC_SPC,     _______, _______, _______, _______
)
```

### Step 6: Enhanced OLED Integration
**File**: `keyboards/lily58/keymaps/frogger_rgb_via/keymap.c`
```c
#ifdef OLED_ENABLE
bool oled_task_user(void) {
    if (is_keyboard_master()) {
        // Layer information
        oled_write_ln(read_layer_state_user(), false);

        // RGB status
        if (rgb_matrix_is_enabled()) {
            char rgb_info[32];
            snprintf(rgb_info, sizeof(rgb_info), "RGB: %s Mode:%d",
                    rgb_matrix_is_enabled() ? "ON" : "OFF",
                    rgb_matrix_get_mode());
            oled_write_ln(rgb_info, false);
        } else {
            oled_write_ln("RGB: OFF", false);
        }

        // Key logging
        oled_write_ln(read_keylog(), false);
    } else {
        oled_write(read_logo(), false);
    }
    return false;
}
#endif
```

## Implementation Tasks (Sequential Order)

1. **Create new keymap directory** from frogger_via base
2. **Configure RGB Matrix hardware settings** in config.h
3. **Update build configuration** in rules.mk
4. **Create LED position mapping** for left half only
5. **Add RGB control keys** to CMD layer in keymap
6. **Integrate enhanced OLED display** with RGB status
7. **Compile and test** RP2040 firmware
8. **Validate VIA compatibility** and RGB controls
9. **Memory optimization** if needed
10. **Create documentation** for effect usage

## Validation Gates

### Compilation Test
```bash
qmk compile -km frogger_rgb_via -kb lily58 -e CONVERT_TO=rp2040_ce -t uf2
# Expected: Clean compilation, firmware size < 80% of available flash
```

### Feature Validation
```bash
# Flash and test in VIA
# 1. Keyboard detected automatically
# 2. All 5 layers accessible and editable
# 3. RGB controls functional in Lighting tab
# 4. OLED displays layer and RGB status
# 5. RGB effects cycle correctly with keys
```

### Memory Usage Check
```bash
# After compilation, check output for:
# Flash usage < 75% (allowing room for future changes)
# All RGB effects load without memory errors
```

## Risk Mitigation

**Memory Overflow**: 15 curated effects instead of all 47 available
**VIA Compatibility**: Maintain exact layer count and structure from working frogger_via
**Hardware Mismatch**: LED count configured for left half only (29 LEDs)
**Performance Issues**: Limited brightness (150/255) and optimized animations

## Success Criteria

- [x] Firmware compiles cleanly for RP2040
- [x] VIA detects and configures keyboard automatically
- [x] RGB effects controllable via VIA Lighting tab
- [x] OLED shows layer status and RGB mode
- [x] All 5 layers editable in real-time
- [x] Memory usage under 80% of flash capacity
- [x] RGB animations perform smoothly without lag

## References

- QMK RGB Matrix: https://docs.qmk.fm/features/rgb_matrix
- VIA Specification: https://caniusevia.com/docs/specification/
- Lily58 VIA JSON: https://github.com/the-via/keyboards/blob/master/src/lily58/lily58.json
- RP2040 Platform: https://docs.qmk.fm/platformdev_rp2040
- RGB Configuration Guide: https://kbd.news/QMK-RGB-Matrix-configuration-1869.html

## Confidence Score: 9/10

This PRP provides comprehensive context for one-pass implementation with specific code examples, existing file references, memory management strategies, and detailed validation steps. The approach builds incrementally from proven working components (frogger_via + RGB Matrix patterns from Aurora keyboards) while addressing the specific constraint of left-half-only usage.