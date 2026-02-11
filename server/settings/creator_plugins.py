"""Creator settings."""
from ayon_server.settings import BaseSettingsModel, SettingsField


class CreateMatchMoveModel(BaseSettingsModel):
    """Matchmove creator settings."""

    enabled: bool = SettingsField(default=True, title="Enabled")
    default_variants: list[str] = SettingsField(
        default_factory=list,
        title="Default Variants"
    )


class EqualizerCreatorPlugins(BaseSettingsModel):
    """Creator plugins settings."""

    CreateMatchMove: CreateMatchMoveModel = SettingsField(
        default_factory=CreateMatchMoveModel,
        title="Create Match Move data"
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
