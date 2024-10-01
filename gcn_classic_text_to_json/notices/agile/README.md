# AGILE Text Conversion

Parses through all webpages with AGILE text notices and creates a JSON with GCN schema keywords. Creates a `agile_jsons` directory inside an `output` directory and saves jsons as `AGILE_{serial_number}_{record_number}.json` where serial_number is a random iterating number with no association to the notices and record_number is the current notice in the webpage.

### Uses the following fields from the core schema for text notice fields
- `id` &#8594; TRIGGER_NUM
- `ra` &#8594; GRB_RA (Ground Only)
- `dec` &#8594; GRB_DEC (Ground Only)
- `ra_dec_error` &#8594; GRB_ERROR (Ground Only)
- `alert_datetime` &#8594; NOTICE_DATE
- `trigger_time` &#8594; GRB_DATE, GRB_TIME
- `latitude`, `longitude` &#8594; SC_LON_LAT (MCAL Only)

### Defines the following new fields for the text notice fields
- `n_events` &#8594; GRB_TOTAL_COUNTS (MCAL Only)
- `n_events_x`, `n_events_y` &#8594; GRB_INTEN (Ground Only)
- `snr_x`, `snr_y` &#8594; GRB_SIGNIF (Ground Only)
- `events_snr` &#8594; GRB_SIGNIF (MCAL Only)
- `lightcurve_url` &#8594; LIGHT_CURVE (MCAL Only)
- `peak_events` &#8594; PEAK_COUNTS (MCAL Only)
- `peak_snr` &#8594; PEAK_SIGNIF (MCAL Only)
- `bkg_events` &#8594; BACKGROUND (MCAL Only)
- `triggering_interval` &#8594; DATA_TIME_SCALE (MCAL Only)
- `events_energy_range` &#8594; ENERGY_RANGE (MCAL Only)
- `trigger_logic` &#8594; TRIGGER_LOGIC
