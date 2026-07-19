import datetime as pydt
from langchain_core.tools import tool

@tool
def compare_dates(date_str:str, reference_date:str='2024-01-01', date_format:str='%Y-%m-%d') -> str:
    """
    Compare date_str against reference_date and generate a label as 'Expired' or 'Upcoming' or 'Ongoing' only

    Args:
        date_str: The input date for comparison, e.g. "2024-02-15".
        reference_date: The date to compare against, e.g. "2024-01-01". Defaults to "2024-01-01".
        date_format: The strptime format both dates are in. Defaults to "%Y-%m-%d".

    Return:
        result_list:  String label, e.g. "Ongoing".
    """
    date_dt = pydt.datetime.strptime(date_str, date_format)
    reference_date_dt = pydt.datetime.strptime(reference_date, date_format)

    day_diff = (date_dt - reference_date_dt).days

    if day_diff < 0:
        label = 'Expired'
    elif day_diff > 0:
        label = 'Upcoming'
    else:
        label = 'Ongoing'

    return label


# if __name__ == "__main__":
#     test = compare_dates("2024-02-15")
#     print(test)
