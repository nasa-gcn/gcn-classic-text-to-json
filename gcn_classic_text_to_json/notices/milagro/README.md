# MILAGRO Text Conversion

Parses through all webpages with MILAGRO text notices and creates a JSON with GCN schema keywords. Creates a `milagro_jsons` directory inside an `output` directory and saves jsons as `MILAGRO_{serial_number}_{record_number}.json` where serial_number is a random iterating number with no association to the notices and record_number is the current notice in the webpage.

### Uses the following fields from the core schema for text notice fields
- `id` &#8594; TRIGGER_NUM
- `ra` &#8594; GRB_RA
- `dec` &#8594; GRB_DEC
- `ra_dec_error` &#8594; GRB_ERROR
- `alert_datetime` &#8594; NOTICE_DATE
- `trigger_time` &#8594; GRB_DATE, GRB_TIME


### Defines the following new fields for the text notice fields
- `n_events` &#8594; GRB_FLUENCE
- `bkg_events` &#8594; BKG
- `duration` &#8594; GRB_DUR
- `stat_signif` &#8594; GRB_SIGNIF
- `annual_rate` &#8594; ANN_RATE
- `zenith` &#8594; GRB_ZEN
