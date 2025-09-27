// Copyright 2025 Dasky (@daskygit)
// SPDX-License-Identifier: GPL-2.0-or-later

#pragma once

// VIA support with 7 layers
#define DYNAMIC_KEYMAP_LAYER_COUNT 7

// RGB Matrix VIA menu support
#define VIA_QMK_RGB_MATRIX_ENABLE

// QMK Trainer CLI configuration
#define RAW_HID_ENABLE
#define TRAINER_MAX_LEDS 20
#define TRAINER_DEFAULT_DURATION 2000

// OLED configuration for trainer mode
#ifdef OLED_ENABLE
#define OLED_TIMEOUT 30000
#define OLED_BRIGHTNESS 128
#endif