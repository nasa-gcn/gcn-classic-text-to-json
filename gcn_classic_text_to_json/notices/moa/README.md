# MOA Text Conversion

Parses through all webpages with MOA text notices and creates a JSON with GCN schema keywords. Creates a `moa_jsons` directory inside an `output` directory and saves jsons as `MOA_{serial_number}_{record_number}.json` where serial_number is a random iterating number with no association to the notices and record_number is the current notice in the webpage.

### Uses the following fields from the core schema for text notice fields
- `id` &#8594; TRIGGER_NUM
- `ra` &#8594; POINT_RA
- `dec` &#8594; POINT_DEC
- `alert_datetime` &#8594; NOTICE_DATE
- `trigger_time` &#8594; DISCOVERY_DATE, DISCOVERY_TIME

### Defines the following new fields for the text notice fields
- `lightcurve_url` &#8594; LC_URL,
- `max_time` &#8594; MAX_DATE, MAX_TIME
- `max_time_error` &#8594; MAX_UNCERT
- `cusp_width`. `cusp_width_error` &#8594; CUSP_WIDTH
- `u0`, `u0_error` &#8594; u0
- `base_mag`, `base_mag_error` &#8594; BASE_MAG
- `max_mag` &#8594; MAX_MAG/PEAK_MAG
- `amplification` &#8594; AMPLIFICATION

## Caveats
- `lightcurve_url` has been converted as is from the GCN text notices but some of them do not link to lightcurves.
- MAX_MAG and AMPLIFICATION has been provided for some of the notices but not for the others. I have updated their associated JSON notices similarly.
- Additionally, there is a LEAD_TIME in the text notices which is the difference between `trigger_time` and `max_time`. Since this can be calculated from these values, I have chosen to not include this in the JSON notices.
- Some text notices have a very different formatting like `https://gcn.gsfc.nasa.gov/other/moa/201500099_moa.txt` and `https://gcn.gsfc.nasa.gov/other/moa/_moa.txt` or notices with no information like `https://gcn.gsfc.nasa.gov/other/moa/201400214_moa.txt` and so I've adopted a slightly different parsing for these.
