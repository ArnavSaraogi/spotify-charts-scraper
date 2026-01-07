# spotify-charts-scraper

## Overview
This project scrapes Spotify Charts for Spotify's Daily Top Songs in all their supported regions. The scraper creates a JSON file with chart data from Spotify's internal API for each day specified. Attached in releases, there's a [dataset](https://github.com/ArnavSaraogi/spotify-charts-scraper/releases/tag/spotify_dataset) of the top 20 streamed songs in the US on Spotify for each day from January 1, 2017 to January 5, 2026, scraped from Spotify's internal API.

## Usage
### Download and Setup
Make sure you have a Spotify account, and that Python 3.7+ is installed.

Paste the commands line by line into terminal:

1. Clone the repository
```bash
git clone https://github.com/ArnavSaraogi/spotify-charts-scraper.git
cd spotify-charts-scraper
```

2. Set up virtual environment and install requirements
```bash
python3 -m venv venv
source venv/bin/activate # on Windows, the command is venv\Scripts\activate
```

3. Install requirements
```bash
pip install -r requirements.txt
```

### Running the Scraper
Open `config.py` in the directory and adjust the fields as desired. The fields are:
* **country**: The name (not the 2-letter abbreviation) of the country (or "Global") that you want data for. You can see what countries are available in countries.py.
* **start_date**: The date the script will start scraping from, in YYYY-MM-DD format. Charts for Daily Songs are available from 2017-01-01.
* **end_date**: The date the script will stop scraping after. It can be entered in YYYY-MM-DD format or as "today".
* **top_n**: The n top songs that will be retrieved. For example, 20 will give you the top 20 songs each day.
* **filename**: The name of the file that will be saved. Must end in .json.
* **update**: Set to `True` to add new data to an existing file, or `False` to create a new file from scratch.
  - When `True`: Ignores country, start_date, end_date, and top_n (uses existing file's settings)
  - When `False`: Ignores update_to
* **update_to**: The end date for updates (YYYY-MM-DD or "today"). Only used when update is `True`.

With your virtual environment activated, run:
```bash
python -m main
```

The first time you do this, the script will open a window through which you have to log in to your Spotify account. When logging in, log in to Spotify directly by entering your email; *do not* log in with Google (it won't let you). Once you're logged in, the window will close and the script will run. The cookies from the login will also be saved in cookies.json, so the login process won't be required again until the cookies expire.

Note that your computer should not sleep when running the script, as this would interrupt the scraping process. 

## Data Format
The JSON file contains metadata (country, start date, end date, and top_n) about the charts, which is used for the update functionality. The Spotify API data from each day is under "charts". Some of the fields include:
- Song name
- Artist name
- Stream count
- Current rank
- Previous rank
- Peak rank
- Labels

**Example JSON**:
```json
{
  "metadata": {
    "country": "us",
    "start_date": "2017-01-01",
    "end_date": "2026-01-05",
    "top_n": 20
  },
  "charts": {
    "2017-01-01": [
      {
        "chartEntryData": {
          "currentRank": 1,
          "previousRank": -1,
          "peakRank": 1,
          "peakDate": "2017-01-01",
          "appearancesOnChart": 1,
          "consecutiveAppearancesOnChart": 1,
          "rankingMetric": {
            "value": "1371493",
            "type": "STREAMS"
          },
          "entryStatus": "NEW_ENTRY",
          "entryRank": 1,
          "entryDate": "2017-01-01"
        },
        "missingRequiredFields": false,
        "trackMetadata": {
          "trackName": "Bad and Boujee (feat. Lil Uzi Vert)",
          "trackUri": "spotify:track:4Km5HrUvYTaSUfiSGPJeQR",
          "displayImageUri": "https://i.scdn.co/image/ab67616d00001e026275aeac316378b0dd4f31fd",
          "artists": [
            {
              "name": "Migos",
              "spotifyUri": "spotify:artist:6oMuImdp5ZcFhWP0ESe6mG",
              "externalUrl": ""
            },
            {
              "name": "Lil Uzi Vert",
              "spotifyUri": "spotify:artist:4O15NlyKLIASxsJ0PrXPfz",
              "externalUrl": ""
            }
          ],
          "producers": [],
          "labels": [
            {
              "name": "Quality Control Music",
              "spotifyUri": "",
              "externalUrl": ""
            }
          ],
          "songWriters": [],
          "releaseDate": "2017-01-27"
        }
      }
    ]
  }
}
```

## Notes
* The scraper is very slow (~4 hours for 9 years of data) as Spotify is extremely strict with rate limiting. It is possible to scrape 41 days with a 1 second delay between fetches and 91 days with a 3 second delay before being rate limited. You can adjust the sleep time in `fetch.py`. 
* When rate limiting occurs, the script uses exponential backoff, starting with 2 minutes, for making requests. It is capped at a backoff of 6 minutes and makes a maximum of 4 attempts. 
* Spotify's internal API endpoint requires authorization via a Bearer token, which makes it necessary to log in to Spotify so that the Bearer token could be scraped and used.
* It is possible the Bearer token expires during the scraping process. This is supported by automatically retrieving a new Bearer token with the cached cookie information.
* The JSON file is written to every 10 days, so in case the script fails midway it isn't necessary to start over.