"""3DEqualizer server addon."""
from ayon_server.addons import BaseServerAddon

from .settings import EqualizerSettings, DEFAULT_EQUALIZER_SETTINGS


class EqualizerAddon(BaseServerAddon):
    """3DEqualizer server addon."""

    name = "equalizer"
    title = "3DEqualizer"

    settings_model: EqualizerSettings = EqualizerSettings

    async def get_default_settings(self):
        settings_model_cls = self.get_settings_model()
        return settings_model_cls(**DEFAULT_EQUALIZER_SETTINGS)
