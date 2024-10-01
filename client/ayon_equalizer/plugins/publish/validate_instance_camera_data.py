"""Plugin to validate if instance has camera data."""
from typing import ClassVar

import pyblish.api
from ayon_core.pipeline import PublishValidationError
from ayon_core.pipeline.publish import ValidateContentsOrder


class ValidateInstanceCameraData(pyblish.api.InstancePlugin):
    """Check if instance has camera data.

    There might not be any camera associated with the instance
    and without it, the instance is not valid.
    """

    order = ValidateContentsOrder
    hosts: ClassVar[list] = ["equalizer"]
    families: ClassVar[list] = ["matchmove"]
    label = "Validate Instance has Camera data"

    def process(self, instance: pyblish.api.Instance) -> None:
        """Process the validation."""
        try:
            _ = instance.data["cameras"]
        except KeyError as e:
            error_msg = "No camera data found"
            raise PublishValidationError(error_msg) from e
