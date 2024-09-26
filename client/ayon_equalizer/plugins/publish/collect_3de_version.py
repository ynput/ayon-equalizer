"""Collect camera data from the scene."""
import re
from collections import namedtuple

import pyblish.api
import tde4


class Collect3DE4Version(pyblish.api.ContextPlugin):
    """Collect camera data from the scene."""

    order = pyblish.api.CollectorOrder
    hosts = ["equalizer"]
    label = "Collect 3Dequalizer version"

    def process(self, context):
        match = re.search(
            r"3DEqualizer4 Release (?P<major>\d+).(?P<minor>\d+)",
            tde4.get3DEVersion())
        if not match["major"] or not match["minor"]:
            raise ValueError("Failed to extract 3DEqualizer version")

        version = namedtuple("Version", ["major", "minor"])
        version.major = int(match["major"])
        version.minor = int(match["minor"])
        context.data["tde4_version"] = version
