"""Base plugin class for 3DEqualizer.

Note:
    3dequalizer 7.1v2 uses Python 3.7.9
    3dequalizer 8.0 uses Python 3.9

"""
from __future__ import annotations

from typing import TYPE_CHECKING

from ayon_core.lib import BoolDef, EnumDef, NumberDef
from ayon_core.pipeline import (
    CreatedInstance,
    Creator,
    OptionalPyblishPluginMixin,
)

if TYPE_CHECKING:
    from .host import EqualizerHost


class EqualizerCreator(Creator):
    """Base class for creating instances in 3DEqualizer."""

    def create(self,
               product_name: str,
               instance_data: dict,
               pre_create_data: dict) -> CreatedInstance:
        """Create a subset in the host application.

        Args:
            product_name (str): Name of the subset to create.
            instance_data (dict): Data of the instance to create.
            pre_create_data (dict): Data from the pre-create step.

        Returns:
            ayon_core.pipeline.CreatedInstance: Created instance.

        """
        self.log.debug("EqualizerCreator.create")
        instance = CreatedInstance(
            self.product_type,
            product_name,
            instance_data,
            self)
        self._add_instance_to_context(instance)

        host: EqualizerHost = self.host
        host.add_publish_instance(instance.data_to_store())

        return instance

    def collect_instances(self) -> None:
        """Collect instances from the host application.

        Returns:
            list[openpype.pipeline.CreatedInstance]: List of instances.

        """
        host: EqualizerHost = self.host
        for instance_data in host.get_publish_instances():
            if instance_data["creator_identifier"] != self.identifier:
                continue
            created_instance = CreatedInstance.from_existing(
                instance_data, self
            )
            self._add_instance_to_context(created_instance)

    def update_instances(self, update_list: list[dict]) -> None:
        """Update instances in the host application."""
        host: EqualizerHost = self.host

        current_instances = host.get_publish_instances()
        cur_instances_by_id = {}
        for instance_data in current_instances:
            instance_id = instance_data.get("instance_id")
            if instance_id:
                cur_instances_by_id[instance_id] = instance_data

        for instance, changes in update_list:
            instance_data = changes.new_value
            cur_instance_data = cur_instances_by_id.get(instance.id)
            if cur_instance_data is None:
                current_instances.append(instance_data)
                continue
            for key in set(cur_instance_data) - set(instance_data):
                cur_instance_data.pop(key)
            cur_instance_data.update(instance_data)
        host.write_publish_instances(current_instances)

    def remove_instances(self, instances: list[CreatedInstance]) -> None:
        """Remove instances from the host application."""
        host: EqualizerHost = self.host
        for instance in instances:
            self._remove_instance_from_context(instance)
            host.remove_publish_instance(instance)


class ExtractScriptBase(OptionalPyblishPluginMixin):
    """Base class for extract script plugins."""

    hide_reference_frame = False
    export_uv_textures = False
    overscan_percent_width = 100
    overscan_percent_height = 100
    units = "mm"

    @classmethod
    def apply_settings(
            cls, project_settings: dict,
            system_settings: dict) -> None:  # noqa: ARG003
        """Apply settings from the configuration."""
        settings = project_settings["equalizer"]["publish"][
            "ExtractMatchmoveScriptMaya"]

        cls.hide_reference_frame = settings.get(
            "hide_reference_frame", cls.hide_reference_frame)
        cls.export_uv_textures = settings.get(
            "export_uv_textures", cls.export_uv_textures)
        cls.overscan_percent_width = settings.get(
            "overscan_percent_width", cls.overscan_percent_width)
        cls.overscan_percent_height = settings.get(
            "overscan_percent_height", cls.overscan_percent_height)
        cls.units = settings.get("units", cls.units)

    @classmethod
    def get_attribute_defs(cls) -> list:
        """Get attribute definitions for the plugin."""
        defs = super().get_attribute_defs()

        defs.extend([
            BoolDef("hide_reference_frame",
                    label="Hide Reference Frame",
                    default=cls.hide_reference_frame),
            BoolDef("export_uv_textures",
                    label="Export UV Textures",
                    default=cls.export_uv_textures),
            NumberDef("overscan_percent_width",
                      label="Overscan Width %",
                      default=cls.overscan_percent_width,
                      decimals=0,
                      minimum=1,
                      maximum=1000),
            NumberDef("overscan_percent_height",
                      label="Overscan Height %",
                      default=cls.overscan_percent_height,
                      decimals=0,
                      minimum=1,
                      maximum=1000),
            EnumDef("units",
                    ["mm", "cm", "m", "in", "ft", "yd"],
                    default=cls.units,
                    label="Units"),
            BoolDef("point_sets",
                    label="Export Point Sets",
                    default=True),
            BoolDef("export_2p5d",
                    label="Export 2.5D Points",
                    default=True),
        ])
        return defs
