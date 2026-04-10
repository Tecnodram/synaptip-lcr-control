"""
validate_v3_6.py — SynAptIp V3.6 Validation Script
Run from project root:
    python validate_v3_6.py
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
desired = [str(_ROOT / 'src_v3_6'), str(_ROOT / 'src_v3'), str(_ROOT / 'src_v3_5')]
for p in reversed(desired):
    if p not in sys.path:
        sys.path.insert(0, p)

results = []

def check(name, fn):
    try:
        fn()
        results.append(('PASS', name, ''))
    except Exception as e:
        results.append(('FAIL', name, str(e)[:120]))

# ---- Licensing ----
from licensing.license_manager import LicenseManagerV36, LicenseState, build_license_content
from licensing.device_fingerprint import get_device_fingerprint
from licensing.license_storage import save_license_path
from pathlib import Path as Pt

fp = get_device_fingerprint()
mgr = LicenseManagerV36()
_lic_dir = _ROOT / 'licenses'
_lic_dir.mkdir(exist_ok=True)

def t1():
    save_license_path('')
    r = mgr.evaluate()
    assert r.state == LicenseState.NOT_LOADED, f'Got {r.state}'
check('Licencia [1/5]: sin licencia -> NOT_LOADED', t1)

def t2():
    lic = _lic_dir / 'synaptip_synaptip_test_v3.6_20260409.lic'
    r = mgr.validate_file(lic)
    assert r.state == LicenseState.VALID, f'Got {r.state}: {r.message}'
    assert r.days_left > 0
check('Licencia [2/5]: valida -> VALID', t2)

def t3():
    c = build_license_content('X','SynAptIp LCR Link Tester','3.6','commercial',fp,'2024-01-01','2024-06-01')
    p = _lic_dir / '_t3.lic'; p.write_text(c)
    r = mgr.validate_file(p); p.unlink()
    assert r.state == LicenseState.EXPIRED, f'Got {r.state}'
check('Licencia [3/5]: vencida -> EXPIRED', t3)

def t4():
    p = _lic_dir / '_t4.lic'
    p.write_text('aGVsbG8gd29ybGQ.' + 'a'*64)
    r = mgr.validate_file(p); p.unlink()
    assert r.state == LicenseState.INVALID, f'Got {r.state}'
check('Licencia [4/5]: invalida -> INVALID', t4)

def t5():
    c = build_license_content('X','SynAptIp LCR Link Tester','3.6','commercial','a'*64,'2026-01-01','2027-01-01')
    p = _lic_dir / '_t5.lic'; p.write_text(c)
    r = mgr.validate_file(p); p.unlink()
    assert r.state == LicenseState.WRONG_DEVICE, f'Got {r.state}'
check('Licencia [5/5]: otro device -> WRONG_DEVICE', t5)

# ---- Compare panel ----
import pandas as pd
from analysis_engine.schema_detector import detect_schema
from analysis_engine.eis_transformer import transform, COL_Z_REAL, COL_MZ_IMG

def t6():
    df = pd.DataFrame({'freq_hz': [1e3,1e4,1e5], 'z_real': [10,8,5], 'z_imag': [5,3,1]})
    tdf = transform(df, detect_schema(df))
    assert COL_Z_REAL in tdf.columns and COL_MZ_IMG in tdf.columns
check('Compare [1/3]: schema_detector + eis_transformer', t6)

def t7():
    from ui_v36.compare_panel import _make_comparison_figure
    df = pd.DataFrame({'freq_hz': [1e2,1e3,1e4,1e5], 'z_real': [20,15,10,5], 'z_imag': [10,8,5,2]})
    tdf = transform(df, detect_schema(df))
    png, log = _make_comparison_figure([('Test CSV 1', tdf)], None)
    assert len(png) > 500, 'PNG too small'
    assert '[OK]' in log
check('Compare [2/3]: 1 archivo -> PNG generado', t7)

def t8():
    from ui_v36.compare_panel import _make_comparison_figure
    datasets = []
    for i in range(3):
        df = pd.DataFrame({'freq_hz': [1e2+i,1e3+i,1e4+i], 'z_real': [20-i*2,15,10], 'z_imag': [8,5,3]})
        datasets.append((f'CSV {i+1}', transform(df, detect_schema(df))))
    png, log = _make_comparison_figure(datasets, None)
    ok_count = log.count('[OK]')
    assert ok_count == 3, f'Expected 3 [OK], got {ok_count}'
check('Compare [3/3]: 3 archivos -> 3 [OK] en log', t8)

# ---- V3.5 intacto ----
def t9():
    from analysis_engine.cleaning_pipeline import clean
    from analysis_engine.export_manager import ExportManager
    from analysis_engine.interpretation_engine import interpret
    from analysis_engine.plot_engine import PlotEngine
check('V3.5: todos los modulos analysis_engine intactos', t9)

def t10():
    from services.csv_exporter import CsvExporter, LIVE_RESULTS_FIELDNAMES
    from services.license_manager import LicenseManager
    from services.device_fingerprint import get_device_id
    from services.scan_runner import ScanRunner
check('V3: todos los servicios intactos', t10)

# ---- Report ----
print()
print('=' * 65)
print('  REPORTE DE VALIDACION COMPLETA — SynAptIp V3.6')
print('=' * 65)
for r in results:
    icon = 'PASS' if r[0] == 'PASS' else 'FAIL'
    print(f'  [{icon}] {r[1]}')
    if r[0] == 'FAIL':
        print(f'         ERROR: {r[2]}')

passed = sum(1 for r in results if r[0] == 'PASS')
failed = sum(1 for r in results if r[0] == 'FAIL')
print('=' * 65)
print(f'  Resultado: {passed}/{len(results)} OK', '-- TODOS PASAN' if failed == 0 else f'-- {failed} FALLO(S)')
print('=' * 65)
sys.exit(0 if failed == 0 else 1)
