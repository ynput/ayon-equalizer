"""Library functions for the AYON Equalizer API."""

def maya_valid_name(name: str) -> str:
    """Make a given name Maya valid and return it.

    This function is taken from 3dequalizer's `export_maya.py` script
    with just slight refactoring, logic is the same to be compliant with
    the 3dequalizer's logic.

    Arguments:
        name (str): Name to make Maya valid.

    Returns:
        str: Maya valid name.

    """
    # make a given name maya valid and return it.
    if not name:
        return ""
    if name[0].lower() not in "abcdefghijklmnopqrstuvwxyz_":
        name = f"_{name}"

    # fix some special ASCII metadata
    name = name.replace("\n", "")
    name = name.replace("\r", "")

    # fix the middle of the file as an array
    name_as_array = list(name)
    for i, letter in enumerate(name_as_array):
        if letter.lower() not in "abcdefghijklmnopqrstuvwxyz0123456789_":
            name_as_array[i] = "_"

    # back to string form
    name = "".join(name_as_array)

    # remove sequential underscores until they are all gone
    while "__" in name:
        name = name.replace("__", "_")

    return name.removesuffix("_")
