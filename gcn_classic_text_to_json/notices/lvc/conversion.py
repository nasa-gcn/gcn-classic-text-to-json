import email
import json
import os

import requests

from ... import conversion

input = {
    "standard": {
        "alert_datetime": "NOTICE_DATE",
        "trigger_datetime": ["TRIGGER_DATE", "TRIGGER_TIME"],
    },
    "additional": {
        "record_number": ("SEQUENCE_NUM", "int"),
        "far": ("FAR", "float"),
        "healpix_url": ("SKYMAP_FITS_URL", "string"),
        "eventpage_url": ("EVENTPAGE_URL", "string"),
    },
}

input_retract = {
    "standard": {
        "alert_datetime": "NOTICE_DATE",
        "trigger_datetime": ["TRIGGER_DATE", "TRIGGER_TIME"],
    },
    "additional": {
        "record_number": ("SEQUENCE_NUM", "int"),
    },
}


def text_to_json_lvc(notice, input):
    """Function calls text_to_json and then adds additional fields depening on whether notice is CBC or Burst.

    Parameters
    -----------
    notice: dict
        The text notice that is being parsed.
    input: dict
        Mapping between text notice keywords and JSON keywords

    Returns
    -------
    dictionary
        A dictionary compliant with the associated schema for the mission."""
    if notice["NOTICE_TYPE"].split()[1] == "Retraction":
        output_dict = conversion.text_to_json(notice, input_retract)
        output_dict["$schema"] = (
            "https://gcn.nasa.gov/schema/main/gcn/notices/classic/lvc/alert.schema.json"
        )
        output_dict["id"] = [notice["TRIGGER_NUM"]]
        output_dict["notice_type"] = "Retraction"
        return output_dict

    output_dict = conversion.text_to_json(notice, input)

    output_dict["$schema"] = (
        "https://gcn.nasa.gov/schema/main/gcn/notices/classic/lvc/alert.schema.json"
    )
    output_dict["mission"] = "LVK"
    output_dict["messenger"] = "GW"

    output_dict["id"] = [notice["TRIGGER_NUM"]]
    output_dict["notice_type"] = notice["NOTICE_TYPE"].split()[1]

    output_dict["group"] = notice["GROUP_TYPE"].split()[-1]
    output_dict["search"] = notice["SEARCH_TYPE"].split()[-1]
    output_dict["pipeline"] = notice["PIPELINE_TYPE"].split()[-1]

    if "CENTRAL_FREQ" in notice:
        output_dict["central_frequency"] = float(notice["CENTRAL_FREQ"].split()[0])
    if "DURATION" in notice:
        output_dict["duration"] = float(notice["DURATION"].split()[0])

    if "CHIRP_MASS" in notice:
        output_dict["chirp_mass"] = float(notice["CHIRP_MASS"].split()[0])
    if "ETA" in notice:
        output_dict["eta"] = float(notice["ETA"].split()[0])
    if "MAX_DIST" in notice:
        output_dict["max_dist"] = float(notice["MAX_DIST"].split()[0])

    classification = {}
    if "PROB_BNS" in notice:
        classification["BNS"] = float(notice["PROB_BNS"].split()[0])
    if "PROB_NSBH" in notice:
        classification["NSBH"] = float(notice["PROB_NSBH"].split()[0])
    if "PROB_BBH" in notice:
        classification["BBH"] = float(notice["PROB_BBH"].split()[0])
    if "PROB_TERRES" in notice:
        classification["Terrestrial"] = float(notice["PROB_TERRES"].split()[0])
        output_dict["p_astro"] = 1 - float(notice["PROB_TERRES"].split()[0])

    if classification:
        output_dict["classification"] = classification

    properties = {}
    if "PROB_NS" in notice:
        properties["HasNS"] = float(notice["PROB_NS"].split()[0])
    if "PROB_REMNANT" in notice:
        properties["HasRemnant"] = float(notice["PROB_REMNANT"].split()[0])
    if "PROB_MassGap" in notice:
        properties["HasMassGa[]"] = float(notice["PROB_MassGap"].split()[0])

    if properties:
        output_dict["properties"] = properties

    return output_dict


def create_all_lvc_jsons():
    """Creates a `lvc_json` directory and fills it with the json for all LVC triggers."""
    output_path = "./output/lvc_jsons/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    archive_link = "https://gcn.gsfc.nasa.gov/lvc_events.html"
    prefix = "https://gcn.gsfc.nasa.gov/"
    search_string = "notices_l/.*lvc"
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

            output = text_to_json_lvc(notice_dict, input)

            with open(f"{output_path}LVC_{sernum+1}.json", "w") as f:
                json.dump(output, f)

            temp_start_idx = data.find("///////////", end_idx)
            start_idx = data.find("\n", temp_start_idx)
            if temp_start_idx == -1:
                break
