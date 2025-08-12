Mohamed Shamroukh is a doctoral researcher at The Impact Hub, School of Architecture, Building and Civil Engineering, Loughborough University. He specialises in Geospatial Intelligence, GIS, Remote Sensing, Urban Planning, and GeoAI (Geospatial Artificial Intelligence). His PhD research focuses on data-driven modelling, geospatial analysis, and machine learning for pedestrian-friendly urban planning and sustainable city development. Mohamed has extensive expertise in geospatial data science, urban analytics, spatial modelling, Python programming, and geospatial databases. He has conducted research and teaching in GIS, remote sensing, and urban studies, including experience as a research and teaching assistant at South Valley University, Egypt. His projects include WiFi-based pedestrian monitoring, point of interest (POI) analysis, street network, and geospatial data integration.
# QGIS Pip Manager Plugin

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![QGIS Version](https://img.shields.io/badge/QGIS-3.x-green)](https://qgis.org)

## Description

The QGIS Pip Manager plugin simplifies the process of managing Python packages within your QGIS environment. It provides a user-friendly interface for searching, installing, and uninstalling packages using `pip`, the Python package installer.  This plugin aims to streamline extending QGIS functionality through Python packages without requiring users to directly interact with the command line.

## Features

*   **Effortless Package Management:** Install, uninstall, and search for Python packages directly within QGIS.
*   **Dependency Resolution:** Simplifies dependency management for other QGIS plugins.
*   **Intuitive Interface:** Provides a simple and intuitive graphical user interface.
*   **Automatic Python Path Detection:** Automatically detects the correct Python executable used by QGIS.
*   **Robust Error Handling:** Clearly displays error messages to the user when package operations fail.

## Screenshots

Here are a few screenshots demonstrating the plugin's functionality:

| Feature               | Screenshot                                                                                                                                                                                                                                                          |
|-----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Plugin Dialog         | [![Plugin Dialog](https://github.com/MohamedShamroukh/QGIS-pip-manager/blob/main/QGIS%20pip%20Manager/plugin_dialog.png?raw=true)](https://github.com/MohamedShamroukh/QGIS-pip-manager/blob/main/QGIS%20pip%20Manager/plugin_dialog.png?raw=true)                     |
| Uninstalling Packages | [![Uninstalling Packages](https://github.com/MohamedShamroukh/QGIS-pip-manager/blob/main/QGIS%20pip%20Manager/uninstalling_packages.png?raw=true)](https://github.com/MohamedShamroukh/QGIS-pip-manager/blob/main/QGIS%20pip%20Manager/uninstalling_packages.png?raw=true)   |
| Installing Packages   | [![Installing Packages](https://github.com/MohamedShamroukh/QGIS-pip-manager/blob/main/QGIS%20pip%20Manager/installing_packages.png?raw=true)](https://github.com/MohamedShamroukh/QGIS-pip-manager/blob/main/QGIS%20pip%20Manager/installing_packages.png?raw=true)     |

*Click on the images to view them in full size.*

## Installation

1.  Download the plugin as a ZIP file from the [Releases](https://github.com/MohamedShamroukh/QGIS-pip-manager/releases) page.
2.  In QGIS, go to `Plugins > Manage and Install Plugins...`
3.  Click on `Install from ZIP` and select the downloaded ZIP file.
4.  The plugin will be installed, and you'll find it under the `Plugins` menu.

## Usage

1.  After installation, find the plugin in the QGIS menu under `Plugins > QGIS Pip Manager`.
2.  Click on `QGIS Pip Manager` to open the plugin dialog.
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
*   Required Python packages: `requests`, `geopandas`, `shapely`, `packaging` (automatically installed if missing).  It's worth noting that `packaging` will be automatically installed if missing.

## Troubleshooting

*   **Plugin doesn't load:** Ensure that the required Python packages are installed. If not, try installing them manually using the QGIS Python console and `pip`.
*   **"Invalid Python Path" error:** Verify that the path to the QGIS Python executable is correct.
*   **Package installation fails:** Check your internet connection and try again. If the problem persists, there might be compatibility issues with the package and your QGIS environment.  Also, ensure the package is compatible with your QGIS and Python versions.

## Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue on the [Issues](https://github.com/MohamedShamroukh/QGIS-pip-manager/issues) page. If you'd like to contribute code, please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them with descriptive commit messages.
4.  Submit a pull request.

## License

This plugin is licensed under the [MIT License](LICENSE).

## Authors

Mohamed Shamroukh, Asya Natapov and Taimaz Larimian

## Contact

*   [m.shamroukh@lboro.ac.uk](mailto:m.shamroukh@lboro.ac.uk)
*   [https://www.linkedin.com/in/mohamed-shamroukh-348083126/](https://www.linkedin.com/in/mohamed-shamroukh-348083126/)
