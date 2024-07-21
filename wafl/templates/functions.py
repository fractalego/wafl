import json
from datetime import datetime
from wafl.exceptions import CloseConversation

_db_filename = "db.json"


def close_conversation():
    raise CloseConversation()


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
