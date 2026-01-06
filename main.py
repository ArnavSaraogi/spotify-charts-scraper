from src.scraper import scrape, scrape_update

from countries import countries
from config import config

from datetime import datetime, date, timedelta
import os

DATE_FLOOR = date(2017, 1, 1)
DATE_CEILING = date.today() - timedelta(days=1) # latest chart on Spotify will always be at most yesterday

def main():
    # validate filename
    filename = config.get("filename")
    if not isinstance(filename, str) or not filename.lower().endswith(".json"):
        print("filename must be a string ending with .json")
        return
    
    # //* UPDATE MODE *//

    # check if update is True
    if config["update"]:
        file_path = f"data/{filename}"
        if not os.path.isfile(file_path):
            print(f"Cannot update: {file_path} does not exist")
            return
        
        if config["update_to"] == "today":
            update_to = DATE_CEILING
        else:
            try:
                update_to = datetime.strptime(config["update_to"], "%Y-%m-%d").date()
            except ValueError:
                print("update_to must be 'today' or in YYYY-MM-DD format")
                return
        
        if update_to > DATE_CEILING:
            print(f"Changed update_to to latest available date: {DATE_CEILING}")
            update_to = DATE_CEILING
        scrape_update(update_to, filename)
        return
    
    # //* NORMAL MODE *//
    
    file_path = f"data/{filename}"
    if os.path.isfile(file_path):
        response = input(f"File {file_path} already exists. Delete it? (y/n): ").strip().lower()
        if response == "y":
            print(f"Deleting existing file: {file_path}")
            os.remove(file_path)
        else:
            print("Keeping existing file. Exiting scrape.")
            return 

    # validate country
    if config["country"] not in countries:
        print("Country not found. See countries.py for available countries")
        return

    # validate dates
    try:
        start = datetime.strptime(config["start_date"], "%Y-%m-%d").date()
    except ValueError:
        print("start_date must be in YYYY-MM-DD format")
        return
    
    try:
        end = datetime.strptime(config["end_date"], "%Y-%m-%d").date()
    except ValueError:
        print("end_date must be in YYYY-MM-DD format")
        return

    if start > end:
        print("start_date must be earlier than or equal to end_date")
        return

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

    scrape(country_code, start, end, top_n, filename)

if __name__ == "__main__":
    main()