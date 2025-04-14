# KONUS Text Conversion

Parses through the table in multiple webpages associated with KONUS triggers and creates `KONUS_{sernum}.json` directory in a `konus_jsons` inside an `output` directory for each trigger where sernum in an iterative number with no relation to the triggers.

### Uses the following fields from the core schema for text notice fields
- `id` &#8594; Trig#
- `trigger_time` &#8594; Trig_Date, Trig_Time
- `classification` &#8594; Event

### Defines the following new fields for the text notice fields
- `lightcurve_image_url` &#8594; GIF
- `lightcurve_textfile_url` &#8594; Text
- `detector_number` &#8594; Det

## Caveats
- In the tables that I have been parsing, some of the fields are just empty. I've elected to skip these and not add the fields in the JSONs as that makes validation simpler.
