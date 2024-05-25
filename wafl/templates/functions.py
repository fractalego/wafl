import json
import html2text
import re
import requests

from datetime import datetime, timedelta
from wafl.exceptions import CloseConversation

_db_filename = "db.json"


def close_conversation():
    raise CloseConversation()


def check_today_weather():
    today = datetime.now().strftime("%Y-%m-%d")
    with open(_db_filename) as file:
        db = json.load(file)
        latitude = db["latitude"]
        longitude = db["longitude"]

    return check_weather_lat_long(latitude, longitude, today)


def check_tomorrow_weather():
    today = datetime.now()
    with open(_db_filename) as file:
        db = json.load(file)
        latitude = db["latitude"]
        longitude = db["longitude"]

    tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    return check_weather_lat_long(latitude, longitude, tomorrow)


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
        return "There is a connection error to the weather API. Please try later. "
    to_say = ""
    for item in data["features"][0]["properties"]["timeSeries"]:
        if day in item["time"]:
            to_say += f"The temperature should be between {int(item['dayLowerBoundMaxTemp'])} and {int(item['dayUpperBoundMaxTemp'])}. "
            if item["dayProbabilityOfPrecipitation"] != 0:
                to_say += f"The probability of rain is {item['dayProbabilityOfPrecipitation']} percent. "

            else:
                to_say += "There is no probability of rain. "

            if item["dayProbabilityOfSnow"] != 0:
                to_say += f"The probability of snow is {item['dayProbabilityOfSnow']} percent. "

            else:
                to_say += "There is no probability of snow. "

    return to_say


def get_website(url):
    text = requests.get(url).content.decode("utf-8")
    h = html2text.HTML2Text()
    h.ignore_links = True
    return h.handle(text).strip()[:1000]


def get_guardian_headlines():
    url = "https://www.theguardian.com/uk"
    text = requests.get(url).content.decode("utf-8")
    pattern = re.compile(r"<h4 .*?><span>(.*?)</span></h4>", re.MULTILINE)
    matches = pattern.findall(text)
    text = "-" + "\n-".join(matches)
    h = html2text.HTML2Text()
    h.ignore_links = True
    return h.handle(text).strip()


def get_time():
    return datetime.now().strftime("%H,%M")


def get_date():
    return datetime.now().strftime("%Y-%m-%d")


def get_day():
    return datetime.now().strftime("%A")


def add_to_shopping_list(list_of_items_to_add):
    db = json.load(open(_db_filename))
    for item in list_of_items_to_add:
        if item not in db["shopping_list"]:
            db["shopping_list"].append(item)

    json.dump(db, open(_db_filename, "w"))

    return "Item added"


def remove_from_shopping_list(list_of_items_to_remove):
    db = json.load(open(_db_filename))
    for item in list_of_items_to_remove:
        if item in db["shopping_list"]:
            db["shopping_list"].remove(item)

    json.dump(db, open(_db_filename, "w"))

    return "Item removed"


def get_shopping_list():
    db = json.load(open(_db_filename))
    if db["shopping_list"] == []:
        return "nothing"

    return ", ".join(db["shopping_list"])


def write_to_file(filename, text):
    with open(filename, "w") as file:
        file.write(text)

    return f"File {filename} saved"
