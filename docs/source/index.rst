manim-databases
===============

A Manim plugin for animating database concepts: tables, B-trees, query plans,
WAL, replication topologies, lock contention, and more.

.. image:: ../../assets/previews/mtable.gif
   :alt: MTable preview
   :align: center

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   reference
   examples

Quick Start
-----------

.. code-block:: python

   from manim import *
   from manim_databases import MTable, MTableStyle

   class OrdersTable(Scene):
       def construct(self):
           table = MTable(
               columns=["id", "customer", "status"],
               rows=[[1, "alice", "shipped"], [2, "bob", "pending"]],
               primary_key="id",
               style=MTableStyle.BLUE,
           )
           self.play(Create(table))
           self.play(table.animate.insert_row([3, "carol", "shipped"]))
           self.play(table.animate.update_cell(1, "status", "shipped"))
           self.play(table.animate.delete_row(0))

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
