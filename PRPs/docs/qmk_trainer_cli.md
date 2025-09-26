# PRD: One-Handed Keyboard Training Helper

**Project:** Lily58 + VIA + Python CLI trainer
**Owner:** DDubyah
**Audience:** Development team

---

## 1. Goals

* Provide a **training CLI app** that helps the user memorize a one-handed “chorded” keyboard layout (FrogPad-style).
* Input: character(s) or string in the CLI.
* Output: Keyboard LEDs flash/highlight the correct keys (chords) to press.
* Show text prompts/messages on the Lily58 OLED during training.
* Preserve the user’s normal RGB animations in daily use, only muting them while the trainer is running.
* Minimal firmware changes, keep VIA editor compatibility.
* Ensure the solution works with only the **left half** connected.

---

## 2. Scope

### In Scope

* Extend VIA-enabled Lily58 firmware minimally:

  * Add `via_custom_value_command_kb()` handler to accept trainer-specific commands.
  * Add LED highlight logic via `rgb_matrix_indicators_advanced_user()`.
  * Add OLED rendering hook (`oled_task_user()`) for host-sent messages.
* Python CLI application:

  * Parse VIA keymap JSON (exported from VIA app).
  * Maintain chord definitions (FrogPad mapping).
  * Map user input → chords → LED indexes using `matrix_to_led` dump.
  * Send HID packets for highlights, OLED messages, and training control (quiet/restore RGB).
* CLI UX: **Typer** (CLI commands), **Rich** (UI/feedback), **uv** (package manager).

### Out of Scope

* Changes to core QMK beyond VIA custom handler and OLED task.
* GUI/web training app.
* Handling right-half keyboard.

---

## 3. Success Criteria

* Running `trainer "cat"` in CLI highlights the correct chord keys and shows OLED prompt messages.
* LEDs return to normal animation mode after training ends.
* VIA editor remains fully functional.
* No sync issues, since only left half is in use.

---

## 4. Architecture

### Firmware (QMK Lily58 + VIA)

* **VIA enabled** (`VIA_ENABLE = yes`).
* **RGB Matrix enabled** (`RGB_MATRIX_ENABLE = yes`).
* **OLED enabled** (`OLED_ENABLE = yes`).
* **Left-only mode:** define `MASTER_LEFT` so the board always treats the left side as master.

**Custom VIA commands:**

* `0x01` → Return `g_led_config.matrix_co` mapping (matrix→LED index).
* `0x02` → Highlight given LED indexes for duration.
* `0x03` → `TRAINER_BEGIN`: Save current RGB mode/HSV; set solid-off backdrop.
* `0x04` → `TRAINER_END`: Restore saved RGB mode/HSV.
* `0x10` → `OLED_TEXT`: ASCII payload; display on OLED.

**Hooks used:**

* `via_custom_value_command_kb()` → parse custom commands.
* `rgb_matrix_indicators_advanced_user()` → set highlight colors.
* `oled_task_user()` → render latest host-provided text.

### Python CLI

* **uv** for dependency/env management.
* **Typer**: CLI subcommands:

  * `highlight` (debug highlight of keys).
  * `train` (sequential chord trainer for a word/string).
  * `drill` (practice mode with feedback).
* **Rich**: progress, status panels, chord visualization.
* **hidapi**: USB communication with VIA.

**Flow:**

1. CLI loads VIA JSON (user’s layout).
2. CLI requests LED map (cmd `0x01`) and caches it.
3. CLI maps user text → chord keys → LED indexes.
4. For each step:

   * Send `TRAINER_BEGIN` (cmd `0x03`).
   * Send `OLED_TEXT` (cmd `0x10`) with instruction (e.g., `"Chord: A"`).
   * Send `HIGHLIGHT` (cmd `0x02`) with LED indexes + duration.
   * Wait for user, continue.
5. At end, send `TRAINER_END` (cmd `0x04`) to restore RGB animations.

---

## 5. Pseudo-Code

### Firmware (C)

```c
static uint8_t hilite_leds[8];
static uint8_t hilite_count = 0;
static uint32_t hilite_started = 0;
static uint16_t hilite_duration = 0;

static uint8_t saved_mode;
static HSV saved_hsv;

char oled_buffer[64];

void via_custom_value_command_kb(uint8_t *data, uint8_t length) {
    switch (data[0]) {
    case 0x01: // return matrix_to_led
        break;
    case 0x02: // highlight LEDs
        hilite_count = data[1];
        memcpy(hilite_leds, &data[2], hilite_count);
        hilite_duration = (data[length-2] | (data[length-1] << 8));
        hilite_started = timer_read32();
        break;
    case 0x03: // TRAINER_BEGIN
        saved_mode = rgb_matrix_get_mode();
        saved_hsv = rgb_matrix_get_hsv();
        rgb_matrix_mode_noeeprom(RGB_MATRIX_SOLID_COLOR);
        rgb_matrix_sethsv_noeeprom(HSV_OFF);
        break;
    case 0x04: // TRAINER_END
        rgb_matrix_mode_noeeprom(saved_mode);
        rgb_matrix_sethsv_noeeprom(saved_hsv);
        break;
    case 0x10: // OLED_TEXT
        memset(oled_buffer, 0, sizeof(oled_buffer));
        memcpy(oled_buffer, &data[1], length-1);
        break;
    }
}

bool rgb_matrix_indicators_advanced_user(uint8_t min, uint8_t max) {
    if (timer_elapsed32(hilite_started) < hilite_duration) {
        for (uint8_t i = 0; i < hilite_count; i++) {
            uint8_t idx = hilite_leds[i];
            if (idx >= min && idx < max) {
                RGB_MATRIX_INDICATOR_SET_COLOR(idx, 0, 255, 0);
            }
        }
    }
    return false;
}

bool oled_task_user(void) {
    oled_write_ln(oled_buffer, false);
    return false;
}
```

### Python CLI (Typer + Rich)

```python
import typer, hid, json, struct
from rich.console import Console

console = Console()
app = typer.Typer()

def send_cmd(cmd, payload=b""):
    # write HID report to VIA device
    pass

@app.command()
def train(text: str):
    send_cmd(0x03)  # TRAINER_BEGIN
    for ch in text:
        chord = resolve_chord(ch)  # (row,col) list
        leds = [rowcol_to_led(rc) for rc in chord]
        send_cmd(0x10, ch.encode("ascii"))  # OLED_TEXT
        payload = bytes([0x02, len(leds), *leds, 0x20, 0x03])
        send_cmd(0x02, payload)
        typer.sleep(1.0)
    send_cmd(0x04)  # TRAINER_END
```

---

## 6. Dependencies

* **Firmware**:

  * QMK with `VIA_ENABLE`, `RGB_MATRIX_ENABLE`, `OLED_ENABLE`, `MASTER_LEFT`.
* **Python**:

  * `uv` (package manager).
  * `hidapi` (HID comms).
  * `typer` (CLI).
  * `rich` (console UI).

---

## 7. Risks & Mitigations

* **Flash size**: Lily58 (ATmega32u4) may run low. → Mitigate with `LTO_ENABLE = yes`, disable unused RGB effects.
* **HID channel conflicts**: Unlikely if we stick to VIA custom channel.
* **OLED buffer overflow**: Cap messages to 63 chars max.
* **Split sync issues**: Not relevant (left half only).

---

## 8. References

* QMK: [VIA Custom Commands](https://github.com/qmk/qmk_firmware/blob/master/docs/feature_via.md#custom-value-commands)
* QMK: [RGB Matrix indicators](https://github.com/qmk/qmk_firmware/blob/master/docs/feature_rgb_matrix.md#indicator-examples)
* QMK: [OLED rendering](https://github.com/qmk/qmk_firmware/blob/master/docs/feature_oled_driver.md)
* QMK: [Split keyboard handedness](https://github.com/qmk/qmk_firmware/blob/master/docs/feature_split_keyboard.md#setting-handedness)
* QMK: [LED config (`g_led_config`)](https://github.com/qmk/qmk_firmware/blob/master/docs/feature_rgb_matrix.md#led-configuration)
* Python HID: [hidapi docs](https://pypi.org/project/hid/)
