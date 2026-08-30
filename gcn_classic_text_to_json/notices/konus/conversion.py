import json
import os
import re

import requests
from bs4 import BeautifulSoup


def create_all_konus_jsons(link, sernum):
    """Parses through the table of KONUS triggers in `link` to create their respective JSONs
    and creates a konus_jsons directory inside an output directory.

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
    output_path = "./output/konus_jsons/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    file = requests.get(link)
    data = file.text

    soup = BeautifulSoup(data, "html.parser")

    rows = soup.find_all("tr")

    for row in rows[1:]:
        output_dict = {
            "$schema": "https://gcn.nasa.gov/schema/main/gcn/notices/classic/konus/alert.schema.json"
        }

        cols = row.find_all("td")

        trigger_date = cols[0].text.strip()
        trigger_time = cols[2].text.split()[0]
        output_dict["trigger_time"] = (
            f"{trigger_date[:4]}-{trigger_date[4:6]}-{trigger_date[-2:]}T{trigger_time}Z"
        )

        if cols[3].text != " " and cols[3].text != "" and cols[3].text != "\n":
            output_dict["detector_number"] = int(cols[3].text)

        if cols[4].text:
            output_dict["classification"] = {cols[4].text.strip(): 1}

        if cols[5].text:
            output_dict["id"] = [int(cols[5].text.strip())]

        incomplete_image_link = cols[7].find("a").get("href")
        output_dict["lightcurve_image_url"] = (
            f"https://gcn.gsfc.nasa.gov/{incomplete_image_link}"
        )

        incomplete_textfile_link = cols[9].find("a").get("href")
        output_dict["lightcurve_textfile_url"] = (
            f"https://gcn.gsfc.nasa.gov/{incomplete_textfile_link}"
        )

        with open(f"{output_path}KONUS_{sernum}.json", "w") as f:
            json.dump(output_dict, f)
        sernum += 1

    return sernum


def parse_all_konus_webpages():
    """The main konus webpage links to muliple webpages with more links.
    This function finds them and calls create_all_konus_triggers for each"""

    main_link = "https://gcn.gsfc.nasa.gov/konus_grbs.html"
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
        sernum = create_all_konus_jsons(link, sernum)
