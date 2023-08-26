import json
import requests

from datetime import datetime, timedelta

# These are the coordinate of central London. Please change at your convenience
latitude = "51.5074"
longitude = "0.1272"


def check_today_weather():
    today = datetime.now().strftime("%Y-%m-%d")
    check_weather_lat_long(latitude, longitude, today)


def check_tomorrow_weather():
    today = datetime.now()
    tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    check_weather_lat_long(latitude, longitude, tomorrow)


def check_weather_lat_long(latitude, longitude, day):
    secrets = json.load(open("secrets.json"))
    result = requests.get(
        f"https://rgw.5878-e94b1c46.eu-gb.apiconnect.appdomain.cloud/metoffice/production/v0/forecasts/point/daily?excludeParameterMetadata=true&includeLocationName=true&latitude={latitude}&longitude={longitude}",
        headers={
            "X-IBM-Client-Id": secrets["key"],
            "X-IBM-Client-Secret": secrets["secret"],
        },
    )
    data = result.json()
    if "features" not in data:
        "% SAY There is a connection error to the weather API. Please try later. %"
        return False

    for item in data["features"][0]["properties"]["timeSeries"]:
        if day in item["time"]:
            f"% SAY The temperature should be between {int(item['dayLowerBoundMaxTemp'])} and {int(item['dayUpperBoundMaxTemp'])}. %"
            if item["dayProbabilityOfPrecipitation"] != 0:
                f"% SAY The probability of rain is {item['dayProbabilityOfPrecipitation']} percent. %"

            if item["dayProbabilityOfSnow"] != 0:
                f"% SAY The probability of snow is {item['dayProbabilityOfSnow']} percent. %"
