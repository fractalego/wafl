Directory structure
===================

Consider the following directory structure in your project

.. code-block:: bash

    .
    ├── functions.py
    ├── wafl.rules            # (1)
    │
    ├── facts
    │       ├── functions.py
    │       └── wafl.rules
    ├── greetings
    │       ├── wafl.rules    # (2)
    │       ├── functions.py
    │       └── facts
    │               ├── wafl.rules
    │               └── functions.py
    └── interruptions
            ├── functions.py
            └── wafl.rules

The rules can be organised into a nested directory structure.
Each directory must contain `rules.wafl` and `functions.py`.
The first one contains the rules as explained in `the rules section <rules.html>`_.

The directories to be used for inference must be used within the `wafl.rules` (1) file according to the following syntax

.. code-block:: text

    #using facts
    #using greetings
    #using interruptions

The keyword `#using <FOLDER_NAME>` includes the specified folder in the inference tree.
Only the rules and facts that are included will be part of the inference.
For example, the keyword `#using facts` within greetings/ (2) will not include the folder above it.
Inference in a subfolder is limited the the rules and facts that are part of that folder or below it.

For more complete example, you can have a look at the (still early) project in
`wafl_home <https://github.com/fractalego/wafl_home>`_.