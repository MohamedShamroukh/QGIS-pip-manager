# QGIS Pip Manager Plugin

## Description

The QGIS Pip Manager plugin allows users to manage Python packages within their QGIS environment. It provides a user-friendly interface for searching, installing, and uninstalling packages using `pip`, the Python package installer. This plugin aims to simplify the process of extending QGIS functionality through Python packages without requiring users to directly interact with the command line.

## Features

*   **Package Management:** Install, uninstall, and search for Python packages directly within QGIS.
*   **Dependency Handling:**  Helps manage dependencies for other QGIS plugins.
*   **User-Friendly Interface:** Provides a simple and intuitive graphical interface.
*   **Automatic Python Path Detection:** Attempts to automatically locate the correct Python executable used by QGIS.
*   **Error Handling:** Displays error messages to the user when package operations fail.

## Installation

1.  Download the plugin as a ZIP file from the GitHub repository.
2.  In QGIS, go to `Plugins > Manage and Install Plugins...`
3.  Click on `Install from ZIP` and select the downloaded ZIP file.
4.  The plugin will be installed, and you'll find it under the `My Plugins` menu.

## Usage

1.  After installation, find the plugin in the QGIS menu under `My Plugins > Pip Manager`.
2.  Click on `Pip Manager` to open the plugin dialog.
3.  **Search:** Enter a package name in the search field and click `Search` to find available packages.
4.  **Install:** Enter a package name in the search field and click `Install` to install the package.
5.  **Uninstall:** Select a package from the list of installed packages and click `Uninstall` to remove it.
6.  If the plugin cannot automatically find the QGIS Python executable, you will be prompted to provide the path manually.

## Configuration

*   The plugin attempts to automatically find the QGIS Python executable path. If it fails, you will be prompted to enter the path manually.
*   The path is stored in QGIS settings and reused in subsequent sessions.

## Dependencies

*   QGIS 3.x
*   Python 3.7 or higher (matching the QGIS Python environment)
*   Required Python packages: `requests`, `geopandas`, `shapely`, `packaging` (automatically installed if missing).

## Troubleshooting

*   **Plugin doesn't load:** Ensure that the required Python packages are installed. If not, try installing them manually using the QGIS Python console and `pip`.
*   **"Invalid Python Path" error:** Verify that the path to the QGIS Python executable is correct.
*   **Package installation fails:** Check your internet connection and try again. If the problem persists, there might be compatibility issues with the package and your QGIS environment.

## Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue on the GitHub repository. If you'd like to contribute code, please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them with descriptive commit messages.
4.  Submit a pull request.

## License

This plugin is licensed under the [MIT License](LICENSE).

## Author

Mohamed Shamroukh and Asya Natapov

## Contact

[m.shamroukh@lboro.ac.uk](mailto:m.shamroukh@lboro.ac.uk)

[https://www.linkedin.com/in/mohamed-shamroukh-348083126/](https://www.linkedin.com/in/mohamed-shamroukh-348083126/)
