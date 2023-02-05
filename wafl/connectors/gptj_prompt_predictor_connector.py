from wafl.connectors.base_gptj_connector import BaseGPTJConnector


class GPTJPromptPredictorConnector(BaseGPTJConnector):
    def __init__(self, config=None):
        super().__init__(config)
