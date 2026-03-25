# Reproducibility Guide: Running the Example Workflow

## 1. Locate Example Datasets

Example datasets are stored in:
- `example_data/resistance_example.csv`
- `example_data/capacitor_example.csv`
- `example_data/rc_example.csv`
- `example_data/rc_dcbias_example.csv`

## 2. Launch the Software

From repository root:

```bash
python src_v3/lcr_control_v3.py
```

Or use the packaged executable if available.

## 3. Load an Example File

In the Nyquist Analysis tab:
1. Select `Load File 1`.
2. Choose one CSV file from `example_data/`.
3. Optionally load File 2 and File 3 for comparison.

## 4. Run Nyquist Analysis

1. Click `Refresh Nyquist` to render the in-app plot.
2. Click `Autozoom` to fit all loaded curves.

## 5. Export Transformed CSV

Click `Export CSV` to generate transformed Nyquist datasets.
Expected files:
- `resistance_example_nyquist_data.csv`
- `capacitor_example_nyquist_data.csv`
- `rc_example_nyquist_data.csv`
- `rc_dcbias_example_nyquist_data.csv`

## 6. Export JPG

For visual outputs:
- Click `Export JPG (compare)` to generate a comparison image.
- Optionally use individual JPG export options as needed.

Expected comparison image:
- `nyquist_compare_examples.jpg`

## 7. Reproduce Expected Outputs

The repository includes example outputs in `example_outputs/` for reference.
To reproduce them:
1. Use the datasets in `example_data/`.
2. Apply the same Nyquist workflow.
3. Export files using the same output naming convention.

Estimated reproduction time for the full example pipeline is typically under 5 minutes on a standard development machine.

## Notes

This guide documents a computational workflow for reproducibility of software behavior. It does not claim institution-specific validation or manufacturer endorsement.
