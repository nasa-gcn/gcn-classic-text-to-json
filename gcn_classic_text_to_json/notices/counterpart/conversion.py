import email
import json
import os

import requests

from ... import conversion

input_grb = {
    "standard": {
        "id": "TRIGGER_NUM",
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["OBS_DATE", "OBS_TIME"],
        "ra": "CNTRPART_RA",
        "dec": "CNTRPART_DEC",
    },
    "additional": {
        "ra_dec_error": ("CNTRPART_ERROR", "float"),
        "submitter_name": ("SUBMITTER", "string"),
        "energy_flux": ("INTENSITY", "float"),
        "duration": ("OBS_DUR", "float"),
    },
}

input_lvc = {
    "standard": {
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["OBS_DATE", "OBS_TIME"],
        "ra": "CNTRPART_RA",
        "dec": "CNTRPART_DEC",
    },
    "additional": {
        "ref_ID": ("EVENT_TRIG_NUM", "string"),
        "ra_dec_error": ("CNTRPART_ERROR", "float"),
        "submitter_name": ("SUBMITTER", "string"),
        "energy_flux": ("INTENSITY", "float"),
        "duration": ("OBS_DUR", "float"),
        "rank": ("RANK", "int"),
    },
}


def text_to_json_counterpart(notice, input, record_number, notice_type):
    """Function calls text_to_json and then adds additional fields for each notice type.

    Parameters
    -----------
    notice: dict
        The text notice that is being parsed.
    input: dict
        The mapping between text notices keywords and GCN schema keywords.
    record_number: int
        The current notice in the webpage being parsed.
    notice_type: string
        Whether it is a GRB or LVC counterpart.

    Returns
    -------
    dictionary
        A dictionary compliant with the associated schema for the mission."""
    output_dict = conversion.text_to_json(notice, input)

    output_dict["$schema"] = (
        "https://gcn.nasa.gov/schema/main/gcn/notices/classic/counterpart/alert.schema.json"
    )
    output_dict["notice_type"] = f"{notice_type}_Counterpart"
    output_dict["record_number"] = record_number
    if record_number == 1:
        output_dict["alert_type"] = "initial"
    else:
        output_dict["alert_type"] = "update"

    telescope_data = notice["TELESCOPE"].split()[0].split("-")
    output_dict["mission"] = telescope_data[0]
    output_dict["instrument"] = telescope_data[1]

    output_dict["ra_dec_error"] /= 3600
    output_dict["energy_flux_error"] = float(notice["INTENSITY"].split()[-2])
    energy_data = notice["ENERGY"].split()[0].split("-")
    output_dict["flux_energy_range"] = [float(energy_data[0]), float(energy_data[1])]

    return output_dict


def create_all_counterpart_jsons():
    """Creates a `counterpart_jsons` directory and fills it with the json for all COUNTERPART triggers."""
    output_path = "./output/counterpart_jsons/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    archive_link = "https://gcn.gsfc.nasa.gov/counterpart_tbl.html"
    prefix = "https://gcn.gsfc.nasa.gov/"
    search_string = "other/.*counterpart"
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

            notice_type = ((notice_dict["TITLE"].split()[0]).split("/")[-1]).split("_")[
                0
            ]
            if notice_type == "LVC":
                output = text_to_json_counterpart(
                    notice_dict, input_lvc, record_number, "LVC"
                )
            elif notice_type == "GRB":
                output = text_to_json_counterpart(
                    notice_dict, input_grb, record_number, "GRB"
                )

            with open(
                f"{output_path}COUNTERPART_{sernum+1}_{record_number}.json", "w"
            ) as f:
                json.dump(output, f)

            record_number += 1
            temp_start_idx = data.find("///////////", end_idx)
            start_idx = data.find("\n", temp_start_idx)
            if temp_start_idx == -1:
                break
