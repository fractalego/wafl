import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from typing import Dict

_device = "cuda" if torch.cuda.is_available() else "cpu"


class LocalWhisperConnector:
    _max_tries = 3

    def __init__(self, config):
        model_name = config["local_model"]
        global model, processor
        self.model = WhisperForConditionalGeneration.from_pretrained(model_name)
        self.model.to(_device)
        self.processor = WhisperProcessor.from_pretrained(model_name)
        self._starting_tokens = self.processor.tokenizer.convert_tokens_to_ids(
            ["<|startoftranscript|>", "<|notimestamps|>"]
        )
        self._ending_tokens = self.processor.tokenizer.convert_tokens_to_ids(
            ["<|endoftext|>"]
        )

    async def predict(self, waveform, hotword=None) -> Dict[str, float]:
        num_beams = 3
        num_tokens = 15
        input_features = self.processor(
            audio=waveform, return_tensors="pt", sampling_rate=16_000
        ).input_features
        hotword_tokens = None
        if hotword:
            hotword_tokens = torch.tensor(
                [
                    item
                    for item in self.processor.tokenizer.encode(f" {hotword}")
                    if item not in set(self._ending_tokens + self._starting_tokens)
                ],
                dtype=torch.int,
            ).unsqueeze(0)

        output = self.model.generate(
            input_features.to(_device),
            num_beams=num_beams,
            return_dict_in_generate=True,
            output_scores=True,
            max_length=num_tokens,
        )
        transcription = self.processor.batch_decode(
            output.sequences, skip_special_tokens=True
        )[0]
        score = output.sequences_scores
        logp = None
        if hotword_tokens is not None:
            logp = self.compute_logp(hotword_tokens, input_features)

        return {
            "transcription": transcription,
            "score": score,
            "logp": logp,
        }

    def compute_logp(self, hotword_tokens, input_features):
        input_ids = torch.tensor([self._starting_tokens]).cuda()
        for _ in range(hotword_tokens.shape[1]):
            logits = self.model(
                input_features.to(_device),
                decoder_input_ids=input_ids,
            ).logits
            new_token = torch.argmax(logits, dim=-1)
            new_token = torch.tensor([[new_token[:, -1]]]).cuda()
            input_ids = torch.cat([input_ids, new_token], dim=-1)

        logprobs = torch.log(torch.softmax(logits, dim=-1))
        sum_logp = 0
        for logp, index in zip(logprobs[0][1:], hotword_tokens):
            sum_logp += logp[int(index)]

        return sum_logp
