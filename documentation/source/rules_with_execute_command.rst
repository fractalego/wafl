Rule with execute command
=========================

There are two special tags that can be used in the rules: <execute> and <memory>.
The <execute> tag is used to execute a python command on the host machine.

Some examples can be added to the rules to make the required output clearer to the bot.
Effectively, each rule is list of suggestions that go into the prompt for the language model.

Consider the following rule:

.. code-block:: yaml

  - the user wants to compute some math operation:
    - Think of the python code that solves the math problem and assigns the result to the variable "result"
    - For example "what is the result of 2 + 2?" should output "<execute>result = 2 + 2</execute>"
    - Another example "what is the square root of 2?" should output "<execute>import math;result = math.sqrt(2)</execute>"
    - output exactly the following "<execute>result = PYTHON CODE THAT SOLVES THE PROBLEM</execute>"


When requested to compute the square of pi, the rule above will be used to generate the following text:

.. code-block:: python

  <execute>import math;result = math.pi**2</execute>

However the user will not see this text.
Everything that is between the <execute> and </execute> tags will be executed as python code and substituted with the value of the variable "result".


Local functions
---------------

A list of Python functions can be specified within the file "functions.py".
These functions can be used in the rules to generate the desired output.

For example, the following rule will output the current date:

.. code-block:: yaml

  - the user wants to know today's date:
    - output "The date is <execute>get_date()</execute>".


As long as the function "get_date" is defined in the file "functions.py".

.. code-block:: python

  def get_date():
      return datetime.datetime.now().strftime("%Y-%m-%d")

In this case the bot will substitute the tag <execute>get_date()</execute> with the string output of the function "get_date()".