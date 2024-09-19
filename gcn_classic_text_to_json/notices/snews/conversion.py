import email
import json
import os

import requests

from ... import conversion

input = {
    "standard": {
        "id": "TRIGGER_NUM",
        "ra": "EVENT_RA",
        "dec": "EVENT_DEC",
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["EVENT_DATE", "EVENT_TIME"],
    },
    "additional": {
        "ra_dec_error": ("EVENT_ERROR", "float"),
        "n_events": ("EVENT_FLUENCE", "int"),
        "duration": ("EVENT_DUR", "float"),
    },
}

input_131 = {
    "standard": {
        "id": "TRIGGER_NUM",
        "ra": "EVT_RA",
        "dec": "EVT_DEC",
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["EVT_DATE", "EVT_TIME"],
    },
    "additional": {
        "ra_dec_error": ("EVT_ERROR", "float"),
        "n_events": ("EVT_FLUENCE", "int"),
        "duration": ("EVT_DUR", "float"),
    },
}

detector_mapping = {
    "Detector_A": "Super-K",
    "Detector_B": "LVD",
    "Detector_C": "IceCube",
    "Detector_D": "KamLAND",
    "Detector_E": "Borexino",
    "Detector_F": "Daya Bay",
    "Detector_G": "HALO",
}


def text_to_json_snews(notice, input):
    """Function calls text_to_json and then adds additional fields with cannot be dealt with by the general function.

    Parameters
    -----------
    notice: dict
        The text notice that is being parsed.
    input: dict
        The notice keyword to GCN schema mapping.

    Returns
    -------
    dictionary
        A dictionary compliant with the associated schema for the mission."""
    output_dict = conversion.text_to_json(notice, input)

    output_dict["$schema"] = (
        "https://gcn.nasa.gov/schema/main/gcn/notices/classic/snews/alert.schema.json"
    )

    if notice["NOTICE_TYPE"].split()[0] == "TEST":
        output_dict["alert_tense"] = "test"

    output_dict["systematic_included"] = True

    output_dict["containment_probability"] = float(
        notice["EVENT_ERROR"].split()[-2][:-1]
    )

    detector_quality = {}
    detector_quality_data = notice["EXPT"].split(",")

    detector_flags = {
        data.split()[0]: data.split()[1]
        for data in detector_quality_data
        if data != " "
    }

    for detector_text, detector_json in detector_mapping.items():
        if detector_text in detector_flags:
            detector_quality[detector_json] = detector_flags[detector_text].lower()
        else:
            detector_quality[detector_json] = "did not contribute"

    output_dict["detector_quality"] = detector_quality

    return output_dict


def text_to_json_snews_131(notice, input):
    """This function is for just one notice with trigger number 131 seems to use a different format from the rest.

    Parameters
    -----------
    notice: dict
        The text notice that is being parsed.
    input: dict
        The notice keyword to GCN schema mapping.

    Returns
    -------
    dictionary
        A dictionary compliant with the associated schema for the mission."""
    output_dict = conversion.text_to_json(notice, input)

    output_dict["alert_tense"] = "test"

    output_dict["systematic_included"] = True

    detector_quality = {}
    detector_quality_data = notice["EXPT"].split(",")

    for data in detector_quality_data:
        if data == " ":
            continue
        detector, flag = data.split()
        detector_quality[detector] = flag.lower()

    output_dict["detector_quality"] = detector_quality

    return output_dict


def create_all_snews_jsons():
    """Creates a `snews_json` directory and fills it with the json for all CALET triggers."""
    output_path = "./output/snews_jsons/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    archive_link = "https://gcn.gsfc.nasa.gov/snews_trans.html"
    prefix = "https://gcn.gsfc.nasa.gov/"
    search_string = "other/.*snews"
    links_set = conversion.parse_trigger_links(archive_link, prefix, search_string)
    links_list = list(links_set)

    for sernum in range(len(links_list)):
        link = links_list[sernum]
        data = requests.get(link).text

        start_idx = data.find("\n") + 1
        while True:
            end_idx = data.find("\n \n ", start_idx)
            notice_message = email.message_from_string(data[start_idx:end_idx].strip())
            comment = "\n".join(notice_message.get_all("COMMENTS"))
            notice_dict = dict(notice_message)
            notice_dict["COMMENTS"] = comment

            if link != "https://gcn.gsfc.nasa.gov/other/131.snews":
                output = text_to_json_snews(notice_dict, input)
            else:
                output = text_to_json_snews_131(notice_dict, input_131)

            with open(f"{output_path}SNEWS_{sernum+1}.json", "w") as f:
                json.dump(output, f)

            temp_start_idx = data.find("///////////", end_idx)
            start_idx = data.find("\n", temp_start_idx)
            if temp_start_idx == -1:
                break
