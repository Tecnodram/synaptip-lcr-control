from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_V35 = ROOT / "src_v3_5"
SRC_V3 = ROOT / "src_v3"
APP_VERSION = "3.5.0"

for path in (SRC_V35, SRC_V3):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

import pandas as pd

from analysis_engine import export_manager as em
from analysis_engine.cleaning_pipeline import run as clean
from analysis_engine.eis_transformer import COL_DC, transform
from analysis_engine.interpretation_engine import interpret
from analysis_engine.plot_engine import PlotEngine
from analysis_engine.schema_detector import detect_schema


def _load_dataset(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def _run_validation(dataset_path: Path) -> None:
    raw_df = _load_dataset(dataset_path)
    schema = detect_schema(raw_df)
    enriched_df = transform(raw_df, schema)

    group_col = None
    if schema.has_dc_bias and COL_DC in enriched_df.columns and enriched_df[COL_DC].notna().any():
        group_col = COL_DC

    result = clean(enriched_df, group_col=group_col)

    # Validation-level normalization consistency check (no analysis logic change).
    dup_cols = ["freq_hz"]
    if group_col:
        dup_cols = [group_col, "freq_hz"]
    dup_count = int(result.clean_df.duplicated(subset=dup_cols, keep=False).sum())
    if dup_count > 0:
        raise RuntimeError(f"Duplicate frequency points detected in cleaned data: {dup_count}")

    run_root = ROOT / "validation" / "outputs"
    timestamp = f"validation_{dataset_path.stem}"
    paths = em.create_run(run_root, timestamp=timestamp)

    em.save_raw_input(paths, raw_df)
    em.save_clean_data(paths, result.clean_df)
    em.save_removed_points(paths, result.removed_df)
    em.save_cleaning_summary(paths, result.summary)

    if group_col:
        em.save_dc_bias_summary(paths, em.build_dc_bias_summary(result.clean_df, group_col))

    plots = PlotEngine(paths.figures_dir).run(result.clean_df, raw_df=enriched_df)
    interpretation = interpret(
        result.clean_df,
        result.global_summary,
        has_dc_bias=schema.has_dc_bias,
        source_filename=dataset_path.name,
        app_version=APP_VERSION,
    )
    em.save_report(paths, interpretation.text, interpretation.markdown)

    detected_warnings = list(schema.warnings) + list(interpretation.warnings) + list(paths.errors)
    em.save_metadata(
        paths,
        run_config={
            "input_file": str(dataset_path),
            "output_dir": str(run_root),
            "selected_outputs": "all",
            "group_col": group_col,
            "timestamp": timestamp,
        },
        app_version=APP_VERSION,
        timestamp=timestamp,
        input_filename=dataset_path.name,
        schema_info={
            "impedance_mode": schema.impedance_mode,
            "column_map": schema.column_map,
            "has_dc_bias": schema.has_dc_bias,
            "has_status": schema.has_status,
            "has_freq": schema.has_freq,
            "warnings": schema.warnings,
        },
        cleaning_summary={
            "global": result.global_summary,
            "per_group": result.summary.to_dict(orient="records"),
        },
        plots_generated=sorted(plots.keys()),
        warnings_detected=detected_warnings,
        normalization_applied=True,
        dc_bias_grouping_used=bool(group_col),
    )

    required_dirs = [
        paths.raw_dir,
        paths.cleaned_dir,
        paths.figures_dir,
        paths.tables_dir,
        paths.report_dir,
        paths.metadata_dir,
    ]
    missing_dirs = [str(path) for path in required_dirs if not path.exists()]
    if missing_dirs:
        raise RuntimeError(f"Missing export directories: {missing_dirs}")
    if not paths.report_txt or not paths.report_md:
        raise RuntimeError("Interpretation report was not generated.")
    if not plots:
        raise RuntimeError("No plots were generated.")
    if detected_warnings:
        raise RuntimeError(f"Warnings detected: {detected_warnings}")

    removed_pct = result.global_summary["percent_removed"]
    print(f"{dataset_path.name}: % points removed = {removed_pct:.2f}")
    print(f"{dataset_path.name}: number of plots = {len(plots)}")
    print(f"{dataset_path.name}: interpretation findings count = {len(interpretation.findings)}")
    print(f"{dataset_path.name}: export folder = {paths.run_dir}")


def main() -> int:
    datasets = [
        ROOT / "validation" / "rc_example.csv",
        ROOT / "validation" / "rc_dcbias_example.csv",
    ]
    for dataset in datasets:
        _run_validation(dataset)
    print("VALIDATION PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())