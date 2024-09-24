# SuperKamiokande_SuperNova Text Conversion

Parses through all webpages with SK_SN text notices and creates a JSON with GCN schema keywords. Creates a `sk_sn_jsons` directory inside an `output` directory and saves jsons as `SK_SN_{serial_number}.json` where serial_number is a random iterating number with no association to the notices.

### Uses the following fields from the core schema for text notice fields
- `id` &#8594; TRIGGER_NUMBER
- `ra` &#8594; SRC_RA
- `dec` &#8594; SRC_DEC
- `alert_datetime` &#8594; NOTICE_DATE
- `trigger_time` &#8594; DISCOVERY_DATE, DISCOVERY_TIME
- `ra_dec_error` &#8594; SRC_ERROR90

### Defines the following new fields for the text notice fields
- `ra_dec_error_68` &#8594; SRC_ERROR68
- `ra_dec_error_95` &#8594; SRC_ERROR95
- `n_events` &#8594; N_EVENTS
- `duration` &#8594; COLLECTION_DURATION
- `energy_limit` &#8594; ENERGY_LIMIT
- `distance_range` &#8594; DISTANCE
