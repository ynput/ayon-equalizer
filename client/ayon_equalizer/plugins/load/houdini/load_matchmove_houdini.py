from __future__ import annotations

from ayon_core.pipeline import load, registered_host
from ayon_core.tools.utils.dialogs import show_message_dialog


class LoadMatchmoveHoudini(load.LoaderPlugin):
    """Load matchmove file

    Could be run from Loader in Houdini.
    """

    product_base_types = ["matchmove"]
    product_types = product_base_types
    representations = ["py_houdini"]
    extensions = ["py"]

    label = "Load Matchmove"
    order = -10
    icon = "video"
    color = "white"

    def load(self, context, name, namespace, data):
        host = registered_host()
        if host.name not in {"houdini"}:
            show_message_dialog(
                title="Warning",
                message=(
                    f"Host {host.name} is not supported yet."
                ),
                level="warning"
            )
            return

        repre_entity = context["representation"]
        repre_id = repre_entity["id"]
        self.log.debug("Representation id `{}` ".format(repre_id))

        filepath = self.filepath_from_context(context)
        if not filepath:
            self.log.warning(
                "Representation id `{}` is failing to load".format(repre_id)
            )
            return

        filepath = filepath.replace("\\", "/")
        self.log.debug("Filepath: `{}` ".format(filepath))

        # Open and execute the file in the current global environment
        with open(filepath, "r") as f:
            exec(f.read(), globals())

        # TODO: Put created nodes into renamed subnet and layout children
