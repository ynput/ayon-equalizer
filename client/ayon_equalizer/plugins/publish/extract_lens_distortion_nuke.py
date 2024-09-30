from pathlib import Path
from unittest.mock import patch

import pyblish.api
import tde4  # noqa: F401
from ayon_core.lib import EnumDef, import_filepath
from ayon_core.pipeline import OptionalPyblishPluginMixin, publish


class ExtractLensDistortionNuke(publish.Extractor,
                                OptionalPyblishPluginMixin):
    """Extract Nuke Lens Distortion data.

    Unfortunately built-in export script from 3DEqualizer is bound to its UI,
    and it is not possible to call it directly from Python. Because of that,
    we are executing the script in the same way as artist would do it, but
    we are patching the UI to silence it and to avoid any user interaction.

    TODO: Utilize attributes defined in ExtractScriptBase
    """

    label = "Extract Lens Distortion Nuke node"
    families = ["lensDistortion"]
    hosts = ["equalizer"]

    order = pyblish.api.ExtractorOrder

    def process(self, instance: pyblish.api.Instance):
        """Extract Nuke Lens Distortion script from 3DEqualizer."""
        if not self.is_active(instance.data):
            return

        cam = tde4.getCurrentCamera()
        offset = tde4.getCameraFrameOffset(cam)
        staging_dir = self.staging_dir(instance)
        file_path = Path(staging_dir) / "nuke_ld_export.nk"
        attr_data = self.get_attr_values_from_data(instance.data)

        # these patched methods are used to silence 3DEqualizer UI:
        def patched_getWidgetValue(_, key: str) -> str:    # noqa: N802, ANN001
            """Return value for given key in widget."""
            return attr_data["fovMode"] if key == "option_menu_fov_mode" else ""  # noqa: E501

        # import export script from 3DEqualizer
        exporter_path = instance.context.data["tde4_path"] / "sys_data" / "py_scripts" / "export_nuke_LD_3DE4_Lens_Distortion_Node.py"  # noqa: E501
        self.log.debug(f"Importing {exporter_path.as_posix()}")
        exporter = import_filepath(exporter_path.as_posix())
        with patch("tde4.getWidgetValue", patched_getWidgetValue):
                exporter.exportNukeDewarpNode(cam, offset, file_path.as_posix())

        # create representation data
        if "representations" not in instance.data:
            instance.data["representations"] = []

        representation = {
            "name": "lensDistortion",
            "ext": "nk",
            "files": file_path.name,
            "stagingDir": staging_dir,
        }
        self.log.debug(f"output: {file_path.as_posix()}")
        instance.data["representations"].append(representation)

    @classmethod
    def get_attribute_defs(cls):
        return [
            *super().get_attribute_defs(),
            EnumDef("fovMode",
                    label="FOV Mode",
                    items=[
                        {"value": "1", "label": "legacy"},
                        {"value": "2", "label": "new (v8+)"}],
                    tooltip="FOV mode (legacy or new)",
                    default="legacy"),
        ]
