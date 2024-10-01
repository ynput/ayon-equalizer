"""Validate Camera Point Group."""
import pyblish.api
import tde4
from ayon_core.pipeline.publish import (
    PublishValidationError,
    ValidateContentsOrder,
)


class ValidateCameraPoingroup(pyblish.api.InstancePlugin):
    """Validate Camera Point Group.

    There must be a camera point group in the scene.
    """

    order = ValidateContentsOrder
    hosts = ["equalizer"]
    families = ["matchmove"]
    label = "Validate Camera Point Group"

    def process(self, _: pyblish.api.Instance):
        """Process the validation."""
        valid = any(
            tde4.getPGroupType(point_group) == "CAMERA"
            for point_group in tde4.getPGroupList()
        )
        if not valid:
            raise PublishValidationError("Missing Camera Point Group")
