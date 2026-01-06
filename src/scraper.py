from src.auth import get_bearer_token
from src.fetch import fetch_chart, UnauthorizedError, TooManyRequestsError

from datetime import timedelta
import time
import json
import os
from tqdm import tqdm
import random

def write_to_json(charts, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    if os.path.isfile(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    else:
        existing_data = {}

    existing_data.update(charts)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)

def scrape(country, start, end, top_n, filename, save_interval=10, max_retries=4, base_delay=120, max_delay=600):
    file_path = f"data/{filename}"
    
    if os.path.isfile(file_path):
        print(f"deleting existing file: {file_path}")
        os.remove(file_path)
    
    token = get_bearer_token()
    charts = {}
    day_counter = 0

    total_days = (end - start).days + 1

    curr = start
    for _ in tqdm(range(total_days), desc=f"Scraping {country}", unit="day"):
        curr_str = curr.strftime("%Y-%m-%d")

        for attempt in range(max_retries):
            try:
                charts[curr_str] = fetch_chart(curr_str, token, country)[:top_n]
                break  # success, exit retry loop
            except UnauthorizedError as e:
                print(e)
                print("Trying new token...")
                token = get_bearer_token()
            except TooManyRequestsError as e:
                delay = min(base_delay * (2 ** attempt), max_delay)
                print(f"{e} - retrying in {delay}s (attempt {attempt+1}/{max_retries})")
                time.sleep(delay)
        else:
            # If all retries failed
            raise RuntimeError(f"Failed to fetch {curr_str} after {max_retries} attempts.")

        day_counter += 1

        if day_counter >= save_interval:
            write_to_json(charts, file_path)
            charts = {}
            day_counter = 0

        curr += timedelta(days=1)
        #time.sleep(random.uniform(3, 6))
        time.sleep(3)

    if charts:
        write_to_json(charts, file_path)