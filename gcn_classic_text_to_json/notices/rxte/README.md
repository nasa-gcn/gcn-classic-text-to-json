# RXTE Text Conversion

Parses through all webpages with RXTE text notices and creates a JSON with GCN schema keywords. Creates a `rxte_jsons` directory inside an `output` directory and saves jsons as `RXTE_{serial_number}_{record_number}.json` where serial_number is a random iterating number with no association to the notices and record_number is the current notice in the webpage.

### Uses the following fields from the core schema for text notice fields
- `id` &#8594; TRIGGER_NUM (PCA Notices Only)
- `ra` &#8594; GRB_LOCBURST_RA (PCA) / GRB_RXTE_RA (ASM)
- `dec` &#8594; GRB_LOCBURST_DEC (PCA) / GRB_RXTE_DEC (ASM)
- `alert_datetime` &#8594; NOTICE_DATE
- `trigger_time` &#8594; GRB_DATE, GRB_TIME
- `ra_dec_error` &#8594; GRB_RXTE_INTEN

### Defines the following new fields for the text notice fields (For ASM Notices Only)
- `position_type` &#8594; POSITION_TYPE
- `flux_energy_crab` &#8594; GRB_RXTE_INTEN

## Caveats
- Some Notices are marked PCA for testing but follow the ASM format. I've manually converted these into ASM Notices.
- There are additional fields associated with the POSITION_TYPE which details the properties of the error box. I've chosen to not include these fields.
