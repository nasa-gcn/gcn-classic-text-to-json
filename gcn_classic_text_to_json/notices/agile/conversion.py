import email
import json
import os

import requests

from ... import conversion

input_ground = {
    "standard": {
        "id": "TRIGGER_NUM",
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["GRB_DATE", "GRB_TIME"],
        "ra": "GRB_RA",
        "dec": "GRB_DEC",
    },
    "additional": {
        "ra_dec_error": ("GRB_ERROR", "float"),
        "n_events_x": ("GRB_INTEN", "float"),
        "snr_x": ("GRB_SIGNIF", "float"),
    },
}

input_mcal = {
    "standard": {
        "id": "TRIGGER_NUM",
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["GRB_DATE", "GRB_TIME"],
    },
    "additional": {
        "n_events": ("GRB_TOTAL_COUNTS", "int"),
        "events_snr": ("GRB_SIGNIF", "float"),
        "peak_events": ("PEAK_COUNTS", "int"),
        "peak_snr": ("PEAK_SIGNIF", "float"),
        "bkg_events": ("BACKGROUND", "int"),
        "triggering_interval": ("DATA_TIME_SCALE", "float"),
        "duration": ("INTEG_TIME", "float"),
        "lightcurve_url": ("LIGHT_CURVE", "string"),
    },
}

triggering_intervals = ["sub-ms", "1ms", "16ms", "64ms", "256ms", "1024ms", "8192ms"]


def text_to_json_agile(notice, input, notice_type):
    """Function calls text_to_json and then adds additional fields depending on the notice type.

    Parameters
    -----------
    notice: dict
        The text notice that is being parsed.
    input: dict
        The mapping between text notices keywords and GCN schema keywords.
    notice_type: string
        If the AGILE notice is a Ground or MCAL notice.

    Returns
    -------
    dictionary
        A dictionary compliant with the associated schema for the mission."""
    output_dict = conversion.text_to_json(notice, input)

    output_dict["$schema"] = (
        "https://gcn.nasa.gov/schema/main/gcn/notices/classic/agile/alert.schema.json"
    )
    output_dict["mission"] = "AGILE"
    output_dict["notice_type"] = notice_type

    if notice_type == "Ground":
        output_dict["systematic_included"] = True
        output_dict["n_events_y"] = float(notice["GRB_INTEN"].split()[1])
        output_dict["snr_y"] = float(notice["GRB_SIGNIF"].split()[1])
        output_dict["ra_dec_error"] /= 60
    elif notice_type == "MCAL":
        lon_lat_data = notice["SC_LON_LAT"].split(",")
        output_dict["longitude"] = float(lon_lat_data[0])
        output_dict["latitude"] = float(lon_lat_data[1].split()[0])

        erange_data = notice["ENERGY_RANGE"].split()
        output_dict["events_energy_range"] = [int(erange_data[0]), int(erange_data[2])]

        triggering_data = notice["TRIGGER_LOGIC"].split(",")
        trigger_logic = {}
        for trigger_interval in triggering_intervals:
            if trigger_interval in triggering_data:
                trigger_logic[trigger_interval] = True
            else:
                trigger_logic[trigger_interval] = False
        output_dict["trigger_logic"] = trigger_logic

    return output_dict


def create_agile_jsons_one_webpage(link, notice_type, output_path, sernum):
    """Parses through a single webpage and creates JSONs for all the triggers in that webpage

    Parameters
    ----------
    link: string
        The web address to the table with all the triggers for `notice_type`
    notice_type: string
        The particular type of notices stored in `link`
    output_path: string
        The path to which to save the JSONs
    sernum: int
        A random iterating serial number with no relation to the data to stored the JSONs

    Returns
    -------
    sernum: int
        Increments sernum and returns it for the next function call"""
    prefix = "https://gcn.gsfc.nasa.gov/"
    search_string = "other/.*agile"
    links_set = conversion.parse_trigger_links(link, prefix, search_string)
    links_list = list(links_set)

    for link in links_list:
        data = requests.get(link).text

        start_idx = data.find("\n") + 1
        while True:
            end_idx = data.find("\n \n ", start_idx)
            notice_message = email.message_from_string(data[start_idx:end_idx].strip())
            comment = "\n".join(notice_message.get_all("COMMENTS"))
            notice_dict = dict(notice_message)
            notice_dict["COMMENTS"] = comment

            if notice_type == "Ground":
                output = text_to_json_agile(notice_dict, input_ground, "Ground")
            elif notice_type == "MCAL":
                output = text_to_json_agile(notice_dict, input_mcal, "MCAL")

            with open(f"{output_path}AGILE_{sernum}.json", "w") as f:
                json.dump(output, f)

            sernum += 1
            temp_start_idx = data.find("///////////", end_idx)
            start_idx = data.find("\n", temp_start_idx)
            if temp_start_idx == -1:
                break

    return sernum


def create_all_agile_jsons():
    """Creates a `agile_jsons` directory inside an `output` directory and fills it with the json for all AGILE triggers."""
    output_path = "./output/agile_jsons/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    sernum = 1
    sernum = create_agile_jsons_one_webpage(
        "https://gcn.gsfc.nasa.gov/agile_grbs.html", "Ground", output_path, sernum
    )
    create_agile_jsons_one_webpage(
        "https://gcn.gsfc.nasa.gov/agile_mcal.html", "MCAL", output_path, sernum
    )
