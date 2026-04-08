"""MQueryPlan placeholder example (mobject not yet implemented)."""

from manim import *

from manim_databases import MQueryPlan


class QueryPlan(Scene):
    def construct(self):
        # MQueryPlan is currently a stub. When implemented, this will render
        # an EXPLAIN tree with cost annotations and animate data flow upward.
        plan = {
            "Node Type": "Hash Join",
            "Total Cost": 1234.56,
            "Plans": [
                {"Node Type": "Seq Scan", "Total Cost": 100.0},
                {"Node Type": "Index Scan", "Total Cost": 50.0},
            ],
        }
        mplan = MQueryPlan(plan)
        self.play(Create(mplan))
