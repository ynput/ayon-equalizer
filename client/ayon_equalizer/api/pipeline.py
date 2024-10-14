"""Pipeline API module."""
import contextlib
from dataclasses import dataclass

import tde4
from ayon_core.pipeline import AYON_CONTAINER_ID


@dataclass
class Container:
    """Container data class."""

    name: str = None
    id: str = AYON_CONTAINER_ID
    namespace: str = ""
    loader: str = None
    representation: str = None
    objectName: str = None  # noqa: N815
    timestamp: int = 0
    version: str = None


@contextlib.contextmanager
def maintained_model_selection() -> None:
    """Maintain model selection during context."""
    point_groups = tde4.getPGroupList()
    point_group = next(
        (
            pg for pg in point_groups
            if tde4.getPGroupType(pg) == "CAMERA"
        ), None,
    )
    selected_models = tde4.get3DModelList(point_group, 1) \
        if point_group else []
    try:
        yield
    finally:
        if point_group:
            # 3 restore model selection
            for model in tde4.get3DModelList(point_group, 0):
                if model in selected_models:
                    tde4.set3DModelSelectionFlag(point_group, model, 1)
                else:
                    tde4.set3DModelSelectionFlag(point_group, model, 0)
