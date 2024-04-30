#
# 3DE4.script.name:     Manage ...
# 3DE4.script.gui:      Main Window::Ayon
# 3DE4.script.comment:  Open AYON Publisher tool
#

from ayon_core.pipeline import install_host, is_installed
from ayon_equalizer.api import EqualizerHost
from ayon_core.tools.utils import host_tools


def install_3de_host():
    print("Running AYON integration ...")
    install_host(EqualizerHost())


if not is_installed():
    install_3de_host()

# show the UI
print("Opening Scene Manager window ...")
host_tools.show_scene_inventory(
    parent=EqualizerHost.get_host().get_main_window())
