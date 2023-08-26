from datetime import datetime, timedelta


def get_date():
    now = datetime.now()
    return now.strftime("%A %d %B %Y")


def get_time():
    now = datetime.now()
    minutes = int(now.strftime("%M"))
    hour = int(now.strftime("%H"))
    if minutes <= 30:
        return f"{minutes} past {hour}"

    else:
        return f"{60 - minutes} to {hour + 1}"
