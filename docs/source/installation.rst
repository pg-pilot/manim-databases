Installation
============

Requirements
------------

- Python 3.10+
- A working `Manim Community <https://docs.manim.community/en/stable/installation.html>`_ installation

Install from PyPI
-----------------

.. code-block:: bash

   pip install manim-databases

Plugin registration
-------------------

``manim-databases`` registers itself as a Manim plugin automatically via the
``manim.plugins`` entry point. After installing, Manim discovers it without
any extra configuration — just import and use:

.. code-block:: python

   from manim_databases import MTable, MBTree

Development install
-------------------

To work on the plugin itself:

.. code-block:: bash

   git clone https://github.com/pg-pilot/manim-databases.git
   cd manim-databases
   pip install -e '.[dev]'

This installs the package in editable mode with linting, testing, and docs
dependencies.
