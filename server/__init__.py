from typing import Type

from ayon_server.addons import BaseServerAddon


from .settings import EqualizerSettings


class EqualizerAddon(BaseServerAddon):
    name = "equalizer"
    title = "3DEqualizer"

    settings_model: Type[EqualizerSettings] = EqualizerSettings
