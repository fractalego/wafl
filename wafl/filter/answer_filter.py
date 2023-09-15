from wafl.connectors.bridges.llm_answer_filter_bridge import AnswerFilterBridge


class AnswerFilter:
    def __init__(self, config):
        self._bridge = AnswerFilterBridge(config)
        self._max_num_past_utterances = 7

    async def filter(self, dialogue_list, query_text) -> str:
        dialogue = dialogue_list[
            -self._max_num_past_utterances :
        ]
        start_time = -1
        if dialogue:
            start_time = dialogue[0][0]

        dialogue_items = dialogue
        dialogue_items = sorted(dialogue_items, key=lambda x: x[0])
        dialogue_items = [item[1] for item in dialogue_items if item[0] >= start_time]
        dialogue_items = "\n".join(dialogue_items)
        answer_text = await self._bridge.get_answer(
            text="",
            dialogue=dialogue_items,
            query=query_text,
        )
        return answer_text
