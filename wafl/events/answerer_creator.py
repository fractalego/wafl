from wafl.answerer.arbiter_answerer import ArbiterAnswerer
from wafl.answerer.inference_answerer import InferenceAnswerer
from wafl.answerer.list_answerer import ListAnswerer
from wafl.events.narrator import Narrator
from wafl.inference.backward_inference import BackwardInference


def create_answerer(knowledge, interface, code_path, logger):
    narrator = Narrator(interface)
    return ListAnswerer(
        [
            ArbiterAnswerer.create_answerer(knowledge, interface, code_path, logger),
            InferenceAnswerer(
                interface,
                BackwardInference(
                    knowledge, interface, narrator, code_path, logger=logger
                ),
                logger,
            ),
        ],
        interface,
        logger,
    )
