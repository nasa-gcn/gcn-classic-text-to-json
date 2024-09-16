# CALET Text Conversion

### Uses the following fields from the core schema for text notice fields
- `id` &#8594; TRIGGER_NUM
- `ra` &#8594; POINT_RA
- `dec` &#8594; POINT_DEC
- `alert_datetime` &#8594; NOTICE_DATE
- `trigger_time` &#8594; TRIGGER_DATE, TRIGGER_TIME
- `rate_snr` &#8594; SIGNIFICANCE
- `latitude`, `longitude` &#8594; SC_LON_LAT
- `rate_energy_range` &#8594; ENERGY_BAND
- `detector_status` &#8594; TRIGGER_DET

### Defines the following new fields for the text notice fields
- `url` &#8594; LC_URL,
- `rate_snr` &#8594; SIGNIFICANCE
- `foreground_duration` &#8594; FOREGND_DUR
- `background_duration` &#8594; BACKGND_DUR1

## Caveats
- `url` has been converted as is from the GCN text notices but some of them do not link to lightcurves.