from wafl.answerer.arbiter_answerer import ArbiterAnswerer
from wafl.answerer.inference_answerer import InferenceAnswerer
from wafl.answerer.list_answerer import ListAnswerer
from wafl.answerer.simple_answerer import SimpleAnswerer
from wafl.events.narrator import Narrator
from wafl.inference.backward_inference import BackwardInference


def create_answerer(knowledge, interface, code_path, logger):
    narrator = Narrator(interface)
    return ListAnswerer(
        [
            SimpleAnswerer(knowledge, narrator, logger),
            InferenceAnswerer(
                interface,
                BackwardInference(
                    knowledge, interface, narrator, code_path, logger=logger
                ),
                logger,
            ),
            ArbiterAnswerer.create_answerer(knowledge, interface, code_path, logger),
        ],
        interface,
        logger,
    )
