"""3DEqualizer server addon."""
from ayon_server.addons import BaseServerAddon

from .settings import (
    DEFAULT_EQUALIZER_SETTINGS,
    EqualizerSettings,
)


class EqualizerAddon(BaseServerAddon):
    """3DEqualizer server addon."""

    name = "equalizer"
    title = "3DEqualizer"

    settings_model: type[EqualizerSettings] = EqualizerSettings

    async def get_default_settings(self) -> EqualizerSettings:
        """Get default settings for the addon.

        Returns:
            EqualizerSettings: Default settings for the addon.

        """
        settings_model_cls = self.get_settings_model()
        return settings_model_cls(**DEFAULT_EQUALIZER_SETTINGS)
