# SNEWS Text Conversion

### Uses the following fields from the core schema for text notice fields
- `id` &#8594; TRIGGER_NUM
- `ra` &#8594; EVENT_RA/EVT_RA
- `dec` &#8594; EVENT_DEC/EVT_DEC
- `alert_datetime` &#8594; NOTICE_DATE
- `trigger_time` &#8594; EVENT_DATE/EVT_DATE, EVENT_TIME/EVT_TIME
- `ra_dec_error` &#8594; EVENT_ERROR/EVT_ERROR
- `containment_probability` &#8594; EVENT_ERROR

### Defines the following new fields for the text notice fields
- `n_events` &#8594; EVENT_FLUENCE/EVT_FLUENCE
- `duration` &#8594; EVENT_DUR/EVT_DUR
- `detector_quality` &#8594; EXPT
