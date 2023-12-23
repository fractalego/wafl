Simple rule
===========

This is a simple rule that shows how the rule engine works.

.. code-block:: yaml

  - the user says "hello":
    - the bot reply "Howdy"

The rule engine will match the user input with the rule and execute the actions.
In this case the user input must be similar to "hello" and the bot will reply "Howdy" to that.

A rule can have multiple actions, for example:

.. code-block:: yaml

  - the user says "hello":
    - the bot reply "Howdy"
    - the bot reply "How are you?"

The rule engine will execute all the actions in order.

