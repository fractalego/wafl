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
        "wafl.connectors.clients",
        "wafl.connectors.factories",
        "wafl.connectors.remote",
        "wafl.data_objects",
        "wafl.events",
        "wafl.handlers",
        "wafl.inference",
        "wafl.interface",
        "wafl.knowledge",
        "wafl.listener",
        "wafl.logger",
        "wafl.parsing",
        "wafl.readers",
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
        "flask[async]==3.0.3",
        "flask-cors==4.0.1",
        "nltk==3.8.1",
        "sklearn==0.0",
        "python-Levenshtein==0.25.1",
        "fuzzywuzzy==0.18.0",
        "PyAudio==0.2.14",
        "num2words==0.5.13",
        "word2number==1.1",
        "aiohttp==3.9.5",
        "werkzeug==3.0.3",
        "sphinx==7.4.6",
        "sphinx-rtd-theme==2.0.0",
        "g2p-en==2.1.0",
        "pyyaml==6.0.1",
        "joblib==1.4.2",
        "pymupdf==1.24.7",
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
