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
import os
import re

import ayon_core.pipeline.load as load
import tde4
from ayon_core.lib.transcoding import IMAGE_EXTENSIONS
from ayon_core.pipeline import (
    get_current_project_name,
    get_representation_path,
)

from ayon_equalizer.api import Container, EqualizerHost


class LoadPlate(load.LoaderPlugin):
    product_types = [
        "imagesequence",
        "review",
        "render",
        "plate",
        "image",
        "online",
    ]

    representations = {"*"}
    extensions = {ext.lstrip(".") for ext in IMAGE_EXTENSIONS}

    label = "Load sequence"
    order = -10
    icon = "code-fork"
    color = "orange"

    def load(self, context, name=None, namespace=None, options=None):
        repre_entity = context["representation"]
        project_name = get_current_project_name()
        version_entity = context["version"]
        version_attributes = version_entity["attrib"]
        version_data = version_entity["data"]

        file_path = get_representation_path(repre_entity)
        file_path = self.format_path(file_path, repre_entity)

        camera = tde4.createCamera("SEQUENCE")
        tde4.setCameraName(camera, name)
        camera_name = tde4.getCameraName(camera)

        print(
            f"Loading: {file_path} into {camera_name}")

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
        )
        print(container)
        EqualizerHost.get_host().add_container(container)

    def update(self, container, context):
        version_entity = context["version"]
        version_attributes = version_entity["attrib"]
        repre_entity = context["representation"]
        camera_list = tde4.getCameraList()
        try:
            camera = [
                c for c in camera_list if
                tde4.getCameraName(c) == container["namespace"]
            ][0]
        except IndexError:
            self.log.error(f'Cannot find camera {container["namespace"]}')
            print(f'Cannot find camera {container["namespace"]}')
            return

        file_path = get_representation_path(repre_entity)
        file_path = self.format_path(file_path, repre_entity)

        # set the path to sequence on the camera
        tde4.setCameraPath(camera, file_path)

        # set the sequence attributes star/end/step
        tde4.setCameraSequenceAttr(
            camera, int(version_attributes.get("frameStart")),
            int(version_attributes.get("frameEnd")), 1)

        print(container)
        EqualizerHost.get_host().add_container(container)

    def switch(self, container, context):
        self.update(container, context)

    @staticmethod
    def format_path(path, representation):
        if not os.path.exists(path):
            raise RuntimeError("Path does not exist: %s" % path)

        ext = os.path.splitext(path)[-1]

        is_sequence = bool(representation["context"].get("frame"))

        if not is_sequence:
            filename = path
        else:
            hashes = "#" * len(str(representation["context"].get("frame")))
            filename = re.sub(r"(.*)\.(\d+){}$".format(re.escape(ext)),
                              "\\1.{}{}".format(hashes, ext),
                              path)

            filename = os.path.join(path, filename)

        filename = os.path.normpath(filename)
        filename = filename.replace("\\", "/")

        return filename

        return self.filepath_from_context(context)
