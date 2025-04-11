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
from typing import TYPE_CHECKING, Optional, Union

import pyblish.api
import tde4
from ayon_core.host import HostBase, ILoadHost, IPublishHost, IWorkfileHost
from ayon_core.pipeline import (
    CreatedInstance,
    register_creator_plugin_path,
    register_loader_plugin_path,
)
from qtpy import QtCore, QtWidgets

from ayon_equalizer import EQUALIZER_HOST_DIR
from ayon_equalizer.api.pipeline import Container

if TYPE_CHECKING:
    from collections.abc import Generator
    from typing import Any


AYON_METADATA_GUARD = "AYON_CONTEXT::{}::AYON_CONTEXT_END"
AYON_METADATA_REGEX = re.compile(
    AYON_METADATA_GUARD.format("(?P<context>.*?)"),
    re.DOTALL)
PLUGINS_DIR = os.path.join(EQUALIZER_HOST_DIR, "plugins")
PUBLISH_PATH = os.path.join(PLUGINS_DIR, "publish")
LOAD_PATH = os.path.join(PLUGINS_DIR, "load")
CREATE_PATH = os.path.join(PLUGINS_DIR, "create")
INVENTORY_PATH = os.path.join(PLUGINS_DIR, "inventory")

EQUALIZER_CONTEXT_KEY = "context"
EQUALIZER_INSTANCES_KEY = "publish_instances"
EQUALIZER_CONTAINERS_KEY = "containers"


class AYONJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for dataclasses."""

    def default(self, obj: object) -> Union[dict, object]:
        """Encode dataclasses as dict."""
        if dataclasses.is_dataclass(obj):
            # type: obj: dataclasses.dataclass
            return dataclasses.asdict(obj)
        if isinstance(obj, CreatedInstance):
            return dict(obj)
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

    def get_containers(self) -> Generator[Container, Any, Optional[list]]:
        """Get containers from the current workfile."""
        # sourcery skip: use-named-expression
        data = self.get_ayon_data() or {}
        for container in data.get(EQUALIZER_CONTAINERS_KEY, []):
            # convert dict to dataclass
            _container = Container(**container)
            # check if the container is valid
            if _container.name and _container.namespace:
                yield _container

    def add_container(self, container: Container) -> None:
        """Add a container to the current workfile.

        Args:
            container (Container): Container to add.

        """
        data = self.get_ayon_data()
        containers = list(self.get_containers())
        to_remove = [
            idx
            for idx, _container in enumerate(containers)
            if _container.name == container.name
            and _container.namespace == container.namespace
        ]
        for idx in reversed(to_remove):
            containers.pop(idx)

        data[EQUALIZER_CONTAINERS_KEY] = [
            *containers, dataclasses.asdict(container)]

        self.update_ayon_data(data)

    def _create_ayon_data(self) -> None:
        """Create AYON data in the current project."""
        tde4.setProjectNotes(
            f"{tde4.getProjectNotes()}\n"
            f"{AYON_METADATA_GUARD}\n")
        # this is really necessary otherwise the data is not saved
        tde4.updateGUI()

    def get_ayon_data(self) -> dict:
        """Get AYON context data from the current project.

        3Dequalizer doesn't have any custom node or other
        place to store metadata, so we store context data in
        the project notes encoded as JSON and wrapped in a
        special guard string `AYON_CONTEXT::...::AYON_CONTEXT_END`.

        Returns:
            dict: Context data.

        """
        # sourcery skip: use-named-expression
        m = re.search(AYON_METADATA_REGEX, tde4.getProjectNotes())
        if not m:
            self._create_ayon_data()
            return {}
        try:
            context = json.loads(m["context"]) if m else {}
        except ValueError:
            self.log.debug("AYON data is not valid json")
            # AYON data not found or invalid, create empty placeholder
            self._create_ayon_data()
            return {}

        return context

    def update_ayon_data(self, data: dict) -> None:
        """Update AYON context data in the current project.

        Serialize context data as json and store it in the
        project notes. If the context data is not found, create
        a placeholder there. See `get_context_data` for more info.

        Args:
            data (dict): Context data.

        """
        original_data = self.get_ayon_data()

        updated_data = original_data.copy()
        updated_data.update(data)
        update_str = json.dumps(
            updated_data or {}, indent=4, cls=AYONJSONEncoder)

        tde4.setProjectNotes(
            re.sub(
                AYON_METADATA_REGEX,
                AYON_METADATA_GUARD.format(update_str),
                tde4.getProjectNotes(),
            )
        )
        tde4.updateGUI()

    def get_context_data(self) -> dict:
        """Get context data from the current project."""
        data = self.get_ayon_data()

        return data.get(EQUALIZER_CONTEXT_KEY, {})

    def update_context_data(self, data: dict, changes: dict) -> None:
        """Update context data in the current project.

        Args:
            data (dict): Context data.
            changes (dict): Changes to the context data.

        Raises:
            RuntimeError: If the context data is not found.

        """
        if not data:
            return
        ayon_data = self.get_ayon_data()
        ayon_data[EQUALIZER_CONTEXT_KEY] = data
        self.update_ayon_data(ayon_data)


    def get_publish_instances(self) -> list[dict]:
        """Get publish instances from the current project."""
        data = self.get_ayon_data()
        return data.get(EQUALIZER_INSTANCES_KEY, [])

    def add_publish_instance(self, instance_data: dict) -> None:
        """Add a publish instance to the current project.

        Args:
            instance_data (dict): Publish instance to add.

        """
        data = self.get_ayon_data()
        publish_instances = self.get_publish_instances()
        publish_instances.append(instance_data)
        data[EQUALIZER_INSTANCES_KEY] = publish_instances

        self.update_ayon_data(data)

    def update_publish_instance(
            self,
            instance_id: str,
            data: dict,
    ) -> None:
        """Update a publish instance in the current project.

        Args:
            instance_id (str): Publish instance id to update.
            data (dict): Data to update.

        """
        ayon_data = self.get_ayon_data()
        publish_instances = self.get_publish_instances()
        for idx, publish_instance in enumerate(publish_instances):
            if publish_instance["instance_id"] == instance_id:
                publish_instances[idx] = data
                break
        ayon_data[EQUALIZER_INSTANCES_KEY] = publish_instances

        self.update_ayon_data(ayon_data)

    def write_create_instances(
            self, instances: list[dict]) -> None:
        """Write publish instances to the current project."""
        ayon_data = self.get_ayon_data()
        ayon_data[EQUALIZER_INSTANCES_KEY] = instances
        self.update_ayon_data(ayon_data)

    def remove_create_instance(self, instance_id: str) -> None:
        """Remove a publish instance from the current project.

        Args:
            instance_id (str): Publish instance id to remove.

        """
        data = self.get_ayon_data()
        publish_instances = self.get_publish_instances()
        publish_instances = [
            publish_instance
            for publish_instance in publish_instances
            if publish_instance["instance_id"] != instance_id
        ]
        data[EQUALIZER_INSTANCES_KEY] = publish_instances

        self.update_ayon_data(data)


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

        heartbeat_interval = os.getenv("AYON_TDE4_HEARTBEAT_INTERVAL") or 100
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
