from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="wafl",
    version="0.0.1",
    url="http://github.com/fractalego/wafl",
    author="Alberto Cetoli",
    author_email="alberto@fractalego.io",
    description="A hybrid chatbot.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=[
        "wafl",
        "wafl.conversation",
        "wafl.inference",
        "wafl.interface",
        "wafl.knowledge",
        "wafl.listener",
        "wafl.parsing",
        "wafl.qa",
        "wafl.speaker",
        "wafl.retriever",
    ],
    package_data={
        "wafl": ["templates/*", "sounds/*", "models/*"],
    },
    install_requires=[
        "flask==2.0.1",
        "flask-cors==3.0.10",
        "flask_dropzone==1.6.0",
        "transformers==4.9.2",
        "sentence_transformers==2.0.0",
        "torch==1.12.1",
        "nltk==3.6.2",
        "gensim==4.0.1",
        "sklearn==0.0",
        "spacy==2.3.7",
        "gender_guesser==0.4.0",
        "fact_checking==0.0.3",
        "python-Levenshtein==0.12.2",
        "wave==0.0.2",
        "conversation-qa==0.0.10",
        "creak-sense==0.0.4",
        "protobuf==4.21.5",
        "fairseq==0.12.2",
        "g2p_en==2.1.0",
    ],
    dependency_links=[
        "git+ssh://git@github.com/kpu/kenlm/archive/master.zip",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
    ],
    include_package_data=True,
    zip_safe=False,
)
