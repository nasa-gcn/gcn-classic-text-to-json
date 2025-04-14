# NEAR Text Conversion

Parses through the table in multiple webpages associated with NEAR triggers and creates `NEAR_{sernum}.json` directory in a `near_jsons` inside an `output` directory for each trigger where sernum in an iterative number with no relation to the triggers.

### Uses the following fields from the core schema for text notice fields
- `trigger_time` &#8594; None given in the webpage

### Defines the following new fields for the text notice fields
- `lightcurve_image_url` &#8594; None given in the webpage
- `lightcurve_textfile_url` &#8594; None given in the webpage
