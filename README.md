Mohamed Shamroukh is a doctoral researcher at The Impact Hub, School of Architecture, Building and Civil Engineering, Loughborough University. He specialises in Geospatial Intelligence, GIS, Remote Sensing, Urban Planning, and GeoAI (Geospatial Artificial Intelligence). His PhD research focuses on data-driven modelling, geospatial analysis, and machine learning for pedestrian-friendly urban planning and sustainable city development. Mohamed has extensive expertise in geospatial data science, urban analytics, spatial modelling, Python programming, and geospatial databases. He has conducted research and teaching in GIS, remote sensing, and urban studies, including experience as a research and teaching assistant at South Valley University, Egypt. His projects include WiFi-based pedestrian monitoring, point of interest (POI) analysis, street network, and geospatial data integration.

# QGIS pip Manager Plugin

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![QGIS Version](https://img.shields.io/badge/QGIS-3.x-green)](https://qgis.org)
[![Version](https://img.shields.io/badge/Version-0.0.4-blue)](https://github.com/MohamedShamroukh/QGIS-pip-manager/releases)

## Description

The QGIS Pip Manager plugin is a powerful utility designed to simplify Python package management directly within your QGIS environment. It provides a robust, user-friendly interface for searching, installing, uninstalling, and managing specific versions of packages using `pip`. This eliminates the need for command-line interaction and is essential for extending QGIS functionality through external Python libraries.

## Key Features

*   **Complete Package Control:** Effortlessly **Install, Uninstall, Upgrade,** or **Downgrade** packages to a specific version.
*   **Asynchronous Operations:** Package listings and installation/uninstallation run in the background, preventing the QGIS interface from freezing.
*   **Intuitive UX:** Features include package list **filtering,** **search highlighting,** and **log clearing** for a streamlined experience.
*   **Quiet Execution:** Subprocess calls (pip operations) run silently on Windows, suppressing disruptive command-line pop-up windows.
*   **Robust Error Handling:** Features improved automatic Python Path detection and clear guidance for **Permission Denied** errors on Windows (UAC).
*   **Dependency Info:** Retrieve detailed information (`pip show`) for installed packages.

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
3.  **Installed Packages:** The list automatically populates with all installed packages (asynchronously). Use the filter box to quickly narrow the list.
4.  **Install/Upgrade:** Enter a package name, optionally select a version from the dropdown, and click **Install/Upgrade**. A QGIS restart prompt will follow successful completion.
5.  **Uninstall:** Enter a package name in the text field or click an item in the list, then click **Uninstall**.

## Configuration

*   The plugin automatically detects the QGIS Python executable path.
*   If automatic detection fails, you will be prompted to enter the path manually.
*   The path is stored persistently in QGIS settings.

## Dependencies

*   QGIS 3.x
*   Python 3.7 or higher (matching the QGIS Python environment)
*   Required Python packages: `requests`, `geopandas`, `shapely`, `packaging` (automatically checked and installed if missing during plugin load).

## Troubleshooting

*   **Plugin doesn't load/Permission Denied:** On Windows, if you encounter "Access is denied" errors, try closing QGIS and running it **"As Administrator."**
*   **"Invalid Python Path" error:** Verify that the path to the QGIS Python executable is correct.
*   **Package operation fails:** Check your internet connection. If the problem persists, review the output log in the plugin dialog for detailed error messages from `pip`.

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
