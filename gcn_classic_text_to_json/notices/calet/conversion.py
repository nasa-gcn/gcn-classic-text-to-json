import email
import json
import os

import requests

from ... import conversion

input = {
    "standard": {
        "id": "TRIGGER_NUM",
        "ra": "POINT_RA",
        "dec": "POINT_DEC",
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["TRIGGER_DATE", "TRIGGER_TIME"],
    },
    "additional": {
        "url": ("LC_URL", "string"),
        "rate_snr": ("SIGNIFICANCE", "float"),
        "foreground_duration": ("FOREGND_DUR", "float"),
        "background_duration": ("BACKGND_DUR1", "float"),
    },
}


def text_to_json_calet(notice, record_number, input):
    """Function calls text_to_json and then adds additional fields with cannot be dealt with by the general function.

    Parameters
    -----------
    notice: dict
        The text notice that is being parsed.
    record_number: int
        The current notice in the webpage being parsed.
    notice_start_idx: int
        The index at which the current text notice begins.

    Returns
    -------
    dictionary
        A dictionary compliant with the associated schema for the mission."""
    output_dict = conversion.text_to_json(notice, input)

    output_dict["record_number"] = record_number
    if record_number == 1:
        output_dict["alert_type"] = "initial"
    else:
        output_dict["alert_type"] = "update"

    output_dict["mission"] = "CALET"
    output_dict["instrument"] = "GBM"
    output_dict["trigger_type"] = "rate"

    lon_lat_data = notice["SC_LON_LAT"].split(",")
    lon, lat = lon_lat_data[0], lon_lat_data[1][:5]
    output_dict["longitude"] = float(lon)
    output_dict["latitude"] = float(lat)

    energy_data = notice["ENERGY_BAND"]
    energy_low, energy_high = energy_data.split()[0].split("-")
    output_dict["rate_energy_range"] = [int(energy_low), int(energy_high)]

    detector_data = notice["TRIGGER_DET"].split()
    detector_opts = ["on", "triggered"]
    output_dict["detector_status"] = {
        detector_data[-3][1:]: detector_opts[int(detector_data[0])],
        detector_data[-2]: detector_opts[int(detector_data[1])],
        detector_data[-1][:-1]: detector_opts[int(detector_data[2])],
    }

    return output_dict


def create_all_calet_jsons():
    """Creates a `calet_json` directory and fills it with the json for all CALET triggers."""
    output_path = "./calet_jsons/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    archive_link = "https://gcn.gsfc.nasa.gov/calet_triggers.html"
    prefix = "https://gcn.gsfc.nasa.gov/"
    links_set = conversion.parse_trigger_links(archive_link, prefix)
    links_list = list(links_set)

    for sernum in range(1, len(links_list) + 1):
        link = links_list[sernum]
        data = requests.get(link).text

        record_number = 1
        start_idx = data.find("\n") + 1
        while True:
            end_idx = data.find("\n \n ", start_idx)
            notice_message = email.message_from_string(data[start_idx:end_idx].strip())
            comment = "".join(notice_message.get_all("COMMENTS"))
            notice_dict = dict(notice_message)
            notice_dict["COMMENTS"] = comment

            output = text_to_json_calet(notice_dict, record_number, input)

            with open(f"{output_path}CALET_GBM_{sernum}.json", "w") as f:
                json.dump(output, f)

            record_number += 1
            temp_start_idx = data.find("///////////", end_idx)
            start_idx = data.find("\n", temp_start_idx)
            if temp_start_idx == -1:
                break
