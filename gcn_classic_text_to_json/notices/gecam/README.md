# GECAM Text Conversion

Parses through all webpages with GECAM text notices and creates a JSON with GCN schema keywords. Creates a `gecam_jsons` directory inside an `output` directory and saves jsons as `GECAM_{serial_number}_{record_number}.json` where serial_number is a random iterating number with no association to the notices and record_number is the current notice in the webpage.

### Uses the following fields from the core schema for text notice fields
- `id` &#8594; TRIGGER_NUMBER
- `ra` &#8594; SRC_RA
- `dec` &#8594; SRC_DEC
- `ra_dec_error` &#8594; SRC_ERROR68
- `alert_datetime` &#8594; NOTICE_DATE
- `trigger_time` &#8594; EVENT_DATE/EVENT_TIME
- `net_count_rate` &#8594; BURST_INTEN
- `rate_duration` &#8594; BURST_DUR
- `rate_snr` &#8594; TRIGGER_SIGNIF
- `rate_energy_range` &#8594; TRIGGER_ERANGE
- `classification` &#8594; SRC_CLASS
- `instrument_phi` &#8594; PHI
- `instrument_theta` &#8594; THETA
- `latitude` &#8594; SC_LAT
- `longitude` &#8594; SC_LON

### Defines the following new fields for the text notice fields
- `notice_type` &#8594; NOTICE_TYPE
- `mission_type` &#8594; MISSION
- `trigger_duration` &#8594; TRIGGER_DUR
- `detector_status` &#8594; TRIGGER_DETS
