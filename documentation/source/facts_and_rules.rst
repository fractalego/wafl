The rules.yaml file
===================

The language model can be guided through a list of rules and facts that are retrieved during the conversation.

This file is written in YAML format as in the following:

.. code-block:: yaml

    facts:
      - This bot is doing well
      - This bot is called Computer

    rules:
      - the user wants to know the time:
        - output "The time is <execute>get_time()</execute>".


Facts
-----
These are simple facts that are retrieved during the conversation.
For examples, if the user asks "How are you?", the bot will retrieve "this bot is doing well" and add it to its prompt,
eventually generating an answer like "I am fine" or "I am doing well".

Rules
-----

Rules are composed of a condition and a list of actions.
The condition is a simple trigger that is matched against the user input.
In the example above, the condition is "the user wants to know the time".
The condition is matched against the user input, and if it matches, the whole rule is added to the prompt of the language model.

The actions are a set of items that the bot will execute in order.
In the example above, the bot should output "The time is <execute>get_time()</execute>" if it thinks that the user wants to know the time.

