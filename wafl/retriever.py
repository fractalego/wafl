import json
import os
import torch
import logging

from gensim.models import KeyedVectors
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

_path = os.path.dirname(__file__)
_logger = logging.getLogger(__file__)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
sentence_model = SentenceTransformer('msmarco-distilbert-base-v3')
sentence_model = sentence_model.to(device)


def get_embeddings_from_text(text):
    outputs = sentence_model.encode(text)
    return outputs


def get_embeddings_from_dialogue_and_query(dialogue, query):
    dialogue_embeddings = get_embeddings_from_text(dialogue)
    query_embeddings = get_embeddings_from_text(query)
    return (query_embeddings + 0.01 * dialogue_embeddings) / 1.01


def get_documents_and_scores(dialogue, query):
    try:
        chapter_embeddings = KeyedVectors.load(os.path.join(_path, '../cache/embeddings.gensim'))
    except EOFError:
        raise RuntimeError("No file has been loaded")
    embeddings = get_embeddings_from_dialogue_and_query(dialogue, query)
    results = chapter_embeddings.similar_by_vector(embeddings, topn=2)
    return results


def update_chapters_embeddings():
    chapter_embeddings = KeyedVectors(768)

    file_paths = json.load(open(os.path.join(_path, '../cache/files.json')))
    for filename in file_paths:
        _logger.info(f'Reading {filename}.')
        text = open(filename, encoding='utf-8').read()
        chapters = get_chapters_from_text(text)
        for chapter in tqdm(chapters):
            if len(chapter.split()) < 10:
                continue
            chapter = ' '.join(chapter.split()[:256])
            embeddings = get_embeddings_from_text(chapter)
            chapter_embeddings.add_vector(chapter, embeddings)
        _logger.info(f'Finished reading {filename}.')

    chapter_embeddings.save(os.path.join(_path, '../cache/embeddings.gensim'))


def reset_embeddings():
    chapter_embeddings = KeyedVectors(768)
    chapter_embeddings.save(os.path.join(_path, '../cache/embeddings.gensim'))


def reset_files():
    with open(os.path.join(_path, '../cache/files.json'), 'w') as file:
        file.write('[]')
