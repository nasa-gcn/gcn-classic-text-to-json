# ALEXIS text conversion

Parses through the table associated with all ALEXIS triggers and creates a JSON with GCN schema keywords. Creates a `alexis_jsons` directory inside an `output` directory and saves jsons as `ALEXIS_{serial_number}.json` where serial_number is a random iterating number with no association to the notices.

### Uses the following fields from the core schema for text notice fields
- `alert_datetime` &#8594; Date and Time UT
- `ra` &#8594; RA
- `dec` &#8594; Dec
- `ra_dec_error` &#8594; Error
- `containment_probability` &#8594; mentioned in mission description
- `systematic_included` &#8594; mentioned in mission description

### Defines the following new fields for the text notice fields
- `map_duration` &#8594; Dur
- `notice_type` &#8594; Type
- `alpha` &#8594; Alpha
- `telescope_id` &#8594; Tele
- `energy_bandpass` &#8594;  mentioned in mission description
