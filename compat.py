"""
compat.py - PyQt5/PyQt6 shim for QGIS 3 and QGIS 4 compatibility.
QFont removed entirely - log font set via setStyleSheet() instead.
"""
try:
    # QGIS 4 / PyQt6
    from PyQt6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
        QLineEdit, QTreeWidget, QTreeWidgetItem, QMessageBox, QComboBox,
        QWidget, QSizePolicy, QApplication, QFileDialog, QTabWidget,
        QLabel, QProgressBar, QCheckBox, QGroupBox, QFormLayout, QInputDialog,
    )
    from PyQt6.QtCore import QThread, pyqtSignal, QObject, Qt, QTimer
    from PyQt6.QtGui import QColor, QIcon, QAction  # QAction in QtGui in PyQt6

    PYQT_VERSION = 6
    Qt_yellow        = Qt.GlobalColor.yellow
    Qt_SingleSel     = QTreeWidget.SelectionMode.SingleSelection
    QMsgBox_Yes      = QMessageBox.StandardButton.Yes
    QMsgBox_No       = QMessageBox.StandardButton.No
    QMsgBox_Ok       = QMessageBox.StandardButton.Ok
    SizePolicy_Fixed = QSizePolicy.Policy.Fixed
    SizePolicy_Pref  = QSizePolicy.Policy.Preferred
    SizePolicy_Exp   = QSizePolicy.Policy.Expanding

except ImportError:
    # QGIS 3 / PyQt5
    from PyQt5.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
        QLineEdit, QTreeWidget, QTreeWidgetItem, QMessageBox, QComboBox,
        QWidget, QSizePolicy, QApplication, QFileDialog, QTabWidget,
        QLabel, QProgressBar, QCheckBox, QGroupBox, QFormLayout,
        QInputDialog, QAction,  # QAction in QtWidgets in PyQt5
    )
    from PyQt5.QtCore import QThread, pyqtSignal, QObject, Qt, QTimer
    from PyQt5.QtGui import QColor, QIcon  # no QFont needed

    PYQT_VERSION = 5
    Qt_yellow        = Qt.yellow
    Qt_SingleSel     = QTreeWidget.SingleSelection
    QMsgBox_Yes      = QMessageBox.Yes
    QMsgBox_No       = QMessageBox.No
    QMsgBox_Ok       = QMessageBox.Ok
    SizePolicy_Fixed = QSizePolicy.Fixed
    SizePolicy_Pref  = QSizePolicy.Preferred
    SizePolicy_Exp   = QSizePolicy.Expanding