from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='wafl',
      version='0.0.1',
      url='http://github.com/fractalego/wafl',
      author='Alberto Cetoli',
      author_email='alberto@nlulite.com',
      description="A rule-based chatbot.",
      long_description=long_description,
      long_description_content_type="text/markdown",
      packages=['wafl',
                'wafl.conversation',
                'wafl.interface',
                'wafl.knowledge',
                'wafl.listener',
                'wafl.qa',
                'wafl.speaker',
                ],
      package_data={
          'wafl': ['templates/*'],
      },
      install_requires=[
          'flask == 2.0.1',
          'flask-cors == 3.0.10',
          'flask_dropzone == 1.6.0',
          'transformers == 4.9.2',
          'sentence_transformers == 2.0.0',
          'torch == 1.9.0',
          'nltk == 3.6.2',
          'gensim == 4.0.1',
          'sklearn == 0.0',
          'torchtext == 0.10.0',
          'spacy == 2.3.7',
          'gender_guesser == 0.4.0',
          'fact_checking == 0.0.3',
      ],
      classifiers=[
          'License :: OSI Approved :: MIT License',
      ],
      include_package_data=True,
      zip_safe=False)
