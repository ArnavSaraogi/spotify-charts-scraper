import requests
import time

class UnauthorizedError(Exception):
    pass

class NotFoundError(Exception):
    pass

class TooManyRequestsError(Exception):
    pass

BASE_URL = "https://charts-spotify-com-service.spotify.com/auth/v0/charts"
SLEEP_TIME = 3

HEADERS_TEMPLATE = {
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "App-Platform": "Browser",
    "Spotify-App-Version": "1.2.45.454.g8d123abc",  # realistic-looking
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}

def fetch_chart(date_str, token, latest_date_str, region="us"):
    headers = HEADERS_TEMPLATE | {
        "Authorization": f"Bearer {token}"
    }
    
    if date_str == latest_date_str:
        url = f"{BASE_URL}/regional-{region}-daily/latest"
    else:
        url = f"{BASE_URL}/regional-{region}-daily/{date_str}"

    r = requests.get(url, headers=headers, timeout=15)

    if r.status_code == 401:
        raise UnauthorizedError("401: Unauthorized")

    if r.status_code == 404:
        raise NotFoundError(f"404: {url} Not Found")

    if r.status_code == 429:
        raise TooManyRequestsError("429: Too Many Requests")

    r.raise_for_status()

    time.sleep(SLEEP_TIME)
    return r.json()["entries"]

def fetch_latest_date(token, region="us"):
    headers = HEADERS_TEMPLATE | {
        "Authorization": f"Bearer {token}"
    }

    url = f"{BASE_URL}/regional-{region}-daily/latest"
    r = requests.get(url, headers=headers, timeout=15)

    if r.status_code == 401:
        raise UnauthorizedError("401: Unauthorized")

    if r.status_code == 404:
        raise NotFoundError(f"404: {url} Not Found")

    if r.status_code == 429:
        raise TooManyRequestsError("429: Too Many Requests")

    r.raise_for_status()

    time.sleep(SLEEP_TIME)
    return r.json()["displayChart"]["date"]