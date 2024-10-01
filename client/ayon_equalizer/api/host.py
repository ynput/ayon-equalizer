"""3dequalizer host implementation.

Note:
    3dequalizer 7.1v2 uses Python 3.7.9
    3dequalizer 8.0 uses Python 3.9.x

"""
from __future__ import annotations

import dataclasses
import json
import os
import re
from typing import Optional, Union

import pyblish.api
import tde4
from ayon_core.host import HostBase, ILoadHost, IPublishHost, IWorkfileHost
from ayon_core.pipeline import (
    register_creator_plugin_path,
    register_loader_plugin_path,
)
from qtpy import QtCore, QtWidgets

from ayon_equalizer import EQUALIZER_HOST_DIR
from ayon_equalizer.api.pipeline import Container

CONTEXT_REGEX = re.compile(
    r"AYON_CONTEXT::(?P<context>.*?)::AYON_CONTEXT_END",
    re.DOTALL)
PLUGINS_DIR = os.path.join(EQUALIZER_HOST_DIR, "plugins")
PUBLISH_PATH = os.path.join(PLUGINS_DIR, "publish")
LOAD_PATH = os.path.join(PLUGINS_DIR, "load")
CREATE_PATH = os.path.join(PLUGINS_DIR, "create")
INVENTORY_PATH = os.path.join(PLUGINS_DIR, "inventory")


class DataclassJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for dataclasses."""

    def default(self, obj: object) -> Union[dict, object]:
        """Encode dataclasses as dict."""
        if dataclasses.is_dataclass(obj):
            # type: obj: dataclasses.dataclass
            return dataclasses.asdict(obj)
        return super().default(obj)


class EqualizerHost(HostBase, IWorkfileHost, ILoadHost, IPublishHost):
    """3DEqualizer host implementation."""

    name = "equalizer"
    _instance = None

    def __new__(cls):
        """Singleton implementation."""
        # singleton - ensure only one instance of the host is created.
        # This is necessary because 3DEqualizer doesn't have a way to
        # store custom data, so we need to store it in the project notes.
        if not hasattr(cls, "_instance") or not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the host."""
        self._qapp = None
        super().__init__()

    def workfile_has_unsaved_changes(self) -> bool:
        """Return the state of the current workfile.

        3DEqualizer returns state as 1 or zero, so we need to invert it.

        Returns:
            bool: True if the current workfile has unsaved changes.

        """
        return not bool(tde4.isProjectUpToDate())

    def get_workfile_extensions(self) -> list[str]:
        """Return the workfile extensions for 3DEqualizer."""
        return [".3de"]

    def save_workfile(self, dst_path: Optional[str]=None) -> str:
        """Save the current workfile.

        Arguments:
            dst_path (str): Destination path to save the workfile.

        """
        if not dst_path:
            dst_path = tde4.getProjectPath()
        result = tde4.saveProject(dst_path, True)  # noqa: FBT003
        if not bool(result):
            err_msg = f"Failed to save workfile {dst_path}."
            raise RuntimeError(err_msg)

        return dst_path

    def open_workfile(self, filepath: str) -> str:
        """Open a workfile in 3DEqualizer."""
        result = tde4.loadProject(filepath, True)  # noqa: FBT003
        if not bool(result):
            err_msg = f"Failed to open workfile {filepath}."
            raise RuntimeError(err_msg)

        return filepath

    def get_current_workfile(self) -> str:
        """Return the current workfile path."""
        return tde4.getProjectPath()

    def get_containers(self) ->list[Container]:
        """Get containers from the current workfile."""
        context = self.get_context_data()
        if context:
            for container in context.get("containers", []):
                yield Container(**container)
        return []

    def add_container(self, container: Container) -> None:
        """Add a container to the current workfile.

        Args:
            container (Container): Container to add.

        """
        context_data = self.get_context_data()
        containers = self.get_containers()
        to_remove = [
            idx
            for idx, _container in enumerate(containers)
            if _container.name == container.name
            and _container.namespace == container.namespace
        ]
        for idx in reversed(to_remove):
            containers.pop(idx)

        context_data["containers"] = [*containers, container]

        self.update_context_data(context_data, {})

    def get_context_data(self) -> dict:
        """Get context data from the current workfile.

        3Dequalizer doesn't have any custom node or other
        place to store metadata, so we store context data in
        the project notes encoded as JSON and wrapped in a
        special guard string `AYON_CONTEXT::...::AYON_CONTEXT_END`.

        Returns:
            dict: Context data.

        """
        # sourcery skip: use-named-expression
        m = re.search(CONTEXT_REGEX, tde4.getProjectNotes())
        try:
            context = json.loads(m["context"]) if m else {}
        except ValueError:
            self.log.debug("context data is not valid json")
            context = {}

        return context

    def update_context_data(self, data: dict, _changes: dict) -> None:
        """Update context data in the current workfile.

        Serialize context data as json and store it in the
        project notes. If the context data is not found, create
        a placeholder there. See `get_context_data` for more info.

        Args:
            data (dict): Context data.
            _changes (dict): Changes to the context data.

        Raises:
            RuntimeError: If the context data is not found.

        """
        notes = tde4.getProjectNotes()
        m = re.search(CONTEXT_REGEX, notes)
        if not m:
            # context data not found, create empty placeholder
            tde4.setProjectNotes(
                f"{tde4.getProjectNotes()}\n"
                f"AYON_CONTEXT::::AYON_CONTEXT_END\n")

        original_data = self.get_context_data()

        updated_data = original_data.copy()
        updated_data.update(data)
        update_str = json.dumps(
            updated_data or {}, indent=4, cls=DataclassJSONEncoder)

        tde4.setProjectNotes(
            re.sub(
                CONTEXT_REGEX,
                f"AYON_CONTEXT::{update_str}::AYON_CONTEXT_END",
                tde4.getProjectNotes(),
            )
        )
        tde4.updateGUI()

    def install(self) -> None:
        """Install the host."""
        if not QtCore.QCoreApplication.instance():
            app = QtWidgets.QApplication([])
            self._qapp = app
            self._qapp.setQuitOnLastWindowClosed(False)

        pyblish.api.register_host("equalizer")

        pyblish.api.register_plugin_path(PUBLISH_PATH)
        register_loader_plugin_path(LOAD_PATH)
        register_creator_plugin_path(CREATE_PATH)

        heartbeat_interval = os.getenv("AYON_TDE4_HEARTBEAT_INTERVAL") or 500
        tde4.setTimerCallbackFunction(
            "EqualizerHost._timer", int(heartbeat_interval))

    @staticmethod
    def _timer() -> None:
        """Timer callback function."""
        QtWidgets.QApplication.instance().processEvents(
            QtCore.QEventLoop.AllEvents)

    @classmethod
    def get_host(cls) -> EqualizerHost:
        """Get the host instance."""
        return cls._instance

    def get_main_window(self) -> QtWidgets.QWidget:
        """Get the main window of the host application."""
        return self._qapp.activeWindow()
