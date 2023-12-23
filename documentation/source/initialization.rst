Initialization
--------------

This command initialises WAFL's work environment

.. code-block:: bash

    $ wafl init

It creates a set of files that can be used to the interface side of WAFL.

.. code-block:: bash

    $ ls
    config.json
    db.json
    functions.py
    main.py
    requirements.txt
    rules.yaml
    secrets.json
    start_llm.sh
    testcases.txt

- the `config.json` file contains some parameters for the chatbot and the url to connect to for the backend.

- the `db.json` file is an auxiliary file that contains some information about the chatbot's state.
  It is a json file that can be edited manually.

- The `functions.py` file contains the functions that can be used in the `rules.yaml` file.

- `main.py` is an auxiliary script that can be used to start a webserver locally to test the chatbot.

- The `requirements.txt` file contains the python packages needed to run the functions in `functions.py`.

- The `rules.yaml` file contains the facts and rules used to guide the conversation with the chatbot.

- The `secrets.json` may contain credentials that are needed to run the the functions in `functions.py`.

- `start_llm.sh` is a script that starts the LLM locally.
  It simply starts a docker container with the LLM image.

- The `testcases.txt` file contains the test cases that can be used to test the LLM.
