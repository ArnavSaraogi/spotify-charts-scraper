from src.scraper import scrape

from countries import countries
from config import config

from datetime import datetime, date

DATE_FLOOR = date(2017, 1, 1)
DATE_CEILING = date.today()

def main():
    # validate country
    if config["country"] not in countries:
        print("Country not found. See countries.py for available countries")
        return

    # validate dates
    start = datetime.strptime(config["start_date"], "%Y-%m-%d").date()
    end = datetime.strptime(config["end_date"], "%Y-%m-%d").date()

    if start < DATE_FLOOR:
        print(f"Changed start to earliest available date: {DATE_FLOOR}")
        start = DATE_FLOOR
    if end > DATE_CEILING:
        print(f"Changed end to latest available date: {DATE_CEILING}")
        end = DATE_CEILING
    
    # validate top_n
    if config["top_n"] < 1 or config["top_n"] > 200:
        print("top_n must be between 1 and 200")
        return
    
    country_code = countries[config["country"]]
    top_n = config["top_n"]

    # validate filename
    filename = config.get("filename")
    if not isinstance(filename, str) or not filename.lower().endswith(".json"):
        print("filename must be a string ending with .json")
        return

    country_code = countries[config["country"]]
    top_n = config["top_n"]

    scrape(country_code, start, end, top_n, filename)

if __name__ == "__main__":
    main()