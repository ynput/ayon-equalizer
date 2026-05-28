from time import time_ns
from typing import ClassVar, Optional

import tde4

from ayon_core.pipeline import get_representation_path, load

from ayon_equalizer.api import Container, EqualizerHost


class LoadModel(load.LoaderPlugin):
    """Load model to the current point group."""

    product_base_types: ClassVar[list[str]] = [
        "model",
    ]
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
        selected_point_group_ids = tuple(
            filter(
                lambda point_group_id: tde4.getPGroupSelectionFlag(point_group_id) > 0,
                tde4.getPGroupList(),
            )
        )
        if not selected_point_group_ids:
            raise ValueError("No point groups selected.")

        if len(selected_point_group_ids) > 1:
            raise ValueError(
                "Multiple point groups selected. Please select only one point group."
            )

        point_group_id = selected_point_group_ids[0]

        repre_entity = context["representation"]
        version_entity = context["version"]

        file_path = self.filepath_from_context(context)

        model_id = tde4.create3DModel(point_group_id)
        tde4.set3DModelName(point_group_id, model_id, name)
        tde4.set3DModelSurveyFlag(point_group_id, model_id, 1)
        tde4.importOBJ3DModel(point_group_id, model_id, file_path)

        container = Container(
            name=name,
            namespace=name,
            loader=self.__class__.__name__,
            representation=str(repre_entity["id"]),
            objectName=name,
            version=str(version_entity["version"]),
            timestamp=time_ns(),
        )
        EqualizerHost.get_host().add_container(container)
        tde4.updateGUI()

    def update(self, container: dict, context: dict) -> None:
        version_entity = context["version"]
        version_attributes = version_entity["attrib"]
        repre_entity = context["representation"]

        point_group_id, model_id = next(
            (
                (point_group_id, model_id)
                for point_group_id in tde4.getPGroupList()
                for model_id in tde4.get3DModelList(point_group_id)
                if tde4.get3DModelName(model_id) == container["namespace"]
            ),
            (None, None),
        )
        if model_id is None:
            raise ValueError(f'Cannot find model {container["namespace"]}')

        file_path = get_representation_path(repre_entity)
        file_path = self.format_path(file_path, repre_entity)

        tde4.importOBJ3DModel(point_group_id, model_id, file_path)

        container["representation"] = repre_entity["id"]
        container["version"] = str(version_entity["version"])

        EqualizerHost.get_host().add_container(Container(**container))
        tde4.updateGUI()

    def switch(self, container: dict, context: dict) -> None:
        self.update(container, context)
