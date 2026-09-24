"""Loader for models."""
from __future__ import annotations

import os
import re
from time import time_ns
from typing import ClassVar, Optional

import tde4
from ayon_core.pipeline import get_representation_path, load
from ayon_core.pipeline.load import LoadError

from ayon_equalizer.api import Container, EqualizerHost


class LoadModel(load.LoaderPlugin):
    """Load model to the current point group."""

    product_base_types: ClassVar[Optional[set[str]]] = {"model"}

    product_types = product_base_types

    representations: ClassVar[list[str]] = ["obj"]
    extensions: ClassVar[list[str]] = ["obj"]

    label = "Load model"
    order = -10
    icon = "cube"
    color = "#6b9bd2"

    def load(
        self,
        context: dict,
        name: Optional[str] = None,
        namespace: Optional[str] = None,
        options: Optional[dict] = None,
    ) -> None:
        """Load the model to the current point group.

        Args:
            context (dict): the context to be used to load the model.
            name (str, optional): the name of the model to be loaded.
            namespace (str, optional): the namespace of the model to be loaded.
            options (dict, optional): the options to be used to load the model.

        Raises:
            LoadError: if no or more than one point groups are selected.

        """
        selected_point_group_ids = tuple(
            filter(
                lambda point_group_id: tde4.getPGroupSelectionFlag(
                    point_group_id) > 0,
                tde4.getPGroupList(),
            )
        )
        if not selected_point_group_ids:
            msg = "No point groups selected."
            raise LoadError(msg)

        if len(selected_point_group_ids) > 1:
            msg = (
                "Multiple point groups selected. "
                "Please select only one point group."
            )
            raise LoadError(msg)

        point_group_id = selected_point_group_ids[0]

        repre_entity = context["representation"]
        version_entity = context["version"]

        file_path = self.filepath_from_context(context)

        model_id = tde4.create3DModel(point_group_id)
        if name:
            tde4.set3DModelName(point_group_id, model_id, name)
        tde4.importOBJ3DModel(point_group_id, model_id, file_path)
        # hardcoded for now until putting orientation and spatial unit
        # data against a published model
        tde4.set3DModelRotationScale3D(
            point_group_id,
            model_id,
            [[100.0, 0.0, 0.0], [0.0, 0.0, -100.0], [0.0, 100.0, 0.0]],
        )
        model_name = tde4.get3DModelName(point_group_id, model_id)

        container = Container(
            name=name or model_name,
            namespace=model_name,
            loader=self.__class__.__name__,
            representation=str(repre_entity["id"]),
            objectName=model_name,
            version=str(version_entity["version"]),
            timestamp=time_ns(),
        )
        EqualizerHost.get_host().add_container(container)
        tde4.updateGUI()

    def update(self, container: dict, context: dict) -> None:
        """Update loaded models.

        Args:
            container (dict): the context to be used to load the model.
            context (dict): the context to be used to load the model.

        """
        version_entity = context["version"]
        repre_entity = context["representation"]

        point_group_id, model_id = next(
            (
                (point_group_id, model_id)
                for point_group_id in tde4.getPGroupList()
                for model_id in tde4.get3DModelList(point_group_id)
                if tde4.get3DModelName(point_group_id, model_id) == container["namespace"]  # noqa: E501
            ),
            (None, None),
        )
        if model_id is None:
            msg = f'Cannot find model {container["namespace"]}'
            raise LoadError(msg)

        file_path = get_representation_path(repre_entity)
        file_path = self.format_path(file_path, repre_entity)

        tde4.importOBJ3DModel(point_group_id, model_id, file_path)

        container["representation"] = repre_entity["id"]
        container["version"] = str(version_entity["version"])

        EqualizerHost.get_host().add_container(Container(**container))
        tde4.updateGUI()

    def switch(self, container: dict, context: dict) -> None:
        """Switch loaded models."""
        self.update(container, context)

    @staticmethod
    def format_path(path: str, representation: dict) -> str:
        """Format file path correctly for single image or sequence."""
        if not os.path.exists(path):
            msg = f"Path does not exist: {path}"
            raise RuntimeError(msg)

        ext = os.path.splitext(path)[-1]

        is_sequence = bool(representation["context"].get("frame"))

        if not is_sequence:
            filename = path
        else:
            hashes = "#" * len(str(representation["context"].get("frame")))
            filename = re.sub(
                f"(.*)\\.(\\d+){re.escape(ext)}$",
                f"\\1.{hashes}{ext}", path)

            filename = os.path.join(path, filename)

        filename = os.path.normpath(filename)
        return filename.replace("\\", "/")
