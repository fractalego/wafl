Initialization
--------------

This command initialises WAFL's work environment

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
      "allow_interruptions": true,
      "waking_up_word": "computer",
      "waking_up_sound": true,
      "deactivate_sound": true,
      "improvise_tasks": true,
      ...
    }

These settings regulate the following:

    * The "allow_interruptions" allows the user to create rules with the highest priority.
      For example, the user might want a rule to be triggered in the middle of a conversation.

    * "waking_up_word" is the name of the bot, used to wake up the system in the "run-audio" mode.

    * "waking_up_sound" and "deactivate_sound" are played to signal the system is up or is back to idle.

    * "improvise_tasks" allows the system to create its own rules to accomplish a goal.


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
