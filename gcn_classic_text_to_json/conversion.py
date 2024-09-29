import re

import requests
from bs4 import BeautifulSoup

months_of_the_year = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

invalid_trigger_dates = ["(yy-mm-dd)", "(yy/mm/dd)", "(yyyy/mm/dd)"]


def parse_trigger_links(link, prefix, regex_string):
    """Returns a list of trigger_links present in `link`.

    The function parses through each row and hyperlink present in the html
    table in `link` and returns a set of links associated with the mission.

    Parameters
    ----------
    link: string
        The webpage with the trigger links listed.
    prefix: string
        The prefix to be added to the incomplete link.
    regex_string: string
        Regex string to search for while looking through links.

    Returns
    -------
    array-like
        A set of link for the various triggers associated with the mission.
    """
    data = requests.get(link).text

    soup = BeautifulSoup(data, "html.parser")

    links = set({})
    for incomplete_link in soup.find_all("a", attrs={"href": re.compile(regex_string)}):
        link = prefix + incomplete_link.get("href")
        links.add(link)
    return links


def text_to_json(notice, keywords_dict):
    """Returns a dictionary with the data associated with fields in `keywords_dict`.

    Additionally, the function adds any data associated with the `COMMENTS` field.

    Paramaters
    ----------
    notice: dict
        The text notice that is being parsed.
    keywords_dict: dictionary
        `keywords_dict` has 2 inner dictionaries:'standard' and 'additional'. 'standard' consists of those
        fields which have a common definition through all notices. Generally, the key is the unified schema keyword
        and the value is the notice keyword (see Notes for exception). 'additional' consists of fields where the
        associated quantity can be extracted as a simple 0-indexed value of a list. The key is the schema keyword
        and the value is a tuple of (notice_keyword, type).
    notice_start_idx: int
        The index at which the current text notice begins.

    Returns
    -------
    dictionary
        A dictionary compliant with the associated schema for the mission.

    Notes
    -----
    Exceptions for the 'standard' dictionary format are 'trigger_time' which has a tuple of (notice_date, notice_time)
    as the value (Since these values are stored in seperate fields) and 'ra_dec' which has a tuple of (ra, dec)
    as the key (Since the format is identical).
    """
    output = {}

    if "alert_datetime" in keywords_dict["standard"]:
        notice_alert_datetime = keywords_dict["standard"]["alert_datetime"]
        alert_datetime_data = notice[notice_alert_datetime].split()

        alert_date = alert_datetime_data[1]
        alert_month = months_of_the_year.index(alert_datetime_data[2]) + 1
        alert_year, alert_time = "20" + alert_datetime_data[3], alert_datetime_data[4]
        alert_datetime = f"{alert_year}-{alert_month}-{alert_date}T{alert_time}Z"

        output["alert_datetime"] = alert_datetime

    if "id" in keywords_dict["standard"]:
        notice_id = keywords_dict["standard"]["id"]
        id_data = notice[notice_id]
        id = id_data.split()[0]
        output["id"] = [int(id)]

    if "trigger_time" in keywords_dict["standard"]:
        notice_date, notice_time = keywords_dict["standard"]["trigger_time"]
        trigger_date_data = notice[notice_date].split()

        trigger_date = trigger_date_data[-1]
        if trigger_date in invalid_trigger_dates:
            trigger_date = trigger_date_data[-2]
        if len(trigger_date) == 8:
            trigger_date = "20" + trigger_date

        trigger_time_data = notice[notice_time]
        trigger_time_start_idx = trigger_time_data.find("{")
        trigger_time_end_idx = trigger_time_data.find("}", trigger_time_start_idx)
        trigger_time = trigger_time_data[
            trigger_time_start_idx + 1 : trigger_time_end_idx
        ]
        trigger_datetime = f"{trigger_date.replace('/', '-', 2)}T{trigger_time}Z"
        output["trigger_time"] = trigger_datetime

    if "ra" in keywords_dict["standard"]:
        notice_ra = keywords_dict["standard"]["ra"]
        ra_data = notice[notice_ra].split()

        if ra_data[0] != "Undefined":
            output["ra"] = float(ra_data[0][:-1])

    if "dec" in keywords_dict["standard"]:
        notice_dec = keywords_dict["standard"]["dec"]
        dec_data = notice[notice_dec].split()

        if dec_data[0] != "Undefined":
            output["dec"] = float(dec_data[0][:-1])

    if "additional" in keywords_dict:
        for json_keyword, notice_keyword_tuple in keywords_dict["additional"].items():
            notice_keyword, keyword_type = notice_keyword_tuple
            if notice.get(notice_keyword) is not None and notice.get(notice_keyword):
                val = notice[notice_keyword].split()[0]
                if keyword_type == "int":
                    val = int(val)
                elif keyword_type == "float":
                    val = float(val)
                output[json_keyword] = val

    output["additional_info"] = notice["COMMENTS"]

    return output
