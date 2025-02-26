# my_pip_manager_plugin.py
import subprocess
import os
import platform
from qgis.core import QgsApplication, QgsSettings
from qgis.utils import iface
from .my_pip_manager_dialog import PipManagerDialog
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QAction, QMessageBox, QInputDialog
from PyQt5.QtGui import QIcon
import importlib


def check_library(library_name):
    """Checks if a Python library is installed."""
    try:
        importlib.import_module(library_name)
        return True
    except ImportError:
        return False


def install_library(library_name, qgis_python_path):
    """Installs a Python library using pip within the QGIS environment."""
    try:
        os_type = platform.system()
        if os_type == 'Windows':
            subprocess.check_call([qgis_python_path, "-m", "pip", "install", library_name],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        elif os_type == 'Linux' or os_type == 'Darwin':  # Darwin is macOS
            subprocess.check_call([qgis_python_path, "-m", "pip3", "install", library_name],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            print(f"Unsupported operating system: {os_type}")
            return False

        print(f"Successfully installed {library_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing {library_name}: {e.stderr.decode()}")  # Print stderr
        return False
    except FileNotFoundError:
        print("QGIS Python executable not found.")
        return False


class MyPipManagerPlugin(QObject):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.dlg = None
        self.action = None
        self.required_libraries = ["requests", "geopandas", "shapely", "packaging"]
        self.qgis_python_path = self.get_qgis_python_path()

    def initGui(self):
        """Called when the plugin is loaded."""
        # Create action that will start plugin configuration
        self.action = QAction(QIcon(":/plugins/pip_manager/icon.png"),  # Use the icon
                              "Pip Manager", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu("My Plugins", self.action)
        self.iface.addToolBarIcon(self.action)

        missing_libraries = []
        for library in self.required_libraries:
            if not check_library(library):
                missing_libraries.append(library)

        if missing_libraries:
            message = "The following required libraries are missing:\n" + "\n".join(missing_libraries) + "\n\nDo you want to install them automatically?"
            reply = QMessageBox.question(self.iface.mainWindow(), 'Missing Libraries',
                                         message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                if not self.qgis_python_path:
                    self.qgis_python_path = self.prompt_for_python_path()

                if self.qgis_python_path:
                    for library in missing_libraries:
                        if not install_library(library, self.qgis_python_path):
                            QMessageBox.critical(self.iface.mainWindow(), "Error",
                                                 f"Failed to install {library}.  The plugin may not function correctly.")
                            return

                    QMessageBox.information(self.iface.mainWindow(), "Success",
                                            "All required libraries installed.  Please restart QGIS.")
                    return
                else:
                    QMessageBox.warning(self.iface.mainWindow(), "Warning",
                                        "Could not determine QGIS Python path.  Cannot install required libraries.")
            else:
                QMessageBox.warning(self.iface.mainWindow(), "Warning",
                                    "The plugin may not function correctly without the required libraries.")

    def unload(self):
        """Called when the plugin is unloaded."""
        if self.action:
            self.iface.removePluginMenu("My Plugins", self.action)
            self.iface.removeToolBarIcon(self.action)
            if self.dlg:
                self.dlg.close()

    def run(self):
        """Called when the plugin's action is triggered."""
        if not self.qgis_python_path:
            self.qgis_python_path = self.prompt_for_python_path()
            if not self.qgis_python_path:
                QMessageBox.critical(self.iface.mainWindow(), "Error", "QGIS Python path is not set. Plugin cannot run.")
                return

        if self.dlg is None:
            self.dlg = PipManagerDialog(qgis_python_path=self.qgis_python_path)  # Pass the path
        self.dlg.show()

    def get_qgis_python_path(self):
        """Gets the QGIS Python path from settings or tries to determine it automatically."""
        settings = QgsSettings()
        python_path = settings.value("pip_manager/python_path")
        if python_path:
            return python_path

        # Attempt to automatically find the path
        qgis_prefix_path = QgsApplication.prefixPath()

        possible_paths = []
        if platform.system() == 'Windows':
            possible_paths.append(os.path.join(qgis_prefix_path, "python3.exe"))  # Basic path
            possible_paths.append(os.path.join(qgis_prefix_path, "apps", "Python39", "python.exe"))  # QGIS 3.22 and earlier
            possible_paths.append(os.path.join(qgis_prefix_path, "apps", "Python310", "python.exe"))  # QGIS 3.22
            possible_paths.append(os.path.join(qgis_prefix_path, "apps", "Python311", "python.exe"))  # QGIS 3.28
            possible_paths.append(os.path.join(qgis_prefix_path, "apps", "Python312", "python.exe"))  # QGIS 3.36 and later
            possible_paths.append(os.path.join(qgis_prefix_path, "apps", "Python37", "python.exe"))  # older qgis version
            possible_paths.append(os.path.join(qgis_prefix_path, "apps", "Python38", "python.exe"))  # older qgis version

            # Look for the path with out /apps/
            possible_paths.append(os.path.join(qgis_prefix_path, "Python39", "python.exe"))  # QGIS 3.22 and earlier
            possible_paths.append(os.path.join(qgis_prefix_path, "Python310", "python.exe"))  # QGIS 3.22
            possible_paths.append(os.path.join(qgis_prefix_path, "Python311", "python.exe"))  # QGIS 3.28
            possible_paths.append(os.path.join(qgis_prefix_path, "Python312", "python.exe"))  # QGIS 3.36 and later
            possible_paths.append(os.path.join(qgis_prefix_path, "Python37", "python.exe"))  # older qgis version
            possible_paths.append(os.path.join(qgis_prefix_path, "Python38", "python.exe"))  # older qgis version

            # Check for OSGeo4W installation (common)
            possible_paths.append(os.path.join("C:\\OSGeo4W64", "bin", "python3.exe"))  # Common OSGeo4W path
            possible_paths.append(os.path.join("C:\\OSGeo4W", "bin", "python3.exe"))  # 32-bit OSGeo4W path

        else:  # Linux or macOS
            possible_paths.append(os.path.join(qgis_prefix_path, "bin", "python3"))  # Basic path
            possible_paths.append(os.path.join(qgis_prefix_path, "python3"))  # Sometimes directly in prefix path

            # Try some common alternative paths on linux and mac
            possible_paths.append(os.path.join(qgis_prefix_path, "bin", "python"))
            possible_paths.append(os.path.join(qgis_prefix_path, "python"))

            # Check for python3 with version number
            possible_paths.append(os.path.join(qgis_prefix_path, "bin", "python3.9"))
            possible_paths.append(os.path.join(qgis_prefix_path, "bin", "python3.10"))
            possible_paths.append(os.path.join(qgis_prefix_path, "bin", "python3.11"))
            possible_paths.append(os.path.join(qgis_prefix_path, "bin", "python3.12"))

            possible_paths.append(os.path.join(qgis_prefix_path, "python3.9"))
            possible_paths.append(os.path.join(qgis_prefix_path, "python3.10"))
            possible_paths.append(os.path.join(qgis_prefix_path, "python3.11"))
            possible_paths.append(os.path.join(qgis_prefix_path, "python3.12"))

        for path in possible_paths:
            if os.path.exists(path):
                self.set_qgis_python_path(path)
                return path

        return None  # Path not found

    def set_qgis_python_path(self, path):
        """Saves the QGIS Python path to QGIS settings."""
        settings = QgsSettings()
        settings.setValue("pip_manager/python_path", path)
        self.qgis_python_path = path

    def prompt_for_python_path(self):
        """Prompts the user to enter the QGIS Python executable path."""
        path, ok = QInputDialog.getText(self.iface.mainWindow(), "QGIS Python Path",
                                         "Enter the path to the QGIS Python executable:",
                                         text=self.qgis_python_path if self.qgis_python_path else "")

        if ok:
            path = path.strip()
            if os.path.exists(path):
                self.set_qgis_python_path(path)
                return path
            else:
                QMessageBox.critical(self.iface.mainWindow(), "Error", "Invalid path. Please try again.")
                return self.prompt_for_python_path()  # Recursive call to re-prompt
        return None


def classFactory(iface):
    """Instantiates the plugin class."""
    return MyPipManagerPlugin(iface)