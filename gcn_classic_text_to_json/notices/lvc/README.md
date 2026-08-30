# LVC Text Conversion

Parses through all the webpages with LVC text notices and creates a JSON with GCN schema keywords. Creates a `lvc_jsons` directory inside an `output` directory and saves jsons as `LVC_{serial_number}.json` where serial_number is a random iterating number with no association to the notices.

### Uses the following fields from the core schema for text notice fields
- `id` &#8594; TRIGGER_NUM
- `alert_datetime` &#8594; NOTICE_DATE
- `trigger_time` &#8594; TRIGGER_DATE, TRIGGER_TIME
- `record_number` &#8594; SEQUENCE_NUM
- `healpix_url` &#8594; SKYMAP_FITS_URL
- `far` &#8594; FAR

### Defines the following new fields for the text notice fields
- `eventpage_url` &#8594; EVENTPAGE_URL,
- `group` &#8594; GROUP_TYPE
- `search` &#8594; SEARCH_TYPE
- `pipeline` &#8594; PIPELINE_TYPE
- `central_frequency` &#8594; CENTRAL_FREQ
- `duration` &#8594; DURATION
- `chirp_mass` &#8594; CHIRP_MASS
- `eta` &#8594; ETA
- `max_dist` &#8594; MAX_DIST
- `classification` &#8594; PROB_BNS, PROB_NSBH, PROB_BBH, PROB_TERRES
- `properties` &#8594; PROB_NS, PROB_REMNANT, PROB_MassGap
