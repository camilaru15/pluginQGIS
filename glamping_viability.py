from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.core import *
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QVariant
from qgis.gui import *
from qgis import processing
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

        # =========================
        # 1. Buscar capas necesarias
        # =========================
        capas_puntos = QgsProject.instance().mapLayersByName('Muestreado')
        capas_mask = QgsProject.instance().mapLayersByName('espana_mask')

        if not capas_puntos or not capas_mask:
            QMessageBox.warning(None, "Error", "Faltan capas: 'Muestreado' o 'espana_mask'")
            return

        puntos = capas_puntos[0]
        mask = capas_mask[0]

        # =========================
        # 2. Aplicar máscara (quitar mar)
        # =========================
        try:
            resultado = processing.run("native:extractbylocation", {
                'INPUT': puntos,
                'PREDICATE': [0],  # dentro de
                'INTERSECT': mask,
                'OUTPUT': 'memory:'
            })
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error aplicando máscara:\n{str(e)}")
            return

        layer = resultado['OUTPUT']
        layer.setName("Resultado_Viabilidad")
        QgsProject.instance().addMapLayer(layer)

        # =========================
        # 3. Crear campo viabilidad
        # =========================
        if 'viabilidad' not in [f.name() for f in layer.fields()]:
            layer.startEditing()
            layer.addAttribute(QgsField('viabilidad', QVariant.Double))
            layer.updateFields()

        if not layer.isEditable():
            layer.startEditing()

        # =========================
        # 4. Obtener índices
        # =========================
        idx_acces = layer.fields().indexFromName('acces_norm')
        idx_turismo = layer.fields().indexFromName('turis_norm')
        idx_pend = layer.fields().indexFromName('pend_norm')
        idx_viab = layer.fields().indexFromName('viabilidad')

        # =========================
        # 5. Validación de campos
        # =========================
        if -1 in (idx_acces, idx_turismo, idx_pend):
            QMessageBox.warning(None, "Error", "Faltan campos necesarios: acces_norm, turis_norm o pend_norm")
            return

        # =========================
        # 6. Calcular viabilidad
        # =========================
        for feat in layer.getFeatures():
            acces = feat[idx_acces] if feat[idx_acces] is not None else 0
            turismo = feat[idx_turismo] if feat[idx_turismo] is not None else 0
            pendiente = feat[idx_pend] if feat[idx_pend] is not None else 0

            viabilidad = (0.3 * acces) + (0.3 * turismo) + (0.4 * pendiente)

            layer.changeAttributeValue(feat.id(), idx_viab, viabilidad)

        layer.commitChanges()

        # =========================
        # 7. SIMBOLOGÍA AUTOMÁTICA
        # =========================
        field_name = 'viabilidad'

        # Rampa de color (rojo → verde)
        style = QgsStyle().defaultStyle()
        ramp = style.colorRamp('RdYlGn')

        ranges = []

        def crear_rango(min_val, max_val, label, color):
            symbol = QgsSymbol.defaultSymbol(layer.geometryType())
            symbol.setSize(2)
            symbol.setColor(color)
            return QgsRendererRange(min_val, max_val, symbol, label)

        ranges.append(crear_rango(0.0, 0.4, "Muy baja", QColor(215, 25, 28)))
        ranges.append(crear_rango(0.4, 0.6, "Baja", QColor(253, 174, 97)))
        ranges.append(crear_rango(0.6, 0.75, "Media", QColor(255, 255, 191)))
        ranges.append(crear_rango(0.75, 0.9, "Alta", QColor(166, 217, 106)))
        ranges.append(crear_rango(0.9, 1.0, "Muy alta", QColor(26, 225, 60)))

        renderer = QgsGraduatedSymbolRenderer(field_name, ranges)
        renderer.setMode(QgsGraduatedSymbolRenderer.Custom)
        renderer.updateColorRamp(ramp)

        layer.setRenderer(renderer)
        layer.triggerRepaint()

        # =========================
        # 8. Mensaje final
        # =========================
        QMessageBox.information(None, "Éxito", "Mapa generado con máscara, viabilidad y simbología automática")