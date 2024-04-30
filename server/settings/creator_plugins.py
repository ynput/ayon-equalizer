from ayon_server.settings import BaseSettingsModel, SettingsField


class CreateMatchMoveModel(BaseSettingsModel):
    enabled: bool = SettingsField(True, title="Enabled")
    default_variants: list[str] = SettingsField(
        [
            "CameraTrack",
            "ObjectTrack",
            "PointTrack",
            "Stabilize",
            "SurveyTrack",
            "UserTrack",
        ], title="Default Variants")
    

class EqualizerCreatorPlugins(BaseSettingsModel):
    CreateMatchMove: CreateMatchMoveModel = SettingsField(
        default_factory=CreateMatchMoveModel,
        title="Create Match Move data"
    )


