"""Create lens distortion data."""
from ayon_equalizer.api import EqualizerCreator


class CreateLensDistortionData(EqualizerCreator):
    """Create lens distortion data."""

    identifier = "io.ayon.creators.equalizer.lens_distortion"
    label = "Lens Distortion"
    product_type = "lensDistortion"
    product_base_type = "lensDistortion"
    icon = "glasses"
