import logging

from fuzzywuzzy import process
from datetime import datetime
from wafl.exceptions import CloseConversation, InterruptTask

_logger = logging.getLogger(__file__)

shopping_list = []


def dummy_add_email(email):
    logging.info("The email is " + email)
    return "fake_newsletter"


def dummy_log_email(email):
    logging.info("The email is " + email)


def get_shopping_list_in_english():
    return ", ".join(sorted(list(set(shopping_list))))


def get_time():
    now = datetime.now()
    return now.strftime("%H, %M")


def equal(lhs, rhs):
    return lhs == rhs


def reset_shopping_list():
    global shopping_list
    shopping_list = []


def append_until_user_is_done():
    while {"% does the user want to add more items %"}:
        item = {"% what does the user want to add %"}
        shopping_list.append(item)


def say_text(text):
    {f"% SAY {text} %"}


def say_twice():
    index = 0
    utterances = ["HELLO", "HELLO"]
    while index < len(utterances):
        {f"% SAY Please say: '{utterances[index]}' %"}

        {"% SAY Your input is recorded %"}

        index += 1


def close_conversation():
    raise CloseConversation()


def close_task():
    raise InterruptTask()


def normalize_name(linename):
    return "victoria"


lines_dict = {
    "overground": "overground",
    "circle": "tube",
    "northern": "tube",
    "jubilee": "tube",
    "victoria": "tube",
    "dlr": "dlr",
}


def check_tfl_line(linename):
    {f"% SAY The {linename} line is running normally %"}


def remove_from_shopping_list(item):
    if not shopping_list:
        return False

    extracted, score = process.extract(item, shopping_list, limit=1)[0]
    if score < 60:
        {f"% SAY I did not quite get the item to remove %"}
        return

    if not {f"% Do you want to remove {extracted} from the shopping list? %"}:
        return False

    shopping_list.remove(extracted)


def add_shopping_list(item):
    shopping_list.append(item)


def add_shopping_list_as_function(item):
    shopping_list.append(item)
    while {"% Do you want to add anything else  %"}:
        item = {"% What do you want to add?%"}
        shopping_list.append(item)
        {f"% SAY {item} has been added to the shopping list%"}
        {"%ERASE MEMORY%"}
