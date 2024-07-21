Modify the original prompt
==========================

The prompt is stored in the file "main.prompt" in the project's root directory.
The name of the file can be changed in the `config.json` file.
The default is:


.. code-block:: text
    A user is chatting with a bot. The chat is happening through a web interface. The user is typing the messages and the bot is replying.

    This is summary of the bot's knowledge:
    {facts}

    The rules that *must* be followed are:
    {rules}

    Create a plausible dialogue based on the aforementioned summary and rules.
    Do not repeat yourself. Be friendly but not too servile.
    Follow the rules if present and they apply to the dialogue. Do not improvise if rules are present.


The variables `{facts}` and `{rules}` are replaced by the actual facts and rules when the prompt is generated.
