from wafl.exceptions import CloseConversation, InterruptTask


def close_conversation():
    raise CloseConversation


def close_task():
    raise InterruptTask
