"""3DEqualizer plugin tests.

These test need to be run in 3DEqualizer.
"""

import json
import re
import unittest
from dataclasses import dataclass

AYON_CONTAINER_ID = "test.container"

CONTEXT_REGEX = re.compile(
    r"AYON_CONTEXT::(?P<context>.*?)::AYON_CONTEXT_END",
    re.DOTALL)


@dataclass
class Container:
    """Container dataclass."""

    name: str = None
    id: str = AYON_CONTAINER_ID
    namespace: str = ""
    loader: str = None
    representation: str = None


class Tde4Mock:
    """Simple class to mock few 3dequalizer functions.

    Just to run the test outside the host itself.
    """

    _notes = ""

    def isProjectUpToDate(self) -> bool:  # noqa: N802
        """Mock function to check if project is up to date."""
        return True

    def setProjectNotes(self, notes: str) -> None:  # noqa: N802
        """Mock function to set project notes."""
        self._notes = notes

    def getProjectNotes(self) -> str:  # noqa: N802
        """Mock function to get project notes."""
        return self._notes


tde4 = Tde4Mock()


def get_context_data() -> dict:
    """Get context data from project notes."""
    m = re.search(CONTEXT_REGEX, tde4.getProjectNotes())
    return json.loads(m["context"]) if m else {}


def update_context_data(data: dict, _: dict) -> None:
    """Update context data in project notes."""
    m = re.search(CONTEXT_REGEX, tde4.getProjectNotes())
    if not m:
        tde4.setProjectNotes("AYON_CONTEXT::::AYON_CONTEXT_END")
    update = json.dumps(data, indent=4)
    tde4.setProjectNotes(
        re.sub(
            CONTEXT_REGEX,
            f"AYON_CONTEXT::{update}::AYON_CONTEXT_END",
            tde4.getProjectNotes()
        )
    )


def get_containers() -> list:
    """Get containers from context data."""
    return get_context_data().get("containers", [])


def add_container(container: Container) -> None:
    """Add container to context data."""
    context_data = get_context_data()
    containers = get_context_data().get("containers", [])

    for _container in containers:
        if _container["name"] == container.name and _container["namespace"] == container.namespace:  # noqa: E501
            containers.remove(_container)
            break

    containers.append(container)

    context_data["containers"] = containers
    update_context_data(context_data, {})


class TestEqualizer(unittest.TestCase):
    """Test 3DEqualizer plugin."""

    def test_context_data(self) -> None:
        """Test context data."""
        # ensure empty project notest

        data = get_context_data()
        assert data == {}, "context data is not empty"  # noqa: S101

        # add container
        add_container(
            Container(name="test", representation="test_A")
        )

        assert len(get_containers()) == 1, "container not added"  # noqa: S101
        assert get_containers()[0]["name"] == "test",\
            "container name is not correct"  # noqa: S101

        # add another container
        add_container(
            Container(name="test2", representation="test_B")
        )

        assert len(get_containers()) == 2, "container not added"  # noqa: S101,PLR2004
        assert get_containers()[1]["name"] == "test2",\
            "container name is not correct"  # noqa: S101

        # update container
        add_container(
            Container(name="test2", representation="test_C")
        )
        assert len(get_containers()) == 2, "container not updated"  # noqa: S101,PLR2004
        assert get_containers()[1]["representation"] == "test_C",\
            "container name is not correct"  # noqa: S101


if __name__ == "__main__":
    unittest.main()
