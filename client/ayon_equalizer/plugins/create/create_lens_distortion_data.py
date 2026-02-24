"""Create lens distortion data."""
from ayon_equalizer.api import EqualizerCreator


class CreateLensDistortionData(EqualizerCreator):
    """Create lens distortion data."""

    identifier = "io.ayon.creators.equalizer.lens_distortion"
    label = "Lens Distortion"
    product_base_type = "lensDistortion"
    product_type = product_base_type
    icon = "glasses"
