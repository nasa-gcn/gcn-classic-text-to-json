import json
import os

import requests
from bs4 import BeautifulSoup
from scipy.stats import norm

contain_prob = norm.cdf(3) - norm.cdf(-3)


def create_all_alexis_jsons():
    """Function parse through an HTML table to generate the JSON associated with each row.
    Then create a alexis_json directory inside an output directory.

    Notes
    ------
    Function skips through the first row with a tag as that is the row associated with the row headers.
    """
    output_path = "./output/alexis_jsons/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    link = "https://gcn.gsfc.nasa.gov/alexis_trans.html"
    data = requests.get(link).text

    soup = BeautifulSoup(data, "html.parser")

    rows = soup.find_all("tr")

    for idx in range(1, len(rows[1:]) + 1):
        row = rows[idx]

        output_dict = {
            "$schema": "https://gcn.nasa.gov/schema/main/gcn/notices/classic/alexis/alert.schema.json",
            "mission": "ALEXIS",
        }

        cols = row.find_all("td")

        year = cols[0].text.replace("/", "-", 2)
        output_dict["end_datetime"] = f"20{year}T{cols[1].text}Z"

        output_dict["map_duration"] = int(cols[2].text)

        output_dict["notice_type"] = cols[3].text

        output_dict["ra"] = float(cols[4].text)

        output_dict["dec"] = float(cols[5].text)

        output_dict["ra_dec_error"] = float(cols[6].text)

        output_dict["containment_probability"] = contain_prob

        output_dict["systematic_included"] = True

        output_dict["alpha"] = float(cols[7].text)

        output_dict["telescope_id"] = cols[8].text

        if output_dict["telescope_id"] == "1A" or output_dict["telescope_id"] == "2A":
            output_dict["energy_bandpass"] = 93
        elif output_dict["telescope_id"] == "1B" or output_dict["telescope_id"] == "3A":
            output_dict["energy_bandpass"] = 70
        elif output_dict["telescope_id"] == "2B" or output_dict["telescope_id"] == "3B":
            output_dict["energy_bandpass"] = 66

        with open(f"{output_path}ALEXIS_{idx}.json", "w") as file:
            json.dump(output_dict, file)
