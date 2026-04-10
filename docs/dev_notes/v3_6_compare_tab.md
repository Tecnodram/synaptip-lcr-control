# V3.6 Tab "Comparar" — Referencia Técnica
SynAptIp Technologies

---

## Archivo

`src_v3_6/ui_v36/compare_panel.py` — `ComparePanel(QWidget)`

## Funcionalidad

- Carga hasta 3 archivos CSV
- Detección automática de columnas (reutiliza `schema_detector` de V3.5)
- Transformación EIS (reutiliza `eis_transformer` de V3.5)
- Gráfica Nyquist superpuesta con leyenda clara
- Soporte para DC bias (múltiples grupos por archivo)
- Exportación PNG (con diálogo de archivo)
- Log de estado por operación

## Módulos reutilizados (sin modificar)

```python
from analysis_engine.schema_detector import detect_schema
from analysis_engine.eis_transformer import (
    transform, COL_FREQ, COL_Z_REAL, COL_MZ_IMG, COL_DC
)
```

## Componentes UI

| Widget | Descripción |
|---|---|
| `_CsvSlot` × 3 | Slot individual: ruta, browse, clear, status |
| `QPushButton#comparePlotBtn` | Genera gráfica |
| `QPushButton#compareClearBtn` | Limpia todos los slots |
| `QPushButton#compareExportBtn` | Exporta PNG último renderizado |
| `QLabel#comparePlotArea` | Muestra la gráfica renderizada |
| `QTextEdit#compareLog` | Log de operaciones (Consolas, tema oscuro) |

## Paleta de colores por dataset

| CSV | Color | Marker |
|---|---|---|
| CSV 1 | `#1d4ed8` (azul) | `o` |
| CSV 2 | `#b45309` (ámbar) | `s` |
| CSV 3 | `#059669` (verde) | `^` |

Cuando hay múltiples grupos DC bias en un dataset, se aplica transparencia escalonada.

## Threading

El plot se genera en `_PlotWorker(QThread)` para no bloquear la UI.
Señales: `finished(bytes, str)` y `error(str)`.

## Integración con la ventana principal

`MainWindowV3_6._sync_compare_output_dir()` sincroniza la carpeta de salida
con el campo "Sample & Output" heredado de V3. Los PNG exportados van a
`<output_folder>/compare/`.

## Resizing

`ComparePanel.resizeEvent()` redimensiona el QPixmap manteniendo aspect ratio.
