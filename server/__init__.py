"""3DEqualizer server addon."""
from ayon_server.addons import BaseServerAddon

from .settings import EqualizerSettings


class EqualizerAddon(BaseServerAddon):
    """3DEqualizer server addon."""

    name = "equalizer"
    title = "3DEqualizer"

    settings_model: EqualizerSettings = EqualizerSettings
