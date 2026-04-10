Quick Start
===========

This page walks through three minimal scenes to get you up and running.

MTable — animated database table
---------------------------------

.. code-block:: python

   from manim import *
   from manim_databases import MTable, MTableStyle

   class OrdersTable(Scene):
       def construct(self):
           table = MTable(
               columns=["id", "customer", "status"],
               rows=[
                   [1, "alice", "shipped"],
                   [2, "bob", "pending"],
               ],
               primary_key="id",
               style=MTableStyle.BLUE,
           )

           self.play(Create(table))
           self.play(table.animate.insert_row([3, "carol", "shipped"]))
           self.play(table.animate.update_cell(1, "status", "shipped"))
           self.play(table.animate.delete_row(0))

Render it:

.. code-block:: bash

   manim -ql my_scene.py OrdersTable

MBTree — search and insert
----------------------------

.. code-block:: python

   from manim import *
   from manim_databases import MBTree, MBTreeStyle

   class BTreeDemo(Scene):
       def construct(self):
           tree = MBTree.from_structure(
               {
                   "keys": [10, 20],
                   "children": [
                       {"keys": [3, 7]},
                       {"keys": [12, 17]},
                       {"keys": [25, 30]},
                   ],
               },
               order=4,
               style=MBTreeStyle.BLUE,
           )

           self.play(Create(tree))
           self.play(tree.animate.search(17))   # highlights search path
           self.play(tree.animate.insert(15))    # smooth insert, no split
           self.play(tree.animate.insert(14))    # triggers a leaf split

MBTree can also be built via sequential insertion:

.. code-block:: python

   tree = MBTree(order=4, keys=[10, 20, 5, 6, 12, 30, 7, 17])

Style variants
--------------

Every mobject ships with four predefined styles:

.. code-block:: python

   MTable(columns=[...], rows=[...], style=MTableStyle.PURPLE)
   MBTree.from_structure({...}, style=MBTreeStyle.GREEN)

You can subclass ``MTableStyle._DefaultStyle`` or ``MBTreeStyle._DefaultStyle``
to build custom styles.
