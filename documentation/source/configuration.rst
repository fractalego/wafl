Configuration
--------------

The file `config.json` contains some parameters for the chatbot and the url to connect to for the backend.

A typical configuration file looks like this:

.. code-block:: text

    {
      "waking_up_word": "computer",
      "waking_up_sound": true,
      "deactivate_sound": true,
      "rules": "rules.yaml",
      "index": "indices.yaml",
      "cache_filename": "knowledge_cache",
      "prompt_filename": "main.prompt",
      "functions": "functions.py",
      "max_recursion": 2,
      "llm_model": {
        "model_host": "localhost",
        "model_port": 8080,
        "temperature": 0.4
      },
      "listener_model": {
        "model_host": "localhost",
        "model_port": 8080,
        "listener_hotword_logp": -8,
        "listener_volume_threshold": 0.6,
        "listener_silence_timeout": 0.7
      },
      "speaker_model": {
        "model_host": "localhost",
        "model_port": 8080
      },
      "text_embedding_model": {
        "model_host": "localhost",
        "model_port": 8080
      }
    }



These settings regulate the following:

    * "waking_up_word" is the name of the bot, used to wake up the system in the "run-audio" mode.

    * "waking_up_sound" and "deactivate_sound" are played to signal the system is up or is back to idle.

    * "rules" is the file containing the facts and rules that guide the chatbot. The default is "rules.yaml".

    * "index" is the file containing the path to the files to index. The default is "indices.yaml".

    * "cache_filename" is the file where the indexed knowledge is cached. The default is "knowledge_cache".

    * "prompt_filename" is the file containing the main prompt for the chatbot. The default is "main.prompt".

    * "functions" is the file containing the functions that can be used in the rules. The default is "functions.py".

    * "frontend_port" is the port where the web frontend is running. The default is 8090.

    * "llm_model" is the configuration to connect to wafl-llm in the backend. The default url is "localhost:8080". The "temperature" parameter is used to set the temperature for the LLM model. The default is 0.4.

    * "listener_model" is the configuration to connect to the listener model in the backend. The default is "localhost:8080".

       - The listener model is used to detect the wake-up word.
         The similarity threshold for the detection can be set with the "listener_hotword_logp" parameter.

       - The "listener_volume_threshold" parameter is used to set the volume threshold for any conversation.
         Any word uttered with a volume below this threshold is ignored.

       - The "listener_silence_timeout" parameter is used to set the silence timeout for any conversation.
         If no word is uttered for a time longer than this timeout, the conversation is considered finished.

    * "speaker_model" is the configuration to connect to the speaker model in the backend. The default is "localhost:8080".

    * "text_embedding_model" is the configuration to connect to the text embedding model in the backend. The default is "localhost:8080".

