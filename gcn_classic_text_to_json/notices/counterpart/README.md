# Counterpart Text Conversion

Parses through all webpages with Counterpart text notices and creates a JSON with GCN schema keywords. Creates a `counterpart_jsons` directory inside an `output` directory and saves jsons as `COUNTERPART_{serial_number}_{record_number}.json` where serial_number is a random iterating number with no association to the notices and record_number is the current notice in the webpage.

### Uses the following fields from the core schema for text notice fields
- `id` &#8594; TRIGGER_NUM (GRB_Counterpart only)
- `ref_ID` &#8594; EVENT_TRIG_NUM (LVC_Counterpart only)
- `ra` &#8594; CNTRPART_RA
- `dec` &#8594; CNTRPART_DEC
- `ra_dec_error` &#8594; CNTRPART_ERROR
- `alert_datetime` &#8594; NOTICE_DATE
- `trigger_time` &#8594; OBS_DATE, OBS_TIME
- `mission`, `instrument` &#8594; TELESCOPE

### Defines the following new fields for the text notice fields
- `submitter_name` &#8594; SUBMITTER
- `energy_flux`, `energy_flux_error` &#8594; INTENSITY
- `flux_energy_range` &#8594; ENERGY
- `duration` &#8594; OBS_DUR
- `rank` &#8594; RANK

## Caveats
- The LVC counterpart notices have two fields called SOURSE_SERNUM and WARN_FLAGS. I could not find what they represented in the documenatation and elected to ignore them.
