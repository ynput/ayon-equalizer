"""3DEqualizer addon package definition."""
name = "equalizer"
title = "3DEqualizer"
version = "0.2.0"
app_host_name = "equalizer"
client_dir = "ayon_equalizer"
project_can_override_addon_version = True

ayon_server_version = ">1.3.0"
ayon_required_addons = {
    "core": ">=1.8.0",
}
ayon_compatible_addons = {}
