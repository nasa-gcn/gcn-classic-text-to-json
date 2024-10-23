import email
import json
import os

import requests

from ... import conversion

input_spiacs = {
    "standard": {
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["GRB_DATE", "GRB_TIME"],
    },
    "additional": {"rate_snr": ("GRB_INTEN", "float")},
}

input_grb = {
    "standard": {
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["GRB_DATE", "GRB_TIME"],
        "ra": "GRB_RA",
        "dec": "GRB_DEC",
    },
    "additional": {
        "ra_dec_error": ("GRB_ERROR", "float"),
        "rate_snr": ("GRB_INTEN", "float"),
        "ra_pointing": ("SC_RA", "float"),
        "dec_pointing": ("SC_DEC", "float"),
    },
}

input_point = {
    "standard": {
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["SLEW_DATE", "SLEW_TIME"],
    }
}


def text_to_json_integral_pointdir(notice, input):
    """Function deals with Pointing Direction notice type.

    Parameters
    -----------
    notice: dict
        The text notice that is being parsed.
    input: dict
        The mapping between text notices keywords and GCN schema keywords.

    Returns
    -------
    dictionary
        A dictionary compliant with the associated schema for the mission."""
    output_dict = conversion.text_to_json(notice, input)

    output_dict["$schema"] = (
        "https://gcn.nasa.gov/schema/main/gcn/notices/classic/integral/alert.schema.json"
    )
    output_dict["mission"] = "INTEGRAL"
    output_dict["notice_type"] = "Pointing Direction"

    output_dict["next_sc_ra"] = float(notice["NEXT_POINT_RA"].split()[0][:-1])
    output_dict["next_sc_dec"] = float(notice["NEXT_POINT_DEC"].split()[0][:-1])

    return output_dict


def text_to_json_integral(notice, input, record_number, notice_type):
    """Function calls text_to_json and then adds additional fields depending on the notice type.

    Parameters
    -----------
    notice: dict
        The text notice that is being parsed.
    input: dict
        The mapping between text notices keywords and GCN schema keywords.
    record_number: int
        The current notice being parsed in a given webpage.
    notice_type: string
        The type of INTEGRAL notice except Pointing Direction.

    Returns
    -------
    dictionary
        A dictionary compliant with the associated schema for the mission."""
    output_dict = conversion.text_to_json(notice, input)

    output_dict["$schema"] = (
        "https://gcn.nasa.gov/schema/main/gcn/notices/classic/integral/alert.schema.json"
    )
    output_dict["mission"] = "INTEGRAL"
    output_dict["notice_type"] = notice_type
    output_dict["record_number"] = record_number

    if record_number == 1:
        output_dict["alert_type"] = "initial"
    else:
        output_dict["alert_type"] = "update"

    output_dict["id"] = [int(notice["TRIGGER_NUM"].split()[0][:-1])]

    return output_dict


def create_integral_jsons_one_webpage(link, output_path, sernum):
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
    search_string = "other/.*integral"
    links_set = conversion.parse_trigger_links(link, prefix, search_string)
    links_list = list(links_set)

    for link in links_list:
        data = requests.get(link).text

        start_idx = data.find("\n") + 1
        record_number = 1
        while True:
            end_idx = data.find("\n \n ", start_idx)
            message = data[start_idx:end_idx].strip()
            while "///////" in message:
                start_idx = data.find("\n", start_idx) + 1
                message = data[start_idx:end_idx].strip()

            if end_idx == -1:
                break
            elif not message:
                temp_start_idx = data.find("///////////", end_idx)
                start_idx = data.find("\n", temp_start_idx)
                if start_idx != -1:
                    continue
                else:
                    break

            notice_message = email.message_from_string(message)
            comment = "\n".join(notice_message.get_all("COMMENTS"))
            notice_dict = dict(notice_message)
            notice_dict["COMMENTS"] = comment

            notice_type = notice_dict["NOTICE_TYPE"].split()[1]
            if notice_type == "Pointing":
                output = text_to_json_integral_pointdir(notice_dict, input_point)
            elif notice_type == "SPI":
                output = text_to_json_integral(
                    notice_dict, input_spiacs, record_number, "SPI-ACS"
                )
            else:
                output = text_to_json_integral(
                    notice_dict, input_grb, record_number, notice_type
                )

            with open(f"{output_path}INTEGRAL_{sernum}_{record_number}.json", "w") as f:
                json.dump(output, f)

            sernum += 1
            record_number += 1
            temp_start_idx = data.find("///////////", end_idx)
            start_idx = data.find("\n", temp_start_idx)
            if temp_start_idx == -1:
                break

    return sernum


def create_all_integral_jsons():
    """Creates a `integral_jsons` directory inside an `output` directory and fills it with the json for all INTEGRAL triggers."""
    output_path = "./output/integral_jsons/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    sernum = 1
    sernum = create_integral_jsons_one_webpage(
        "https://gcn.gsfc.nasa.gov/integral_spiacs.html", output_path, sernum
    )
    create_integral_jsons_one_webpage(
        "https://gcn.gsfc.nasa.gov/integral_grbs.html", output_path, sernum
    )
