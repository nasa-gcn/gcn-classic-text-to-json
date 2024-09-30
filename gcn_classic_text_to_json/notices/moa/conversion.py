import email
import json
import os

import requests

from ... import conversion

input = {
    "standard": {
        "id": "SRC_ID_NUM",
        "ra": "SRC_RA",
        "dec": "SRC_DEC",
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["DISCOVERY_DATE", "DISCOVERY_TIME"],
    },
    "additional": {
        "max_time_error": ("MAX_UNCERT", "float"),
        "cusp_width": ("CUSP_WIDTH", "float"),
        "u0": ("u0", "float"),
        "base_mag": ("BASE_MAG", "float"),
        "lightcurve_url": ("LC_URL", "string"),
    },
}


def text_to_json_moa(notice, input, record_number):
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

    output_dict["$schema"] = (
        "https://gcn.nasa.gov/schema/main/gcn/notices/classic/moa/alert.schema.json"
    )
    output_dict["mission"] = "MOA"
    output_dict["record_number"] = record_number
    if record_number == 1:
        output_dict["alert_type"] = "initial"
    else:
        output_dict["alert_type"] = "update"

    max_date_data = notice["MAX_DATE"].split()

    max_date = max_date_data[-1]
    if max_date == "(yy/mm/dd)":
        max_date = "20" + max_date_data[-2]

    max_time_data = notice["MAX_TIME"]
    max_time_start_idx = max_time_data.find("{")
    max_time_end_idx = max_time_data.find("}", max_time_start_idx)
    trigger_time = max_time_data[max_time_start_idx + 1 : max_time_end_idx]
    max_datetime = f"{max_date.replace('/', '-', 2)}T{trigger_time}Z"
    output_dict["max_time"] = max_datetime

    if "MAX_MAG" in notice:
        max_mag = notice["MAX_MAG"].split()[0]
    elif "PEAK_MAG" in notice:
        max_mag = notice["PEAK_MAG"].split()[0]
    if max_mag != "No":
        output_dict["max_mag"] = float(max_mag)

    amplification = notice["AMPLIFICATION"].split()[0]
    if amplification != "No":
        output_dict["amplification"] = float(amplification)

    output_dict["cusp_width_error"] = float(notice["CUSP_WIDTH"].split()[-2])

    output_dict["u0_error"] = float(notice["u0"].split()[-2])

    output_dict["base_mag_error"] = float(notice["BASE_MAG"].split()[-2])

    return output_dict


def create_all_moa_jsons():
    """Creates a `moa_jsons` directory and fills it with the json for all MOA triggers."""
    output_path = "./output/moa_jsons/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    archive_link = "https://gcn.gsfc.nasa.gov/moa_events.html"
    prefix = "https://gcn.gsfc.nasa.gov/"
    search_string = "other/.*moa.txt"
    links_set = conversion.parse_trigger_links(archive_link, prefix, search_string)
    links_list = list(links_set)

    for sernum in range(len(links_list)):
        link = links_list[sernum]
        data = requests.get(link).text

        if link == "https://gcn.gsfc.nasa.gov/other/moa/201400214_moa.txt":
            continue

        record_number = 1
        if (
            link != "https://gcn.gsfc.nasa.gov/other/moa/201500099_moa.txt"
            and link != "https://gcn.gsfc.nasa.gov/other/moa/_moa.txt"
        ):
            start_idx = data.find("\n") + 1
        else:
            start_idx = data.find("TITLE")

        while True:
            if (
                link != "https://gcn.gsfc.nasa.gov/other/moa/201500099_moa.txt"
                and link != "https://gcn.gsfc.nasa.gov/other/moa/_moa.txt"
            ):
                end_idx = data.find("\n \n ", start_idx)
            else:
                end_idx = data.find("unavailable", start_idx) + len("unavailable") + 1

            notice_message = email.message_from_string(data[start_idx:end_idx].strip())
            print(link)
            # print(notice_message)
            comment = "\n".join(notice_message.get_all("COMMENTS"))
            notice_dict = dict(notice_message)
            notice_dict["COMMENTS"] = comment

            output = text_to_json_moa(notice_dict, input, record_number)

            with open(f"{output_path}MOA_{sernum+1}_{record_number}.json", "w") as f:
                json.dump(output, f)

            record_number += 1
            if (
                link != "https://gcn.gsfc.nasa.gov/other/moa/201500099_moa.txt"
                and link != "https://gcn.gsfc.nasa.gov/other/moa/_moa.txt"
            ):
                temp_start_idx = data.find("///////////", end_idx)
                start_idx = data.find("\n", temp_start_idx)
                if temp_start_idx == -1:
                    break
            else:
                start_idx = data.find("TITLE", end_idx)
                if start_idx == -1:
                    break
