# Nyquist Preview V2 Compatibility

This note defines lightweight Nyquist-preview compatibility for Version 2 exports.

## Raw Triple Interpretation

Expected raw response from confirmed fetch path:
- FETC? -> z_ohm, theta_deg, status

Example:
- +2.76843E+04,-2.41235E+01,0

Interpretation:
- Field 1: z_ohm
- Field 2: theta_deg
- Field 3: status

## Conversion Formula

Use:
- theta_rad = theta_deg * pi / 180
- z_real = z_ohm * cos(theta_rad)
- z_imag = z_ohm * sin(theta_rad)

## Nyquist Plotting Convention

For preview plotting:
- X = z_real
- Y = -z_imag

The negative sign follows standard Nyquist display convention.

## File-Type Compatibility

The preview loader should accept both V2 file types.

Type A (raw):
- Use primary as z_ohm and secondary as theta_deg when present.
- If primary/secondary missing, parse raw_response directly.

Type B (enriched):
- Prefer z_real and z_imag when already present.
- Otherwise compute from z_ohm and theta_deg.
- Keep raw_response as fallback parser source.

## Lightweight Scaffold Scope

Version 2 currently includes only a preview-read scaffold:
- parser for either file type
- conversion helper for z_real/z_imag
- utility to emit Nyquist X/Y arrays

It intentionally does not include full Nyquist fitting, model solving, or report generation.
