import json
import os
import re

import requests
from bs4 import BeautifulSoup


def create_near_jsons(link, sernum):
    """Parses through the table in `link` and creates JSONs for each row.
    Then and creates a near_jsons directory inside an output directory

    Parameters
    ----------
    link: string
        The link to be parsed.
    sernum: int
        An iterative number for saving the JSONs. This number has no relation with the data in the JSONs.

    Returns
    -------
    sernum: int
        returns sernum to be used in the next iteration of the function"""
    output_path = "./output/near_jsons/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    file = requests.get(link)
    data = file.text

    start_idx = data.find("<!XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX>")
    start_idx = data.find("<LI>", start_idx)

    while start_idx != -1:
        output_dict = {
            "$schema": "https://gcn.nasa.gov/schema/main/gcn/notices/classic/near/alert.schema.json"
        }
        end_idx = data.find("\n", start_idx)

        row_data = data[start_idx:end_idx].split()

        trigger_date_data = row_data[1]
        trigger_time = row_data[4]

        if trigger_date_data[:2] == "99":
            output_dict["trigger_time"] = (
                f"19{trigger_date_data[:2]}-{trigger_date_data[2:4]}-{trigger_date_data[-2:]}T{trigger_time}Z"
            )
        else:
            output_dict["trigger_time"] = (
                f"20{trigger_date_data[:2]}-{trigger_date_data[2:4]}-{trigger_date_data[-2:]}T{trigger_time}Z"
            )

        postscript_url_start_idx = data.find("<A", start_idx)
        jpeg_url_start_idx = data.find("<A", postscript_url_start_idx)
        jpeg_url_end_idx = data.find(">", jpeg_url_start_idx)
        textfile_url_start_idx = data.find("<A", jpeg_url_start_idx)
        textfile_url_end_idx = data.find(">", textfile_url_start_idx)

        jpeg_url_incomplete = data[jpeg_url_start_idx:jpeg_url_end_idx]
        jpeg_url = f"https://gcn.gsfc.nasa.gov/{jpeg_url_incomplete}"

        textfile_url_incomplete = data[textfile_url_start_idx:textfile_url_end_idx]
        textfile_url = f"https://gcn.gsfc.nasa.gov/{textfile_url_incomplete}"

        output_dict["lightcurve_image_url"] = f"https://gcn.gsfc.nasa.gov/{jpeg_url}"

        output_dict["lightcurve_textfile_url"] = (
            f"https://gcn.gsfc.nasa.gov/{textfile_url}"
        )

        with open(f"{output_path}NEAR_{sernum}.json", "w") as f:
            json.dump(output_dict, f)

        sernum += 1
        start_idx = data.find("<LI>", end_idx)

    return sernum


def parse_all_near_triggers():
    """The main near webpage links to muliple webpages with more links.
    This function finds them and calls create_all_konus_triggers for each"""
    main_link = "https://gcn.gsfc.nasa.gov/near_grbs.html"
    file = requests.get(main_link)
    data = file.text

    soup = BeautifulSoup(data, "html.parser")

    search_string = re.compile("grbs.html")
    html_tags = soup.find_all("a", attrs={"href": search_string})

    html_links = []

    for tag in html_tags:
        incomplete_link = tag.get("href")
        html_links.append(f"https://gcn.gsfc.nasa.gov/{incomplete_link}")

    html_links.append(main_link)

    sernum = 1
    for link in html_links:
        sernum = create_near_jsons(link, sernum)
