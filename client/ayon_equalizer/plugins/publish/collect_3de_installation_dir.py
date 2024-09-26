"""Collect camera data from the scene."""
import pyblish.api
import tde4
from pathlib import Path


class Collect3DE4InstallationDir(pyblish.api.ContextPlugin):
    """Collect camera data from the scene."""

    order = pyblish.api.CollectorOrder
    hosts = ["equalizer"]
    label = "Collect 3Dequalizer directory"

    def process(self, context):
        tde4_path = Path(tde4.get3DEInstallPath())
        context.data["tde4_path"] = tde4_path
