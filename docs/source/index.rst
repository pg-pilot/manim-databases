manim-databases
===============

A `Manim <https://www.manim.community/>`_ plugin for animating database
concepts: tables, B-trees, indexes, query execution plans, WAL, replication
topologies, lock contention, and more.

.. image:: ../../assets/previews/mtable.gif
   :alt: MTable — animated database table
   :align: center

.. image:: ../../assets/previews/mbtree.gif
   :alt: MBTree — animated B-tree with search and insert
   :align: center

Built for educators, content creators, and database tooling developers who
want to explain how databases actually work.

Features
--------

- **MTable** — animated database table with insert, update, delete, and
  per-row highlighting
- **MBTree** — B-tree with search path animation, smooth insert, and
  cascading splits
- **Style variants** — every mobject ships with ``DEFAULT``, ``BLUE``,
  ``PURPLE``, and ``GREEN`` styles
- Stubs for **MIndex**, **MQueryPlan**, **MWal**, **MReplicationTopology**,
  and **MLock** — coming in future releases

.. toctree::
   :maxdepth: 2
   :caption: Contents

   installation
   quickstart
   api
   examples

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
