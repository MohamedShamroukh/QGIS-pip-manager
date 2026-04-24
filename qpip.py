"""
qpip.py - Core pip backend for QGIS Pip Manager
Compatible with OSGeo4W, conda, and standalone Python on Windows/Linux/macOS.
"""
import os
import json
import platform
import re
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

if platform.system() == "Windows":
    SUBPROCESS_FLAGS = 0x08000000  # CREATE_NO_WINDOW
else:
    SUBPROCESS_FLAGS = 0


def _safe_cwd():
    """Return a writable directory so subprocesses never inherit QGIS cwd."""
    return (os.environ.get("TEMP")
            or os.environ.get("TMP")
            or tempfile.gettempdir()
            or str(Path.home()))


def _is_conda_env(python_path):
    return (Path(python_path).parent.parent / "conda-meta").exists()


def _pip_version(python_path):
    try:
        r = subprocess.run(
            [python_path, "-m", "pip", "--version"],
            capture_output=True, text=True,
            creationflags=SUBPROCESS_FLAGS,
            cwd=_safe_cwd(),
        )
        m = re.search(r"pip (\d+)\.(\d+)(?:\.(\d+))?", r.stdout)
        if m:
            return tuple(int(x or 0) for x in m.groups())
    except Exception:
        pass
    return (0, 0, 0)


class QGISPipManager:

    def __init__(self, qgis_python_path, proxy="", extra_index_url="",
                 index_url="", snapshots_dir=""):
        if not qgis_python_path:
            raise ValueError("No QGIS Python path provided.")

        p = Path(qgis_python_path)
        if not p.exists() or not p.is_file():
            raise ValueError(
                "Invalid QGIS Python path: '{}'".format(qgis_python_path))

        self.qgis_python_path = str(p)
        self.python_path      = self.qgis_python_path

        self.proxy           = proxy.strip()
        self.extra_index_url = extra_index_url.strip()
        self.index_url       = index_url.strip()

        # Snapshots directory
        if snapshots_dir:
            self.snapshots_dir = Path(snapshots_dir)
        else:
            appdata = os.environ.get("APPDATA") or os.environ.get("HOME", "")
            if appdata:
                self.snapshots_dir = Path(appdata) / "QGIS" / "pip_manager_snapshots"
            else:
                self.snapshots_dir = Path(__file__).parent / "pip_manager_snapshots"
        try:
            self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            self.snapshots_dir = (
                Path(tempfile.gettempdir()) / "pip_manager_snapshots")
            self.snapshots_dir.mkdir(parents=True, exist_ok=True)

        self.is_conda = _is_conda_env(self.qgis_python_path)
        self.pip_ver  = _pip_version(self.qgis_python_path)

    # -- helpers ---------------------------------------------------------------

    def _pip_args(self, *extra):
        cmd = [self.qgis_python_path, "-m", "pip"] + list(extra)
        if self.proxy:           cmd += ["--proxy",           self.proxy]
        if self.index_url:       cmd += ["--index-url",       self.index_url]
        if self.extra_index_url: cmd += ["--extra-index-url", self.extra_index_url]
        return cmd

    def _run(self, cmd, stream_cb=None):
        """Run a subprocess. Inherits the parent environment — do NOT rewrite PATH."""
        cwd = _safe_cwd()

        if stream_cb:
            # Merge stderr into stdout so we don't deadlock on full stderr buffer
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, creationflags=SUBPROCESS_FLAGS, cwd=cwd)
            lines = []
            for line in proc.stdout:
                lines.append(line)
                stream_cb(line.rstrip())
            proc.wait()
            return proc.returncode, "".join(lines), ""

        r = subprocess.run(
            cmd, capture_output=True, text=True,
            creationflags=SUBPROCESS_FLAGS, cwd=cwd)
        return r.returncode, r.stdout, r.stderr

    # -- package listing -------------------------------------------------------

    def get_installed_packages(self):
        """
        Query the target QGIS Python environment via subprocess.
        Returns an empty list on any failure so the GUI never hangs.
        """
        try:
            rc, out, err = self._run(self._pip_args("list", "--format=json"))
            if rc != 0:
                return []
            pkgs = json.loads(out)
            if not pkgs:
                return []
            return sorted(pkgs, key=lambda x: x["name"].lower())
        except Exception:
            return []

    def get_outdated_packages(self):
        rc, out, _ = self._run(
            self._pip_args("list", "--outdated", "--format=json"))
        try:
            return json.loads(out) if rc == 0 else []
        except json.JSONDecodeError:
            return []

    # -- install / uninstall ---------------------------------------------------

    def install_package(self, package_name, version=None, stream_cb=None):
        spec = "{}=={}".format(package_name, version) if version else package_name
        rc, out, err = self._run(
            self._pip_args("install", "--upgrade", spec), stream_cb)
        return ((True, "Installed {}.".format(spec))
                if rc == 0 else (False, err or out))

    def uninstall_package(self, package_name, stream_cb=None):
        rc, out, err = self._run(
            self._pip_args("uninstall", "-y", package_name), stream_cb)
        return ((True, "Uninstalled {}.".format(package_name))
                if rc == 0 else (False, err or out))

    def install_packages_list(self, packages, stream_cb=None):
        results, all_ok = [], True
        for spec in packages:
            spec = spec.strip()
            if not spec or spec.startswith("#"):
                continue
            ok, msg = self.install_package(spec, stream_cb=stream_cb)
            results.append("{} {}: {}".format("OK" if ok else "FAIL", spec, msg))
            if not ok:
                all_ok = False
        return all_ok, "\n".join(results)

    # -- versions --------------------------------------------------------------

    def get_package_versions(self, package_name):
        if self.pip_ver >= (22, 0, 0):
            rc, out, _ = self._run(
                self._pip_args("index", "versions", package_name))
            m = re.search(r"Available versions: (.*)", out)
            if m:
                return [v.split()[0] for v in m.group(1).split(",") if v.strip()]
        return self._pypi_versions(package_name)

    def _pypi_versions(self, package_name):
        try:
            import urllib.request
            with urllib.request.urlopen(
                    "https://pypi.org/pypi/{}/json".format(package_name),
                    timeout=8) as resp:
                data = json.loads(resp.read())
            return sorted(data.get("releases", {}).keys(), reverse=True)[:40]
        except Exception as exc:
            return ["Error: {}".format(exc)]

    # -- PyPI search -----------------------------------------------------------

    def pypi_search(self, query):
        try:
            import urllib.request
            with urllib.request.urlopen(
                    "https://pypi.org/pypi/{}/json".format(query),
                    timeout=8) as resp:
                info = json.loads(resp.read()).get("info", {})
            return {
                "name":            info.get("name", query),
                "version":         info.get("version", ""),
                "summary":         info.get("summary", "No description available."),
                "author":          info.get("author", ""),
                "home_page":       info.get("home_page", ""),
                "requires_python": info.get("requires_python", ""),
                "license":         info.get("license", ""),
            }
        except Exception as exc:
            return {"error": str(exc)}

    # -- details / conflicts ---------------------------------------------------

    def get_package_details(self, package_name):
        rc, out, err = self._run(self._pip_args("show", package_name))
        return out if rc == 0 else "Not found.\n{}".format(err)

    def check_conflicts(self):
        rc, out, err = self._run(self._pip_args("check"))
        return rc == 0, (out or err).strip() or "No conflicts detected."

    def dry_run_install(self, package_name, version=None):
        if self.pip_ver < (22, 0, 0):
            return self.check_conflicts()
        spec = "{}=={}".format(package_name, version) if version else package_name
        rc, out, err = self._run(self._pip_args("install", "--dry-run", spec))
        return rc == 0, (out + err).strip()

    # -- requirements.txt ------------------------------------------------------

    def export_requirements(self, file_path):
        rc, out, err = self._run(self._pip_args("freeze"))
        if rc != 0:
            return False, err
        try:
            Path(file_path).write_text(out, encoding="utf-8")
            return True, "Exported to:\n{}".format(file_path)
        except OSError as exc:
            return False, str(exc)

    def import_requirements(self, file_path, stream_cb=None):
        try:
            lines = Path(file_path).read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            return False, str(exc)
        return self.install_packages_list(lines, stream_cb=stream_cb)

    # -- snapshots -------------------------------------------------------------

    def save_snapshot(self, label=""):
        rc, out, err = self._run(self._pip_args("freeze"))
        if rc != 0:
            return False, err
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe  = re.sub(r"[^\w\-]", "_", label)[:40]
        name  = "snapshot_{}{}.txt".format(stamp, "_" + safe if safe else "")
        path  = self.snapshots_dir / name
        try:
            path.write_text(out, encoding="utf-8")
            return True, str(path)
        except OSError as exc:
            return False, str(exc)

    def list_snapshots(self):
        return [str(f) for f in sorted(
            self.snapshots_dir.glob("snapshot_*.txt"), reverse=True)]

    def restore_snapshot(self, snapshot_path, stream_cb=None):
        return self.import_requirements(snapshot_path, stream_cb=stream_cb)

    def delete_snapshot(self, snapshot_path):
        try:
            Path(snapshot_path).unlink()
            return True, "Snapshot deleted."
        except OSError as exc:
            return False, str(exc)

    # -- restart-free import ---------------------------------------------------

    @staticmethod
    def try_import(package_name):
        import importlib
        import_name = package_name.replace("-", "_").split("==")[0]
        try:
            mod = importlib.import_module(import_name)
            importlib.reload(mod)
            return True, "'{}' available now - no restart needed.".format(import_name)
        except Exception:
            pass
        return False, "'{}' requires a QGIS restart.".format(import_name)

    # -- conda -----------------------------------------------------------------

    def conda_install(self, package_name, stream_cb=None):
        import shutil
        exe = shutil.which("mamba") or shutil.which("conda")
        if not exe:
            return False, "conda/mamba not found on PATH."
        rc, out, err = self._run([exe, "install", "-y", package_name], stream_cb)
        return ((True, "conda: installed {}.".format(package_name))
                if rc == 0 else (False, err or out))
