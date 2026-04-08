"""Scene tests for MTable.

These run via Manim's Scene framework. Render with:
    manim -ql tests/test_mtable.py Init
"""

from manim import *

from manim_databases import MTable, MTableStyle


class Init(Scene):
    def construct(self):
        table = MTable(
            columns=["id", "name"],
            rows=[[1, "alice"], [2, "bob"]],
            primary_key="id",
            style=MTableStyle.BLUE,
        )
        self.play(Create(table))
        self.wait()


class CrudOperations(Scene):
    def construct(self):
        table = MTable(
            columns=["id", "customer", "status", "total"],
            rows=[
                [1, "alice", "shipped", 120],
                [2, "bob", "pending", 85],
                [3, "carol", "shipped", 200],
            ],
            primary_key="id",
            style=MTableStyle.PURPLE,
        ).scale(0.8)

        self.play(Create(table))
        self.play(table.animate.insert_row([4, "dave", "shipped", 55]))
        self.play(table.animate.insert_row([5, "eve", "pending", 310]))
        self.play(table.animate.update_cell(1, "status", "shipped"))
        self.play(table.animate.update_cell(0, "total", 999))
        self.play(table.animate.highlight_row(2))
        self.play(table.animate.delete_row(0))
        self.wait(1)


class ColumnNameAccess(Scene):
    def construct(self):
        table = MTable(
            columns=["id", "name"],
            rows=[[1, "alice"]],
            style=MTableStyle.GREEN,
        )
        self.play(Create(table))
        # update_cell accepts both column names and indices
        self.play(table.animate.update_cell(0, "name", "ALICE"))
        self.play(table.animate.update_cell(0, 1, "Alice"))
        self.wait()
