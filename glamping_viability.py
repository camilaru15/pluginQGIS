from qgis.PyQt.QtWidgets import (
    QAction,
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSlider
)

from qgis.core import *
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QVariant, Qt
from qgis import processing

import os.path


class ViabilityDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Glamping Viability Analyzer")
        self.setMinimumWidth(300)

        layout = QVBoxLayout()

        # =========================
        # ACCESIBILIDAD
        # =========================

        self.label_acces = QLabel("Accesibilidad: 0.30")

        self.slider_acces = QSlider(Qt.Horizontal)
        self.slider_acces.setRange(0, 100)
        self.slider_acces.setValue(30)

        self.slider_acces.valueChanged.connect(
            lambda v: self.label_acces.setText(
                f"Accesibilidad: {v/100:.2f}"
            )
        )

        # =========================
        # TURISMO
        # =========================

        self.label_tur = QLabel("Turismo: 0.30")

        self.slider_tur = QSlider(Qt.Horizontal)
        self.slider_tur.setRange(0, 100)
        self.slider_tur.setValue(30)

        self.slider_tur.valueChanged.connect(
            lambda v: self.label_tur.setText(
                f"Turismo: {v/100:.2f}"
            )
        )

        # =========================
        # PENDIENTE
        # =========================

        self.label_pend = QLabel("Pendiente: 0.40")

        self.slider_pend = QSlider(Qt.Horizontal)
        self.slider_pend.setRange(0, 100)
        self.slider_pend.setValue(40)

        self.slider_pend.valueChanged.connect(
            lambda v: self.label_pend.setText(
                f"Pendiente: {v/100:.2f}"
            )
        )

        # =========================
        # BOTÓN
        # =========================

        self.btn_run = QPushButton("Calcular viabilidad")

        # =========================
        # LAYOUT
        # =========================

        layout.addWidget(self.label_acces)
        layout.addWidget(self.slider_acces)

        layout.addWidget(self.label_tur)
        layout.addWidget(self.slider_tur)

        layout.addWidget(self.label_pend)
        layout.addWidget(self.slider_pend)

        layout.addWidget(self.btn_run)

        self.setLayout(layout)


class GlampingViability:

    def __init__(self, iface):

        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action = None

    def initGui(self):

        self.action = QAction(
            "Glamping Viability Analyzer",
            self.iface.mainWindow()
        )

        self.action.triggered.connect(self.run)

        self.iface.addPluginToMenu(
            "Glamping Viability Analyzer",
            self.action
        )

        self.iface.addToolBarIcon(self.action)

    def unload(self):

        self.iface.removePluginMenu(
            "Glamping Viability Analyzer",
            self.action
        )

        self.iface.removeToolBarIcon(self.action)

    def run(self):

        dialog = ViabilityDialog()

        def ejecutar():

            # =========================
            # PESOS DINÁMICOS
            # =========================

            peso_acces = dialog.slider_acces.value() / 100
            peso_turismo = dialog.slider_tur.value() / 100
            peso_pend = dialog.slider_pend.value() / 100

            total = (
                peso_acces +
                peso_turismo +
                peso_pend
            )

            if total == 0:

                QMessageBox.warning(
                    None,
                    "Error",
                    "Los pesos no pueden ser 0"
                )

                return

            # =========================
            # NORMALIZAR PESOS
            # =========================

            peso_acces /= total
            peso_turismo /= total
            peso_pend /= total

            # =========================
            # CAPAS
            # =========================

            capas_puntos = QgsProject.instance().mapLayersByName(
                'Muestreado'
            )

            capas_mask = QgsProject.instance().mapLayersByName(
                'espana_mask'
            )

            capas_costa = QgsProject.instance().mapLayersByName(
                'costa_asturias'
            )

            if not capas_puntos or not capas_mask or not capas_costa:

                QMessageBox.warning(
                    None,
                    "Error",
                    "Faltan capas necesarias"
                )

                return

            puntos = capas_puntos[0]
            mask = capas_mask[0]
            costa = capas_costa[0]

            # =========================
            # QUITAR MAR
            # =========================

            resultado = processing.run(
                "native:extractbylocation",
                {
                    'INPUT': puntos,
                    'PREDICATE': [0],
                    'INTERSECT': mask,
                    'OUTPUT': 'memory:'
                }
            )

            layer = resultado['OUTPUT']

            # =========================
            # REPROYECTAR COSTA
            # =========================

            costa_proj = processing.run(
                "native:reprojectlayer",
                {
                    'INPUT': costa,
                    'TARGET_CRS': QgsCoordinateReferenceSystem(
                        'EPSG:3041'
                    ),
                    'OUTPUT': 'memory:'
                }
            )['OUTPUT']

            # =========================
            # BUFFER LEGAL 150m
            # =========================

            buffer_result = processing.run(
                "native:buffer",
                {
                    'INPUT': costa_proj,
                    'DISTANCE': 150,
                    'SEGMENTS': 5,
                    'END_CAP_STYLE': 0,
                    'JOIN_STYLE': 0,
                    'MITER_LIMIT': 2,
                    'DISSOLVE': True,
                    'OUTPUT': 'memory:'
                }
            )

            buffer_costa = buffer_result['OUTPUT']

            # =========================
            # ELIMINAR ZONA COSTERA
            # =========================

            legal_result = processing.run(
                "native:extractbylocation",
                {
                    'INPUT': layer,
                    'PREDICATE': [2],  # disjoint
                    'INTERSECT': buffer_costa,
                    'OUTPUT': 'memory:'
                }
            )

            layer = legal_result['OUTPUT']

            layer.setName("Resultado_Final_Legal")

            # =========================
            # CREAR CAMPO VIABILIDAD
            # =========================

            if 'viabilidad' not in [
                f.name() for f in layer.fields()
            ]:

                layer.startEditing()

                layer.addAttribute(
                    QgsField(
                        'viabilidad',
                        QVariant.Double
                    )
                )

                layer.updateFields()

            if not layer.isEditable():
                layer.startEditing()

            # =========================
            # ÍNDICES
            # =========================

            idx_acces = layer.fields().indexFromName(
                'acces_norm'
            )

            idx_turismo = layer.fields().indexFromName(
                'turis_norm'
            )

            idx_pend = layer.fields().indexFromName(
                'pend_norm'
            )

            idx_viab = layer.fields().indexFromName(
                'viabilidad'
            )

            if -1 in (
                idx_acces,
                idx_turismo,
                idx_pend
            ):

                QMessageBox.warning(
                    None,
                    "Error",
                    "Faltan campos necesarios"
                )

                return

            # =========================
            # CALCULAR VIABILIDAD
            # =========================

            for feat in layer.getFeatures():

                acces = feat[idx_acces] or 0
                turismo = feat[idx_turismo] or 0
                pendiente = feat[idx_pend] or 0

                viabilidad = (
                    (peso_acces * acces) +
                    (peso_turismo * turismo) +
                    (peso_pend * pendiente)
                )

                layer.changeAttributeValue(
                    feat.id(),
                    idx_viab,
                    viabilidad
                )

            layer.commitChanges()

            # =========================
            # SIMBOLOGÍA
            # =========================

            ranges = []

            def rango(minv, maxv, label, color):

                sym = QgsSymbol.defaultSymbol(
                    layer.geometryType()
                )

                sym.setSize(2)
                sym.setColor(color)

                return QgsRendererRange(
                    minv,
                    maxv,
                    sym,
                    label
                )

            ranges.append(
                rango(
                    0.0,
                    0.4,
                    "Muy baja",
                    QColor(215, 25, 28)
                )
            )

            ranges.append(
                rango(
                    0.4,
                    0.6,
                    "Baja",
                    QColor(253, 174, 97)
                )
            )

            ranges.append(
                rango(
                    0.6,
                    0.75,
                    "Media",
                    QColor(255, 255, 191)
                )
            )

            ranges.append(
                rango(
                    0.75,
                    0.9,
                    "Alta",
                    QColor(166, 217, 106)
                )
            )

            ranges.append(
                rango(
                    0.9,
                    1.0,
                    "Muy alta",
                    QColor(26, 150, 65)
                )
            )

            renderer = QgsGraduatedSymbolRenderer(
                'viabilidad',
                ranges
            )

            renderer.setMode(
                QgsGraduatedSymbolRenderer.Custom
            )

            layer.setRenderer(renderer)

            layer.triggerRepaint()

            # =========================
            # AÑADIR CAPA FINAL
            # =========================

            QgsProject.instance().addMapLayer(layer)

            # =========================
            # MENSAJE FINAL
            # =========================

            QMessageBox.information(
                None,
                "Éxito",
                "Mapa generado correctamente"
            )

            dialog.close()

        # =========================
        # CONECTAR BOTÓN
        # =========================

        dialog.btn_run.clicked.connect(ejecutar)

        # =========================
        # MOSTRAR VENTANA
        # =========================

        dialog.exec_()