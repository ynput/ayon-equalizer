import os
from ayon_core.addon import AYONAddon, IHostAddon
from .version import __version__


EQUALIZER_HOST_DIR = os.path.dirname(os.path.abspath(__file__))


class EqualizerAddon(AYONAddon, IHostAddon):
    name = "equalizer"
    host_name = "equalizer"
    heartbeat = 500
    version = __version__

    def initialize(self, settings):
        self.heartbeat = settings.get("heartbeat_interval", 500)
        self.enabled = True

    def add_implementation_envs(self, env, _app):
        # 3dEqualizer utilize TDE4_ROOT for its root directory
        # and PYTHON_CUSTOM_SCRIPTS_3DE4 as a colon separated list of
        # directories to look for additional python scripts.
        # (Windows: list is separated by semicolons).
        # Ad

        startup_path = os.path.join(EQUALIZER_HOST_DIR, "startup")
        if "PYTHON_CUSTOM_SCRIPTS_3DE4" in env:
            startup_path = os.path.join(
                env["PYTHON_CUSTOM_SCRIPTS_3DE4"],
                startup_path)

        env["PYTHON_CUSTOM_SCRIPTS_3DE4"] = startup_path
        env["AYON_TDE4_HEARTBEAT_INTERVAL"] = str(self.heartbeat)

    def get_launch_hook_paths(self, app):
        if app.host_name != self.host_name:
            return []
        return [
            os.path.join(EQUALIZER_HOST_DIR, "hooks")
        ]

    def get_workfile_extensions(self):
        return [".3de"]
