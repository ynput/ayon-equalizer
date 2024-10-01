"""Collect camera data from the scene."""
import re
from typing import NamedTuple

import pyblish.api
import tde4


class Version(NamedTuple):
    """3DEqualizer version."""

    major: int
    minor: int


class Collect3DE4Version(pyblish.api.ContextPlugin):
    """Collect camera data from the scene."""

    order = pyblish.api.CollectorOrder
    hosts = ("equalizer")
    label = "Collect 3Dequalizer version"

    def process(self, context: pyblish.api.Context) -> None:
        """Collect 3DEqualizer version."""
        match = re.search(
            r"3DEqualizer4 Release (?P<major>\d+).(?P<minor>\d+)",
            tde4.get3DEVersion())
        if not match["major"] or not match["minor"]:
            error_msg = "Failed to extract 3DEqualizer version"
            raise ValueError(error_msg)

        version = Version(
            major=int(match["major"]),
            minor=int(match["minor"]))

        context.data["tde4_version"] = version
