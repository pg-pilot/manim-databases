Examples
========

Runnable example scenes live in the
`examples/ <https://github.com/pg-pilot/manim-databases/tree/main/examples>`_
directory of the source repo. Render any of them with:

.. code-block:: bash

   manim -ql examples/<file>.py <SceneName>

Use ``-ql`` for fast 480p iteration, ``-qh`` for 1080p final renders.

01 — Table basics
-----------------

**File:** ``examples/01_table_basic.py`` — Scene: ``OrdersTable``

Demonstrates the core ``MTable`` workflow: creating a table with typed columns,
then animating insert, update (with highlight/unhighlight), and delete operations.
Models a realistic orders lifecycle (new order → ship → cancel).

.. code-block:: bash

   manim -ql examples/01_table_basic.py OrdersTable

02 — B-tree search and insert
------------------------------

**File:** ``examples/02_btree_search.py`` — Scene: ``BTreeSearchAndInsert``

Walks through three operations on an order-4 B-tree:

1. **Search** — highlights the comparison path from root to leaf.
2. **Insert (no split)** — cells slide apart to make room.
3. **Insert (with split)** — the overflowing leaf tears apart, the median
   key floats up to the parent, and new edges draw in.

.. code-block:: bash

   manim -ql examples/02_btree_search.py BTreeSearchAndInsert

03 — Index lookup
------------------

**File:** ``examples/03_index_lookup.py`` — Scene: ``IndexLookup``

Builds a table with six rows and creates a B-tree index on the ``total``
column.  Demonstrates:

1. **Index creation** — arrows drawn from each leaf key to its table row.
2. **Animated lookup** — walks the B-tree, follows the pointer, highlights
   the matching row.
3. **Insert** — adds a row to the table and updates the index.

.. code-block:: bash

   manim -ql examples/03_index_lookup.py IndexLookup

04–06 — Stubs
--------------

``examples/04_wal_append.py`` through ``examples/06_lock_contention.py`` are
placeholder scenes for mobjects that are not yet implemented. They document the
intended API and will become runnable as each mobject lands.
