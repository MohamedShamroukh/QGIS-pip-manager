"""
my_pip_manager_dialog.py  -  QGIS Pip Manager
Tabbed dialog: Packages | Install | Snapshots | Presets | Settings
PyQt5/PyQt6 compatible via compat.py.
"""
import os
import json
import tempfile
from pathlib import Path

from .compat import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
    QLineEdit, QTreeWidget, QTreeWidgetItem, QMessageBox, QComboBox,
    QWidget, QSizePolicy, QFileDialog, QTabWidget, QLabel, QProgressBar,
    QCheckBox, QGroupBox, QFormLayout, QThread, pyqtSignal, QObject,
    Qt, QTimer, QColor,
    Qt_SingleSel, QMsgBox_Yes, QMsgBox_No,
    SizePolicy_Fixed, SizePolicy_Pref,
)
from .qpip import QGISPipManager


# == Worker thread =============================================================

class Worker(QObject):
    finished      = pyqtSignal()
    result        = pyqtSignal(str)
    error         = pyqtSignal(str)
    status        = pyqtSignal(str)
    package_list  = pyqtSignal(list)
    versions_list = pyqtSignal(list)
    pypi_info     = pyqtSignal(dict)
    progress_line = pyqtSignal(str)

    def __init__(self, manager, operation, *args):
        super().__init__()
        self.manager   = manager
        self.operation = operation
        self.args      = args

    def run(self):
        try:
            m, op = self.manager, self.operation
            cb = self.progress_line.emit

            if op == "install":
                pkg = self.args[0]
                ver = self.args[1] if len(self.args) > 1 else None
                ok, msg = m.install_package(pkg, ver, stream_cb=cb)
                (self.result if ok else self.error).emit(msg)

            elif op == "uninstall":
                ok, msg = m.uninstall_package(self.args[0], stream_cb=cb)
                (self.result if ok else self.error).emit(msg)

            elif op == "list_packages":
                self.status.emit("Loading installed packages...")
                self.package_list.emit(m.get_installed_packages())

            elif op == "get_outdated":
                self.status.emit("Checking for outdated packages...")
                self.package_list.emit(m.get_outdated_packages())

            elif op == "get_versions":
                self.versions_list.emit(m.get_package_versions(self.args[0]))

            elif op == "pypi_search":
                self.pypi_info.emit(m.pypi_search(self.args[0]))

            elif op == "get_details":
                self.result.emit(m.get_package_details(self.args[0]))

            elif op == "check_conflicts":
                ok, report = m.check_conflicts()
                self.result.emit(("OK: " if ok else "WARNING: ") + report)

            elif op == "dry_run":
                pkg = self.args[0]
                ver = self.args[1] if len(self.args) > 1 else None
                ok, report = m.dry_run_install(pkg, ver)
                self.result.emit(
                    ("No conflicts.\n" if ok else "Conflicts detected:\n") + report)

            elif op == "export_req":
                ok, msg = m.export_requirements(self.args[0])
                (self.result if ok else self.error).emit(msg)

            elif op == "import_req":
                ok, msg = m.import_requirements(self.args[0], stream_cb=cb)
                (self.result if ok else self.error).emit(msg)

            elif op == "save_snapshot":
                ok, msg = m.save_snapshot(self.args[0] if self.args else "")
                (self.result if ok else self.error).emit(msg)

            elif op == "restore_snapshot":
                ok, msg = m.restore_snapshot(self.args[0], stream_cb=cb)
                (self.result if ok else self.error).emit(msg)

            elif op == "conda_install":
                ok, msg = m.conda_install(self.args[0], stream_cb=cb)
                (self.result if ok else self.error).emit(msg)

            else:
                self.error.emit("Unknown worker operation: '{}'".format(op))

        except Exception as exc:
            self.error.emit(str(exc))
        finally:
            self.finished.emit()


# == Main dialog ===============================================================

class PipManagerDialog(QDialog):

    def __init__(self, parent=None, qgis_python_path=None, settings=None):
        super().__init__(parent)
        self.setWindowTitle("QGIS Pip Manager")
        self.resize(840, 660)

        self._settings      = settings
        self._proxy         = self._gs("proxy", "")
        self._index_url     = self._gs("index_url", "")
        self._extra_index   = self._gs("extra_index_url", "")
        self._snapshots_dir = self._gs("snapshots_dir", "")

        self.manager = QGISPipManager(
            qgis_python_path,
            proxy           = self._proxy,
            extra_index_url = self._extra_index,
            index_url       = self._index_url,
            snapshots_dir   = self._snapshots_dir,
        )

        self.installed_packages = []
        self._active_threads    = []
        self._active_workers    = []   # <-- FIX: keep Python refs alive

        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._trigger_pypi_search)

        self._build_ui()
        self._load_presets()
        self._populate_packages()

    # -- settings helpers ------------------------------------------------------

    def _gs(self, key, default=""):
        return (self._settings.value("pip_manager/{}".format(key), default)
                if self._settings else default)

    def _ss(self, key, value):
        if self._settings:
            self._settings.setValue("pip_manager/{}".format(key), value)

    # -- UI construction -------------------------------------------------------

    def _build_ui(self):
        root = QVBoxLayout(self)

        tabs = QTabWidget()
        tabs.addTab(self._tab_packages(),  "Packages")
        tabs.addTab(self._tab_install(),   "Install")
        tabs.addTab(self._tab_snapshot(),  "Snapshots")
        tabs.addTab(self._tab_presets(),   "Presets")
        tabs.addTab(self._tab_settings(),  "Settings")
        root.addWidget(tabs)

        log_group = QGroupBox("Log")
        lg = QVBoxLayout(log_group)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(160)
        self.log.setStyleSheet(
            "font-family: 'Courier New', monospace; font-size: 9pt;")
        lg.addWidget(self.log)

        btn_row = QHBoxLayout()
        self._btn("Clear Log",     btn_row, lambda: self.log.clear())
        self._btn("Export Log...", btn_row, self._export_log)
        lg.addLayout(btn_row)
        root.addWidget(log_group)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        root.addWidget(self.progress)

    # -- Tab: Packages ---------------------------------------------------------

    def _tab_packages(self):
        w = QWidget()
        lay = QVBoxLayout(w)

        fr = QHBoxLayout()
        self.filter_field = QLineEdit()
        self.filter_field.setPlaceholderText("Filter installed packages...")
        self.filter_field.textChanged.connect(self._filter_list)
        fr.addWidget(self.filter_field)
        self._btn("Refresh",         fr, self._populate_packages)
        self._btn("Check Outdated",  fr, self._check_outdated)
        self._btn("Check Conflicts", fr, self._check_conflicts)
        lay.addLayout(fr)

        self.pkg_tree = QTreeWidget()
        self.pkg_tree.setHeaderLabels(["Name", "Installed Version"])
        self.pkg_tree.setSelectionMode(Qt_SingleSel)
        self.pkg_tree.itemClicked.connect(self._pkg_clicked)
        lay.addWidget(self.pkg_tree)

        br = QHBoxLayout()
        self._btn("Show Details", br, self._show_details)
        self._btn("Uninstall",    br, self._uninstall)
        lay.addLayout(br)
        return w

    # -- Tab: Install ----------------------------------------------------------

    def _tab_install(self):
        w = QWidget()
        lay = QVBoxLayout(w)

        sg = QGroupBox("PyPI Search (live - type a package name)")
        sl = QVBoxLayout(sg)
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText(
            "e.g. pandas, geopandas, scikit-learn ...")
        self.search_field.textChanged.connect(self._debounce_search)
        sl.addWidget(self.search_field)
        self.pypi_preview = QTextEdit()
        self.pypi_preview.setReadOnly(True)
        self.pypi_preview.setMaximumHeight(90)
        self.pypi_preview.setPlaceholderText(
            "Package info from PyPI will appear here...")
        sl.addWidget(self.pypi_preview)
        lay.addWidget(sg)

        ar = QHBoxLayout()
        ar.addWidget(QLabel("Version:"))
        self.version_combo = QComboBox()
        self.version_combo.addItem("Latest")
        self.version_combo.setSizePolicy(SizePolicy_Fixed, SizePolicy_Pref)
        ar.addWidget(self.version_combo)
        self._btn("Install / Upgrade", ar, self._install)
        self._btn("Dry-run Check",     ar, self._dry_run)
        self.conda_chk = QCheckBox("Use conda instead")
        self.conda_chk.setVisible(self.manager.is_conda)
        ar.addWidget(self.conda_chk)
        lay.addLayout(ar)

        rg = QGroupBox("requirements.txt")
        rl = QHBoxLayout(rg)
        self._btn("Import requirements.txt...", rl, self._import_requirements)
        self._btn("Export requirements.txt...", rl, self._export_requirements)
        lay.addWidget(rg)
        lay.addStretch()
        return w

    # -- Tab: Snapshots --------------------------------------------------------

    def _tab_snapshot(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.addWidget(QLabel(
            "Snapshots save your current pip environment as a timestamped\n"
            "requirements file. Restore one if a bad install breaks QGIS."
        ))
        br = QHBoxLayout()
        self._btn("Save Snapshot Now", br, self._save_snapshot)
        lay.addLayout(br)

        self.snapshot_list = QTreeWidget()
        self.snapshot_list.setHeaderLabels(["Snapshot file"])
        lay.addWidget(self.snapshot_list)
        self._refresh_snapshot_list()

        ar = QHBoxLayout()
        self._btn("Restore Selected", ar, self._restore_snapshot)
        self._btn("Delete Selected",  ar, self._delete_snapshot)
        lay.addLayout(ar)
        return w

    # -- Tab: Presets ----------------------------------------------------------

    def _tab_presets(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.addWidget(QLabel(
            "One-click installation of common GIS / data-science stacks.\n"
            "Edit presets.json in the plugin folder to add your own."
        ))
        self.preset_tree = QTreeWidget()
        self.preset_tree.setHeaderLabels(["Preset", "Packages"])
        lay.addWidget(self.preset_tree)
        self._btn("Install Selected Preset", lay, self._install_preset)
        lay.addStretch()
        return w

    # -- Tab: Settings ---------------------------------------------------------

    def _tab_settings(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        form = QFormLayout()

        self.proxy_field = QLineEdit(self._proxy)
        self.proxy_field.setPlaceholderText("http://user:pass@host:3128")
        form.addRow("HTTP/HTTPS Proxy:", self.proxy_field)

        self.index_url_field = QLineEdit(self._index_url)
        self.index_url_field.setPlaceholderText("Leave blank for default PyPI")
        form.addRow("Index URL:", self.index_url_field)

        self.extra_index_field = QLineEdit(self._extra_index)
        self.extra_index_field.setPlaceholderText(
            "https://company.example/simple")
        form.addRow("Extra Index URL:", self.extra_index_field)

        snap_row = QHBoxLayout()
        self.snapshots_dir_field = QLineEdit(str(self.manager.snapshots_dir))
        snap_row.addWidget(self.snapshots_dir_field)
        self._btn("Browse...", snap_row, self._browse_snapshots_dir)
        form.addRow("Snapshots folder:", snap_row)

        lay.addLayout(form)

        # Python path display (read-only info)
        self.python_path_label = QLabel(
            "Python: {}".format(self.manager.qgis_python_path))
        self.python_path_label.setWordWrap(True)
        lay.addWidget(self.python_path_label)

        self._btn("Save Settings", lay, self._save_settings)

        pip_v = ".".join(str(x) for x in self.manager.pip_ver)
        env   = ("conda env detected" if self.manager.is_conda
                 else "pip / OSGeo4W env")
        lay.addWidget(QLabel(
            "pip version: {}   |   {}".format(pip_v, env)))
        lay.addStretch()
        return w

    # -- generic helpers -------------------------------------------------------

    @staticmethod
    def _btn(label, layout, slot):
        b = QPushButton(label)
        b.clicked.connect(slot)
        layout.addWidget(b)
        return b

    def _log(self, msg):
        self.log.append(str(msg))

    def _busy(self, state):
        self.progress.setVisible(state)

    def _run_worker(self, operation, *args,
                    on_result=None, on_error=None,
                    on_package_list=None, on_versions=None,
                    on_pypi_info=None, on_finished=None):
        thread = QThread(self)
        worker = Worker(self.manager, operation, *args)
        worker.moveToThread(thread)

        # FIX: keep a Python reference so GC doesn't delete the worker
        self._active_workers.append(worker)
        self._active_threads.append(thread)

        worker.status.connect(self._log)
        worker.progress_line.connect(self._log)

        if on_error:
            worker.error.connect(on_error)
        else:
            worker.error.connect(lambda m: (
                self._log("ERROR: {}".format(m)),
                QMessageBox.critical(self, "Error", m),
            ))

        if on_result:       worker.result.connect(on_result)
        if on_package_list: worker.package_list.connect(on_package_list)
        if on_versions:     worker.versions_list.connect(on_versions)
        if on_pypi_info:    worker.pypi_info.connect(on_pypi_info)

        def _done():
            self._busy(False)
            if on_finished:
                on_finished()
            # clean up finished thread/worker
            self._active_threads = [
                t for t in self._active_threads if t != thread]
            self._active_workers = [
                w for w in self._active_workers if w != worker]

        worker.finished.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(_done)
        thread.started.connect(worker.run)

        self._busy(True)
        thread.start()

    # -- Packages tab ----------------------------------------------------------

    def _populate_packages(self):
        self.pkg_tree.clear()
        self._run_worker("list_packages",
                         on_package_list=self._update_pkg_tree,
                         on_error=lambda m: (
                             self._log("ERROR: {}".format(m)),
                             self._busy(False),
                         ))

    def _update_pkg_tree(self, packages):
        self.installed_packages = packages
        self._filter_list(self.filter_field.text())
        if not packages:
            self._log("No packages found in this environment.")

    def _filter_list(self, text):
        ft = text.lower()
        self.pkg_tree.clear()
        for p in self.installed_packages:
            if ft and ft not in p["name"].lower():
                continue
            QTreeWidgetItem(self.pkg_tree, [p["name"], p["version"]])

    def _pkg_clicked(self, item, _col):
        name = item.text(0)
        self.search_field.setText(name)
        self.version_combo.clear()
        self.version_combo.addItem("Fetching versions...")
        self._run_worker("get_versions", name,
                         on_versions=self._update_versions)

    def _update_versions(self, versions):
        self.version_combo.clear()
        self.version_combo.addItem("Latest")
        for v in versions:
            self.version_combo.addItem(v)

    def _show_details(self):
        name = self.search_field.text().strip()
        if not name:
            QMessageBox.warning(self, "No package",
                                "Select or type a package name first.")
            return
        self._run_worker("get_details", name, on_result=self._log)

    def _uninstall(self):
        name = self.search_field.text().strip()
        if not name:
            QMessageBox.warning(self, "No package",
                                "Select or type a package name.")
            return
        if QMessageBox.question(
                self, "Confirm Uninstall",
                "Uninstall '{}'?".format(name),
                QMsgBox_Yes | QMsgBox_No) != QMsgBox_Yes:
            return
        self._run_worker("uninstall", name,
                         on_result=self._log,
                         on_finished=self._populate_packages)

    def _check_outdated(self):
        self._run_worker("get_outdated",
                         on_package_list=self._show_outdated)

    def _show_outdated(self, packages):
        if not packages:
            self._log("All packages are up to date.")
            return
        self._log("Outdated packages:")
        for p in packages:
            self._log("  {}  installed={}  latest={}".format(
                p["name"], p["version"], p.get("latest_version", "?")))

    def _check_conflicts(self):
        self._run_worker("check_conflicts", on_result=self._log)

    # -- Install tab -----------------------------------------------------------

    def _debounce_search(self, text):
        if len(text.strip()) >= 2:
            self._search_timer.start(450)

    def _trigger_pypi_search(self):
        query = self.search_field.text().strip()
        if query:
            self._run_worker("pypi_search", query,
                             on_pypi_info=self._show_pypi_info)

    def _show_pypi_info(self, info):
        if "error" in info:
            self.pypi_preview.setPlainText(
                "Not found on PyPI: {}".format(info["error"]))
            return
        self.pypi_preview.setPlainText(
            "{}  {}\n{}\nAuthor: {}   Requires Python: {}".format(
                info["name"], info["version"], info["summary"],
                info["author"], info["requires_python"])
        )
        self.version_combo.clear()
        self.version_combo.addItem("Fetching versions...")
        self._run_worker("get_versions", info["name"],
                         on_versions=self._update_versions)

    def _install(self):
        name = self.search_field.text().strip()
        if not name:
            QMessageBox.warning(self, "No package", "Enter a package name.")
            return
        ver_text = self.version_combo.currentText()
        ver = (None if ver_text in ("Latest", "Fetching versions...", "")
               else ver_text)

        if self.conda_chk.isVisible() and self.conda_chk.isChecked():
            self._run_worker("conda_install", name,
                             on_result=self._post_install,
                             on_finished=self._populate_packages)
            return

        self._run_worker("install", name, ver,
                         on_result=self._post_install,
                         on_finished=self._populate_packages)

    def _post_install(self, msg):
        self._log(msg)
        name = self.search_field.text().strip()
        ok, im_msg = QGISPipManager.try_import(name)
        self._log(im_msg)
        if not ok:
            QMessageBox.information(
                self, "Restart Needed",
                "{}\n\n{}\n\nPlease restart QGIS.".format(msg, im_msg))

    def _dry_run(self):
        name = self.search_field.text().strip()
        if not name:
            QMessageBox.warning(self, "No package", "Enter a package name.")
            return
        ver_text = self.version_combo.currentText()
        ver = (None if ver_text in ("Latest", "Fetching versions...", "")
               else ver_text)
        self._run_worker("dry_run", name, ver, on_result=self._log)

    def _import_requirements(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import requirements.txt", "", "Text files (*.txt)")
        if not path:
            return
        self._run_worker("import_req", path,
                         on_result=self._log,
                         on_finished=self._populate_packages)

    def _export_requirements(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export requirements.txt", "requirements.txt",
            "Text files (*.txt)")
        if not path:
            return
        self._run_worker("export_req", path, on_result=self._log)

    # -- Snapshots tab ---------------------------------------------------------

    def _refresh_snapshot_list(self):
        self.snapshot_list.clear()
        for p in self.manager.list_snapshots():
            QTreeWidgetItem(self.snapshot_list, [p])

    def _save_snapshot(self):
        self._run_worker(
            "save_snapshot", "",
            on_result=lambda m: (self._log(m),
                                 self._refresh_snapshot_list()))

    def _restore_snapshot(self):
        items = self.snapshot_list.selectedItems()
        if not items:
            QMessageBox.warning(self, "None selected",
                                "Select a snapshot to restore.")
            return
        path = items[0].text(0)
        if QMessageBox.question(
                self, "Confirm Restore",
                "Restore environment from:\n{}?".format(path),
                QMsgBox_Yes | QMsgBox_No) != QMsgBox_Yes:
            return
        self._run_worker("restore_snapshot", path,
                         on_result=self._log,
                         on_finished=self._populate_packages)

    def _delete_snapshot(self):
        items = self.snapshot_list.selectedItems()
        if not items:
            return
        ok, msg = self.manager.delete_snapshot(items[0].text(0))
        self._log(msg)
        self._refresh_snapshot_list()

    # -- Presets tab -----------------------------------------------------------

    def _load_presets(self):
        presets_file = Path(__file__).parent / "presets.json"
        self._presets = []
        if presets_file.exists():
            try:
                self._presets = json.loads(
                    presets_file.read_text(encoding="utf-8"))
            except Exception as exc:
                self._log("Warning: could not load presets.json: {}".format(exc))
        self.preset_tree.clear()
        for p in self._presets:
            QTreeWidgetItem(self.preset_tree, [
                p.get("name", ""),
                ", ".join(p.get("packages", [])),
            ])

    def _install_preset(self):
        items = self.preset_tree.selectedItems()
        if not items:
            QMessageBox.warning(self, "None selected",
                                "Select a preset to install.")
            return
        idx    = self.preset_tree.indexOfTopLevelItem(items[0])
        preset = self._presets[idx]
        pkgs   = preset.get("packages", [])
        if QMessageBox.question(
                self, "Confirm Preset Install",
                "Install preset '{}'?\n\nPackages:\n{}".format(
                    preset["name"], "\n".join(pkgs)),
                QMsgBox_Yes | QMsgBox_No) != QMsgBox_Yes:
            return
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8")
        tmp.write("\n".join(pkgs))
        tmp.close()
        self._run_worker("import_req", tmp.name,
                         on_result=self._log,
                         on_finished=self._populate_packages)

    # -- Settings tab ----------------------------------------------------------

    def _browse_snapshots_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select snapshots folder")
        if d:
            self.snapshots_dir_field.setText(d)

    def _save_settings(self):
        self._proxy       = self.proxy_field.text().strip()
        self._index_url   = self.index_url_field.text().strip()
        self._extra_index = self.extra_index_field.text().strip()
        snaps             = self.snapshots_dir_field.text().strip()

        self._ss("proxy",           self._proxy)
        self._ss("index_url",       self._index_url)
        self._ss("extra_index_url", self._extra_index)
        self._ss("snapshots_dir",   snaps)

        self.manager.proxy           = self._proxy
        self.manager.index_url       = self._index_url
        self.manager.extra_index_url = self._extra_index
        if snaps:
            self.manager.snapshots_dir = Path(snaps)
            self.manager.snapshots_dir.mkdir(parents=True, exist_ok=True)

        self._log("Settings saved.")
        QMessageBox.information(self, "Saved", "Settings saved.")

    # -- Log -------------------------------------------------------------------

    def _export_log(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Log", "pip_manager_log.txt", "Text files (*.txt)")
        if not path:
            return
        try:
            Path(path).write_text(self.log.toPlainText(), encoding="utf-8")
            self._log("Log exported to: {}".format(path))
        except OSError as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def closeEvent(self, event):
        for t in self._active_threads:
            t.quit()
            t.wait(2000)
        super().closeEvent(event)
