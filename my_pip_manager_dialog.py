# my_pip_manager_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QTreeWidget, QTreeWidgetItem, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from .qpip import QGISPipManager  # Import your QGISPipManager class


class Worker(QObject):
    finished = pyqtSignal()
    result = pyqtSignal(str)
    error = pyqtSignal(str)
    detailed_error = pyqtSignal(str)

    def __init__(self, manager, operation, *args):
        super().__init__()
        self.manager = manager
        self.operation = operation
        self.args = args

    def run(self):
        try:
            if self.operation == "install":
                print(f"Worker: Starting install operation for {self.args}")  # Debugging
                success = self.manager.install_package(*self.args)
                if not success:
                    error_message = f"Worker: Failed to install {self.args[0]}"
                    print(error_message)
                    self.detailed_error.emit(error_message)
                    print("emit detailed error")
                else:
                    print(f"Worker: Successfully installed {self.args[0]}")
            elif self.operation == "uninstall":
                success = self.manager.uninstall_package(*self.args)
                if not success:
                    self.error.emit(f"Failed to uninstall {self.args[0]}")

            elif self.operation == "search":
                result = self.manager.search_package(*self.args)
                self.result.emit(result)
        except Exception as e:
            self.error.emit(str(e))
            print(f"Error in thread: {e}")
        finally:
            print("Worker Finished")  # Debugging
            self.finished.emit()


class PipManagerDialog(QDialog):
    def __init__(self, parent=None, qgis_python_path=None):
        super().__init__(parent)
        self.setWindowTitle("QGIS Pip Manager")
        self.qgis_pip_manager = QGISPipManager(qgis_python_path)

        self.layout = QVBoxLayout()

        self.package_list = QTreeWidget()
        self.package_list.setHeaderLabels(["Name", "Version"])
        self.layout.addWidget(self.package_list)

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search Package...")
        self.layout.addWidget(self.search_field)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_package)
        self.layout.addWidget(self.search_button)

        self.install_button = QPushButton("Install")
        self.install_button.clicked.connect(self.install_package)
        self.layout.addWidget(self.install_button)

        self.uninstall_button = QPushButton("Uninstall")
        self.uninstall_button.clicked.connect(self.uninstall_package)
        self.layout.addWidget(self.uninstall_button)

        self.log_text = QTextEdit()
        self.layout.addWidget(self.log_text)

        self.setLayout(self.layout)
        self.populate_packages()

    def populate_packages(self):
        self.package_list.clear()
        packages = self.qgis_pip_manager.get_installed_packages()
        for package in packages:
            item = QTreeWidgetItem([package["name"], package["version"]])
            self.package_list.addTopLevelItem(item)

    def search_package(self):
        package_name = self.search_field.text()
        self.thread = QThread()
        self.worker = Worker(self.qgis_pip_manager, "search", package_name)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.result.connect(self.set_search_text)
        self.worker.error.connect(self.show_error)
        self.thread.start()

    def install_package(self):
        package_name = self.search_field.text()
        print(f"PipManagerDialog: install_package called with {package_name}")  # Debugging

        self.thread = QThread()
        self.worker = Worker(self.qgis_pip_manager, "install", package_name)
        self.worker.detailed_error.connect(self.show_error)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.populate_packages)
        self.worker.error.connect(self.show_error)

        self.thread.start()
        print("thread started")

    def uninstall_package(self):
        selected_items = self.package_list.selectedItems()
        if selected_items:
            package_name = selected_items[0].text(0)
            self.thread = QThread()
            self.worker = Worker(self.qgis_pip_manager, "uninstall", package_name)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.populate_packages)
            self.worker.error.connect(self.show_error)
            self.thread.start()

    def set_search_text(self, text):
        self.log_text.clear()
        self.log_text.setText(text)

    def show_error(self, message):
        print("show_error triggered:", message)  # Add this line
        QMessageBox.critical(self, "Error", message)