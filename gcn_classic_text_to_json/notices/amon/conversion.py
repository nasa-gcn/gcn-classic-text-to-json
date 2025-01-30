import email
import json
import os

import requests

from ... import conversion

input_gold_bronze = {
    "standard": {
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["DISCOVERY_DATE", "DISCOVERY_TIME"],
        "ra": "SRC_RA",
        "dec": "SRC_DEC",
    },
    "additional": {
        "ra_dec_error": ("SRC_ERROR", "float"),
        "ra_dec_error_50": ("SRC_ERROR50", "float"),
        "record_number": ("REVISION", "int"),
        "energy": ("ENERGY", "float"),
        "signalness": ("SIGNALNESS", "float"),
        "far": ("FAR", "float"),
    },
}

input_burst = {
    "standard": {
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["DISCOVERY_DATE", "DISCOVERY_TIME"],
        "ra": "SRC_RA",
        "dec": "SRC_DEC",
    },
    "additional": {
        "ra_dec_error": ("SRC_ERROR", "float"),
        "record_number": ("REVISION", "int"),
        "far": ("FAR", "float"),
        "delta_time": ("delta_T", "float"),
        "p_value": ("Pvalue", "float"),
    },
}

input_coincidence = {
    "standard": {
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["DISCOVERY_DATE", "DISCOVERY_TIME"],
        "ra": "SRC_RA",
        "dec": "SRC_DEC",
    },
    "additional": {
        "ra_dec_error": ("SRC_ERROR", "float"),
        "ra_dec_error_50": ("SRC_ERROR50", "float"),
        "record_number": ("REVISION", "int"),
        "delta_time": ("delta_T", "float"),
        "far": ("FAR", "float"),
        "event_date": ("EVENT_DATE", "string"),
    },
}

input_cascade = {
    "standard": {
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["DISCOVERY_DATE", "DISCOVERY_TIME"],
        "ra": "SRC_RA",
        "dec": "SRC_DEC",
    },
    "additional": {
        "ra_dec_error": ("SRC_ERROR", "float"),
        "ra_dec_error_50": ("SRC_ERROR50", "float"),
        "record_number": ("REVISION", "int"),
        "energy": ("ENERGY", "float"),
        "signalness": ("SIGNALNESS", "float"),
        "far": ("FAR", "float"),
    },
}

input_ehe = {
    "standard": {
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["DISCOVERY_DATE", "DISCOVERY_TIME"],
        "ra": "SRC_RA",
        "dec": "SRC_DEC",
    },
    "additional": {
        "ra_dec_error": ("SRC_ERROR", "float"),
        "record_number": ("REVISION", "int"),
        "energy": ("ENERGY", "float"),
        "signalness": ("SIGNALNESS", "float"),
        "n_events": ("N_EVENTS", "int"),
        "delta_time": ("DELTA_T", "float"),
        "sigma_time": ("SIGMA_T", "float"),
        "charge": ("CHARGE", "float"),
    },
}

input_hese = {
    "standard": {
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["DISCOVERY_DATE", "DISCOVERY_TIME"],
        "ra": "SRC_RA",
        "dec": "SRC_DEC",
    },
    "additional": {
        "ra_dec_error": ("SRC_ERROR", "float"),
        "ra_dec_error_50": ("SRC_ERROR50", "float"),
        "record_number": ("REVISION", "int"),
        "signalness": ("SIGNAL_TRACKNESS", "float"),
        "n_events": ("N_EVENTS", "int"),
        "delta_time": ("DELTA_T", "float"),
        "sigma_time": ("SIGMA_T", "float"),
        "charge": ("CHARGE", "float"),
        "p_value": ("PVALUE", "float"),
        "false_positive": ("FALSE_POS", "float"),
    },
}


def text_to_json_amon(notice, input, notice_type):
    """Function calls text_to_json and then adds additional fields with cannot be dealt with by the general function.

    Parameters
    -----------
    notice: dict
        The text notice that is being parsed.
    input: dict
        The mapping between text notices keywords and GCN schema keywords.
    notice_type: string
        The type of AMON notice.

    Returns
    -------
    dictionary
        A dictionary compliant with the associated schema for the mission."""
    output_dict = conversion.text_to_json(notice, input)

    output_dict["$schema"] = (
        "https://gcn.nasa.gov/schema/main/gcn/notices/classic/amon/alert.schema.json"
    )
    output_dict["mission"] = "AMON"
    output_dict["notice_type"] = notice_type

    output_dict["record_number"] += 1

    if notice_type != "HESE" and notice_type != "EHE":
        output_dict["far"] /= 365 * 24 * 60 * 60

    output_dict["id"] = [
        f"{notice["RUN_NUM"].split()[0]}_{notice["EVENT_NUM"].split()[0]}"
    ]

    if notice_type != "Cascade":
        output_dict["ra_dec_error"] /= 60

    if notice_type == "Astrotrack Gold" or notice_type == "Astrotrack Bronze":
        output_dict["energy"] *= 1e9
        output_dict["ra_dec_error_50"] /= 60
    elif notice_type == "Neutrino-EM Coincidence":
        output_dict["coincidence_with"] = [notice["COINC_PAIR"].split()[1]]
        output_dict["ra_dec_error_50"] /= 60
    elif notice_type == "Cascade" or notice_type == "EHE" or notice_type == "HESE":
        output_dict["systematic_included"] = True
        if notice_type == "Cascade":
            output_dict["event_name"] = [notice["EVENT_NAME"].split()[0]]
        if notice_type == "EHE":
            output_dict["containment_probability"] = 0.5
        if notice_type == "HESE":
            output_dict["ra_dec_error_50"] /= 60

    return output_dict


def create_amon_jsons_one_webpage(link, search_string, output_path, sernum):
    """Parse through all the triggers in `link` and convert them to JSONs

    Parameters
    ----------
    link: string
        The webpage with the table of triggers
    search_string: string
        The search string for finding trigger links
    output_path: string
        The path to save the JSONs to
    sernum: int
        The random iterating number with no relations to the data in the JSONs

    Returns
    --------
    sernum: int
        returns sernum for the next function call"""
    prefix = "https://gcn.gsfc.nasa.gov/"
    links_set = conversion.parse_trigger_links(link, prefix, search_string)
    links_list = list(links_set)

    for link in links_list:
        data = requests.get(link).text

        start_idx = data.find("\n") + 1
        while True:
            end_idx = data.find("\n \n ", start_idx)
            if end_idx == -1:
                break

            notice_message = email.message_from_string(data[start_idx:end_idx].strip())
            if "\n\n" in notice_message.as_string():
                notice_string = data[start_idx:end_idx].strip()
                notice_dict = conversion.parse_notice(notice_string)
            else:
                comment_list = notice_message.get_all("COMMENTS")
                comment_list = [item for item in comment_list if item]
                comment = "\n".join(comment_list)
                notice_dict = dict(notice_message)
                notice_dict["COMMENTS"] = comment

            notice_type = notice_message["NOTICE_TYPE"].split()[1]
            if notice_type == "Astrotrack":
                notice_type = f"Astrotrack {notice_message["NOTICE_TYPE"].split()[2]}"
                output = text_to_json_amon(notice_dict, input_gold_bronze, notice_type)
            elif notice_type == "Burst":
                output = text_to_json_amon(notice_dict, input_burst, notice_type)
            elif notice_type == "Neutrino-EM":
                notice_type = f"Neutrino-EM {notice_message["NOTICE_TYPE"].split()[2]}"
                output = text_to_json_amon(notice_dict, input_coincidence, notice_type)
            elif notice_type == "Cascade":
                output = text_to_json_amon(notice_dict, input_cascade, notice_type)
            elif notice_type == "ICECUBE":
                notice_type = notice_message["NOTICE_TYPE"].split()[2]
                if notice_type == "EHE":
                    output = text_to_json_amon(notice_dict, input_ehe, notice_type)
                elif notice_type == "HESE":
                    output = text_to_json_amon(notice_dict, input_hese, notice_type)

            with open(
                f"{output_path}AMON_{sernum}_{output["record_number"]}.json", "w"
            ) as f:
                json.dump(output, f)

            sernum += 1
            temp_start_idx = data.find("///////////", end_idx)
            start_idx = data.find("\n", temp_start_idx)
            if temp_start_idx == -1:
                break

    return sernum


def create_all_amon_jsons():
    """Creates a `amon_jsons` directory and fills it with the json for all AMON triggers."""
    output_path = "./output/amon_jsons/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    sernum = 1
    sernum = create_amon_jsons_one_webpage(
        "https://gcn.gsfc.nasa.gov/amon_icecube_gold_bronze_events.html",
        "notices_amon_g_b/.*amon",
        output_path,
        sernum,
    )
    sernum = create_amon_jsons_one_webpage(
        "https://gcn.gsfc.nasa.gov/amon_hawc_events.html",
        "notices_amon_hawc/.*amon",
        output_path,
        sernum,
    )
    sernum = create_amon_jsons_one_webpage(
        "https://gcn.gsfc.nasa.gov/amon_nu_em_coinc_events.html",
        "notices_amon_nu_em/.*amon",
        output_path,
        sernum,
    )
    sernum = create_amon_jsons_one_webpage(
        "https://gcn.gsfc.nasa.gov/amon_icecube_cascade_events.html",
        "notices_amon_icecube_cascade/.*amon",
        output_path,
        sernum,
    )
    sernum = create_amon_jsons_one_webpage(
        "https://gcn.gsfc.nasa.gov/amon_ehe_events.html",
        "notices_amon/.*amon",
        output_path,
        sernum,
    )
    sernum = create_amon_jsons_one_webpage(
        "https://gcn.gsfc.nasa.gov/amon_hese_events.html",
        "notices_amon/.*amon",
        output_path,
        sernum,
    )
