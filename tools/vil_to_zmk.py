#!/usr/bin/env python3
"""Convert Talor's PSKEEB5 Vial JSON keymap to a ZMK keymap.

This is intentionally small and specific to the PSKEEB5 3x5+4 layout.  It uses
QMK's LAYOUT_split_3x5_4 matrix order so the saved .vil lands on the same
physical keys in ZMK's visual binding order.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


QMK_LAYOUT_ORDER = [
    (0, 4), (0, 3), (0, 2), (0, 1), (0, 0),
    (4, 0), (4, 1), (4, 2), (4, 3), (4, 4),
    (1, 4), (1, 3), (1, 2), (1, 1), (1, 0),
    (5, 0), (5, 1), (5, 2), (5, 3), (5, 4),
    (2, 4), (2, 3), (2, 2), (2, 1), (2, 0),
    (6, 0), (6, 1), (6, 2), (6, 3), (6, 4),
    (3, 1), (3, 4), (3, 3), (3, 2),
    (7, 2), (7, 3), (7, 4), (7, 1),
]

KEY_ALIASES = {
    "KC_TRNS": "&trans",
    "KC_NO": "&none",
    "KC_A": "&kp A",
    "KC_B": "&kp B",
    "KC_C": "&kp C",
    "KC_D": "&kp D",
    "KC_E": "&kp E",
    "KC_F": "&kp F",
    "KC_G": "&kp G",
    "KC_H": "&kp H",
    "KC_I": "&kp I",
    "KC_J": "&kp J",
    "KC_K": "&kp K",
    "KC_L": "&kp L",
    "KC_M": "&kp M",
    "KC_N": "&kp N",
    "KC_O": "&kp O",
    "KC_P": "&kp P",
    "KC_Q": "&kp Q",
    "KC_R": "&kp R",
    "KC_S": "&kp S",
    "KC_T": "&kp T",
    "KC_U": "&kp U",
    "KC_V": "&kp V",
    "KC_W": "&kp W",
    "KC_X": "&kp X",
    "KC_Y": "&kp Y",
    "KC_Z": "&kp Z",
    "KC_1": "&kp N1",
    "KC_2": "&kp N2",
    "KC_3": "&kp N3",
    "KC_4": "&kp N4",
    "KC_5": "&kp N5",
    "KC_6": "&kp N6",
    "KC_7": "&kp N7",
    "KC_8": "&kp N8",
    "KC_9": "&kp N9",
    "KC_0": "&kp N0",
    "KC_F1": "&kp F1",
    "KC_F2": "&kp F2",
    "KC_F3": "&kp F3",
    "KC_F4": "&kp F4",
    "KC_F5": "&kp F5",
    "KC_F6": "&kp F6",
    "KC_F7": "&kp F7",
    "KC_F8": "&kp F8",
    "KC_F9": "&kp F9",
    "KC_F10": "&kp F10",
    "KC_F11": "&kp F11",
    "KC_F12": "&kp F12",
    "KC_ESCAPE": "&kp ESC",
    "KC_ESC": "&kp ESC",
    "KC_GESC": "&gresc",
    "KC_TAB": "&kp TAB",
    "KC_ENTER": "&kp ENTER",
    "KC_ENT": "&kp ENTER",
    "KC_SPACE": "&kp SPACE",
    "KC_SPC": "&kp SPACE",
    "KC_BSPACE": "&kp BSPC",
    "KC_BSPC": "&kp BSPC",
    "KC_DELETE": "&kp DEL",
    "KC_DEL": "&kp DEL",
    "KC_LEFT": "&kp LEFT",
    "KC_RIGHT": "&kp RIGHT",
    "KC_RGHT": "&kp RIGHT",
    "KC_UP": "&kp UP",
    "KC_DOWN": "&kp DOWN",
    "KC_HOME": "&kp HOME",
    "KC_END": "&kp END",
    "KC_PGUP": "&kp PG_UP",
    "KC_PGDOWN": "&kp PG_DN",
    "KC_PGDN": "&kp PG_DN",
    "KC_LGUI": "&kp LGUI",
    "KC_RGUI": "&kp RGUI",
    "KC_LCTRL": "&kp LCTRL",
    "KC_LCTL": "&kp LCTRL",
    "KC_RCTRL": "&kp RCTRL",
    "KC_RCTL": "&kp RCTRL",
    "KC_LALT": "&kp LALT",
    "KC_RALT": "&kp RALT",
    "KC_LSHIFT": "&kp LSHFT",
    "KC_LSFT": "&kp LSHFT",
    "KC_RSHIFT": "&kp RSHFT",
    "KC_RSFT": "&kp RSHFT",
    "KC_MINUS": "&kp MINUS",
    "KC_MINS": "&kp MINUS",
    "KC_EQUAL": "&kp EQUAL",
    "KC_EQL": "&kp EQUAL",
    "KC_LBRACKET": "&kp LBKT",
    "KC_LBRC": "&kp LBKT",
    "KC_RBRACKET": "&kp RBKT",
    "KC_RBRC": "&kp RBKT",
    "KC_QUOTE": "&kp SQT",
    "KC_QUOT": "&kp SQT",
    "KC_DQUO": "&kp DQT",
    "KC_SCOLON": "&kp SEMI",
    "KC_SCLN": "&kp SEMI",
    "KC_COMMA": "&kp COMMA",
    "KC_COMM": "&kp COMMA",
    "KC_DOT": "&kp DOT",
    "KC_SLASH": "&kp FSLH",
    "KC_SLSH": "&kp FSLH",
    "KC_BSLASH": "&kp BSLH",
    "KC_BSLS": "&kp BSLH",
    "KC_GRAVE": "&kp GRAVE",
    "KC_GRV": "&kp GRAVE",
    "KC_EXLM": "&kp EXCL",
    "KC_ASTR": "&kp STAR",
    "KC_TILD": "&kp TILDE",
    "KC_UNDS": "&kp UNDER",
    "KC_PIPE": "&kp PIPE",
    "KC_AT": "&kp AT",
    "KC_HASH": "&kp HASH",
    "KC_DLR": "&kp DLLR",
    "KC_LPRN": "&kp LPAR",
    "KC_RPRN": "&kp RPAR",
    "KC_LCBR": "&kp LBRC",
    "KC_RCBR": "&kp RBRC",
    "KC_PERC": "&kp PRCNT",
    "KC_CIRC": "&kp CARET",
    "KC_AMPR": "&kp AMPS",
    "KC_CAPSLOCK": "&kp CAPS",
    "KC_CAPS": "&kp CAPS",
    "KC_MPLY": "&kp C_PP",
    "KC_MUTE": "&kp C_MUTE",
    "KC_VOLU": "&kp C_VOL_UP",
    "KC_VOLD": "&kp C_VOL_DN",
    "KC_MNXT": "&kp C_NEXT",
    "KC_MPRV": "&kp C_PREV",
    "KC_WBAK": "&kp C_AC_BACK",
    "KC_WFWD": "&kp C_AC_FORWARD",
    "KC_BRIU": "&kp C_BRI_UP",
    "KC_BRID": "&kp C_BRI_DN",
    "KC_PMNS": "&kp KP_MINUS",
    "KC_PPLS": "&kp KP_PLUS",
    "KC_PAST": "&kp KP_MULTIPLY",
    "KC_PSLS": "&kp KP_DIVIDE",
    "KC_PDOT": "&kp KP_DOT",
    "KC_KP_ASTERISK": "&kp KP_MULTIPLY",
    "KC_KP_SLASH": "&kp KP_DIVIDE",
    "KC_KP_MINUS": "&kp KP_MINUS",
    "KC_KP_PLUS": "&kp KP_PLUS",
    "KC_KP_DOT": "&kp KP_DOT",
    "KC_BTN1": "&mkp LCLK",
    "KC_BTN2": "&mkp RCLK",
    "KC_BTN3": "&mkp MCLK",
    "KC_MS_U": "&mmv MOVE_UP",
    "KC_MS_D": "&mmv MOVE_DOWN",
    "KC_MS_L": "&mmv MOVE_LEFT",
    "KC_MS_R": "&mmv MOVE_RIGHT",
    "KC_WH_U": "&msc SCRL_UP",
    "KC_WH_D": "&msc SCRL_DOWN",
    "KC_WH_L": "&msc SCRL_LEFT",
    "KC_WH_R": "&msc SCRL_RIGHT",
    "FN_MO13": "&mo 1",
    "FN_MO23": "&mo 2",
    "QK_LAYER_LOCK": "&layer_lock_3",
    "QK_BOOT": "&bootloader",
    "USER00": "&cmdtab",
    "USER05": "&sc_btn 3 MCLK",
}

MOD_TAP = {
    "LCTL_T": "LCTRL",
    "LSFT_T": "LSHFT",
    "LALT_T": "LALT",
    "LGUI_T": "LGUI",
    "RCTL_T": "RCTRL",
    "RSFT_T": "RSHFT",
    "RALT_T": "RALT",
    "RGUI_T": "RGUI",
    "SGUI_T": "LS(LGUI)",
}

MODS = {
    "LCTL": "LC",
    "LSFT": "LS",
    "LALT": "LA",
    "LGUI": "LG",
    "RCTL": "RC",
    "RSFT": "RS",
    "RALT": "RA",
    "RGUI": "RG",
}

TAP_DANCES = {
    "TD(0)": "&space_arrows 2 0",
    "TD(2)": "&td_enter_equal",
    "TD(5)": "&td_slash_backslash",
    "TD(6)": "&td_key_ht ESC Q",
    "TD(7)": "&td_key_ht COMMA MINUS",
    "TD(8)": "&td_key_ht ESC F1",
    "TD(12)": "&layer_lock_2",
}

BASE_ENCODER_FALLBACK = None
REVERSE_ENCODERS = True
ENCODER_SCROLL_ARGS = {
    "SCRL_UP": "0x118",
    "SCRL_DOWN": "0xfee8",
    "SCRL_LEFT": "0xfee80000",
    "SCRL_RIGHT": "0x1180000",
}


def kp_arg(binding: str) -> str:
    if not binding.startswith("&kp "):
        raise ValueError(f"expected &kp binding, got {binding}")
    return binding.split(" ", 1)[1]


def mouse_arg(binding: str) -> str:
    if binding.startswith("&msc "):
        return binding.split(" ", 1)[1]
    if binding.startswith("&mkp "):
        return binding.split(" ", 1)[1]
    raise ValueError(f"expected mouse binding, got {binding}")


def convert_keycode(code: str | int) -> str:
    if code == -1:
        raise ValueError("non-key matrix slot should not be in layout order")
    if not isinstance(code, str):
        raise TypeError(f"unexpected keycode value: {code!r}")
    if code in TAP_DANCES:
        return TAP_DANCES[code]
    if code in KEY_ALIASES:
        return KEY_ALIASES[code]

    m = re.fullmatch(r"KC_(F\d{1,2})", code)
    if m:
        return f"&kp {m.group(1)}"

    m = re.fullmatch(r"LT(\d+)\((.+)\)", code)
    if m:
        return f"&lt_qmk {m.group(1)} {kp_arg(convert_keycode(m.group(2)))}"

    m = re.fullmatch(r"MO\((\d+)\)", code)
    if m:
        return f"&mo {m.group(1)}"

    m = re.fullmatch(r"TT\((\d+)\)", code)
    if m:
        return f"&mo {m.group(1)}"

    m = re.fullmatch(r"TO\((\d+)\)", code)
    if m:
        return f"&to {m.group(1)}"

    m = re.fullmatch(r"DF\((\d+)\)", code)
    if m:
        return f"&to {m.group(1)}"

    for fn, mod in MOD_TAP.items():
        m = re.fullmatch(rf"{fn}\((.+)\)", code)
        if m:
            return f"&mt_qmk {mod} {kp_arg(convert_keycode(m.group(1)))}"

    for qmk_mod, zmk_mod in MODS.items():
        m = re.fullmatch(rf"{qmk_mod}\((.+)\)", code)
        if m:
            return f"&kp {zmk_mod}({kp_arg(convert_keycode(m.group(1)))})"

    raise ValueError(f"unmapped keycode: {code}")


def encoder_code_to_binding(code: str) -> tuple[str, str]:
    if code == "KC_TRNS":
        return ("trans", "")

    stripped = code
    m = re.fullmatch(r"[LR]GUI\((KC_WH_[UDLR])\)", code)
    if m:
        stripped = m.group(1)

    binding = convert_keycode(stripped)
    if binding.startswith("&msc "):
        return ("&rot_msc", ENCODER_SCROLL_ARGS[mouse_arg(binding)])
    if binding.startswith("&mkp "):
        return ("&rot_mkp", mouse_arg(binding))
    return ("&inc_dec_kp", kp_arg(binding))


def format_encoder_bindings(vil: dict, index: int) -> str:
    global BASE_ENCODER_FALLBACK

    encoders = vil["encoder_layout"][index]
    encoder_parts = []
    for encoder_index, pair in enumerate(encoders):
        left_behavior, left_arg = encoder_code_to_binding(pair[0])
        right_behavior, right_arg = encoder_code_to_binding(pair[1])

        if index == 3 and encoder_index == 0:
            left_behavior, left_arg = ("&rot_msc", "0xfee8")
            right_behavior, right_arg = ("&rot_msc", "0x118")

        if left_behavior == "trans" and right_behavior == "trans":
            encoder_parts.append(BASE_ENCODER_FALLBACK[encoder_index])
            continue
        if left_behavior != right_behavior:
            raise ValueError(f"mixed encoder behavior on layer {index}: {pair}")
        if REVERSE_ENCODERS:
            left_arg, right_arg = right_arg, left_arg
        encoder_parts.append([left_behavior, left_arg, right_arg])

    if index == 0:
        BASE_ENCODER_FALLBACK = [binding[:] for binding in encoder_parts]

    return " ".join(part for binding in encoder_parts for part in binding)


def layer_bindings(layer: list[list[str | int]]) -> list[str]:
    return [convert_keycode(layer[row][col]) for row, col in QMK_LAYOUT_ORDER]


def format_layer(vil: dict, index: int, bindings: list[str]) -> str:
    name = [
        "base_layer",
        "lower_layer",
        "raise_layer",
        "num_layer",
        "delete_layer",
        "function_layer",
        "hex_layer",
        "mouse_layer",
    ][index]
    display_names = {
        0: "Base",
        2: "Arrows",
        3: "Numbers",
        4: "Misc",
        5: "Function",
        7: "Mouse",
    }
    if index == 2:
        bindings = [
            {
                "&msc SCRL_UP": "&cmd_scroll_up",
                "&msc SCRL_DOWN": "&cmd_scroll_down",
                "&msc SCRL_LEFT": "&cmd_scroll_left",
                "&msc SCRL_RIGHT": "&cmd_scroll_right",
            }.get(binding, binding)
            for binding in bindings
        ]
    rows = [
        bindings[0:10],
        bindings[10:20],
        bindings[20:30],
        bindings[30:38],
    ]
    out = [f"        {name} {{", "            bindings = <"]
    if index in display_names:
        out = [f"        {name} {{", f'            display-name = "{display_names[index]}";', "            bindings = <"]
    for row in rows:
        out.append("                " + "  ".join(f"{b:<16}" for b in row).rstrip())
    out += [
        "            >;",
        f"            sensor-bindings = <{format_encoder_bindings(vil, index)}>;",
        "        };",
    ]
    return "\n".join(out)


def render(vil: dict) -> str:
    global BASE_ENCODER_FALLBACK
    BASE_ENCODER_FALLBACK = None
    layers = [format_layer(vil, i, layer_bindings(layer)) for i, layer in enumerate(vil["layout"])]
    return """// Generated from /Users/talorbach/Library/CloudStorage/Dropbox/VIAL setups/a.vil
// by tools/vil_to_zmk.py.  Only tap dances referenced by the keymap are defined.

#include <behaviors.dtsi>
#include <dt-bindings/zmk/keys.h>
#include <dt-bindings/zmk/mouse.h>
#include <dt-bindings/zmk/bt.h>
#include <dt-bindings/zmk/outputs.h>
#include <dt-bindings/zmk/modifiers.h>

/ {
    behaviors {
        mt_qmk: qmk_mod_tap {
            compatible = "zmk,behavior-hold-tap";
            #binding-cells = <2>;
            display-name = "QMK Mod-Tap";
            flavor = "balanced";
            tapping-term-ms = <175>;
            quick-tap-ms = <120>;
            bindings = <&kp>, <&kp>;
        };

        lt_qmk: qmk_layer_tap {
            compatible = "zmk,behavior-hold-tap";
            #binding-cells = <2>;
            display-name = "QMK Layer-Tap";
            flavor = "balanced";
            tapping-term-ms = <175>;
            quick-tap-ms = <120>;
            bindings = <&mo>, <&kp>;
        };

        td_key_ht: tap_dance_key_hold {
            compatible = "zmk,behavior-hold-tap";
            #binding-cells = <2>;
            display-name = "Tap Dance Key Hold";
            flavor = "balanced";
            tapping-term-ms = <200>;
            quick-tap-ms = <120>;
            bindings = <&kp>, <&kp>;
        };

        cmdtab_ht: cmd_tab_hold_tap {
            compatible = "zmk,behavior-hold-tap";
            #binding-cells = <2>;
            display-name = "Cmd-Tab Hold-Tap";
            flavor = "balanced";
            tapping-term-ms = <175>;
            quick-tap-ms = <120>;
            bindings = <&mo>, <&kp>;
        };

        cmdtab: cmd_tab_mod_morph {
            compatible = "zmk,behavior-mod-morph";
            #binding-cells = <0>;
            display-name = "Cmd-Tab";
            bindings = <&cmdtab_ht 3 SPACE>, <&kp TAB>;
            mods = <(MOD_LGUI | MOD_RGUI)>;
            keep-mods = <(MOD_LGUI | MOD_RGUI)>;
        };

        sc_btn: scroll_layer_mouse_button {
            compatible = "zmk,behavior-hold-tap";
            #binding-cells = <2>;
            display-name = "Scroll Layer Mouse Button";
            flavor = "balanced";
            tapping-term-ms = <175>;
            quick-tap-ms = <120>;
            bindings = <&mo>, <&mkp>;
        };

        rot_msc: sensor_rotate_scroll {
            compatible = "zmk,behavior-sensor-rotate-var";
            #sensor-binding-cells = <2>;
            bindings = <&msc>, <&msc>;
            tap-ms = <20>;
        };

        rot_mkp: sensor_rotate_mouse_button {
            compatible = "zmk,behavior-sensor-rotate-var";
            #sensor-binding-cells = <2>;
            bindings = <&mkp>, <&mkp>;
            tap-ms = <20>;
        };

        space_arrows: space_arrows_hold_tap {
            compatible = "zmk,behavior-hold-tap";
            #binding-cells = <2>;
            display-name = "Space / Arrows";
            flavor = "balanced";
            tapping-term-ms = <175>;
            quick-tap-ms = <120>;
            bindings = <&mo>, <&td_space_dotspace>;
        };

        td_space_dotspace: tap_dance_space_dotspace {
            compatible = "zmk,behavior-tap-dance";
            #binding-cells = <0>;
            display-name = "Space / Dot-Space";
            tapping-term-ms = <250>;
            bindings = <&kp SPACE>, <&m0>;
        };

        td_enter_equal: tap_dance_enter_equal {
            compatible = "zmk,behavior-tap-dance";
            #binding-cells = <0>;
            display-name = "Enter / Equal";
            tapping-term-ms = <200>;
            bindings = <&kp ENTER>, <&kp EQUAL>;
        };

        td_slash_backslash: tap_dance_slash_backslash {
            compatible = "zmk,behavior-tap-dance";
            #binding-cells = <0>;
            display-name = "Slash / Backslash";
            tapping-term-ms = <250>;
            bindings = <&kp FSLH>, <&kp BSLH>;
        };
    };

    combos {
        compatible = "zmk,combos";

        combo_tab {
            timeout-ms = <50>;
            layers = <0>;
            key-positions = <2 3>;
            bindings = <&kp TAB>;
        };

        combo_middle_click {
            timeout-ms = <50>;
            layers = <7>;
            key-positions = <34 36>;
            bindings = <&mkp MCLK>;
        };
    };

    macros {
        m0: macro_0 {
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            display-name = "Dot Space";
            bindings = <&kp KP_DOT>, <&kp SPACE>;
        };

        layer_lock_2: layer_lock_2 {
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            display-name = "Lock Arrows";
            bindings = <&macro_pause_for_release>, <&to 2>;
        };

        layer_lock_3: layer_lock_3 {
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            display-name = "Lock Numbers";
            bindings = <&macro_pause_for_release>, <&to 3>;
        };

        cmd_scroll_up: cmd_scroll_up {
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            display-name = "Cmd Scroll Up";
            bindings = <&macro_press &kp LGUI &msc SCRL_UP>, <&macro_pause_for_release>, <&macro_release &msc SCRL_UP &kp LGUI>;
        };

        cmd_scroll_down: cmd_scroll_down {
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            display-name = "Cmd Scroll Down";
            bindings = <&macro_press &kp LGUI &msc SCRL_DOWN>, <&macro_pause_for_release>, <&macro_release &msc SCRL_DOWN &kp LGUI>;
        };

        cmd_scroll_left: cmd_scroll_left {
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            display-name = "Cmd Scroll Left";
            bindings = <&macro_press &kp LGUI &msc SCRL_LEFT>, <&macro_pause_for_release>, <&macro_release &msc SCRL_LEFT &kp LGUI>;
        };

        cmd_scroll_right: cmd_scroll_right {
            compatible = "zmk,behavior-macro";
            #binding-cells = <0>;
            display-name = "Cmd Scroll Right";
            bindings = <&macro_press &kp LGUI &msc SCRL_RIGHT>, <&macro_pause_for_release>, <&macro_release &msc SCRL_RIGHT &kp LGUI>;
        };
    };

    keymap {
        compatible = "zmk,keymap";
""" + "\n\n".join(layers) + """
    };
};
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("vil", type=Path)
    parser.add_argument("--output", "-o", type=Path, required=True)
    args = parser.parse_args()
    with args.vil.open() as f:
        vil = json.load(f)
    args.output.write_text(render(vil))


if __name__ == "__main__":
    main()
