# HETE Text Conversion

Parses through all webpages with HETE text notices and creates a JSON with GCN schema keywords. Creates a `hete_jsons` directory inside an `output` directory and saves jsons as `HETE_{serial_number}_{record_number}.json` where serial_number is a random iterating number with no association to the notices and record_number is the current notice in the webpage.

### Uses the following fields from the core schema for text notice fields
- `id` &#8594; TRIGGER_NUM
- `record_number` &#8594; Seq_Num
- `ra` &#8594; SC_-Z_RA
- `dec` &#8594; SC_-Z_DEC
- `alert_datetime` &#8594; NOTICE_DATE
- `trigger_time` &#8594; GRB_DATE, GRB_TIME
- `rate_snr` &#8594; WXM_SIG/NOISE
- `longitude` &#8594; SC_LONG
- `rate_energy_range` &#8594; TRIGGER_SOURCE
- `net_count_rate`, `rate_duration` &#8594; GAMMA_RATE

### Defines the following new fields for the text notice fields
- `notice_type` &#8594; NOTICE_TYPE
- `wxm_ra` &#8594; WXM_CNTR_RA
- `wxm_dec` &#8594; WXM_CNTR_DEC
- `wxm_ra_dec_error` &#8594; WXM_MAX_SIZE
- `wxm_image_snr` &#8594; WXM_LOC_SN
- `sxc_ra` &#8594; SXC_CNTR_RA
- `sxc_dec` &#8594; SXC_CNTR_DEC
- `sxc_ra_dec_error` &#8594; SXC_MAX_SIZE
- `sxc_image_snr` &#8594; SXC_LOC_SN

## Caveats
- There were fields which encapsulated the snr of the WXM and SXC instuments along the x and y directions which I have not included in the conversions
