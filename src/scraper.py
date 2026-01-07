from src.auth import get_bearer_token
from src.fetch import fetch_chart, fetch_latest_date, UnauthorizedError, TooManyRequestsError

from datetime import timedelta, date, datetime
import time
import json
import os
from tqdm import tqdm

def write_to_json(new_data, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    if os.path.isfile(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = {"metadata": {}, "charts": {}}

    # update metadata
    existing["metadata"].update(new_data.get("metadata", {}))

    # merge charts by date
    existing["charts"].update(new_data.get("charts", {}))

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

def scrape(country, start, end, top_n, filename, save_interval=10, max_retries=4, base_delay=120, max_delay=600):
    file_path = f"data/{filename}"

    token = get_bearer_token()
    latest_date_str = fetch_latest_date(token, country)
    end = min(end, datetime.strptime(latest_date_str, "%Y-%m-%d").date())

    charts = {
        "metadata": {
            "country": country,
            "start_date": start.strftime("%Y-%m-%d"),
            "end_date": start.strftime("%Y-%m-%d"),
            "top_n": top_n,
        },
        "charts": {}
    }

    day_counter = 0
    total_days = (end - start).days + 1
    curr = start
    last_written_date = None

    for _ in tqdm(range(total_days), desc=f"Scraping {country}", unit="day"):
        curr_str = curr.strftime("%Y-%m-%d")

        for attempt in range(max_retries):
            try:
                charts["charts"][curr_str] = fetch_chart(curr_str, token, latest_date_str, country)[:top_n]
                last_written_date = curr_str
                break
            except UnauthorizedError as e:
                print(e)
                print("Trying new token...")
                token = get_bearer_token()
            except TooManyRequestsError as e:
                delay = min(base_delay * (2 ** attempt), max_delay)
                print(f"{e} - retrying in {delay}s (attempt {attempt+1}/{max_retries})")
                time.sleep(delay)
        else:
            raise RuntimeError(f"Failed to fetch {curr_str} after {max_retries} attempts.")

        day_counter += 1

        if day_counter >= save_interval:
            if last_written_date:
                charts["metadata"]["end_date"] = last_written_date
            write_to_json(charts, file_path)
            charts["charts"] = {}
            day_counter = 0

        curr += timedelta(days=1)

    if charts["charts"]:
        if last_written_date:
            charts["metadata"]["end_date"] = last_written_date
        write_to_json(charts, file_path)

def scrape_update(update_to, filename, save_interval=10, max_retries=4, base_delay=120, max_delay=600):
    file_path = f"data/{filename}"
    token = get_bearer_token()

    # Load existing data
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    metadata = data["metadata"]
    country = metadata["country"]

    latest_date_str = fetch_latest_date(token, country)
    update_to = min(update_to, datetime.strptime(latest_date_str, "%Y-%m-%d").date())

    top_n = metadata["top_n"]
    curr = datetime.strptime(metadata["end_date"], "%Y-%m-%d").date() + timedelta(days=1)

    if curr > update_to:
        print("Data already up to date.")
        return

    charts = {
        "metadata": {},
        "charts": {}
    }

    total_days = (update_to - curr).days + 1
    day_counter = 0
    last_written_date = None

    for _ in tqdm(range(total_days), desc=f"Updating {country}", unit="day"):
        curr_str = curr.strftime("%Y-%m-%d")

        for attempt in range(max_retries):
            try:
                charts["charts"][curr_str] = fetch_chart(curr_str, token, latest_date_str, country)[:top_n]
                last_written_date = curr_str
                break
            except UnauthorizedError:
                print("Unauthorized, fetching new token...")
                token = get_bearer_token()
            except TooManyRequestsError as e:
                delay = min(base_delay * (2 ** attempt), max_delay)
                print(f"{e} — retrying in {delay}s (attempt {attempt+1}/{max_retries})")
                time.sleep(delay)
        else:
            raise RuntimeError(f"Failed to fetch {curr_str} after {max_retries} attempts.")

        day_counter += 1

        if day_counter >= save_interval:
            if last_written_date:
                charts["metadata"]["end_date"] = last_written_date
            write_to_json(charts, file_path)
            charts["charts"] = {}
            day_counter = 0

        curr += timedelta(days=1)

    if charts["charts"]:
        if last_written_date:
            charts["metadata"]["end_date"] = last_written_date
        write_to_json(charts, file_path)