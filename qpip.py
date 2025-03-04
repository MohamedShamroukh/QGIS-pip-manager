# qpip.py
import subprocess
import os

class QGISPipManager:
    def __init__(self, qgis_python_path):
        # Use provided path, or fallback to a default if needed.  Raise error if still not valid
        self.qgis_python_path = qgis_python_path
        if not self.qgis_python_path or not os.path.exists(self.qgis_python_path):
            raise ValueError("Invalid QGIS Python path provided.")

        print(f"QGIS Python path: {self.qgis_python_path}")  # Debugging

        # Ensure pip is available
        try:
            subprocess.run([self.qgis_python_path, '-m', 'pip', '--version'], check=True, capture_output=True)
            print("pip version check successful")  # Debugging
        except FileNotFoundError as e:
            print(f"QGIS Python or pip not found: {e}")
            print(f"Error: {e}")  # More specific error message
            raise  # Re-raise the exception to signal the issue

    def get_installed_packages(self):
        """Returns a list of installed packages within the QGIS environment."""
        import json
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
