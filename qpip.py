# qpip.py 
import subprocess
import os
import json
import platform
import re # Import regex for parsing pip index versions output

# Define creation flags for subprocess on Windows to hide the console window
if platform.system() == "Windows":
    # CREATE_NO_WINDOW is 0x08000000
    CREATE_NO_WINDOW = 0x08000000
    SUBPROCESS_FLAGS = CREATE_NO_WINDOW
else:
    SUBPROCESS_FLAGS = 0


class QGISPipManager:
    def __init__(self, qgis_python_path):
        self.qgis_python_path = qgis_python_path
        if not self.qgis_python_path or not os.path.exists(self.qgis_python_path):
            raise ValueError("Invalid QGIS Python path provided.")

        print(f"QGIS Python path: {self.qgis_python_path}")

        try:
            subprocess.run([self.qgis_python_path, '-m', 'pip', '--version'],
                           check=True,
                           capture_output=True,
                           creationflags=SUBPROCESS_FLAGS)
            print("pip version check successful")
        except PermissionError as e:
            error_message = (
                "Permission Error: Access is denied when trying to execute the QGIS Python interpreter. "
                "This often happens on Windows due to User Account Control (UAC). "
                "Please close QGIS and try running it 'As Administrator' to use the Pip Manager functionality."
            )
            print(f"PermissionError during pip check: {e}")
            raise PermissionError(error_message) from e
        except FileNotFoundError as e:
            print(f"QGIS Python or pip not found: {e}")
            print(f"Error: {e}")
            raise

    def get_installed_packages(self):
        """Returns a list of installed packages within the QGIS environment."""
        try:
            process = subprocess.run([self.qgis_python_path, '-m', 'pip', 'list', '--format=json'],
                                     capture_output=True,
                                     text=True,
                                     creationflags=SUBPROCESS_FLAGS)
            output = process.stdout
            packages = json.loads(output)
            return packages

        except Exception as e:
            print(f"Error getting installed packages: {e}")
            return []

    def search_package(self, package_name):
        try:
            print(f"Searching for package: {package_name}...")
            # Note: pip search is deprecated and might return unstructured output, keeping the raw output for now.
            process = subprocess.run([self.qgis_python_path, '-m', 'pip', 'search', package_name],
                                     capture_output=True,
                                     text=True,
                                     creationflags=SUBPROCESS_FLAGS)
            output = process.stdout
            print(f"Search completed for {package_name}.")
            return output
        except Exception as e:
            print(f"Error searching for package: {e}")
            return f"Error: {e}"

    def install_package(self, package_name, version=None):
        """Installs a package into the QGIS environment."""
        try:
            package_spec = f"{package_name}=={version}" if version else package_name
            print(f"Installing {package_spec}...")
            process = subprocess.run([self.qgis_python_path, '-m', 'pip', 'install', package_spec],
                                     capture_output=True,
                                     text=True,
                                     creationflags=SUBPROCESS_FLAGS)

            if process.returncode == 0:
                print(f"Successfully installed {package_spec}")
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
            print(f"Uninstalling {package_name}...")
            process = subprocess.run([self.qgis_python_path, '-m', 'pip', 'uninstall', '-y', package_name],
                                     capture_output=True,
                                     text=True,
                                     creationflags=SUBPROCESS_FLAGS)
            if process.returncode == 0:
                print(f"Successfully uninstalled {package_name}")
                return True
            else:
                print(f"Error uninstalling {package_name}: {process.stderr}")
                return False
        except Exception as e:
            print(f"Error uninstalling package: {e}")
            return False

    def get_package_versions(self, package_name):
        """Retrieves available versions for a package from PyPI."""
        try:
            # Use 'pip index versions' as 'pip install package==*' doesn't work for listing versions
            process = subprocess.run([self.qgis_python_path, '-m', 'pip', 'index', 'versions', package_name],
                                     capture_output=True,
                                     text=True,
                                     creationflags=SUBPROCESS_FLAGS)
            output = process.stdout

            # Example parsing for output: "Available versions: 1.0, 1.1, 1.2"
            match = re.search(r'Available versions: (.*)', output)
            if match:
                versions_str = match.group(1).strip()
                # Clean up the string (remove ' (latest)') and split by comma
                versions = [v.split(' ')[0] for v in versions_str.split(',')]
                # Filter out empty strings and return the list
                return [v for v in versions if v]
            else:
                return [f"Could not parse versions for {package_name}"]

        except Exception as e:
            print(f"Error getting package versions: {e}")
            return [f"Error: {e}"]
            
    def get_package_details(self, package_name):
        """Retrieves detailed information for an installed package using 'pip show'."""
        try:
            process = subprocess.run([self.qgis_python_path, '-m', 'pip', 'show', package_name],
                                     capture_output=True,
                                     text=True,
                                     creationflags=SUBPROCESS_FLAGS)
            
            if process.returncode == 0:
                return process.stdout
            else:
                return f"Package '{package_name}' not found or error: {process.stderr}"
        except Exception as e:
            return f"Error retrieving details: {e}"
