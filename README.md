# QGIS Pip Manager Plugin

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![QGIS Version](https://img.shields.io/badge/QGIS-3.x-green)](https://qgis.org)
[![Version](https://img.shields.io/badge/Version-0.1.0-blue)](https://github.com/MohamedShamroukh/QGIS-pip-manager/releases)

## Description

The **QGIS Pip Manager** plugin is a powerful utility designed to simplify Python package management directly within your QGIS environment. It provides a robust, tabbed user interface for searching, installing, uninstalling, upgrading, downgrading, and managing Python packages using `pip` — all without touching the command line.

Whether you need a single library or an entire data-science stack, QGIS Pip Manager handles it asynchronously so your QGIS interface never freezes.

## Key Features

*   **Complete Package Control:** Effortlessly **Install, Uninstall, Upgrade,** or **Downgrade** packages to a specific version.
*   **PyPI Live Search:** Type a package name and get real-time metadata from PyPI (summary, author, Python requirements).
*   **Version Selection:** Fetch available versions from PyPI and pick exactly the one you need.
*   **Asynchronous Operations:** All pip operations run in background threads — the QGIS UI stays responsive.
*   **Package List Filtering:** Instantly filter your installed packages by name.
*   **Snapshots:** Save your current environment as a timestamped requirements file and restore it later — perfect for rolling back bad installs.
*   **Presets:** One-click installation of common GIS / data-science stacks (Data Science, Geospatial, Hydrology, Remote Sensing). Edit `presets.json` to add your own.
*   **requirements.txt Support:** Import and export full environments via standard `requirements.txt` files.
*   **Conflict & Outdated Checks:** Run `pip check` and `pip list --outdated` directly from the GUI.
*   **Dry-Run Install:** Preview what an install would change before committing.
*   **Conda Support:** Optionally use `conda` / `mamba` instead of `pip` when working in a conda environment.
*   **Custom Index URLs:** Configure private PyPI mirrors, extra index URLs, and HTTP proxies from the Settings tab.
*   **Cross-Platform:** Works on **Windows** (OSGeo4W & standalone), **macOS**, and **Linux**.
*   **PyQt5 / PyQt6 Compatible:** Runs on both QGIS 3 (PyQt5) and future QGIS 4 (PyQt6) builds.
*   **Quiet Execution:** Subprocess calls run silently on Windows — no disruptive command-line pop-ups.
*   **Robust Error Handling:** Improved automatic Python path detection and clear guidance for **Permission Denied** errors (UAC).

## Screenshots

| Feature | Screenshot |
|---------|------------|
| Packages Tab | *List, filter, and manage installed packages* |
| Install Tab | *Search PyPI, pick versions, install or dry-run* |
| Snapshots Tab | *Save and restore environment snapshots* |
| Presets Tab | *One-click install of common stacks* |
| Settings Tab | *Configure proxies, index URLs, and paths* |

## Installation

1.  Download the plugin as a ZIP file from the [Releases](https://github.com/MohamedShamroukh/QGIS-pip-manager/releases) page.
2.  In QGIS, go to `Plugins > Manage and Install Plugins...`
3.  Click on `Install from ZIP` and select the downloaded ZIP file.
4.  The plugin will be installed, and you'll find it under the `Plugins` menu.

## Usage

1.  After installation, find the plugin in the QGIS menu under `Plugins > QGIS Pip Manager`.
2.  Click on **QGIS Pip Manager** to open the plugin dialog.

### Tabs

**Packages**
*   The list automatically populates with all installed packages.
*   Use the **Filter** box to quickly narrow the list.
*   Click a package to auto-fill the install field and fetch its versions.
*   **Refresh**, **Check Outdated**, and **Check Conflicts** buttons keep your environment healthy.

**Install**
*   Type a package name in the **PyPI Search** field — live info appears after a short pause.
*   Select a version from the dropdown (or leave as **Latest**).
*   Click **Install / Upgrade** or **Dry-run Check** to preview changes.
*   Use **Import / Export requirements.txt** to move whole environments in or out.

**Snapshots**
*   Click **Save Snapshot Now** to capture your current environment.
*   Select a snapshot and click **Restore Selected** to roll back.
*   **Delete Selected** removes old snapshots you no longer need.

**Presets**
*   Select a preset (e.g., *Data Science*, *Geospatial*) and click **Install Selected Preset**.
*   Edit `presets.json` in the plugin folder to add custom stacks.

**Settings**
*   Set **HTTP/HTTPS Proxy**, **Index URL**, **Extra Index URL**, and **Snapshots folder**.
*   The detected Python path and pip version are displayed for verification.
*   All settings persist across QGIS sessions.

## Configuration

*   The plugin **automatically detects** the QGIS Python executable path on first run.
*   If auto-detection fails, you will be prompted to enter the path manually.
*   The path is stored persistently in QGIS settings (`pip_manager/python_path`).

## Dependencies

*   QGIS 3.x
*   Python 3.7 or higher (matching the QGIS Python environment)
*   `pip` must be available in the detected Python environment.

> **Note:** Earlier versions required `requests`, `geopandas`, `shapely`, and `packaging` to be pre-installed. These hard dependencies have been removed — the plugin now uses only the Python standard library plus `pip`.

## Troubleshooting

*   **Plugin doesn't load / Permission Denied:** On Windows, if you encounter "Access is denied" errors, try closing QGIS and running it **"As Administrator."**
*   **"Invalid Python Path" error:** Verify that the path to the QGIS Python executable is correct in the **Settings** tab.
*   **Buttons do nothing / empty package list:** This usually means the detected Python path is wrong. Go to **Settings**, check the displayed Python path, and correct it if necessary.
*   **Package operation fails:** Check your internet connection. If the problem persists, review the output **Log** in the plugin dialog for detailed error messages from `pip`.

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
