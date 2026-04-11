API Reference
=============

Mobjects
--------

MTable
^^^^^^

.. autoclass:: manim_databases.MTable
   :members:
   :undoc-members: False

MBTree
^^^^^^

.. autoclass:: manim_databases.MBTree
   :members:
   :undoc-members: False

.. autoclass:: manim_databases.MBTreeNode
   :members:
   :undoc-members: False

MIndex
^^^^^^

.. autoclass:: manim_databases.MIndex
   :members:
   :undoc-members: False

Stubs
^^^^^

The following mobjects are planned but not yet implemented. They export a
stable public API that raises ``NotImplementedError`` — this keeps the
namespace consistent from day one.

.. autoclass:: manim_databases.MQueryPlan
   :members:

.. autoclass:: manim_databases.MWal
   :members:

.. autoclass:: manim_databases.MReplicationTopology
   :members:

.. autoclass:: manim_databases.MLock
   :members:

Styles
------

Each mobject has a companion style class with ``DEFAULT``, ``BLUE``,
``PURPLE``, and ``GREEN`` variants.

.. autoclass:: manim_databases.MTableStyle
   :members:
   :no-index:

.. autoclass:: manim_databases.MBTreeStyle
   :members:
   :no-index:

.. autoclass:: manim_databases.MIndexStyle
   :members:
   :no-index:
