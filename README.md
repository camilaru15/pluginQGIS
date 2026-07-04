
# Plugin QGIS para la Evaluación de la Viabilidad Territorial de Glampings

## Descripción

Este repositorio contiene el código fuente del plugin desarrollado para QGIS como parte del Trabajo Fin de Máster:

> **Desarrollo de un plugin para QGIS que evalúe la viabilidad económica de glampings**

El complemento permite automatizar la evaluación de la aptitud territorial para la implantación de proyectos de glamping mediante técnicas de análisis espacial y evaluación multicriterio (Weighted Linear Combination, WLC).

El plugin integra diferentes variables territoriales y genera un índice de viabilidad que facilita la identificación de áreas potencialmente aptas para el desarrollo de este tipo de alojamientos turísticos.

---

## Funcionalidades

- Validación automática de las capas necesarias.
- Configuración de los pesos de los criterios de evaluación.
- Aplicación de restricciones territoriales mediante la capa `suelo_apto_glamping`.
- Cálculo automático del índice de viabilidad territorial.
- Clasificación de los resultados.
- Aplicación automática de simbología graduada.
- Visualización inmediata de los resultados en QGIS.

---

## Variables utilizadas

El modelo multicriterio considera las siguientes variables:

- Pendiente del terreno.
- Accesibilidad a la red viaria.
- Proximidad a localidades.
- Restricción territorial mediante la capa `suelo_apto_glamping`.

---

## Requisitos

- QGIS 3.34 o superior
- Python 3
- PyQGIS

---

## Instalación

1. Descargar el repositorio.

2. Copiar la carpeta del plugin en:

### Windows

```
C:\Users\<usuario>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins
```

### Linux

```
~/.local/share/QGIS/QGIS3/profiles/default/python/plugins
```

3. Abrir QGIS.

4. Activar el complemento desde:

```
Complementos → Administrar e instalar complementos
```

---

## Datos de entrada

El plugin requiere disponer en el proyecto de las siguientes capas:

| Capa | Tipo |
|------|------|
| Muestreado | Puntos |
| Asturias_Mask | Polígono |
| buffer_costa_150m | Polígono |
| suelo_apto_glamping | Polígono |

La capa de puntos debe contener los siguientes campos normalizados:

- acces_norm
- turis_norm
- pend_norm

---

## Flujo de trabajo

1. Cargar las capas necesarias.
2. Configurar los pesos de cada criterio.
3. Ejecutar el plugin.
4. Calcular el índice de viabilidad.
5. Visualizar el mapa de resultados.

---

## Metodología

El índice de viabilidad territorial se calcula mediante el método de **Combinación Lineal Ponderada (Weighted Linear Combination, WLC)**:

```
Viabilidad =
(PesoAccesibilidad × Accesibilidad)
+
(PesoTurismo × Proximidad)
+
(PesoPendiente × Pendiente)
```

Los pesos pueden modificarse desde la interfaz gráfica del complemento para generar diferentes escenarios de evaluación.

---

## Estructura del proyecto

```
plugin/
│
├── __init__.py
├── metadata.txt
├── plugin.py
├── dialog.py
├── dialog.ui
├── resources.py
├── resources.qrc
├── icon.png
└── README.md
```

---

## Resultados

El complemento genera automáticamente:

- Campo con el índice de viabilidad.
- Clasificación temática.
- Simbología graduada.
- Visualización de la capa resultante.

---

## Limitaciones

Este complemento constituye una herramienta de apoyo a la decisión y no sustituye la normativa urbanística, ambiental o territorial vigente.

Los resultados deben interpretarse como una evaluación preliminar de aptitud territorial.

---

## Autor

**[Tu nombre]**

Trabajo Fin de Máster

Máster en Dirección y Planificación del Turismo

Universidad de Oviedo

---

## Licencia

Este proyecto se distribuye bajo la licencia MIT.
