"""Settings for the 3DEqualizer Addon."""
from ayon_server.settings import BaseSettingsModel, SettingsField

from .creator_plugins import EqualizerCreatorPlugins


class EqualizerSettings(BaseSettingsModel):
    """3DEqualizer Addon Settings."""

    heartbeat_interval: int = SettingsField(
        100, title="Heartbeat Interval",
        description=(
            "The interval in milliseconds to pass"
            "control to Qt UI. Value like 100 means it will be "
            "passed every 10x per second. Recommended value is 100 - 50 "
            "(20x per second).")
        )

    create: EqualizerCreatorPlugins = SettingsField(
        default_factory=EqualizerCreatorPlugins,
        title="Creator plugins"
    )
