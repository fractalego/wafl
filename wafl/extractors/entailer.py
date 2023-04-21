from typing import Dict, Union
from wafl.connectors.entailment_connector import EntailmentConnector


class Entailer:
    def __init__(self, logger=None):
        self._logger = logger
        self._connector = EntailmentConnector()

    async def get_relation(self, premise: str, hypothesis: str) -> Dict[str, float]:
        return await self._connector.predict(premise, hypothesis)

    async def entails(
        self,
        premise: str,
        hypothesis: str,
        threshold=0.75,
        contradiction_threshold=0.65,
        return_threshold=False,
    ) -> Union[str, float]:
        if self._logger:
            self._logger.write("Starting entailment procedure.")

        prediction = await self.get_relation(premise, hypothesis)
        if prediction["entailment"] > threshold:
            if self._logger:
                self._logger.write(f"Entailment: The premise is {premise}")
                self._logger.write(f"Entailment: The hypothesis is {hypothesis}")
                self._logger.write(f"Entailment: The results are {str(prediction)}")

            if return_threshold:
                return prediction["entailment"]

            return "True"

        if prediction["contradiction"] < contradiction_threshold:
            premise = self._add_presuppositions_to_premise(premise)
            prediction = await self.get_relation(premise, hypothesis)

        if self._logger:
            self._logger.write(f"Entailment: The premise is {premise}")
            self._logger.write(f"Entailment: The hypothesis is {hypothesis}")
            self._logger.write(f"Entailment: The results are {str(prediction)}")

        if prediction["entailment"] > threshold:
            if return_threshold:
                return prediction["entailment"]

            return "True"

        if return_threshold:
            return 0

        if prediction["neutral"] > threshold:
            return "Unknown"

        return "False"

    async def is_neutral(
        self,
        premise: str,
        hypothesis: str,
        threshold=0.75,
    ) -> Union[str, float]:
        if self._logger:
            self._logger.write("Starting entailment neutral check.")

        prediction = await self.get_relation(premise, hypothesis)
        if prediction["neutral"] > threshold:
            if self._logger:
                self._logger.write(f"Entailment: The premise is {premise}")
                self._logger.write(f"Entailment: The hypothesis is {hypothesis}")
                self._logger.write(f"Entailment: The results are {str(prediction)}")

            return True

        if self._logger:
            self._logger.write(f"Entailment: The premise is {premise}")
            self._logger.write(f"Entailment: The hypothesis is {hypothesis}")
            self._logger.write(f"Entailment: The results are {str(prediction)}")

        if prediction["neutral"] > threshold:
            return True

        return False

    def _add_presuppositions_to_premise(self, premise):
        premise = premise.replace("user says:", "user says to this bot:")
        premise = premise.replace("user asks:", "user asks to this bot:")
        return premise
