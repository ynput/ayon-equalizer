"""Tests for Equalizer addon environment handling."""

from __future__ import annotations

import importlib
import os
import sys
import types
from pathlib import Path


def _import_addon_module():
    client_path = Path(__file__).resolve().parents[1] / "client"
    if str(client_path) not in sys.path:
        sys.path.insert(0, str(client_path))

    ayon_core_module = types.ModuleType("ayon_core")
    addon_module = types.ModuleType("ayon_core.addon")
    addon_module.AYONAddon = type("AYONAddon", (), {})
    addon_module.IHostAddon = type("IHostAddon", (), {})
    ayon_core_module.addon = addon_module

    sys.modules["ayon_core"] = ayon_core_module
    sys.modules["ayon_core.addon"] = addon_module

    return importlib.import_module("ayon_equalizer.addon")


def _create_addon(addon_module):
    addon = addon_module.EqualizerAddon.__new__(addon_module.EqualizerAddon)
    addon.heartbeat = 100
    return addon


def test_add_implementation_envs_sets_startup_path_when_missing():
    addon_module = _import_addon_module()
    addon = _create_addon(addon_module)
    env = {}

    addon.add_implementation_envs(env, None)

    expected_startup_path = os.path.join(
        addon_module.EQUALIZER_HOST_DIR,
        "startup",
    )
    assert env["PYTHON_CUSTOM_SCRIPTS_3DE4"] == expected_startup_path
    assert env["AYON_TDE4_HEARTBEAT_INTERVAL"] == "100"


def test_add_implementation_envs_appends_startup_path_to_existing_value():
    addon_module = _import_addon_module()
    addon = _create_addon(addon_module)
    existing_path = os.path.join(os.sep, "custom", "scripts")
    env = {"PYTHON_CUSTOM_SCRIPTS_3DE4": existing_path}

    addon.add_implementation_envs(env, None)

    expected_startup_path = os.path.join(
        addon_module.EQUALIZER_HOST_DIR,
        "startup",
    )
    assert env["PYTHON_CUSTOM_SCRIPTS_3DE4"] == os.pathsep.join(
        (existing_path, expected_startup_path)
    )
