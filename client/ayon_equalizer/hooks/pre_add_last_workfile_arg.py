"""Add last workfile path to launch arguments."""
from __future__ import annotations

import os
from typing import ClassVar

from ayon_applications import LaunchTypes, PreLaunchHook


class AddLast3DEWorkfileToLaunchArgs(PreLaunchHook):
    """Add last workfile path to launch arguments.

    Copied from ayon_core/hooks/pre_add_last_workfile_arg.py.
    Checks 'start_last_workfile', if set to False, it will not open last
    workfile. This property is set explicitly in Launcher.
    """

    # Execute after workfile template copy
    order = 10
    app_groups: ClassVar[set[str]] = {"equalizer"}
    launch_types: ClassVar[set[str]] = {LaunchTypes.local}

    def execute(self) -> None:
        """Execute the hook."""
        workfile_path = self.get_workfile_path()
        # Add path to workfile to arguments
        if workfile_path:
            self.launch_context.launch_args.extend(["-open", workfile_path])

    def get_workfile_path(self) -> str | None:
        """Get path to workfile on launch.

        Returns:
            str | None: Path to workfile on launch.

        """
        workfile_path = self.data.get("workfile_path")
        if workfile_path:
            return workfile_path

        if not self.data.get("start_last_workfile"):
            self.log.info("It is set to not start last workfile on start.")
            return None

        last_workfile = self.data.get("last_workfile_path")
        if not last_workfile:
            self.log.warning("Last workfile was not collected.")
            return None

        if not os.path.exists(last_workfile):
            self.log.info("Current context does not have any workfile yet.")
            return None
        return last_workfile
