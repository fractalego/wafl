Running wafl init
-----------------

What does this command do?

.. code-block:: bash

    $ wafl init

It creates a set of files that can be used to the interface side of WAFL.

.. code-block:: bash

    $ ls
    config.json
    events.py
    functions.py
    rules.wafl
    start_llm.sh
    testcases.txt

- The `config.json` file contains the configuration.

.. code-block:: text

    {
      "allow_interruptions": true,                  # interruptions are allowed in the conversation
      "waking_up_word": "computer",                 # the word that wakes up the LLM and the name of the chatbot
      "waking_up_sound": true,                      # A sound is generated when the LLM is woken up
      "deactivate_sound": true,                     # A sound is generated when the LLM is woken up
      "listener_model": "openai/whisper-tiny.en",   # The model used for speech recognition.
                                                    # Only whisper models are supported
      "listener_hotword_logp": -8,                  # The threshold log probability of the hotword
      "listener_volume_threshold": 0.6,             # The threshold volume when listening
      "listener_silence_timeout": 0.7,              # The silence timeout when listening
      "model_host": "127.0.0.1",                    # The host of the LLM
      "model_port": 8080                            # The port of the LLM
    }


- The rules.wafl file contains the rules that guide the chatbot.
The rules are written in the WAFL language, with a trigger condition on top and a list of actions below.

.. code-block:: text

    The user says "bring yourself online"
      SAY Hello there!

This rule is activated when the user says "bring yourself online", and the action is for the machine to say "Hello there!".


- The `functions.py` file contains the functions that can be used in the `rules.wafl` file.

- The `events.py` file contains the event generation functions.
  For example, there is a function that returns the time and one that returns the data.
  These functions are executed every minute and may be used to activate one of the rules.

- `start_llm.sh` is a script that starts the LLM locally.
  It simply starts a docker container with the LLM image.

- The `testcases.txt` file contains the test cases that can be used to test the LLM.