# SUZAKU Text Conversion

Parses through all webpages with SUZAKU text notices and creates a JSON with GCN schema keywords. Creates a `suzaku_jsons` directory inside an `output` directory and saves jsons as `SUZAKU_WAM_{serial_number}_{record_number}.json` where serial_number is a random iterating number with no association to the notices and record_number is the current notice in the webpage.

### Uses the following fields from the core schema for text notice fields
- `id` &#8594; TRIGGER_NUM
- `alert_datetime` &#8594; NOTICE_DATE
- `trigger_time` &#8594; TRIGGER_DATE, TRIGGER_TIME

### Defines the following new fields for the text notice fields
- `lightcurve_url` &#8594; LC_URL
