# MAXI Text Conversion

Parses through all webpages with MAXI text notices and creates a JSON with GCN schema keywords. Creates a `maxi_jsons` directory inside an `output` directory and saves jsons as `MAXI_{serial_number}_{record_number}.json` where serial_number is a random iterating number with no association to the notices and record_number is the current notice in the webpage.

### Uses the following fields from the core schema for text notice fields
- `id` &#8594; SRC_ID_NUM/EVENT_ID_NUM
- `ra` &#8594; SRC_RA/EVENT_RA
- `dec` &#8594; SRC_DEC/EVENT_DEC
- `ra_dec_error`  &#8594; SRC_ERROR/EVENT_ERROR
- `alert_datetime` &#8594; NOTICE_DATE
- `trigger_time` &#8594; SRC_DATE/EVENT_DATE, SRC_TIME/EVENT_TIME
- `latitude`, `longitude` &#8594; ISS_LON_LAT
- `energy_flux` &#8594; SRC_FLUX/EVENT_FLUX
- `flux_energy_range` &#8594; SRC_EBAND/EVENT_EBAND
- `classification`  &#8594; SRC_CLASS

### Defines the following new fields for the text notice fields
- `notice_type` &#8594; NOTICE_TYPE
- `source_name` &#8594; SRC_NAME
- `duration` &#8594; SRC_TSCALE/EVENT_TSCALE
- `rate_snr` &#8594; SIGNIFICANCE
- `source_flux_low_band`, `background_flux_low_band`, `source_flux_medium_band`, `background_flux_medium_band`, `source_flux_high_band`, `background_flux_high_band` &#8594; BAND_FLUX

## Caveats
- ISS_LAT_LON is just defined as 0.00, 0.00 for some notices. In this case, I have not added these values to the notices.
- Similarly, sometimes EVENT_FLUX has errors but these are always 0 so again I have not added these.
- There are a series of links that have empty notices. I have chosen to skip these.
