# INTEGRAL Text Conversion

Parses through all webpages with INTEGRAL text notices and creates a JSON with GCN schema keywords. Creates a `integral_jsons` directory inside an `output` directory and saves jsons as `INTEGRAL_{serial_number}_{record_number}.json` where serial_number is a random iterating number with no association to the notices and record_number is the current notice in the webpage.

### Uses the following fields from the core schema for text notice fields
- `id` &#8594; TRIGGER_NUM
- `ra` &#8594; GRB_RA
- `dec` &#8594; GRB_DEC
- `ra_dec_error` &#8594; GRB_ERROR
- `alert_datetime` &#8594; NOTICE_DATE
- `trigger_time` &#8594; GRB_DATE, GRB_TIME

### Defines the following new fields for the text notice fields
- `sc_ra` &#8594; SC_RA
- `sc_dec` &#8594; SC_DEC
- `snr` &#8594; GRB_INTEN
