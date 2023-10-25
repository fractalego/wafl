from wafl.connectors.bridges.llm_answer_filter_bridge import AnswerFilterBridge


class AnswerFilter:
    def __init__(self, config):
        self._bridge = AnswerFilterBridge(config)
        self._max_num_past_utterances = 7

    async def filter(self, dialogue_list, query_text) -> str:
        return query_text
