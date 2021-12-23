import logging

_logger = logging.getLogger(__file__)

shopping_list = []


def dummy_add_email(email):
    logging.info("The email is " + email)
    return "fake_newsletter"


def dummy_log_email(email):
    logging.info("The email is " + email)


def get_shopping_list_in_english():
    return ", ".join(list(set(shopping_list)))
