from wafl.variables import get_variables
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="wafl",
    version=get_variables()["version"],
    url="http://github.com/fractalego/wafl",
    author="Alberto Cetoli",
    author_email="alberto@fractalego.io",
    description="A hybrid chatbot.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=[
        "wafl",
        "wafl.answerer",
        "wafl.connectors",
        "wafl.connectors.bridges",
        "wafl.connectors.factories",
        "wafl.connectors.remote",
        "wafl.events",
        "wafl.extractors",
        "wafl.inference",
        "wafl.interface",
        "wafl.knowledge",
        "wafl.listener",
        "wafl.logger",
        "wafl.parsing",
        "wafl.retriever",
        "wafl.runners",
        "wafl.scheduler",
        "wafl.simple_text_processing",
        "wafl.speaker",
    ],
    package_data={
        "wafl": [
            "templates/*",
            "sounds/*",
            "models/*",
            "frontend/*",
        ],
    },
    install_requires=[
        "flask[async]==2.0.1",
        "flask-cors==3.0.10",
        "flask_dropzone==1.6.0",
        "werkzeug==2.1.2",
        "nltk==3.6.2",
        "gensim==4.3.1",
        "sklearn==0.0",
        "python-Levenshtein==0.12.2",
        "wave==0.0.2",
        "fuzzywuzzy==0.18.0",
        "PyAudio==0.2.13",
        "pyctcdecode==0.2.1",
        "num2words==0.5.12",
        "word2number==1.1",
        "aiohttp==3.8.4",
        "einops==0.6.1",
        "g2p-en==2.1.0",
        "pyyaml==6.0.1",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        "console_scripts": ["wafl=wafl.command_line:main"],
    },
    include_package_data=True,
    zip_safe=False,
)
