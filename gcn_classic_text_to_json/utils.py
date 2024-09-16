def find_string_between(data, first, last):
    """Find string between `first` and `last` beginning at `start_idx`.

    Parameters
    ----------
    data: string
        The string through which to search for `first` and `last`.
    first: string
        The text preceeding the string to be returned.
    last: string
        The text succeeding the string to be returned.

    Returns
    -------
    string
        The text between `first` and `last`."""
    first_idx = data.find(first) + len(first)
    last_idx = data.find(last, first_idx)
    return data[first_idx:last_idx]
