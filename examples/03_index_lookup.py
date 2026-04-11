"""MIndex basics: build an index on a table, animate a lookup, then insert.

Demonstrates:

1. Building an MTable with several rows.
2. Creating a B-tree index on the ``total`` column via ``MIndex.from_table``.
3. Animated lookup — the search walks the B-tree, follows the pointer
   arrow, and highlights the matching row in the table.
4. Inserting a new row into the table and updating the index to match.

Run with:
    manim -ql examples/03_index_lookup.py IndexLookup
"""

from manim import *

from manim_databases import MIndex, MIndexStyle, MTable, MTableStyle


class IndexLookup(Scene):
    def construct(self):
        # ── 1. Build the table ───────────────────────────────────────
        table = MTable(
            columns=["id", "customer", "status", "total"],
            rows=[
                [1, "alice", "shipped", 120],
                [2, "bob", "pending", 85],
                [3, "carol", "shipped", 200],
                [4, "dave", "pending", 55],
                [5, "eve", "shipped", 150],
                [6, "frank", "pending", 310],
            ],
            primary_key="id",
            style=MTableStyle.BLUE,
        ).scale(0.6)

        # Position table on the right half of the frame.
        table.shift(RIGHT * 2.8)

        self.play(Create(table))
        self.wait(0.3)

        # ── 2. Create the index on "total" ───────────────────────────
        index = MIndex.from_table(
            table,
            column="total",
            name="idx_orders_total",
            order=4,
            style=MIndexStyle.BLUE,
        )

        title = Text(
            "idx_orders_total", font="Cascadia Code", font_size=20, color=YELLOW
        )
        title.next_to(index.tree, UP, buff=0.3)

        self.play(Create(index.tree), FadeIn(title), run_time=0.8)
        self.wait(0.2)

        # Draw all pointer arrows in one go.
        self.play(
            *[Create(a, run_time=0.4) for a in index._arrows],
        )
        self.wait(0.5)

        # ── 3. Animated lookup ───────────────────────────────────────
        lookup_label = Text(
            "WHERE total = 200", font="Cascadia Code", font_size=20, color=GREEN
        )
        lookup_label.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(lookup_label))
        self.play(index.animate.lookup(200))
        self.wait(0.2)
        self.play(FadeOut(lookup_label))

        # ── 4. Insert a row and update the index ─────────────────────
        insert_label = Text(
            "INSERT (7, 'grace', 'shipped', 175)",
            font="Cascadia Code",
            font_size=18,
            color=PURPLE_B,
        )
        insert_label.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(insert_label))

        # Insert into the table.
        self.play(table.animate.insert_row([7, "grace", "shipped", 175]))
        self.wait(0.2)

        # Update the index in three smooth phases:
        #   1. Fade out old arrows
        #   2. Smooth tree insert (cells slide, median floats up on split)
        #   3. Rebuild and draw new arrows

        # Phase 1: fade out old arrows.
        self.play(*[FadeOut(a, run_time=0.3) for a in index._arrows])
        for a in list(index._arrows):
            if a in index.submobjects:
                index -= a
        index._arrows.clear()

        # Phase 2: smooth B-tree insert (reuses MBTree's animation).
        new_row = table.get_row(len(table) - 1)
        index._key_to_row[175] = new_row
        self.play(index.tree.animate.insert(175))

        # Phase 3: reposition tree, rebuild arrows, draw them in.
        index._position_beside_table()
        index._rebuild_arrows()
        self.play(*[Create(a, run_time=0.4) for a in index._arrows])
        self.wait(1.0)
