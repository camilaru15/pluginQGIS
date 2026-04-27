from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.core import *
from PyQt5.QtCore import QVariant
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
        # Buscar la capa
        layers = QgsProject.instance().mapLayersByName('Muestreado')
        
        if not layers:
            QMessageBox.warning(None, "Error", "No se encontró la capa puntos_final")
            return
        
        layer = layers[0]

        # Crear campo viabilidad si no existe
        if 'viabilidad' not in [f.name() for f in layer.fields()]:
            layer.startEditing()
            layer.addAttribute(QgsField('viabilidad', QVariant.Double))
            layer.updateFields()

        # Iniciar edición SI NO está activa
        if not layer.isEditable():
            layer.startEditing()

        idx_viab = layer.fields().indexFromName('viabilidad')
        
        # Obtener índices de campos
        idx_acces = layer.fields().indexFromName('acces_norm')
        idx_turismo = layer.fields().indexFromName('turis_norm')
        idx_pend = layer.fields().indexFromName('pend_norm')
        idx_viab = layer.fields().indexFromName('viabilidad')
        
        # Comprobar campos
        if -1 in (idx_acces, idx_turismo, idx_pend):
            QMessageBox.warning(None, "Error", "Faltan campos necesarios")
            return
        
        # Calcular viabilidad
        for feat in layer.getFeatures():
            acces = feat[idx_acces] if feat[idx_acces] is not None else 0
            turismo = feat[idx_turismo] if feat[idx_turismo] is not None else 0
            pendiente = feat[idx_pend] if feat[idx_pend] is not None else 0
            
            viabilidad = (0.3 * acces) + (0.3 * turismo) + (0.4 * pendiente)
            
            layer.changeAttributeValue(feat.id(), idx_viab, viabilidad)
        
        # Guardar cambios
        layer.commitChanges()
        
        QMessageBox.information(None, "Éxito", "Viabilidad calculada correctamente")