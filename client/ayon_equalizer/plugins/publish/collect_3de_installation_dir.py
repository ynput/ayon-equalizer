"""Collect camera data from the scene."""
from pathlib import Path
from typing import ClassVar

import pyblish.api
import tde4


class Collect3DE4InstallationDir(pyblish.api.ContextPlugin):
    """Collect camera data from the scene."""

    order = pyblish.api.CollectorOrder
    hosts: ClassVar[list] = ["equalizer"]
    label = "Collect 3Dequalizer directory"

    def process(self, context: pyblish.api.Context) -> None:
        """Collect installation directory."""
        tde4_path = Path(tde4.get3DEInstallPath())
        context.data["tde4_path"] = tde4_path
