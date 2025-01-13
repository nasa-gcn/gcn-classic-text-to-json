import email
import json
import os

import requests

from ... import conversion

input = {
    "standard": {
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["GRB_DATE", "GRB_TIME"],
    },
    "additional": {"longitude": ("SC_LONG", "float")},
}


def text_to_json_hete(notice, input):
    """Function calls text_to_json and then adds specific fields depending on notice_type.

    Parameters
    -----------
    notice: dict
        The text notice that is being parsed.
    input: dict
        The mapping between text notices keywords and GCN schema keywords.

    Returns
    -------
    dictionary
        A dictionary compliant with the associated schema for the mission.
    record_number
        the order of `notice` in the webpage"""
    output_dict = conversion.text_to_json(notice, input)

    output_dict["$schema"] = (
        "https://gcn.nasa.gov/schema/main/gcn/notices/classic/hete/alert.schema.json"
    )
    output_dict["mission"] = "HETE"

    notice_type = notice["NOTICE_TYPE"].split()[1]
    output_dict["notice_type"] = notice_type

    id_record_number_data = notice["TRIGGER_NUM"].split()
    output_dict["id"] = [int(id_record_number_data[0][:-1])]
    record_number = int(id_record_number_data[-1])
    output_dict["record_number"] = record_number

    trigger_range = notice["TRIGGER_SOURCE"].split()[-3].split("-")
    output_dict["rate_energy_range"] = [int(trigger_range[0]), int(trigger_range[1])]

    if "GAMMA_RATE" in notice:
        count_rate_data = notice["GAMMA_RATE"]
        output_dict["net_count_rate"] = int(count_rate_data.split()[0])
        output_dict["rate_duration"] = float(count_rate_data.split()[-3])

    if "WXM_SIG/NOISE" in notice:
        output_dict["rate_snr"] = float(notice["WXM_SIG/NOISE"].split()[0])

    if "SC_-Z_RA" and "SC_-Z_DEC" in notice:
        output_dict["ra"] = float(notice["SC_-Z_RA"].split()[0])
        output_dict["dec"] = float(notice["SC_-Z_DEC"].split()[0])

    if "WXM_CNTR_RA" and "WXM_CNTR_DEC" in notice:
        output_dict["wxm_ra"] = float(notice["WXM_CNTR_RA"].split()[0][:-1])
        output_dict["wxm_dec"] = float(notice["WXM_CNTR_DEC"].split()[0][:-1])
        output_dict["wxm_ra_dec_error"] = float(notice["WXM_MAX_SIZE"].split()[0]) / 120
        output_dict["wxm_image_snr"] = float(notice["WXM_LOC_SN"].split()[0])

    if "SXC_CNTR_RA" and "SXC_CNTR_DEC" in notice:
        output_dict["sxc_ra"] = float(notice["SXC_CNTR_RA"].split()[0][:-1])
        output_dict["sxc_dec"] = float(notice["SXC_CNTR_DEC"].split()[0][:-1])
        output_dict["sxc_ra_dec_error"] = float(notice["SXC_MAX_SIZE"].split()[0]) / 120
        output_dict["sxc_image_snr"] = float(notice["SXC_LOC_SN"].split()[0])

    return (output_dict, record_number)


def create_all_hete_trigger():
    """Creates a `hete_jsons` directory and fills it with the json for all HETE triggers."""
    output_path = "./output/hete_jsons/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    archive_link = "https://gcn.gsfc.nasa.gov/hete_grbs.html"
    prefix = "https://gcn.gsfc.nasa.gov/"
    search_string = "other/.*hete"
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

            output, record_number = text_to_json_hete(notice_dict, input)

            with open(f"{output_path}HETE_{sernum + 1}_{record_number}.json", "w") as f:
                json.dump(output, f)

            temp_start_idx = data.find("///////////", end_idx)
            start_idx = data.find("\n", temp_start_idx)
            if temp_start_idx == -1:
                break
