import email
import json
import os

import requests

from ... import conversion

input = {
    "standard": {
        "id": "TRIGGER_NUM",
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["TRIGGER_DATE", "TRIGGER_TIME"],
    }
}


def text_to_json_suzaku(notice, input, record_number):
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
        "https://gcn.nasa.gov/schema/main/gcn/notices/classic/suzaku/alert.schema.json"
    )

    output_dict["record_number"] = record_number
    if record_number == 1:
        output_dict["alert_type"] = "initial"
    else:
        output_dict["alert_type"] = "update"

    output_dict["mission"] = "SUZAKU"
    output_dict["instrument"] = "WAM"
    output_dict["trigger_type"] = "rate"

    url = notice["LC_URL"]
    output_dict["lightcurve_url"] = f"https://gcn.gsfc.nasa.gov/notices_suz/{url}"

    return output_dict


def create_all_suzaku_jsons():
    """Creates a `suzaku_jsons` directory and fills it with the json for all CALET triggers."""
    output_path = "./output/suzaku_jsons/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    archive_link = "https://gcn.gsfc.nasa.gov/suzaku_wam.html"
    prefix = "https://gcn.gsfc.nasa.gov/"
    search_string = "other/.*suzaku"
    links_set = conversion.parse_trigger_links(archive_link, prefix, search_string)
    links_list = list(links_set)

    for sernum in range(len(links_list)):
        link = links_list[sernum]
        data = requests.get(link).text

        record_number = 1
        start_idx = data.find("\n") + 1
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
            output = text_to_json_suzaku(notice_dict, input, record_number)

            with open(
                f"{output_path}SUZAKU_WAM_{sernum+1}_{record_number}.json", "w"
            ) as f:
                json.dump(output, f)

            record_number += 1
            temp_start_idx = data.find("///////////", end_idx)
            start_idx = data.find("\n", temp_start_idx) + 1
            if temp_start_idx == -1:
                break
