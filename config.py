"""
See countries.py for the list of available countries
Start_date and end_date must be in YYYY-MM-DD format
top_n must be between 1 and 200

When update is True, the file in filename is updated up to the date in update_to. update_to can take dates and "today" as a param.
Note that when "today" is used today's data (and sometimes yesterday's) isn't available so won't be added.
The fields country, start_date, end_date, and top_n are ignored.
"""

config = {
    "country": "USA",
    "start_date": "2025-01-01",
    "end_date": "2025-01-3",
    "top_n": 3,
    "filename": "charts.json",
    "update": True,
    "update_to": "2025-01-15"
}