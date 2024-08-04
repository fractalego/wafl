from wafl.connectors.clients.entailer_client import EntailerClient


class Entailer:
    def __init__(self, config):
        self.entailer_client = EntailerClient(config)
        self._config = config

    async def left_entails_right(self, lhs: str, rhs: str) -> bool:
        prediction = await self.entailer_client.get_entailment_score(lhs, rhs)
        return prediction > 0.5

    async def get_score(self, lhs: str, rhs: str) -> float:
        return await self.entailer_client.get_entailment_score(lhs, rhs)
