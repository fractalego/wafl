Creating a testcase
===================

The file testcases.txt contains a list of testcases.
Each testcase consists of a title and a list of utterances.

.. code-block:: bash

    test the greetings work
     user: Hello
     bot: Hello there! What is your name
     user: Bob
     bot: Nice to meet you, bob!


The title is used to name the testcase.
Each line starting with "user:" is an utterance from the user.
Conversely, each line starting with "bot:" is an utterance from the bot.
The test passes if the bot responds with the utterance from the bot in a way that is consistent with the
answers in the testcase.
The test fails if the bot responds with an utterance that is not in the testcase.


Running the testcases
---------------------

To run the testcases, run the following command:

.. code-block:: bash

    $ wafl run-tests

This will run all the testcases in the testcases.txt file.


Negative testcases
------------------

Negative testcases are testcases that are expected to fail.
They are useful to test that the bot does not respond in a certain way.
Negative testcases are prefixed with "!".

.. code-block:: bash

    ! test the greetings uses the correct name
      user: Hello
      bot: Hello there! What is your name
      user: Bob
      bot: Nice to meet you, unknown!