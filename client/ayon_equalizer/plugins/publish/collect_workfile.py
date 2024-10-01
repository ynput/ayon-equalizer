"""Collect camera data from the scene."""
from typing import ClassVar

import pyblish.api
import tde4


class CollectWorkfile(pyblish.api.ContextPlugin):
    """Collect camera data from the scene."""

    order = pyblish.api.CollectorOrder
    hosts: ClassVar[list] = ["equalizer"]
    label = "Collect Workfile"

    def process(self, context: pyblish.api.Context) -> None:
        """Collect 3DE project as a workfile."""
        context.data["currentFile"] = tde4.getProjectPath()
