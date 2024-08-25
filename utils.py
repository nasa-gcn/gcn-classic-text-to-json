import requests


def find_string_between(data, first, last, start_idx):
    """Find string between `first` and `last` beginning at `start_idx`.
    
    Parameters
    ----------
    data: string
        The string through which to search for `first` and `last`.
    first: string
        The text preceeding the string to be returned.
    last: string
        The text succeeding the string to be returned.
    start_idx: int
        The index from which to begin search for `first`.
        
    Returns
    -------
    string
        The text between `first` and `last`."""
    first_idx = data.find(first, start_idx) + len(first)
    last_idx = data.find(last, first_idx)
    return data[first_idx:last_idx]


def parse_trigger_ids(link):
    """Returns a list of trigger_id present in `link`.

    The function parses through each row and hyperlink present
    in the html table in `link` and returns a list of strings.

    Parameters
    ----------
    link: string
        The webpage with the trigger ids listed.
    
    Returns
    -------
    array-like
        A list of trigger ids as strings.
    """
    file = requests.get(link)
    data = file.text

    start_idx = data.find('<!XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX>')
    trig_nums = set({})

    while True:
        row_idx = data.find("<tr", start_idx)
        link_idx = data.find("<a", row_idx)

        val = find_string_between(data, ">", "</a>", link_idx)

        start_idx = data.find("</tr>", row_idx)

        if start_idx == -1:
            break
        else:
            trig_nums.add(val)
    return trig_nums


def set_id(data, notice_keyword, notice_start_idx):
    """Function to extract id from text notice.

    Parameters
    ----------
    data: string
        The text notice that is being parsed.
    notice_keyword: string
        The text notice equivalent for id.
    notice_start_idx: int
        The index at which the current text notice begins.

    Returns
    -------
    array-like
        A list with one element which is the id.

    Notes
    -----
    Assumes that id is present in every text notice.
    """
    id_data = find_string_between(data, notice_keyword, "\n", notice_start_idx)
    id = id_data.split()[0]
    return [int(id)]


def set_ra_and_dec(data, ra_notice_keyword, dec_notice_keyword, notice_start_idx):
    """Function to extract ra/dec from text notices.
    
    Parameters
    ----------
    data: string
        The text notice that is being parsed.
    ra_notice_keyword: string
        The text notice equivalent for ra.
    dec_notice_keyword: string
        The text notice equivalent for dec.
    notice_start_idx: int
        The index at which the current text notice begins.

    Returns
    -------
    tuple of floats
        A tuple containing ra and dec
    
    Notes
    -----
    Assumes that ra/dec is present in every text notice.
    """
    ra_data = find_string_between(data, ra_notice_keyword, "\n", notice_start_idx)
    ra = float(ra_data.split()[0][:-1])
    dec_data = find_string_between(data, dec_notice_keyword, "\n", notice_start_idx)
    dec = float(dec_data.split()[0][:-1])
    return (ra, dec)


def set_alert_datetime(data, notice_keyword, notice_start_idx):
    """Function to extract alert_datetime from text notices and convert to ISO 8601 format.
    
    Parameters
    ----------
    data: string
        The text notice that is being parsed.
    notice_keyword: string
        The text notice equivalent for alert_datetime.
    notice_start_idx: int
        The index at which the current text notice begins.

    Returns
    -------
    string
        returns datetime in ISO 8601 format.

    Notes
    -----
    Assumes that alert_datetime is present in every text notice.
    """
    months_of_the_year = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    alert_datetime_data = find_string_between(data, notice_keyword, notice_start_idx).split()

    alert_date, alert_month = alert_datetime_data[1], months_of_the_year.index(alert_datetime_data[2])+1
    alert_year, alert_time = "20"+alert_datetime_data[3], alert_datetime_data[4]
    alert_datetime = f"{alert_year}-{alert_month}-{alert_date}T{alert_time}Z"
    return alert_datetime


def set_trigger_time(data, notice_date_keyword, notice_time_keyword, notice_start_idx):
    """Funtion to extract trigger_time from text notices and convert to ISO 8601 format.
    
    Parameters
    ----------
    data: string
        The text notice that is being parsed.
    notice_date_keyword: string
        The text notice equivalent for trigger date.
    notice_time_keyword: string
        The text notice equivalent for trigger time.
    notice_start_idx: int
        The index at which the current text notice begins.
        
    Returns
    -------
    string
        returns datetime in ISO 8601 format.
        
    Notes
    -----
    The date is either the last or the second last value in the trigger_date field equivalent
    for the text notices. The code handles both possibilities."""
    trigger_date_data = find_string_between(data, notice_date_keyword, "\n", notice_start_idx).split()

    trigger_date = trigger_date_data[-1]
    if trigger_date == "(yy-mm-dd)":
        trigger_date = trigger_date_data[-2]

    trigger_time_idx = data.find(notice_time_keyword, notice_start_idx)
    trigger_time_start_idx = data.find("{", trigger_time_idx)
    trigger_time_end_idx = data.find("}", trigger_time_start_idx)
    trigger_time = data[trigger_time_start_idx+1:trigger_time_end_idx]

    return f"{trigger_date.replace('/', '-', 2)}T{trigger_time}Z"