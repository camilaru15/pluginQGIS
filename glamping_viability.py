from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.core import *
from qgis.gui import *
import os.path

class GlampingViability:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action = None

    def initGui(self):
        self.action = QAction("Glamping Viability Analyzer", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu("Glamping Viability Analyzer", self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removePluginMenu("Glamping Viability Analyzer", self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        QMessageBox.information(
            self.iface.mainWindow(),
            "Glamping Viability",
            "¡Plugin funcionando correctamente!"
        )
