# V3.6 Licensing System — Technical Reference
SynAptIp Technologies

---

## Arquitectura

```
src_v3_6/licensing/
├── __init__.py
├── device_fingerprint.py    ← SHA-256(hostname|OS|CPU|cpu_count|MAC)
├── license_manager.py       ← LicenseManagerV36, LicenseResult, LicenseState
└── license_storage.py       ← Persistencia en %APPDATA%/SynAptIp/license_v36.json
```

## Diferencias con sistema V3

| Aspecto | V3 | V3.6 |
|---|---|---|
| Formato | Clave de texto (`SYNAPT-V3-xxx`) | Archivo `.lic` |
| Payload | device_id + expires_utc + plan | 7 campos estructurados |
| issued_to | No incluido | Incluido |
| product_name | No verificado | Verificado |
| license_type | Solo "standard" | commercial/academic/evaluation/trial |
| Almacenamiento | `license.json` con activation_key | `license_v36.json` con ruta de .lic |
| Secret | `SynAptIp-V3-License-Offline-Validation-2026` | `SynAptIp-V3.6-License-Professional-2026-Offline` |
| Fingerprint | SHA-256(node|system|processor) | SHA-256(node|system|processor|cpu_count|MAC) |
| Trial | 14 días (automático) | Sin trial — requiere .lic |

## Estados LicenseState

```python
class LicenseState(Enum):
    VALID        = "valid"         # válida y vigente
    EXPIRED      = "expired"       # vencida
    INVALID      = "invalid"       # firma inválida o producto incorrecto
    WRONG_DEVICE = "wrong_device"  # fingerprint no coincide
    NOT_LOADED   = "not_loaded"    # sin archivo .lic
    CORRUPT      = "corrupt"       # archivo malformado
```

## LicenseResult

```python
@dataclass
class LicenseResult:
    state:        LicenseState
    message:      str
    issued_to:    str   # "Cliente S.A."
    license_type: str   # "commercial"
    issued_at:    str   # "2026-04-09"
    expires_at:   str   # "2026-10-09"
    days_left:    int   # 183
    fingerprint:  str   # 64-char hex
```

## Formato .lic

```
<base64url_payload_json>.<hmac_sha256_hex_full>
```

Payload JSON (ordenado, compacto):
```json
{"expires_at":"2026-10-09","issued_at":"2026-04-09","issued_to":"...","license_type":"commercial","machine_fingerprint":"...","product_name":"SynAptIp LCR Link Tester","product_version":"3.6"}
```

## Uso programático

```python
from licensing.license_manager import LicenseManagerV36
from pathlib import Path

mgr = LicenseManagerV36()

# Obtener fingerprint
fp = mgr.device_fingerprint

# Cargar y persistir licencia
result = mgr.load_from_file(Path("cliente.lic"))
if result.is_valid:
    print(f"Válida hasta {result.expires_at}")

# Evaluar licencia almacenada
result = mgr.evaluate()
print(result.state, result.message)

# Limpiar
mgr.clear_license()
```
