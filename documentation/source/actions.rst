Running Actions
===============

It is possible to run actions from the command line.
This is useful to carry out conversational tasks as command line scripts or cron jobs.

To run an action from the command line, use the following command:

.. code-block:: bash

    $ wafl run-action <action-name>

For example, to run the ``hello-world`` action, use the following command:

.. code-block:: bash

    $ wafl run-action hello-world


The ``run-action`` command will look in to the file actions.yaml.
A typical actions.yaml file looks like this:

.. code-block:: yaml

    hello-world:
      -
        action: say "hello world"
        expected: the bot outputs a greeting
      -
        action: say "hello world" again
        expected: the bot outputs another greeting


Each action is a list of steps.
Each step is a dictionary with two keys: ``action`` and ``expected``.
The ``action`` key is the action to be executed.
The ``expected`` key is the expected response from the bot.
If the bot does not respond as expected, the action will run again until it is successful for a maximum of 10 times.

The ``run-action`` command will run the action and print the result to the console.
Each action will call rules and functions as in a normal conversation.

