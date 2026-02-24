"""Creator settings."""
from ayon_server.settings import BaseSettingsModel, SettingsField


class ProductTypeItemModel(BaseSettingsModel):
    """Product type item for creator plugins."""

    _layout = "compact"
    product_type: str = SettingsField(
        title="Product type",
        description="Product type name",
    )
    label: str = SettingsField(
        "",
        title="Label",
        description="Label to display in UI for the product type",
    )


class CreateMatchMoveModel(BaseSettingsModel):
    """Matchmove creator settings."""

    enabled: bool = SettingsField(default=True, title="Enabled")
    default_variants: list[str] = SettingsField(
        default_factory=list,
        title="Default Variants"
    )
    product_type_items: list[ProductTypeItemModel] = SettingsField(
        default_factory=list,
        title="Product type items",
        description=(
            "Optional list of product types that this plugin can create."
        )
    )


class CreateLensDistortionModel(BaseSettingsModel):
    """Lens distortion creator settings."""

    product_type_items: list[ProductTypeItemModel] = SettingsField(
        default_factory=list,
        title="Product type items",
        description=(
            "Optional list of product types that this plugin can create."
        )
    )


class EqualizerCreatorPlugins(BaseSettingsModel):
    """Creator plugins settings."""

    CreateMatchMove: CreateMatchMoveModel = SettingsField(
        default_factory=CreateMatchMoveModel,
        title="Create Match Move data"
    )
    CreateLensDistortionData: CreateLensDistortionModel = SettingsField(
        default_factory=CreateLensDistortionModel,
        title="Create Lens Distortion data",
    )


DEFAULT_EQUALIZER_CREATE_SETTINGS = {
    "CreateMatchMove": {
        "default_variants": [
            "CameraTrack",
            "ObjectTrack",
            "PointTrack",
            "Stabilize",
            "SurveyTrack",
            "UserTrack",
        ],
    }
}
