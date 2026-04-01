import email
import json
import os

import requests

from ... import conversion

input_known = {
    "standard": {
        "id": "SRC_ID_NUM",
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["SRC_DATE", "SRC_TIME"],
        "ra": "SRC_RA",
        "dec": "SRC_DEC",
    },
    "additional": {
        "ra_dec_error": ("SRC_ERROR", "float"),
        "energy_flux": ("SRC_FLUX", "float"),
        "duration": ("SRC_TSCALE", "string"),
        "source_name": ("SOURCE_NAME", "string"),
    },
}

input_unknown = {
    "standard": {
        "id": "EVENT_ID_NUM",
        "alert_datetime": "NOTICE_DATE",
        "trigger_time": ["EVENT_DATE", "EVENT_TIME"],
        "ra": "EVENT_RA",
        "dec": "EVENT_DEC",
    },
    "additional": {
        "ra_dec_error": ("EVENT_ERROR", "float"),
        "energy_flux": ("EVENT_FLUX", "float"),
        "duration": ("EVENT_TSCALE", "string"),
    },
}

# From Kawamura et al. 2018
conversion_factors = [4e-12, 1.24e-11, 1.65e-11, 8.74e-12]
energy_range_options = [[2, 4], [4, 10], [10, 20], [2, 10]]
source_band_flux = [
    ("source_flux_low_band", "background_flux_low_band"),
    ("source_flux_medium_band", "background_flux_medium_band"),
    ("source_flux_high_band", "background_flux_high_band"),
]

bad_links = [
    "https://gcn.gsfc.nasa.gov/other/6743227223.maxi",
    "https://gcn.gsfc.nasa.gov/other/6397334289.maxi",
    "https://gcn.gsfc.nasa.gov/other/6841168969.maxi",
    "https://gcn.gsfc.nasa.gov/other/6731800001.maxi",
    "https://gcn.gsfc.nasa.gov/other/6397381732.maxi",
    "https://gcn.gsfc.nasa.gov/other/6741178054.maxi",
]


def text_to_json_maxi(notice, input, record_number, notice_type):
    """Function calls text_to_json and then adds additional fields depeding on the `notice_type`.

    Parameters
    -----------
    notice: dict
        The text notice that is being parsed.
    input: dict
        The mapping between text notices keywords and GCN schema keywords.
    record_number: int
        The current notice in the webpage being parsed.
    notice_type:
        The type of MAXI notice.

    Returns
    -------
    dictionary
        A dictionary compliant with the associated schema for the mission."""
    output_dict = conversion.text_to_json(notice, input)

    output_dict["$schema"] = (
        "https://gcn.nasa.gov/schema/main/gcn/notices/classic/maxi/alert.schema.json"
    )
    output_dict["notice_type"] = notice_type
    output_dict["systematic_included"] = True

    output_dict["record_number"] = record_number
    if record_number == 1:
        output_dict["alert_type"] = "initial"
    else:
        output_dict["alert_type"] = "update"

    if notice_type == "Known":
        eband_data = notice["SRC_EBAND"].split()[1].split("-")
    elif notice_type == "Unknown":
        eband_data = notice["EVENT_EBAND"].split()[1].split("-")
    eband = [int(eband_data[0]), int(eband_data[1])]
    output_dict["flux_energy_range"] = eband
    index = energy_range_options.index(eband)
    output_dict["energy_flux"] = output_dict["energy_flux"] * conversion_factors[index]

    if notice_type == "Known":
        output_dict["classification"] = {notice["SRC_CLASS"].split()[0]: 1}

        band_fluxes = notice["BAND_FLUX"].split("\n")

        for idx in range(len(band_fluxes)):
            band_flux_data = band_fluxes[idx].split(",")

            output_dict[source_band_flux[idx][0]] = (
                float(band_flux_data[0][:-1]) * conversion_factors[idx]
            )
            output_dict[source_band_flux[idx][1]] = (
                float(band_flux_data[1].split()[0]) * conversion_factors[idx]
            )

        lon_lat_data = notice["ISS_LON_LAT"].split(",")
        if lon_lat_data[0] != "0.00":
            output_dict["longitude"] = float(lon_lat_data[0])
        if lon_lat_data[1] != " 0.00":
            output_dict["latitude"] = float(lon_lat_data[1].split()[0])

    return output_dict


def create_all_maxi_jsons():
    """Creates a `maxi_jsons` directory inside an `output` directory and fills it with the json for all CALET triggers."""
    output_path = "./output/maxi_jsons/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    archive_link = "https://gcn.gsfc.nasa.gov/maxi_grbs.html"
    prefix = "https://gcn.gsfc.nasa.gov/"
    search_string = "other/.*maxi"
    links_set = conversion.parse_trigger_links(archive_link, prefix, search_string)
    links_list = list(links_set)

    for sernum in range(len(links_list)):
        link = links_list[sernum]
        data = requests.get(link).text

        if link in bad_links:
            continue

        record_number = 1
        start_idx = data.find("\n") + 1
        while True:
            end_idx = data.find("\n \n", start_idx)
            # Sometimes there is a \n\n isntead of a \n after SRC_NAME
            # This messes with the email package
            message = data[start_idx:end_idx].strip().replace("\n\n", "\n")
            notice_message = email.message_from_string(message)
            comment = "\n".join(notice_message.get_all("COMMENTS"))
            notice_dict = dict(notice_message)
            notice_dict["COMMENTS"] = comment

            notice_type = notice_dict["NOTICE_TYPE"].split()[1]

            if notice_type == "Known":
                band_flux = "\n".join(notice_message.get_all("BAND_FLUX"))
                notice_dict["BAND_FLUX"] = band_flux
                output = text_to_json_maxi(
                    notice_dict, input_known, record_number, "Known"
                )
            elif notice_type == "Unknown":
                output = text_to_json_maxi(
                    notice_dict, input_unknown, record_number, "Unknown"
                )

            with open(f"{output_path}MAXI_{sernum+1}_{record_number}.json", "w") as f:
                json.dump(output, f)

            record_number += 1
            temp_start_idx = data.find("///////////", end_idx)
            start_idx = data.find("\n", temp_start_idx)
            if temp_start_idx == -1:
                break
