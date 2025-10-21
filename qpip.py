# qpip.py
import subprocess
import os
import json # json is only used in get_installed_packages, but kept here for clarity.
from qgis.PyQt.QtWidgets import QMessageBox # Import for user-facing message

class QGISPipManager:
    def __init__(self, qgis_python_path):
        self.is_initialized_ok = False # <-- NEW STATUS FLAG: Set to True only on success
        
        # Use provided path, or fallback to a default if needed.  Raise error if still not valid
        self.qgis_python_path = qgis_python_path
        if not self.qgis_python_path or not os.path.exists(self.qgis_python_path):
            raise ValueError("Invalid QGIS Python path provided.")

        print(f"QGIS Python path: {self.qgis_python_path}")  # Debugging

        # Ensure pip is available
        try:
            # ORIGINAL PROBLEM LINE: subprocess.run([self.qgis_python_path, '-m', 'pip', '--version'], check=True, capture_output=True)
            subprocess.run([self.qgis_python_path, '-m', 'pip', '--version'], check=True, capture_output=True)
            print("pip version check successful")  # Debugging
            self.is_initialized_ok = True # <-- Set to True on successful command execution

        # --- FIX APPLIED HERE: Catch PermissionError (WinError 5) ---
        except PermissionError as e:
            # Display a user-friendly error message using QMessageBox
            error_message = (
                "The Pip Manager plugin failed to start due to a Permission Error.\n\n"
                "**Error Details:** Access is denied when trying to execute the QGIS "
                "Python interpreter to check the 'pip' version.\n\n"
                "**Solution:** Please close QGIS and **Run QGIS as an Administrator** "
                "to resolve this issue and use the plugin."
            )
            
            # Show a critical error message box
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Pip Manager Startup Failed")
            msg.setInformativeText(error_message)
            msg.setWindowTitle("Permission Error")
            msg.exec_()
            
            # Keep self.is_initialized_ok as False and do NOT raise an exception.
            
        # -----------------------------------------------------------

        except FileNotFoundError as e:
            print(f"QGIS Python or pip not found: {e}")
            print(f"Error: {e}")  # More specific error message
            # Keep self.is_initialized_ok as False and do NOT raise an exception.
            
    # --- NEW HELPER METHOD ---
    def is_ready(self):
        """Returns True if the initialization check (pip --version) was successful."""
        return self.is_initialized_ok

    def get_installed_packages(self):
        """Returns a list of installed packages within the QGIS environment."""
        if not self.is_ready():
            print("ERROR: QGISPipManager is not ready. Cannot get installed packages.")
            return []

        try:
            process = subprocess.run([self.qgis_python_path, '-m', 'pip', 'list', '--format=json'], capture_output=True, text=True)
            output = process.stdout
            packages = json.loads(output)
            print(f"Successfully retrieved installed packages: {packages}")  # Debugging
            return packages

        except Exception as e:
            print(f"Error getting installed packages: {e}")
            return []

    def search_package(self, package_name):
        if not self.is_ready():
            print("ERROR: QGISPipManager is not ready. Cannot search for package.")
            return ""

        try:
            print(f"Searching for package: {package_name}...")  # Log start
            process = subprocess.run([self.qgis_python_path, '-m', 'pip', 'search', package_name], capture_output=True, text=True)
            output = process.stdout
            print(f"Search results for {package_name}: {output}")  # Debugging
            print(f"Search completed for {package_name}.")  # Log end
            return output
        except Exception as e:
            print(f"Error searching for package: {e}")
            return ""

    def install_package(self, package_name, version=None):
        """Installs a package into the QGIS environment."""
        if not self.is_ready():
            print("ERROR: QGISPipManager is not ready. Cannot install package.")
            return False

        try:
            package_spec = f"{package_name}=={version}" if version else package_name
            print(f"Installing {package_spec}...")  # Log start
            process = subprocess.run([self.qgis_python_path, '-m', 'pip', 'install', package_spec], capture_output=True, text=True)

            if process.returncode == 0:
                print(f"Successfully installed {package_spec}")  # Log success
                print(f"Installation completed for {package_spec}.")  # Log end
                return True
            else:
                error_message = f"Error installing {package_spec}: {process.stderr}"
                print(error_message)
                return False
        except Exception as e:
            error_message = f"Error installing package: {e}"
            print(error_message)
            return False

    def uninstall_package(self, package_name):
        """Uninstalls a package from the QGIS environment."""
        if not self.is_ready():
            print("ERROR: QGISPipManager is not ready. Cannot uninstall package.")
            return False

        try:
            print(f"Uninstalling {package_name}...")  # Log start
            process = subprocess.run([self.qgis_python_path, '-m', 'pip', 'uninstall', '-y', package_name], capture_output=True, text=True)
            if process.returncode == 0:
                print(f"Successfully uninstalled {package_name}")  # Log success
                print(f"Uninstallation completed for {package_name}.")  # Log end
                return True
            else:
                print(f"Error uninstalling {package_name}: {process.stderr}")  #Print stderr
                return False
        except Exception as e:
            print(f"Error uninstalling package: {e}")
            return False

    def get_package_versions(self, package_name):
        """Retrieves available versions for a package from PyPI."""
        if not self.is_ready():
            print("ERROR: QGISPipManager is not ready. Cannot get package versions.")
            return []

        try:
            process = subprocess.run([self.qgis_python_path, '-m', 'pip', 'index', 'versions', package_name], capture_output=True, text=True)
            output = process.stdout
            # Parse the output to extract available versions
            versions = []
            # Parse based on output format
            return versions

        except Exception as e:
            print(f"Error getting package versions: {e}")
            return []
