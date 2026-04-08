"""MTable basics: insert, update, delete, highlight.

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
                [1, "alice", "shipped", 120],
                [2, "bob", "pending", 85],
                [3, "carol", "shipped", 200],
            ],
            primary_key="id",
            style=MTableStyle.BLUE,
        ).scale(0.8)

        title = Text("orders", font="Cascadia Code", font_size=32)
        title.next_to(table, UP, buff=0.5)

        self.play(FadeIn(title), Create(table))
        self.wait(0.8)

        # Insert a new row
        self.play(table.animate.insert_row([4, "dave", "shipped", 55]))
        self.wait(0.5)

        # Highlight the second row
        self.play(table.animate.highlight_row(1))
        self.wait(0.4)

        # Update its status
        self.play(table.animate.update_cell(1, "status", "shipped"))
        self.wait(0.5)

        # Delete the first row
        self.play(table.animate.delete_row(0))
        self.wait(1)
