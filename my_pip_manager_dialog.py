# my_pip_manager_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QTreeWidget, QTreeWidgetItem, QMessageBox, QHBoxLayout, QComboBox, QWidget, QSizePolicy
from PyQt5.QtCore import QThread, pyqtSignal, QObject, Qt
from PyQt5.QtGui import QColor
from .qpip import QGISPipManager # Assuming qpip.py has been updated with get_package_versions and get_package_details

# --- Worker Class (Simplified for brevity, assuming full functionality from previous steps) ---
class Worker(QObject):
    finished = pyqtSignal()
    result = pyqtSignal(str)
    error = pyqtSignal(str)
    detailed_error = pyqtSignal(str)
    status = pyqtSignal(str)
    package_list = pyqtSignal(list)
    versions_list = pyqtSignal(list)
    
    def __init__(self, manager, operation, *args):
        super().__init__()
        self.manager = manager
        self.operation = operation
        self.args = args

    def run(self):
        try:
            if self.operation == "install":
                # Install/Upgrade/Downgrade logic uses manager.install_package
                pkg_name, version = self.args[0], (self.args[1] if len(self.args) > 1 else None)
                action = "Updating" if self.args[2] else "Installing" # args[2] is the boolean for is_update
                self.status.emit(f"{action} {pkg_name} to {version or 'latest'}...")
                success = self.manager.install_package(pkg_name, version)
                if not success:
                    self.detailed_error.emit(f"Failed to {action.lower()} {pkg_name}")
                    self.status.emit(f"Failed to {action.lower()} {pkg_name}. See error message.")
                else:
                    self.result.emit(f"SUCCESS: {action} {pkg_name} completed.") # NEW: Success message for final notification
                    self.status.emit(f"Successfully {action.lower().replace('ing', 'ed')} {pkg_name}.")
            elif self.operation == "uninstall":
                self.status.emit(f"Uninstalling {self.args[0]}...")
                success = self.manager.uninstall_package(*self.args)
                if not success:
                    self.error.emit(f"Failed to uninstall {self.args[0]}")
                    self.status.emit(f"Failed to uninstall {self.args[0]}. See error message.")
                else:
                    self.result.emit(f"SUCCESS: Uninstall {self.args[0]} completed.") # NEW: Success message for final notification
                    self.status.emit(f"Successfully uninstalled {self.args[0]}.")
            elif self.operation == "search":
                self.status.emit(f"Searching for {self.args[0]}...")
                result = self.manager.search_package(*self.args)
                self.result.emit(result)
                self.status.emit(f"Search completed for {self.args[0]}.")
            elif self.operation == "list_packages":
                self.status.emit("Retrieving installed packages...")
                packages = self.manager.get_installed_packages()
                self.package_list.emit(packages)
                self.status.emit("Package list retrieved.")
            elif self.operation == "get_versions":
                self.status.emit(f"Checking versions for {self.args[0]}...")
                versions = self.manager.get_package_versions(*self.args)
                self.versions_list.emit(versions)
                self.status.emit(f"Versions retrieved for {self.args[0]}.")
            elif self.operation == "get_details":
                self.status.emit(f"Retrieving details for {self.args[0]}...")
                details = self.manager.get_package_details(*self.args)
                self.result.emit(details)
                self.status.emit(f"Details retrieved for {self.args[0]}.")
                
        except Exception as e:
            self.error.emit(str(e))
            self.status.emit(f"An error occurred: {str(e)}")
        finally:
            self.finished.emit()

# --- PipManagerDialog Class ---
class PipManagerDialog(QDialog):
    def __init__(self, parent=None, qgis_python_path=None):
        super().__init__(parent)
        self.setWindowTitle("QGIS Pip Manager")
        self.qgis_pip_manager = QGISPipManager(qgis_python_path)

        self.layout = QVBoxLayout()
        
        # Package Filtering
        self.filter_field = QLineEdit()
        self.filter_field.setPlaceholderText("Filter installed packages...")
        self.filter_field.textChanged.connect(self._filter_package_list)
        self.layout.addWidget(self.filter_field)
        
        self.package_list = QTreeWidget()
        self.package_list.setHeaderLabels(["Name", "Version"])
        self.package_list.itemClicked.connect(self.package_item_clicked)
        self.package_list.setSelectionMode(QTreeWidget.SingleSelection) # Ensure only one can be selected
        self.layout.addWidget(self.package_list)
        
        # Input/Action Layout
        input_layout = QHBoxLayout()
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search or Enter Package Name...")
        input_layout.addWidget(self.search_field)
        
        self.version_combo = QComboBox()
        self.version_combo.addItem("Latest")
        self.version_combo.setToolTip("Select a specific version to install/upgrade/downgrade.")
        self.version_combo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        input_layout.addWidget(self.version_combo)
        
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_package)
        input_layout.addWidget(self.search_button)
        
        # New: Upgrade/Install Logic
        self.install_button = QPushButton("Install/Upgrade")
        self.install_button.clicked.connect(self.install_package)
        input_layout.addWidget(self.install_button)
        
        self.uninstall_button = QPushButton("Uninstall")
        self.uninstall_button.clicked.connect(self.uninstall_package)
        input_layout.addWidget(self.uninstall_button)
        
        self.layout.addLayout(input_layout)
        
        # Management/Details/Log Control Layout
        control_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.clicked.connect(self.populate_packages_async)
        control_layout.addWidget(self.refresh_button)
        
        self.details_button = QPushButton("Show Details")
        self.details_button.clicked.connect(self.show_package_details)
        control_layout.addWidget(self.details_button)
        
        self.clear_log_button = QPushButton("Clear Log") # NEW: Clear Log Button
        self.clear_log_button.clicked.connect(lambda: self.log_text.clear())
        control_layout.addWidget(self.clear_log_button)
        
        self.layout.addLayout(control_layout)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.layout.addWidget(self.log_text)

        self.setLayout(self.layout)
        self.installed_packages = [] # Store the complete list
        self.populate_packages_async()

    def _filter_package_list(self, text):
        """Filters the package list based on the text in the filter field."""
        filter_text = text.lower()
        
        # Clear existing items
        self.package_list.clear()
        
        # Populate with filtered list
        if not filter_text:
            packages_to_display = self.installed_packages
        else:
            packages_to_display = [p for p in self.installed_packages if filter_text in p["name"].lower()]

        for package in packages_to_display:
            item = QTreeWidgetItem([package["name"], package["version"]])
            self.package_list.addTopLevelItem(item)

    def populate_packages_async(self):
        """Starts a worker thread to list installed packages."""
        self.package_list.clear()
        self.filter_field.setText("")
        loading_item = QTreeWidgetItem(["Loading packages. Please wait...", ""])
        self.package_list.addTopLevelItem(loading_item)
        
        self.thread = QThread()
        self.worker = Worker(self.qgis_pip_manager, "list_packages")
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)

        self.worker.package_list.connect(self._update_package_list_ui)
        self.worker.status.connect(self.set_search_text)
        self.worker.error.connect(self.show_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.start()

    def _update_package_list_ui(self, packages):
        """Updates the TreeWidget and internal list with packages."""
        self.installed_packages = packages # Store the full list
        self.package_list.clear()
        
        # Call the filter method to populate the list from the stored data
        self._filter_package_list(self.filter_field.text()) 

    def package_item_clicked(self, item, column):
        """Populates the search field and triggers version check on item click."""
        package_name = item.text(0)
        self.search_field.setText(package_name)
        self.get_available_versions(package_name)
        
    def get_available_versions(self, package_name):
        # ... (Method remains the same as previous step, fetching versions asynchronously) ...
        self.version_combo.clear()
        self.version_combo.addItem("Fetching...")
        
        self.thread = QThread()
        self.worker = Worker(self.qgis_pip_manager, "get_versions", package_name)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        
        self.worker.versions_list.connect(self._update_version_combo)
        self.worker.status.connect(self.set_search_text)
        self.worker.error.connect(self.show_error)
        
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.start()

    def _update_version_combo(self, versions):
        # ... (Method remains the same as previous step) ...
        self.version_combo.clear()
        self.version_combo.addItem("Latest")
        
        for version in versions:
            if version and version != "Could not parse versions for":
                 self.version_combo.addItem(version)
        
        if self.version_combo.count() == 1 and self.version_combo.currentText() == "Latest":
            self.version_combo.addItem("No other versions")

    def search_package(self):
        package_name = self.search_field.text().strip()
        if not package_name:
            QMessageBox.warning(self, "Input Required", "Please enter a package name to search.")
            return

        # NEW: Highlight the package in the installed list if present
        self._highlight_package_in_list(package_name)

        self.thread = QThread()
        self.worker = Worker(self.qgis_pip_manager, "search", package_name)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.result.connect(self.set_search_text)
        self.worker.status.connect(self.set_search_text)
        self.worker.error.connect(self.show_error)
        self.thread.start()
        
    def _highlight_package_in_list(self, package_name):
        """Hihglights a package in the tree list if it exists."""
        item_found = self.package_list.findItems(package_name, Qt.MatchExactly, 0)
        self.package_list.clearSelection() # Clear previous selections
        
        if item_found:
            item = item_found[0]
            item.setSelected(True)
            self.package_list.scrollToItem(item)
            item.setBackground(0, QColor(Qt.yellow).lighter(150))
            item.setBackground(1, QColor(Qt.yellow).lighter(150))
        
        # NOTE: Clearing the highlight on next action is recommended for better UX

    def show_package_details(self):
        # ... (Method remains the same as previous step) ...
        package_name = self.search_field.text().strip()
        if not package_name:
            QMessageBox.warning(self, "Input Required", "Please enter or select a package to show details.")
            return

        self.thread = QThread()
        self.worker = Worker(self.qgis_pip_manager, "get_details", package_name)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        
        self.log_text.clear()
        self.worker.result.connect(self.set_search_text)
        self.worker.status.connect(self.set_search_text)
        self.worker.error.connect(self.show_error)
        self.thread.start()

    def install_package(self):
        package_name = self.search_field.text().strip()
        version = self.version_combo.currentText()
        
        if not package_name:
            QMessageBox.warning(self, "Input Required", "Please enter a package name.")
            return
            
        # Determine the version spec: None for "Latest", otherwise the chosen version
        version_spec = None
        is_update = False
        if version == "Latest":
            version_spec = None
        elif version.startswith("Fetch") or version.startswith("No version"):
            version_spec = None # Treat as 'Latest' or default install
        else:
            version_spec = version

        # Check if package is already installed to determine if it's an update/downgrade
        is_installed = any(p["name"].lower() == package_name.lower() for p in self.installed_packages)
        
        if is_installed and (version_spec or version == "Latest"):
            is_update = True
        
        # Confirmation for update/downgrade
        if is_update:
            msg = f"Do you want to {('install' if not version_spec else 'upgrade/downgrade')} '{package_name}' to version: {version or 'latest'}?"
            reply = QMessageBox.question(self, 'Confirm Update', msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        self.thread = QThread()
        # Pass name, version spec, and is_update flag
        self.worker = Worker(self.qgis_pip_manager, "install", package_name, version_spec, is_update)
        self.worker.detailed_error.connect(self.show_error)
        self.worker.status.connect(self.set_search_text)
        self.worker.result.connect(self.show_completion_message) # NEW
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.populate_packages_async) 
        self.worker.error.connect(self.show_error)

        self.thread.start()

    def uninstall_package(self):
        package_name = self.search_field.text().strip()
        if not package_name:
            QMessageBox.warning(self, "Input Required", "Please enter a package name to uninstall.")
            return

        reply = QMessageBox.question(self, 'Confirm Uninstall',
            f"Are you sure you want to uninstall '{package_name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.No:
            return

        self.thread = QThread()
        self.worker = Worker(self.qgis_pip_manager, "uninstall", package_name)
        self.worker.moveToThread(self.thread)
        self.worker.status.connect(self.set_search_text)
        self.worker.result.connect(self.show_completion_message) # NEW
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.populate_packages_async) 
        self.worker.error.connect(self.show_error)
        self.thread.start()
        
    def show_completion_message(self, message):
        """Shows a message box and QGIS restart prompt on success."""
        self.set_search_text(message) # Also log the success message

        if message.startswith("SUCCESS"):
            # Inform the user that QGIS needs to be restarted
            QMessageBox.information(self, "Operation Complete",
                                    message + "\n\n**Please restart QGIS to ensure all changes take effect.**")
        else:
            QMessageBox.information(self, "Operation Complete", message)


    def set_search_text(self, text):
        self.log_text.append(text)

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)
