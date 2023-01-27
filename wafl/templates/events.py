from datetime import datetime


def get_date():
    now = datetime.now()
    return "Today's date is " + now.strftime("%A %d %B %Y")


def get_clock():
    now = datetime.now()
    minutes = int(now.strftime("%M"))
    hour = int(now.strftime("%H"))
    return f"The time is {hour}, {minutes} "


def get_time_in_natural_language():
    now = datetime.now()
    minutes = int(now.strftime("%M"))
    hour = int(now.strftime("%H"))
    if minutes <= 30:
        return f"The time is {minutes} past {hour}"

    else:
        return f"The time is {60 - minutes} to {hour + 1}"
