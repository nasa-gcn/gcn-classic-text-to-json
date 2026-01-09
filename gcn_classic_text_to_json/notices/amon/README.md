# AMON Text Conversion

Parses through all webpages with AMON text notices and creates a JSON with GCN schema keywords. Creates a `amon_jsons` directory inside an `output` directory and saves jsons as `AMON_{serial_number}_{record_number}.json` where serial_number is a random iterating number with no association to the notices and record_number is the current notice in the webpage.

### Uses the following fields from the core schema for text notice fields
- `id` &#8594; EVENT_NUM, RUN_NUM
- `ra` &#8594; SRC_RA
- `dec` &#8594; SRC_DEC
- `ra_dec_error` &#8594; SRC_ERROR
- `alert_datetime` &#8594; NOTICE_DATE
- `trigger_time` &#8594; DISCOVERY_DATE, DISCOVERY_TIME
- `event_name` &#8594; EVENT_NAME
- `record_number` &#8594; REVISION
- `far` &#8594; FAR

### Defines the following new fields for the text notice fields
- `notice_type` &#8594; NOTICE_TYPE
- `n_events` &#8594; N_EVENTS
- `delta_time` &#8594; DELTA_T
- `sigma_time` &#8594; SIGMA_T
- `false_positive` &#8594; FALSE_POS
- `charge` &#8594; CHARGE
- `signalness` &#8594; SIGNALNESS, SIGNAL_TRACKNESS
- `coincidence_with` &#8594; COINC_PAIR

## Caveats
- The notices have a field called STREAM, but these seems to be degenrate with NOTICE_TYPE and so I've not added these to the JSONs
- SKYMAP_FITS_URL is a field for the Burst notice but these are not available for any of the notices. Hence, I've not included them in the JSONs
