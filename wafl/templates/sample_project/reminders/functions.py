from datetime import datetime, timedelta
from word2number import w2n


def get_integer_from_string(text):
    words = text.split()
    for word in words:
        number = w2n.word_to_num(word)
        if number is not None:
            return number

    return None


def get_time_in_future(minutes_from_now):
    num_minutes = get_integer_from_string(minutes_from_now)
    if not num_minutes:
        return False

    now = datetime.now()
    final_time = now + timedelta(minutes=num_minutes)
    return final_time.strftime("%H, %M")
