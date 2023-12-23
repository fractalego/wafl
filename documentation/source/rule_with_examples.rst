Rule with examples
==================

Some examples can be added to the rules to make the required output clearer to the bot.
Effectively, each rule is list of suggestions that go into the prompt for the language model.

Consider the following rule:

.. code-block:: yaml

  - the user wants to compute some math operation in Python:
    - Think of the python code that solves the math problem and assigns the result to the variable "result"
    - For example "what is the result of 2 + 2?" should output "result = 2 + 2"
    - Another example "what is the square root of 2?" should output "import math;result = math.sqrt(2)"
    - output exactly the following "PYTHON CODE THAT SOLVES THE PROBLEM"

When requested to compute the square of pi, the rule above will be used to generate the following code:

.. code-block:: python

  import math;result = math.pi**2


Notice that the format of the output is the same as the one specified in the rule.
