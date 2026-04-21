# V3.7 Release Handoff

Fecha de validacion: 2026-04-21

## Estado

V3.7 queda validada como base funcional para continuar.

Se confirmo:

- El ejecutable abre correctamente desde la entrega final.
- `Control & Scan` ya usa `Scan Mode` de V3.7.
- `Adaptive Logarithmic Sweep` usa la configuracion de `Log Sweep Designer`.
- `Preview Run Plan` y `Run` ya pasan por la ruta nueva de sweep logaritmico.
- La logica de DC bias permanece separada del selector de scan mode.

## Rutas correctas

### Ejecutar desde fuente

```powershell
cd C:\Projects\SynAptIp-LCR-Link-Tester
.\.venv\Scripts\python.exe src_v3_7\lcr_control_v3_7.py
```

### Compilar V3.7

```powershell
cd C:\Projects\SynAptIp-LCR-Link-Tester
cmd /c build_v3_7.bat
```

### Ejecutable final para distribuir

Carpeta a copiar completa:

`C:\Projects\SynAptIp-LCR-Link-Tester\dist\SynAptIp_Nyquist_Analyzer_V3_7`

Ejecutable dentro de esa carpeta:

`C:\Projects\SynAptIp-LCR-Link-Tester\dist\SynAptIp_Nyquist_Analyzer_V3_7\SynAptIp_Nyquist_Analyzer_V3_7.exe`

## Archivos clave que quedaron bien

- `src_v3_7\ui_v37\main_window_v3_7.py`
- `src_v3_7\lcr_control_v3_7.py`
- `lcr_control_v3_7.spec`
- `build_v3_7.bat`
- `requirements.txt`

## Entorno

La `.venv` anterior estaba rota porque apuntaba a un Python que ya no existia.

Se dejo una `.venv` nueva funcional en:

`C:\Projects\SynAptIp-LCR-Link-Tester\.venv`

Respaldo de la venv anterior:

`C:\Projects\SynAptIp-LCR-Link-Tester\.venv_broken_20260421_012630`

## Regla importante para la siguiente version

Tomar V3.7 como base estable.

Para V3.8 o siguiente:

- Duplicar desde la entrega ya validada.
- Mantener la cadena de herencia V3.7 -> V3.6 -> V3.5 -> V3.
- Si se modifica el empaquetado, validar tambien el `.spec`.
- Probar siempre:
  - apertura del `.exe`
  - `Preview Run Plan`
  - `Run`
  - `Adaptive Logarithmic Sweep`
  - modo con y sin DC bias

## PPO recordatorio corto

`PPO` = puntos por orden de magnitud.

Formula:

```text
points = int((log10(stop_hz) - log10(start_hz)) * PPO) + 1
```

Ejemplo:

- `10 Hz -> 100 kHz` son 4 decadas
- con `PPO = 10`
- total = `4 * 10 + 1 = 41 puntos`

## Recomendacion de limpieza

Conservar:

- `.venv`
- `dist\SynAptIp_Nyquist_Analyzer_V3_7`
- `build_v3_7.bat`
- `lcr_control_v3_7.spec`
- este archivo de handoff

No borrar todavia si no hay otra copia:

- `.venv_broken_20260421_012630`

Se puede borrar despues, cuando todo quede confirmado tambien en la otra computadora.
