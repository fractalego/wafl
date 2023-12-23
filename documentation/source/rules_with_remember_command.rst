Rule with remember command
==========================

There are two special tags that can be used in the rules: <execute> and <remember>.
The <remember> tag is used to remember an intermediate result that can be used to generate the final output.

Consider the following rule:

.. code-block:: yaml

  - the user wants to summarise a website:
      - you'll need the website url to summarise
      - output exactly "<remember> The website content is <execute>get_website('WEBSITE_URL')</execute> </remember>".
      - summarise the website content given what you remember
      - output the summary


When requested to summarise a website, the rule will check if the website url is provided.
Then it will execute the python code in the <execute> tag and remember the result.
The result is added to the language model's prompt through the <remember> tag.
Finally, it will summarise the website content - inserted to the prompt in the prior step - and output the summary.
