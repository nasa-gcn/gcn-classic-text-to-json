import email
import json
import os

import requests

from ... import conversion

input = {
    "standard": {
        "id": "TRIGGER_NUM",
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["GRB_DATE", "GRB_TIME"],
        "ra": "GRB_RA",
        "dec": "GRB_DEC",
    },
    "additional": {
        "ra_dec_error": ("GRB_ERROR", "float"),
        "n_events": ("GRB_FLUENCE", "int"),
        "bkg_events": ("BKG", "float"),
        "stat_signif": ("GRB_SIGNIF", "float"),
        "annual_rate": ("ANN_RATE", "float"),
        "duration": ("GRB_DUR", "float"),
        "zenith": ("GRB_ZEN", "float"),
    },
}


def text_to_json_milagro(notice, record_number, input):
    """Function calls text_to_json and then adds additional fields with cannot be dealt with by the general function.

    Parameters
    -----------
    notice: dict
        The text notice that is being parsed.
    input: dict
        The mapping between text notices keywords and GCN schema keywords.
    record_number: int
        The current notice in the webpage being parsed.

    Returns
    -------
    dictionary
        A dictionary compliant with the associated schema for the mission."""
    output_dict = conversion.text_to_json(notice, input)

    output_dict["mission"] = "MILAGRO"
    output_dict["$schema"] = (
        "https://gcn.nasa.gov/schema/main/gcn/notices/classic/milagro/alert.schema.json"
    )
    output_dict["record_number"] = record_number

    if record_number == 1:
        output_dict["alert_type"] = "initial"
    else:
        output_dict["alert_type"] = "update"

    output_dict["systematic_included"] = True

    return output_dict


def create_all_milagro_jsons():
    """Creates a `milagro_jsons` directory and fills it with the json for all MILAGRO triggers."""
    output_path = "./output/milagro_jsons/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    archive_link = "https://gcn.gsfc.nasa.gov/milagro_trans.html"
    prefix = "https://gcn.gsfc.nasa.gov/"
    search_string = "other/.*milagro"
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
            comment = "\n".join(notice_message.get_all("COMMENTS"))
            notice_dict = dict(notice_message)
            notice_dict["COMMENTS"] = comment

            output = text_to_json_milagro(notice_dict, record_number, input)

            with open(
                f"{output_path}MILAGRO_{sernum + 1}_{record_number}.json", "w"
            ) as f:
                json.dump(output, f)

            record_number += 1
            temp_start_idx = data.find("///////////", end_idx)
            start_idx = data.find("\n", temp_start_idx)
            if temp_start_idx == -1:
                break
