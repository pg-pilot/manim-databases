"""MTable basics: an order lifecycle story.

Walks through a small orders table going through realistic database events:
a new order arrives, an existing order ships, and a customer cancels.

Run with:
    manim -ql examples/01_table_basic.py OrdersTable
"""

from manim import *

from manim_databases import MTable, MTableStyle


class OrdersTable(Scene):
    def construct(self):
        table = MTable(
            columns=["id", "customer", "status", "total"],
            rows=[
                [1, "alice", "shipped",    120],
                [2, "bob",   "pending",    85],
                [3, "carol", "processing", 200],
            ],
            primary_key="id",
            style=MTableStyle.BLUE,
        ).scale(0.8)

        title = Text("orders", font="Cascadia Code", font_size=32)
        title.next_to(table, UP, buff=0.5)

        self.play(FadeIn(title), Create(table))
        self.wait(0.8)

        # 1. A new order arrives — insert dave with pending status.
        self.play(table.animate.insert_row([4, "dave", "pending", 55]))
        self.wait(0.6)

        # 2. Bob's order ships. Highlight him first to focus the viewer,
        #    perform the update, then unhighlight to clean up.
        self.play(table.animate.highlight_row(1))
        self.wait(0.3)
        self.play(table.animate.update_cell(1, "status", "shipped"))
        self.wait(0.3)
        self.play(table.animate.unhighlight_row(1))
        self.wait(0.5)

        # 3. Carol cancels her order — delete the row.
        self.play(table.animate.delete_row(2))
        self.wait(1)
