"""Loader for image sequences.

This loads published sequence to the current camera
because this workflow is the most common in production.

If current camera is not defined, it will try to use first camera and
if there is no camera at all, it will create new one.

TODO (antirotor):
    * Support for setting handles, calculation frame ranges, EXR
      options, etc.
    * Add support for color management - at least put correct gamma
      to image corrections.

"""
from __future__ import annotations

import os
import re
import time
from typing import Optional

import tde4
from ayon_core.lib.transcoding import IMAGE_EXTENSIONS
from ayon_core.pipeline import get_representation_path, load

from ayon_equalizer.api import Container, EqualizerHost


class LoadPlate(load.LoaderPlugin):
    """Load image sequence to the current camera."""

    product_types = [
        "imagesequence",
        "review",
        "render",
        "plate",
        "image",
        "online",
    ]

    representations = ["*"]
    extensions = {ext.lstrip(".") for ext in IMAGE_EXTENSIONS}

    label = "Load sequence"
    order = -10
    icon = "code-fork"
    color = "orange"

    def load(self, context: dict, name: Optional[str] = None,
             namespace: Optional[str] = None, options: Optional[dict]=None):
        """Load image sequence to the current camera."""
        repre_entity = context["representation"]
        version_entity = context["version"]
        version_attributes = version_entity["attrib"]

        file_path = self.filepath_from_context(repre_entity)
        file_path = self.format_path(file_path, repre_entity)

        camera = tde4.createCamera("SEQUENCE")
        tde4.setCameraName(camera, name)
        camera_name = tde4.getCameraName(camera)

        self.log.debug(f"Loading: {file_path} into {camera_name}")

        # set the path to sequence on the camera
        tde4.setCameraPath(camera, file_path)

        # set the sequence attributes star/end/step
        tde4.setCameraSequenceAttr(
            camera, int(version_attributes.get("frameStart")),
            int(version_attributes.get("frameEnd")), 1)

        container = Container(
            name=name,
            namespace=camera_name,
            loader=self.__class__.__name__,
            representation=str(repre_entity["id"]),
            objectName=camera_name,
            version=str(version_entity["version"]),
            timestamp=time.time_ns()
        )
        EqualizerHost.get_host().add_container(container)
        tde4.updateGUI()

    def update(self, container: dict, context: dict):
        """Update the image sequence on the current camera."""
        version_entity = context["version"]
        version_attributes = version_entity["attrib"]
        repre_entity = context["representation"]
        camera_list = tde4.getCameraList()
        try:
            camera = next(
                c for c in camera_list if
                tde4.getCameraName(c) == container["namespace"]
            )
        except IndexError:
            self.log.exception(f'Cannot find camera {container["namespace"]}')
            return

        file_path = get_representation_path(repre_entity)
        file_path = self.format_path(file_path, repre_entity)

        # set the path to sequence on the camera
        tde4.setCameraPath(camera, file_path)

        # set the sequence attributes star/end/step
        tde4.setCameraSequenceAttr(
            camera, int(version_attributes.get("frameStart")),
            int(version_attributes.get("frameEnd")), 1)
        self.log.info(f"Updating: {file_path} into {container['namespace']}")
        container["representation"] = repre_entity["id"]
        container["version"] = str(version_entity["version"])

        EqualizerHost.get_host().add_container(container)
        tde4.updateGUI()

    def switch(self, container: dict, context: dict):
        """Switch the image sequence on the current camera."""
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

