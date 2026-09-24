"""Extract project for Houdini."""

from pathlib import Path
from typing import ClassVar

import pyblish.api
import tde4
from ayon_core.lib import import_filepath
from ayon_core.pipeline import (
    KnownPublishError,
    OptionalPyblishPluginMixin,
    publish,
)

from ayon_equalizer.api import ExtractScriptBaseHoudini

EQUALIZER_7 = 7
EQUALIZER_8 = 8


class ExtractMatchmoveScriptHoudini(
    publish.Extractor, ExtractScriptBaseHoudini, OptionalPyblishPluginMixin
):
    """Extract Houdini python script for matchmove.

    This is using a modified version of the built-in export script
    from 3DEqualizer.
    """

    label = "Extract Houdini Script"
    families: ClassVar[list] = ["matchmove"]
    hosts: ClassVar[list] = ["equalizer"]
    optional = True

    order = pyblish.api.ExtractorOrder

    def process(self, instance: pyblish.api.Instance) -> None:
        """Extract Houdini script from 3DEqualizer.

        This method is using export script shipped with 3DEqualizer to
        maintain as much compatibility as possible. Instead of invoking it
        from the UI, it calls directly the function that is doing the export.
        For that it needs to pass some data that are collected in 3dequalizer
        from the UI, so we need to determine them from the instance itself and
        from the state of the project.

        """
        if not self.is_active(instance.data):
            return
        attr_data = self.get_attr_values_from_data(instance.data)
        self.log.debug(f"attr_data: {attr_data}")

        # import custom houdini export script from Ayon-Equalizer
        exporter_path = (
            Path(__file__).resolve().parent.parent.parent
            / "py_scripts"
            / "export_houdini.py"
        )
        self.log.debug("Importing %s", exporter_path.as_posix())
        exporter = import_filepath(exporter_path.as_posix())

        # get camera point group
        _point_group = None
        point_groups = tde4.getPGroupList()
        for pg in point_groups:
            if tde4.getPGroupType(pg) == "CAMERA":
                _point_group = pg
                break
        else:
            # this should never happen as it should be handled by validator
            error_msg = "No camera point group found."
            raise KnownPublishError(error_msg)

        cam = tde4.getCurrentCamera()
        start = 1001
        end = 1100
        step = 1
        if cam:
            start, end, step = tde4.getCameraSequenceAttr(cam)
        else:
            error_msg = "No camera found."
            raise KnownPublishError(error_msg)

        overscan_width = attr_data["overscan_percent_width"] / 100.0
        overscan_height = attr_data["overscan_percent_height"] / 100.0

        staging_dir = self.staging_dir(instance)

        unit_scales = {
            "mm": 10.0,  # cm -> mm
            "cm": 1.0,  # cm -> cm
            "m": 0.01,  # cm -> m
            "in": 0.393701,  # cm -> in
            "ft": 0.0328084,  # cm -> ft
            "yd": 0.0109361,  # cm -> yd
        }
        scale_factor = unit_scales[attr_data["units"]]

        file_path = Path(staging_dir) / "houdini_export"
        if instance.context.data.get("tde4_version"):
            self.log.debug("Exporting to: %s", file_path.as_posix())

        # create representation data
        if "representations" not in instance.data:
            instance.data["representations"] = []

        export_path = f"{file_path.as_posix()}.py"

        status = exporter.export_py_file(
            path=export_path,
            startframe=start,
            scale_factor=scale_factor,
            overscan_width=overscan_width,
            overscan_height=overscan_height,
        )
        representation = {
            "name": "py_houdini",
            "ext": "py",
            "files": f"{file_path.name}.py",
            "stagingDir": staging_dir,
        }

        if status != 1:
            # for EM102
            err_msg = f"Export failed {status}"
            raise KnownPublishError(err_msg)

        self.log.debug("output: %s", file_path.as_posix())
        instance.data["representations"].append(representation)
