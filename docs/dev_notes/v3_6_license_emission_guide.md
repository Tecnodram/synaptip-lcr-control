# V3.6 License Emission Guide
SynAptIp Technologies
Fase 3 — Guía de Emisión de Licencias

---

## 1. OBTENER EL FINGERPRINT DEL CLIENTE

El cliente ejecuta desde la carpeta del proyecto (o del exe):

```bash
python tools/show_fingerprint.py
```

**Salida ejemplo:**
```
Full fingerprint:  f049c1597c05b8c9f56839015b17f31f612ca06513def788b2be6355d308a86f
Short (display):   F049C1597C05B8C9
```

El cliente **envía el fingerprint completo (64 hex chars)** a SynAptIp Technologies.

---

## 2. GENERAR LA LICENCIA

Desde la carpeta raíz del proyecto con el venv activo:

```bash
python tools/generate_license.py \
  --issued-to "Nombre del Cliente" \
  --product "SynAptIp LCR Link Tester" \
  --version "3.6" \
  --license-type commercial \
  --months 6 \
  --fingerprint "f049c1597c05b8c9f56839015b17f31f612ca06513def788b2be6355d308a86f"
```

**Parámetros:**

| Parámetro | Descripción | Valores válidos |
|---|---|---|
| `--issued-to` | Nombre o empresa del cliente | Texto libre |
| `--product` | Nombre del producto | `SynAptIp LCR Link Tester` (por defecto) |
| `--version` | Versión | `3.6` (por defecto) |
| `--license-type` | Tipo de licencia | `commercial`, `academic`, `evaluation`, `trial` |
| `--months` | Duración en meses | Número entero (por defecto: 6) |
| `--fingerprint` | Fingerprint del cliente | 64 hex chars |
| `--output` | Ruta del archivo de salida | Opcional (auto si omitido) |

**Salida:** archivo `.lic` en `licenses/` con nombre automático o el especificado.

---

## 3. ENTREGAR LA LICENCIA AL CLIENTE

- Enviar el archivo `.lic` por email o medio seguro.
- El cliente **NO modifica el archivo** — cualquier cambio invalida la firma.

---

## 4. EL CLIENTE CARGA LA LICENCIA

Al iniciar `SynAptIp_Nyquist_Analyzer_V3_6.exe`:

1. Aparece el diálogo de licencia.
2. Si no hay licencia cargada: status = "Sin licencia cargada".
3. Hacer clic en **"Cargar licencia (.lic)"**.
4. Seleccionar el archivo `.lic` recibido.
5. Si es válido: status cambia a verde con días restantes.
6. Hacer clic en **"Continuar"** para abrir la aplicación.

La ruta del archivo queda guardada en `%APPDATA%/SynAptIp/license_v36.json`.
No es necesario cargarla de nuevo cada vez.

---

## 5. RENOVAR UNA LICENCIA

Para renovar antes de que expire:

1. Obtener el fingerprint actual del cliente (puede cambiar si cambia la máquina).
2. Generar un nuevo `.lic` con nueva fecha de vencimiento.
3. Enviar al cliente.
4. El cliente carga el nuevo archivo desde el diálogo.

---

## 6. ESTADOS DE LICENCIA

| Estado | Descripción | Acción |
|---|---|---|
| `valid` | Licencia válida y vigente | Permite continuar |
| `expired` | Licencia vencida | Renovar con nueva fecha |
| `invalid` | Firma inválida (archivo modificado o falso) | Emitir licencia nueva |
| `wrong_device` | Fingerprint no coincide | Verificar fingerprint del cliente |
| `not_loaded` | Ningún archivo cargado | Cliente debe cargar .lic |
| `corrupt` | Archivo malformado | Reenviar el .lic original |

---

## 7. FORMATO DEL ARCHIVO .LIC

El archivo contiene una sola línea:
```
<base64url_json_payload>.<hmac_sha256_hex>
```

El payload JSON (antes de codificar) contiene:
```json
{
  "expires_at": "2026-10-09",
  "issued_at": "2026-04-09",
  "issued_to": "Nombre del Cliente",
  "license_type": "commercial",
  "machine_fingerprint": "f049c1597c05b8c9...",
  "product_name": "SynAptIp LCR Link Tester",
  "product_version": "3.6"
}
```

La firma usa HMAC-SHA256 con el secret de V3.6.
**El secret es diferente al de V3** — las licencias V3 no sirven en V3.6.

---

## 8. VARIABLES DE ENTORNO

Para testing/desarrollo (omite el diálogo de licencia):

```bash
set SYNAPTIP_LICENSE_DISABLED=1
python src_v3_6/lcr_control_v3_6.py
```
