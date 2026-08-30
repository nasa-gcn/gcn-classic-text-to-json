import email
import json
import os

import requests

from ... import conversion

input_pca = {
    "standard": {
        "id": "TRIGGER_NUM",
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["GRB_DATE", "GRB_TIME"],
    }
}

input_pca_burst_alert = {
    "standard": {
        "id": "TRIGGER_NUM",
        "ra": "GRB_LOCBURST_RA",
        "dec": "GRB_LOCBURST_DEC",
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["GRB_DATE", "GRB_TIME"],
    }
}

input_pca_burst_position = {
    "standard": {
        "id": "TRIGGER_NUM",
        "ra": "GRB_RXTE_RA",
        "dec": "GRB_RXTE_RA",
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["GRB_DATE", "GRB_TIME"],
    },
    "additional": {
        "ra_dec_error": ("GRB_RXTE_ERROR", "float"),
        "flux_energy_mcrab": ("GRB_RXTE_INTEN", "float"),
    },
}

input_asm = {
    "standard": {
        "ra": "GRB_RXTE_RA",
        "dec": "GRB_RXTE_DEC",
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["GRB_DATE", "GRB_TIME"],
    },
    "additional": {
        "position_type": ("POSITION_TYPE", "string"),
        "ra_dec_error": ("GRB_RXTE_ERROR", "float"),
        "flux_energy_mcrab": ("GRB_RXTE_INTEN", "float"),
    },
}


def text_to_json_rxte(notice, input, record_number, instrument):
    """Function calls text_to_json and then adds additional fields depending on the type of instrument.

    Parameters
    -----------
    notice: dict
        The text notice that is being parsed.
    input: dict
        The mapping between text notices keywords and GCN schema keywords.
    record_number: int
        The current notice in the webpage being parsed.
    instrument:
        The RXTE notice type. Either PCS or ASM.


    Returns
    -------
    dictionary
        A dictionary compliant with the associated schema for the mission.
    Notes
    -----
    It seems that there are some ASM notices labelled PCA (It says for testing purposes).
    I've changed these manually."""
    if "RXTE-PCA was NOT able to localize this GRB." in notice["COMMENTS"]:
        return conversion.text_to_json(notice, input_pca)
    output_dict = conversion.text_to_json(notice, input)

    output_dict["$schema"] = (
        "https://gcn.nasa.gov/schema/main/gcn/notices/classic/rxte/alert.schema.json"
    )
    output_dict["mission"] = "RXTE"
    output_dict["instrument"] = instrument
    output_dict["messenger"] = "EM"

    output_dict["record_number"] = record_number
    if record_number == 1:
        output_dict["alert_type"] = "initial"
    else:
        output_dict["alert_type"] = "update"

    if "ra_dec_error" in output_dict:
        output_dict["systematic_included"] = True

    return output_dict


def create_all_rxte_jsons():
    """Creates a `rxte_jsons` directory and fills it with the json for all RXTE triggers."""
    output_path = "./output/rxte_jsons/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    archive_link = "https://gcn.gsfc.nasa.gov/rxte_grbs.html"
    prefix = "https://gcn.gsfc.nasa.gov/"
    search_string = "other/.*rxte"
    links_set = conversion.parse_trigger_links(archive_link, prefix, search_string)
    links_list = list(links_set)

    for sernum in range(len(links_list)):
        link = links_list[sernum]
        data = requests.get(link).text

        record_number = 1
        start_idx = data.find("TITLE")
        while True:
            end_idx = data.find("\n \n ", start_idx)
            if end_idx == -1:
                break

            notice = data[start_idx:end_idx]
            if "///////////" in notice:
                notice = notice.replace("/", "")

            notice_message = email.message_from_string(notice.strip())
            comment = "\n".join(notice_message.get_all("COMMENTS"))
            notice_dict = dict(notice_message)
            notice_dict["COMMENTS"] = comment

            instrument = notice_dict["NOTICE_TYPE"].split()[0][-3:]

            if instrument == "PCA":
                if "POSITION_TYPE" in notice_dict:
                    output = text_to_json_rxte(
                        notice_dict, input_asm, record_number, "ASM"
                    )
                elif "BURST ALERT" in notice_dict["TITLE"]:
                    output = text_to_json_rxte(
                        notice_dict, input_pca_burst_alert, record_number, instrument
                    )
                else:
                    output = text_to_json_rxte(
                        notice_dict, input_pca_burst_position, record_number, instrument
                    )

            elif instrument == "ASM":
                output = text_to_json_rxte(
                    notice_dict, input_asm, record_number, instrument
                )

            with open(f"{output_path}RXTE_{sernum+1}_{record_number}.json", "w") as f:
                json.dump(output, f)

            record_number += 1
            start_idx = data.find("TITLE", end_idx)
            if start_idx == -1:
                break
