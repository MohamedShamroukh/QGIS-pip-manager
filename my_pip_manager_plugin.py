"""
my_pip_manager_plugin.py  -  QGIS Pip Manager v0.2.0
Robust Python path detection for OSGeo4W, conda, Homebrew, and system Python.
"""
import os
import platform
import subprocess
import sys
import sysconfig
import tempfile
from pathlib import Path

from qgis.core import QgsApplication, QgsSettings
from .compat import QAction, QIcon, QMessageBox, QInputDialog
from .my_pip_manager_dialog import PipManagerDialog

if platform.system() == "Windows":
    SUBPROCESS_FLAGS = 0x08000000
else:
    SUBPROCESS_FLAGS = 0


class MyPipManagerPlugin:

    def __init__(self, iface):
        self.iface       = iface
        self.dlg         = None
        self.action      = None
        self.settings    = QgsSettings()
        self.python_path = self._detect_python()

    # -- GUI lifecycle ---------------------------------------------------------

    def initGui(self):
        icon_path = Path(__file__).parent / "icon.png"
        icon = QIcon(str(icon_path)) if icon_path.exists() else QIcon()
        self.action = QAction(icon, "Pip Manager", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu("Pip Manager", self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        if self.action:
            self.iface.removePluginMenu("Pip Manager", self.action)
            self.iface.removeToolBarIcon(self.action)
        if self.dlg:
            self.dlg.close()

    # -- Run -------------------------------------------------------------------

    def run(self):
        if not self.python_path:
            self.python_path = self._prompt_python_path()
            if not self.python_path:
                QMessageBox.critical(
                    self.iface.mainWindow(), "Error",
                    "Could not find QGIS Python executable.\n"
                    "Please set the path manually in the Settings tab.")
                return

        if self.dlg and self.dlg.isVisible():
            self.dlg.raise_()
            self.dlg.activateWindow()
            return

        try:
            self.dlg = PipManagerDialog(
                parent           = self.iface.mainWindow(),
                qgis_python_path = self.python_path,
                settings         = self.settings,
            )
            self.dlg.show()
        except PermissionError as exc:
            QMessageBox.critical(self.iface.mainWindow(), "Permission Error", str(exc))
        except (ValueError, FileNotFoundError) as exc:
            QMessageBox.critical(self.iface.mainWindow(), "Path Error", str(exc))
        except Exception as exc:
            QMessageBox.critical(self.iface.mainWindow(), "Fatal Error", str(exc))

    # -- Python path detection -------------------------------------------------

    @staticmethod
    def _python_names():
        """Platform-appropriate Python executable names."""
        if platform.system() == "Windows":
            return ["python.exe", "python3.exe"]
        return ["python3", "python"]

    def _detect_python(self):
        """
        Detect the Python interpreter that is running this plugin.
        Validates every candidate by actually importing pip.
        """
        # 1. Check cached path first (and validate it — never trust blindly)
        saved = self.settings.value("pip_manager/python_path", "")
        if saved and self._validate(saved):
            return saved
        if saved:
            self.settings.remove("pip_manager/python_path")

        candidates = []
        system = platform.system()

        # 2. sysconfig BINDIR — most reliable, tells us where python was built
        bindir = sysconfig.get_config_var("BINDIR")
        if bindir:
            for name in self._python_names():
                candidates.append(str(Path(bindir) / name))

        # 3. sys.prefix / sys.base_prefix
        for prefix_attr in ("base_prefix", "prefix"):
            prefix = getattr(sys, prefix_attr, None)
            if not prefix:
                continue
            p = Path(prefix)
            for name in self._python_names():
                candidates.append(str(p / name))
                if system != "Windows":
                    candidates.append(str(p / "bin" / name))

        # 4. Derive from sys.executable (QGIS binary location)
        #    Typical layouts:
        #    Win:  C:\OSGeo4W\bin\qgis-bin.exe  → ..\apps\Python3xx\python.exe
        #    macOS: /Applications/QGIS.app/Contents/MacOS/QGIS → ../Resources/python
        #    Linux: /usr/bin/qgis → /usr/bin/python3
        try:
            exe = Path(sys.executable).resolve()
            if exe.parent.name.lower() in ("bin", "macos"):
                root = exe.parent.parent
                if system == "Windows":
                    # OSGeo4W / QGIS standalone: apps/Python3*
                    for pydir in sorted(root.glob("apps/Python3*")):
                        for name in self._python_names():
                            candidates.append(str(pydir / name))
                # Also check root/bin for Unix-style or older OSGeo4W installs
                for name in self._python_names():
                    candidates.append(str(root / "bin" / name))
        except (OSError, ValueError):
            pass

        # 5. Walk sys.path to catch conda/envs and odd installs
        seen_roots = set()
        for entry in sys.path:
            try:
                p = Path(entry).resolve()
                for _ in range(3):
                    key = str(p)
                    if key not in seen_roots:
                        seen_roots.add(key)
                        for name in self._python_names():
                            candidates.append(str(p / name))
                            if system != "Windows":
                                candidates.append(str(p / "bin" / name))
                            else:
                                candidates.append(str(p / "Scripts" / name))
                    p = p.parent
            except (OSError, ValueError):
                continue

        # 6. Test candidates in order
        seen = set()
        for p in candidates:
            p = str(p).strip()
            if not p or p in seen:
                continue
            seen.add(p)
            if self._validate(p):
                return self._cache(p)

        return ""

    def _validate(self, path):
        """
        A path is valid only if:
          1. It exists and is a file
          2. Its name contains 'python' (avoids QGIS binaries)
          3. Running 'import pip' succeeds
        We do NOT reject based on folder names — that breaks OSGeo4W & QGIS.
        """
        if not path:
            return False

        p = Path(path)
        if not p.exists() or not p.is_file():
            return False

        name = p.name.lower()
        # Reject known QGIS application binaries
        qgis_bins = {
            "qgis.exe", "qgis-bin.exe", "qgis-ltr-bin.exe",
            "qgis-bin-g7.4.2.exe", "qgis-ltr-bin-g7.4.2.exe",
            "qgis", "qgis-ltr", "qgis-bin",
        }
        if name in qgis_bins:
            return False

        # If it doesn't look like a Python binary, skip it
        if "python" not in name:
            return False

        safe_cwd = (os.environ.get("TEMP")
                    or os.environ.get("TMP")
                    or tempfile.gettempdir()
                    or str(Path.home()))

        try:
            r = subprocess.run(
                [path, "-c", "import pip; print(pip.__version__)"],
                capture_output=True, text=True, timeout=10,
                creationflags=SUBPROCESS_FLAGS, cwd=safe_cwd,
            )
            return r.returncode == 0 and bool(r.stdout.strip())
        except Exception:
            return False

    def _cache(self, path):
        self.settings.setValue("pip_manager/python_path", path)
        return path

    def _prompt_python_path(self):
        system = platform.system()
        example = (
            "C:/OSGeo4W/apps/Python312/python.exe"
            if system == "Windows"
            else "/usr/bin/python3"
        )
        path, ok = QInputDialog.getText(
            self.iface.mainWindow(),
            "Set Python Path",
            "Auto-detection failed.\nPaste the full path to the Python executable\n"
            "e.g. {}".format(example),
            text="",
        )
        if ok:
            path = path.strip()
            if self._validate(path):
                return self._cache(path)
            QMessageBox.critical(
                self.iface.mainWindow(), "Invalid Path",
                "Not a valid Python with pip:\n{}".format(path))
        return ""
