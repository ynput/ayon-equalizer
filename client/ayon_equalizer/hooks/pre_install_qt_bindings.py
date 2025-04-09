"""Install PySide2 python module to 3dequalizer's python.

If 3dequalizer doesn't have PySide2 module installed, it will try to install
it.

Note:
    This needs to be changed in the future so the UI is decoupled from the
    host application.

"""
from __future__ import annotations

import contextlib
import os
import subprocess
from pathlib import Path
from platform import system
from typing import Union

from ayon_applications import LaunchTypes, PreLaunchHook

python_versions = {7, 8, 9, 10, 11, 12, 13}
MAX_PYSIDE2_PYTHON_VERSION = 10

class InstallQtBinding(PreLaunchHook):
    """Install Qt binding to 3dequalizer's python packages."""

    app_groups = ("equalizer", "sdv_3dequalizer")
    launch_types = (LaunchTypes.local)

    def execute(self) -> None:
        """Entry point for the hook."""
        try:
            self._execute()
        except Exception:  # noqa: BLE001
            self.log.warning(
                "Processing of %s crashed.",
                self.__class__.__name__, exc_info=True
            )

    @staticmethod
    def _find_python_executable(
            path_str: str) -> tuple[Union[Path, None], Union[int, None]]:
        """Find python executable in 3de4's directory.

        Args:
            path_str (str): Path string with "{version}" placeholder.

        Returns:
            valid_path (Path): Path to python executable.

        """
        for version in python_versions:
            python_dir = Path(path_str.format(version=version))
            if python_dir.exists():
                return python_dir, version
        return None, None

    def _execute(self) -> None:  # noqa: PLR0912, C901
        """Execute the hook.

        Todo:
            * This method is too complex (PLR0912). It should be refactored
              to smaller methods.

        """
        platform = system().lower()
        executable = Path(self.launch_context.executable.executable_path)
        expected_executable = "3de4"
        if platform == "windows":
            expected_executable += ".exe"

        if not self.launch_context.env.get("TDE4_ROOT"):
            if executable.name.lower() != expected_executable:
                self.log.warning(
                    "Executable %s does not lead "
                    "to %s file. "
                    "Can't determine 3dequalizer's python to "
                    "check/install PySide2/PySide6. %s",
                    executable.as_posix(), expected_executable,
                    executable.name
                )
                return

            python_path_str = os.path.join(
                executable.parent.parent.as_posix(),
                "sys_data", "py3{version}_inst")
        else:
            python_path_str = os.path.join(
                self.launch_context.env["TDE4_ROOT"],
                "sys_data", "py3{version}_inst")

        python_dir, py_version = self._find_python_executable(python_path_str)

        if not python_dir:
            self.log.warning(
                "Couldn't find python executable "
                "for 3de4 in %s", python_path_str)
            return

        if platform == "windows":
            python_executable = Path(python_dir) / "python.exe"
        else:
            python_executable = Path(python_dir) / "python"
            # Check for python with enabled 'pymalloc'
            if not python_executable.exists():
                python_executable = Path(python_dir) / f"python3.{py_version}m"

        if not python_executable.exists():
            self.log.warning(
                "Couldn't find python executable "
                "for 3de4 %s", python_executable.as_posix())

            return

        pyside_name = "PySide6"
        if py_version <= MAX_PYSIDE2_PYTHON_VERSION:
            pyside_name = "PySide2"


        # Check if PySide2 is installed and skip if yes
        if self.is_pyside_installed(python_executable, pyside_name):
            self.log.debug(
                "3Dequalizer has already installed %s.", pyside_name)
            return

        # Install PySide2/PySide6 in 3de4's python
        if platform == "windows":
            result = self.install_pyside_windows(python_executable)
        else:
            result = self.install_pyside(python_executable, pyside_name)

        if result:
            self.log.info(
                "Successfully installed %s module to 3de4.", pyside_name)
        else:
            self.log.warning(
                "Failed to install %s module to 3de4.", pyside_name)

    def install_pyside_windows(
            self, python_executable: Path) -> Union[None, int]:
        """Install PySide2 python module to 3de4's python.

        Installation requires administration rights that's why it is required
        to use "pywin32" module which can execute command's and ask for
        administration rights.

        Note:
            This is asking for administrative right always, no matter if
            it is actually needed or not. Unfortunately getting
            correct permissions for directory on Windows isn't that trivial.
            You can either use `win32security` module or run `icacls` command
            in subprocess and parse its output.

        """
        try:
            import pywintypes
            import win32con
            import win32event
            import win32process
            from win32comext.shell import shellcon
            from win32comext.shell.shell import ShellExecuteEx
        except Exception:  # noqa: BLE001
            self.log.warning(
                "Couldn't import 'pywin32' modules", exc_info=True)
            return None

        with contextlib.suppress(pywintypes.error):
            # Parameters
            # - use "-m pip" as module pip to install PySide2 and argument
            #   "--ignore-installed" is to force install module to 3de4's
            #   site-packages and make sure it is binary compatible
            parameters = "-m pip install --ignore-installed PySide2"

            # Execute command and ask for administrator's rights
            process_info = ShellExecuteEx(
                nShow=win32con.SW_SHOWNORMAL,
                fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                lpVerb="runas",
                lpFile=python_executable.as_posix(),
                lpParameters=parameters,
                lpDirectory=python_executable.parent.as_posix()
            )
            process_handle = process_info["hProcess"]
            win32event.WaitForSingleObject(
                process_handle, win32event.INFINITE)
            return_code = win32process.GetExitCodeProcess(process_handle)
            return return_code == 0

    def install_pyside(
            self, python_executable: Path, pyside_name: str) -> int:
        """Install PySide2 python module to 3de4's python."""
        args = [
            python_executable.as_posix(),
            "-m",
            "pip",
            "install",
            "--ignore-installed",
            pyside_name,
        ]

        try:
            # Parameters
            # - use "-m pip" as module pip to install PySide2/6 and argument
            #   "--ignore-installed" is to force install module to 3de4
            #   site-packages and make sure it is binary compatible

            process = subprocess.Popen(
                args, stdout=subprocess.PIPE, universal_newlines=True,
                env=self.launch_context.env,
            )
            process.communicate()

        except PermissionError:
            self.log.warning(
                'Permission denied with command: "%s".', " ".join(args),
                exc_info=True)
        except OSError as error:
            self.log.warning(
                'OS error has occurred: "%s".', error, exc_info=True)
        except subprocess.SubprocessError:
            pass
        else:
            return process.returncode == 0

    def is_pyside_installed(
            self, python_executable: Path, pyside_name: str) -> bool:
        """Check if PySide2/6 module is in 3de4 python env.

        Args:
            python_executable (Path): Path to python executable.
            pyside_name (str): Name of pyside (to distinguish between PySide2
                and PySide6).

        Returns:
            bool: True if PySide2 is installed, False otherwise.

        """
        # Get pip list from 3de4's python executable
        args = [python_executable.as_posix(), "-m", "pip", "list"]
        process = subprocess.Popen(
            args, stdout=subprocess.PIPE, env=self.launch_context.env)
        stdout, _ = process.communicate()
        lines = stdout.decode().split(os.linesep)
        # Second line contain dashes that define maximum length of module name.
        #   Second column of dashes define maximum length of module version.
        package_dashes, *_ = lines[1].split(" ")
        package_len = len(package_dashes)

        # Got through printed lines starting at line 3
        for idx in range(2, len(lines)):
            line = lines[idx]
            if not line:
                continue
            package_name = line[:package_len].strip()
            if package_name.lower() == pyside_name.lower():
                return True
        return False
