Indexing Files
==============

There is a special file called `indices.yaml` that is used to define the paths for the files
that need to be indexed.
The indexed files can be queried from the interface in a RAG fashion.
At the moment, the only supported file types are `txt` and `pdf`.

.. code-block:: yaml

  paths:
    - /path/to/files/

From the command line you can manually add a path as in the following

.. code-block:: bash

  $ wafl add /path/to/files/