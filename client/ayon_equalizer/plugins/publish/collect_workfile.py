"""Collect camera data from the scene."""
import pyblish.api
import tde4


class CollectWorkfile(pyblish.api.ContextPlugin):
    """Collect camera data from the scene."""

    order = pyblish.api.CollectorOrder
    hosts = ["equalizer"]
    label = "Collect Workfile"

    def process(self, context: pyblish.api.Context):

        context.data["currentFile"] = tde4.getProjectPath()
