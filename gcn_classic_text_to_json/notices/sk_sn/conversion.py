import email
import json
import os

import requests

from ... import conversion

input = {
    "standard": {
        "ra": "SRC_RA",
        "dec": "SRC_DEC",
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["DISCOVERY_DATE", "DISCOVERY_TIME"],
    },
    "additional": {
        "ra_dec_error": ("SRC_ERROR90", "float"),
        "ra_dec_error_68": ("SRC_ERROR68", "float"),
        "ra_dec_error_95": ("SRC_ERROR95", "float"),
        "n_events": ("N_EVENTS", "int"),
        "collection_duration": ("DURATION", "float"),
        "energy_limit": ("ENERGY_LIMIT", "float"),
    },
}


def text_to_json_sk_sn(notice, input):
    """Function calls text_to_json and then adds additional fields with cannot be dealt with by the general function.
    Additionally, convert some values from the general function into units required by the Unified Schema.

    Parameters
    -----------
    notice: dict
        The text notice that is being parsed.
    input: dict
        The mapping between the text keywords and the GCN schema fields.

    Returns
    -------
    dictionary
        A dictionary compliant with the associated schema for the mission."""
    output_dict = conversion.text_to_json(notice, input)

    output_dict["mission"] = "Super-Kamiokande"
    output_dict["messenger"] = "Neutrino"

    if notice["NOTICE_TYPE"].split()[1] == "TEST":
        output_dict["alert_tense"] = "test"

    output_dict["id"] = [int(notice["TRIGGER_NUMBER"].split()[1])]

    output_dict["energy_limit"] *= 1e3

    distance_data = notice["DISTANCE"].split()
    output_dict["distance_range"] = [
        float(distance_data[0]) * 1e-3,
        float(distance_data[2]) * 1e-3,
    ]

    return output_dict


def create_all_sk_sn_jsons():
    """Creates a `sk_sn_json` directory and fills it with the json for all SK_SN triggers."""
    output_path = "./output/sk_sn_jsons/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    archive_link = "https://gcn.gsfc.nasa.gov/sk_sn_events.html"
    prefix = "https://gcn.gsfc.nasa.gov/"
    links_set = conversion.parse_trigger_links(archive_link, prefix)
    links_list = list(links_set)

    for sernum in range(len(links_list)):
        link = links_list[sernum]
        data = requests.get(link).text

        start_idx = data.find("\n") + 1
        while True:
            end_idx = data.find("\n \n ", start_idx)
            notice_message = email.message_from_string(data[start_idx:end_idx].strip())
            comment = "".join(notice_message.get_all("COMMENTS"))
            notice_dict = dict(notice_message)
            notice_dict["COMMENTS"] = comment

            output = text_to_json_sk_sn(notice_dict, input)

            with open(f"{output_path}SK_SN_{sernum+1}.json", "w") as f:
                json.dump(output, f)

            temp_start_idx = data.find("///////////", end_idx)
            start_idx = data.find("\n", temp_start_idx)
            if temp_start_idx == -1:
                break
