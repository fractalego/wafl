Rules and backtracking
======================

An input that satisfies a trigger condition will make the most relevant rule go through the list of actions within.
However, if one of the actions fails then the next most relevant rule will be activated, and so on until there are
no more relevant rules.

For example, if there are two rules

.. code-block:: text

    The user is feeling well
        the user's name is John
        SAY Happy you are feeling well, John

    The user is feeling ok
        the user's name is Jane
        SAY Happy you are feeling well, Jane

and the user says: "My name is Jane and I am feeling well".
The first rule will be activated first, until the condition "the user's name is John" returns False.
Then the second rule will be activated because "feeling ok" is very similar to "feeling well".
The end result is that the bot will say "Happy you are feeling well, Jane"

The backtracking of rules applies recursively.
In the end, a rule returns True only if all its actions return True.
Otherwise, execution is truncated and the next relevant rule starts a new inference branch.

