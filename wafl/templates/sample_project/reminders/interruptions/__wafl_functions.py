from wafl.exceptions import CloseConversation, InterruptTask


def close_conversation(inference, task_memory):
    raise CloseConversation


def close_task(inference, task_memory):
    raise InterruptTask
