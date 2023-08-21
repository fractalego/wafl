import csv
import os
import joblib

from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

_path = os.path.dirname(__file__)


async def load_knowledge_from_file(filename, config):
    items_list = []
    with open(os.path.join(_path, "../../data/", filename + ".csv")) as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            items_list.append(row[0].strip())

    knowledge = await SingleFileKnowledge.create_from_list(items_list, config)
    joblib.dump(knowledge, os.path.join(_path, f"../../data/{filename}.knowledge"))
    return knowledge
