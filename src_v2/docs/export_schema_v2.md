# Export Schema V2

This document defines Version 2 export layout for SynAptIp LCR Control V2.

## File Types

Type A: raw instrument-compatible measurement rows

Columns:
- timestamp
- sample_id
- freq_hz
- dc_bias_v
- raw_response
- primary
- secondary
- status

Notes:
- raw_response stores the exact comma-separated line returned by the instrument.
- primary maps to the first numeric value in the triple (expected z_ohm in Z-theta mode).
- secondary maps to the second numeric value in the triple (expected theta_deg in Z-theta mode).

Type B: enriched CSV for analysis and Nyquist preview

Columns:
- timestamp
- sample_id
- freq_hz
- ac_voltage_v
- dc_bias_on
- dc_bias_v
- z_ohm
- theta_deg
- status
- raw_response
- optional z_real
- optional z_imag
- notes

Notes:
- z_real and z_imag are optional because they may be backfilled later from z_ohm/theta_deg.
- raw_response remains present for traceability and parser fallback.

## File-Level Metadata Block

Each CSV begins with comment-prefixed metadata rows in this format:

- # key: value

The metadata keys are:
- project_name
- app_name
- app_version
- instrument_model
- instrument_idn
- com_port
- baudrate
- terminator
- created_at
- operator
- sample_id
- notes
- frequency_start_hz
- frequency_stop_hz
- frequency_step_hz
- bias_list
- point_settle_delay_s
- bias_settle_delay_s
- main_display_assumption
- secondary_display_assumption
- range_mode
- speed_mode

## Confirmed Command Context (V2)

This export schema assumes data is acquired through confirmed lab command paths:
- FREQ <value in Hz>
- VOLT <value>
- BIAS ON
- BIAS OFF
- :BIAS:VOLTage <value>

Optional verification reads:
- :BIAS?
- :BIAS:STAT?
- :BIAS:VOLT?

Measurement fetch path:
- FETC? with response shape like:
  +2.76843E+04,-2.41235E+01,0
