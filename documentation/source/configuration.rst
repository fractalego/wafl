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
  "frontend_port": 8090,
  "backend": {
    "host": "localhost",
    "port": 8080,
    "token": "secret"
  },
  "generation_config": {
    "temperature": 0.4
  },
  "listener_model": {
    "listener_hotword_logp": -8,
    "listener_volume_threshold": 0.6,
    "listener_silence_timeout": 0.7,
    "interruptible": true
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

    * "backend" is the configuration related to the backend. The default is "localhost:8080".

    * "generation_config" is the configuration related to the generation of the response. The default is "temperature: 0.4".

    * "listener_model" is the configuration related to the listener model.
      These items determine the thresholds for hotword detection, volume threshold, silence timeout, and whether the listener is interruptible.
      The default is "listener_hotword_logp: -8", "listener_volume_threshold: 0.6", "listener_silence_timeout: 0.7", "interruptible: true".
