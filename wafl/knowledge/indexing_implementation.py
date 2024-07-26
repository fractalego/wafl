import asyncio
import os
import joblib
import yaml
import threading
from tqdm import tqdm

from wafl.config import Configuration
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from wafl.readers.reader_factory import ReaderFactory


async def add_file_to_knowledge(knowledge, filename):
    reader = ReaderFactory.get_reader(filename)
    for chunk in reader.get_chunks(filename):
        await knowledge.add_fact(chunk)


async def _add_indices_to_knowledge(knowledge, text):
    indices = yaml.safe_load(text)
    if "paths" not in indices or not indices["paths"]:
        return knowledge

    for path in indices["paths"]:
        print(f"Indexing path: {path}")
        file_count = sum(len(files) for _, _, files in os.walk(path))
        with tqdm(total=file_count) as pbar:
            for root, _, files in os.walk(path):
                threads = []
                for file in files:
                    threads.append(
                        threading.Thread(
                            target=asyncio.run,
                            args=(
                                add_file_to_knowledge(
                                    knowledge, os.path.join(root, file)
                                ),
                            ),
                        )
                    )
                num_threads = min(10, len(threads))
                for i in range(0, len(threads), num_threads):
                    for thread in threads[i : i + num_threads]:
                        thread.start()
                    for thread in threads[i : i + num_threads]:
                        thread.join()
                    pbar.update(num_threads)

    return knowledge


async def load_knowledge(config, logger=None):
    if ".yaml" in config.get_value("rules") and not any(
        item in config.get_value("rules") for item in [" ", "\n"]
    ):
        rules_filename = config.get_value("rules")
        with open(config.get_value("rules")) as file:
            rules_txt = file.read()

    else:
        rules_filename = None
        rules_txt = config.get_value("rules")

    index_filename = config.get_value("index")
    if not os.path.exists(index_filename):
        raise RuntimeError(f"Index file {index_filename} does not exist.")
    with open(index_filename) as file:
        index_txt = file.read()

    cache_filename = config.get_value("cache_filename")
    if os.path.exists(cache_filename):
        if (
            rules_filename
            and os.path.getmtime(cache_filename) > os.path.getmtime(rules_filename)
            and os.path.getmtime(cache_filename) > os.path.getmtime(index_filename)
        ):
            knowledge = joblib.load(cache_filename)
            return knowledge

    knowledge = SingleFileKnowledge(config, rules_txt, logger=logger)
    knowledge = await _add_indices_to_knowledge(knowledge, index_txt)
    await knowledge.initialize_retrievers()
    joblib.dump(knowledge, config.get_value("cache_filename"))
    return knowledge


def add_to_index(path):
    config = Configuration.load_local_config()
    index_filename = config.get_value("index")
    with open(index_filename) as file:
        indices = yaml.safe_load(file.read())
        if path in indices["paths"]:
            return

        indices["paths"].append(path)

    with open(index_filename, "w") as file:
        yaml.dump(indices, file)
