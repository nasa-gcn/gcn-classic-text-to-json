import email
import json
import os

import requests
from scipy.stats import norm

from ... import conversion

input = {
    "standard": {
        "id": "TRIGGER_NUMBER",
        "ra": "SRC_RA",
        "dec": "SRC_DEC",
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["EVENT_DATE", "EVENT_TIME"],
    },
    "additional": {
        "notice_type": ("NOTICE_TYPE", "string"),
        "mission_type": ("MISSION", "string"),
        "ra_dec_error": ("SRC_ERROR68", "float"),
        "net_count_rate": ("BURST_INTEN", "float"),
        "rate_duration": ("BURST_DUR", "float"),
        "instrument_phi": ("PHI", "float"),
        "instrument_theta": ("THETA", "float"),
        "latitude": ("SC_LAT", "float"),
        "longitude": ("SC_LON", "float"),
    },
}

detector_status_opts = ["on", "triggered"]

containment_prob = norm().cdf(1) - norm.cdf(-1)


def text_to_json_gecam(notice, input, record_number):
    """Function calls text_to_json and then adds additional fields with cannot be dealt with by the general function.

    Parameters
    -----------
    notice: dict
        The text notice that is being parsed.
    input: dict
        Mapping between text notice keywords and json keywords.
    record_number: int
        The current notice in the webpage being parsed.

    Returns
    -------
    dictionary
        A dictionary compliant with the associated schema for the mission."""
    output_dict = conversion.text_to_json(notice, input)

    output_dict["$schema"] = (
        "https://gcn.nasa.gov/schema/main/gcn/notices/classic/gecam/alert.schema.json"
    )
    output_dict["mission"] = "GECAM"
    output_dict["trigger_type"] = "rate"
    output_dict["messenger"] = "EM"

    output_dict["record_number"] = record_number
    if record_number == 1:
        output_dict["alert_type"] = "initial"
    else:
        output_dict["alert_type"] = "update"

    output_dict["classification"] = {notice["SRC_CLASS"]: 1}

    output_dict["containment_probability"] = containment_prob

    if output_dict["notice_type"] == "GECAM_FLT":
        output_dict["rate_snr"] = float(notice["TRIGGER_SIGNIF"].split()[0])
        output_dict["trigger_duration"] = float(notice["TRIGGER_DUR"].split()[0])

        trigger_energy_data = notice["TRIGGER_ERANGE"].split()
        output_dict["rate_energy_range"] = [
            int(trigger_energy_data[-4]),
            int(trigger_energy_data[-2]),
        ]

        trigger_dets_data = notice["TRIGGER_DETS"].split()[0]
        trigger_dets_bits = list(
            reversed([int(val) for val in bin(int(trigger_dets_data, 16))[2:]])
        )
        while len(trigger_dets_bits) != 25:
            trigger_dets_bits.append(0)
        output_dict["detector_status"] = {
            idx: detector_status_opts[trigger_dets_bits[idx - 1]]
            for idx in range(1, 26)
        }

    return output_dict


def create_all_gecam_jsons():
    """Creates a `gecam_jsons` directory and fills it with the json for all CALET triggers."""
    output_path = "./output/gecam_jsons/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    archive_link = "https://gcn.gsfc.nasa.gov/gecam_events.html"
    prefix = "https://gcn.gsfc.nasa.gov/"
    search_string = "other/.*gecam"
    links_set = conversion.parse_trigger_links(archive_link, prefix, search_string)
    links_list = list(links_set)

    for sernum in range(len(links_list)):
        link = links_list[sernum]
        data = requests.get(link).text

        record_number = 1
        start_idx = data.find("\n") + 1
        while True:
            end_idx = data.find("\n \n ", start_idx)
            notice_message = email.message_from_string(data[start_idx:end_idx].strip())
            notice_dict = dict(notice_message)

            output = text_to_json_gecam(notice_dict, input, record_number)

            with open(
                f"{output_path}GECAM_{sernum + 1}_{record_number}.json", "w"
            ) as f:
                json.dump(output, f)

            record_number += 1
            temp_start_idx = data.find("///////////", end_idx)
            start_idx = data.find("\n", temp_start_idx)
            if temp_start_idx == -1:
                break
