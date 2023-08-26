from wafl.exceptions import CloseConversation, InterruptTask


async def close_conversation(inference, policy, task_memory):
    raise CloseConversation


async def close_task(inference, policy, task_memory):
    raise InterruptTask
