from ayon_server.settings import BaseSettingsModel, SettingsField

from .creator_plugins import (
    EqualizerCreatorPlugins,
)


class EqualizerSettings(BaseSettingsModel):
    """3DEqualizer Addon Settings."""

    heartbeat_interval: int = SettingsField(
        500, title="Heartbeat Interval",
        description=(
            "The interval in milliseconds to pass"
            "control to 3D Equalizer. Can affect"
            "responsiveness of the application.")
        )

    create: EqualizerCreatorPlugins = SettingsField(
        default_factory=EqualizerCreatorPlugins,
        title="Creator plugins"
    )
    