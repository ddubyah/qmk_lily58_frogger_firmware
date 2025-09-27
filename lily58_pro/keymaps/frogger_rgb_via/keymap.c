// Copyright 2025 Dasky (@daskygit)
// SPDX-License-Identifier: GPL-2.0-or-later

#include QMK_KEYBOARD_H
#include "print.h"

// QMK Trainer CLI Commands
#define CMD_GET_LED_MAP    0x01  // Return matrix_co mapping
#define CMD_HIGHLIGHT_LEDS 0x02  // Highlight given LED indexes with layer colors
#define CMD_TRAINER_BEGIN  0x03  // Save RGB mode, set backdrop
#define CMD_TRAINER_END    0x04  // Restore RGB mode
#define CMD_OLED_TEXT      0x10  // Display text on OLED
#define CMD_GET_FIRMWARE_INFO 0x20  // Get firmware build info

// Build info - updated on each build
#define TRAINER_FIRMWARE_VERSION "1.0.1"
#define BUILD_TIMESTAMP __DATE__ " " __TIME__

// Forward declaration
void via_custom_value_command_kb(uint8_t *data, uint8_t length);

// Trainer state variables
static uint8_t hilite_leds[20];        // LED indexes to highlight
static uint8_t hilite_count = 0;       // Number of LEDs to highlight
static uint8_t hilite_r = 255;         // Red component
static uint8_t hilite_g = 255;         // Green component
static uint8_t hilite_b = 255;         // Blue component
static uint16_t hilite_duration = 0;   // Duration in milliseconds
static uint32_t hilite_started = 0;    // Timer start
static bool trainer_active = false;    // Trainer mode flag
static uint8_t saved_mode;   // Saved RGB mode


#ifdef OLED_ENABLE
static char oled_buffer[64];           // OLED text buffer
static bool oled_text_active = false; // OLED text mode flag
#endif

// clang-format off
const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {

 [0] = LAYOUT(
  KC_ESC,   KC_1,   KC_2,    KC_3,    KC_4,    KC_5,                     KC_6,    KC_7,    KC_8,    KC_9,    KC_0,    KC_GRV,
  KC_TAB,   KC_Q,   KC_W,    KC_E,    KC_R,    KC_T,                     KC_Y,    KC_U,    KC_I,    KC_O,    KC_P,    KC_MINS,
  KC_LCTL,  KC_A,   KC_S,    KC_D,    KC_F,    KC_G,                     KC_H,    KC_J,    KC_K,    KC_L,    KC_SCLN, KC_QUOT,
  KC_LSFT,  KC_Z,   KC_X,    KC_C,    KC_V,    KC_B, KC_LBRC,  KC_RBRC,  KC_N,    KC_M,    KC_COMM, KC_DOT,  KC_SLSH,  KC_RSFT,
                           KC_LALT, KC_LGUI, MO(1), KC_SPC, KC_ENT, MO(2), KC_BSPC, KC_RGUI
),

[1] = LAYOUT(
  _______, _______, _______, _______, _______, _______,                   _______, _______, _______,_______, _______, _______,
  KC_F1,   KC_F2,   KC_F3,   KC_F4,   KC_F5,   KC_F6,                     KC_F7,   KC_F8,   KC_F9,   KC_F10,  KC_F11,  KC_F12,
  KC_GRV, KC_EXLM, KC_AT,   KC_HASH, KC_DLR,  KC_PERC,                   KC_CIRC, KC_AMPR, KC_ASTR, KC_LPRN, KC_RPRN, KC_TILD,
  _______, _______, _______, _______, _______, _______, _______, _______, XXXXXXX, KC_UNDS, KC_PLUS, KC_LCBR, KC_RCBR, KC_PIPE,
                             _______, _______, _______, _______, _______,  MO(3), _______, _______
),


[2] = LAYOUT(
  _______, _______, _______, _______, _______, _______,                     _______, _______, _______, _______, _______, _______,
  KC_GRV,  KC_1,    KC_2,    KC_3,    KC_4,    KC_5,                        KC_6,    KC_7,    KC_8,    KC_9,    KC_0,    _______,
  KC_F1,  KC_F2,    KC_F3,   KC_F4,   KC_F5,   KC_F6,                       XXXXXXX, KC_LEFT, KC_DOWN, KC_UP,   KC_RGHT, XXXXXXX,
  KC_F7,   KC_F8,   KC_F9,   KC_F10,  KC_F11,  KC_F12,   _______, _______,  KC_PLUS, KC_MINS, KC_EQL,  KC_LBRC, KC_RBRC, KC_BSLS,
                             _______, _______, MO(3),  _______, _______,  _______, _______, _______
),

  [3] = LAYOUT(
  XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,                   XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
  XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,                   XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
  RM_TOGG, RM_HUEU, RM_SATU, RM_VALU, XXXXXXX, XXXXXXX,                   XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
  RM_NEXT, RM_HUED, RM_SATD, RM_VALD, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
                             _______, _______, _______, _______, _______,  MO(4), _______, _______
  ),

  [4] = LAYOUT(
  XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,                   XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
  XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,                   XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
  XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,                   XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
  XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
                             _______, _______, _______, _______, _______,  _______, _______, _______
  ),

  [5] = LAYOUT(
  XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,                   XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
  XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,                   XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
  XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,                   XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
  XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
                             _______, _______, _______, _______, _______,  _______, _______, _______
  ),

  [6] = LAYOUT(
  XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,                   XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
  XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,                   XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
  XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,                   XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
  XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
                             _______, _______, _______, _______, _______,  _______, _______, _______
  )
};

#if defined(ENCODER_MAP_ENABLE)
const uint16_t PROGMEM encoder_map[][NUM_ENCODERS][NUM_DIRECTIONS] = {
    [0] =  { ENCODER_CCW_CW(KC_VOLD, KC_VOLU),      ENCODER_CCW_CW(KC_VOLD, KC_VOLU)},
    [1] =  { ENCODER_CCW_CW(KC_TRNS, KC_TRNS),      ENCODER_CCW_CW(KC_TRNS, KC_TRNS)},
    [2] =  { ENCODER_CCW_CW(KC_TRNS, KC_TRNS),      ENCODER_CCW_CW(KC_TRNS, KC_TRNS)},
    [3] =  { ENCODER_CCW_CW(KC_TRNS, KC_TRNS),      ENCODER_CCW_CW(KC_TRNS, KC_TRNS)},
    [4] =  { ENCODER_CCW_CW(KC_TRNS, KC_TRNS),      ENCODER_CCW_CW(KC_TRNS, KC_TRNS)},
    [5] =  { ENCODER_CCW_CW(KC_TRNS, KC_TRNS),      ENCODER_CCW_CW(KC_TRNS, KC_TRNS)},
    [6] =  { ENCODER_CCW_CW(KC_TRNS, KC_TRNS),      ENCODER_CCW_CW(KC_TRNS, KC_TRNS)}
};
#endif
// clang-format on

// Console-based trainer commands
void keyboard_post_init_user(void) {
    // Enable debug and console output
    debug_enable = true;
    debug_matrix = false;
    debug_keyboard = false;

    print("QMK Trainer initialized!\n");
    print("Commands: H<leds> = highlight, T = trainer mode, O<text> = OLED\n");
}

bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    return true;
}

// VIA Custom Command Handler (keeping for completeness)
void via_custom_value_command_kb(uint8_t *data, uint8_t length) {
    switch (data[0]) {
        case CMD_GET_LED_MAP: {
            // Send g_led_config.matrix_co mapping back via raw_hid_send
            uint8_t response[32] = {0};
            uint8_t idx = 1; // Skip command byte
            
            // Pack matrix rows and columns with their LED indexes
            for (uint8_t row = 0; row < MATRIX_ROWS && idx < 31; row++) {
                for (uint8_t col = 0; col < MATRIX_COLS && idx < 29; col++) {
                    uint8_t led_idx = g_led_config.matrix_co[row][col];
                    if (led_idx != NO_LED && idx < 29) {
                        response[idx++] = row;
                        response[idx++] = col;
                        response[idx++] = led_idx;
                    }
                }
            }
            response[0] = CMD_GET_LED_MAP; // Echo command
            memcpy(data, response, 32);
            break;
        }
        
        case CMD_HIGHLIGHT_LEDS: {
            if (length >= 3) {
                hilite_count = data[1];
                if (hilite_count > 20) hilite_count = 20; // Limit array bounds
                
                // Copy LED indexes
                for (uint8_t i = 0; i < hilite_count && (2 + i) < length; i++) {
                    hilite_leds[i] = data[2 + i];
                }
                
                // Extract RGB color values (3 bytes after LED indexes)
                if (length >= (2 + hilite_count + 3)) {
                    hilite_r = data[2 + hilite_count];
                    hilite_g = data[2 + hilite_count + 1];
                    hilite_b = data[2 + hilite_count + 2];
                }
                
                // Extract duration (2 bytes at end)
                if (length >= (2 + hilite_count + 5)) {
                    hilite_duration = (data[length - 2]) | (data[length - 1] << 8);
                } else {
                    hilite_duration = 2000; // Default 2 seconds
                }
                
                hilite_started = timer_read32();
            }
            break;
        }
        
        case CMD_TRAINER_BEGIN: {
            trainer_active = true;
            saved_mode = rgb_matrix_get_mode();
            // Set a neutral backdrop mode
            rgb_matrix_mode(RGB_MATRIX_SOLID_COLOR);
            rgb_matrix_sethsv(0, 0, 50); // Low brightness white backdrop
            break;
        }
        
        case CMD_TRAINER_END: {
            trainer_active = false;
            hilite_count = 0; // Clear highlights
            rgb_matrix_mode(saved_mode); // Restore previous mode
#ifdef OLED_ENABLE
            oled_text_active = false; // Clear OLED text
#endif
            break;
        }
        
#ifdef OLED_ENABLE
        case CMD_OLED_TEXT: {
            if (length >= 2) {
                uint8_t text_len = length - 1;
                if (text_len > 63) text_len = 63; // Limit buffer size
                
                memcpy(oled_buffer, &data[1], text_len);
                oled_buffer[text_len] = 0; // Null terminate
                oled_text_active = true;
            }
            break;
        }
#endif

        case CMD_GET_FIRMWARE_INFO: {
            uint8_t response[32] = {0};
            response[0] = CMD_GET_FIRMWARE_INFO; // Echo command

            // Pack version string and build timestamp
            const char* version = TRAINER_FIRMWARE_VERSION;
            const char* timestamp = BUILD_TIMESTAMP;
            uint8_t idx = 1;

            // Copy version (max 8 chars)
            for (uint8_t i = 0; i < 8 && version[i] && idx < 31; i++) {
                response[idx++] = version[i];
            }
            response[idx++] = 0; // Null terminator

            // Copy timestamp (remaining space)
            for (uint8_t i = 0; timestamp[i] && idx < 31; i++) {
                response[idx++] = timestamp[i];
            }

            memcpy(data, response, 32);
            break;
        }
    }
}

// RGB Matrix Indicators for LED highlighting
bool rgb_matrix_indicators_advanced_user(uint8_t led_min, uint8_t led_max) {
    if (hilite_count > 0 && timer_elapsed32(hilite_started) < hilite_duration) {
        for (uint8_t i = 0; i < hilite_count; i++) {
            uint8_t idx = hilite_leds[i];
            if (idx >= led_min && idx < led_max && idx < RGB_MATRIX_LED_COUNT) {
                rgb_matrix_set_color(idx, hilite_r, hilite_g, hilite_b);
            }
        }
        return true; // Return true to indicate we've set custom colors
    }
    return false;
}

#ifdef OLED_ENABLE
// OLED Display Handler
bool oled_task_user(void) {
    if (oled_text_active) {
        oled_clear();
        oled_write(oled_buffer, false);
    } else {
        // Default OLED content when not in trainer mode  
        oled_write_P(PSTR("Frogger58\n"), false);
        
        // Show current layer
        oled_write_P(PSTR("Layer: "), false);
        oled_write_char('0' + get_highest_layer(layer_state), false);
        oled_write_P(PSTR("\n"), false);
        
        // Show RGB mode if available
        if (rgb_matrix_is_enabled()) {
            oled_write_P(PSTR("RGB: "), false);
            oled_write_char('0' + rgb_matrix_get_mode(), false);
        }
    }
    return false;
}
#endif
