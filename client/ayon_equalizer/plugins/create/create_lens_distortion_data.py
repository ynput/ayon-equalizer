"""Create lens distortion data."""
from ayon_equalizer.api import EqualizerCreator


class CreateLensDistortionData(EqualizerCreator):
    """Create lens distortion data."""

    identifier = "io.ayon.creators.equalizer.lens_distortion"
    label = "Lens Distortion"
    product_type = "lensDistortion"
    icon = "glasses"

    def create(
            self, product_name: str,
            instance_data: dict, pre_create_data: dict):
        """Create lens distortion data."""
        super().create(product_name, instance_data, pre_create_data)
