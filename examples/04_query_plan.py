"""MQueryPlan: visualize a PostgreSQL EXPLAIN plan and animate execution.

Demonstrates:

1. Building an execution plan tree from a nested dict matching
   PostgreSQL's EXPLAIN (FORMAT JSON) output.
2. Node rendering with operator type, relation name, and cost/rows.
3. Animated execution flow — leaves scan first, data pulses upward
   through edges, cascading to the root.

Run with:
    manim -ql examples/04_query_plan.py QueryPlanDemo
"""

from manim import *

from manim_databases import MQueryPlan, MQueryPlanStyle


class QueryPlanDemo(Scene):
    def construct(self):
        title = Text(
            "EXPLAIN (FORMAT JSON)", font="Cascadia Code", font_size=28
        )
        title.to_edge(UP, buff=0.5)

        plan = MQueryPlan(
            {
                "Node Type": "Aggregate",
                "Total Cost": 245.00,
                "Plan Rows": 1,
                "Plans": [
                    {
                        "Node Type": "Hash Join",
                        "Total Cost": 230.00,
                        "Plan Rows": 100,
                        "Plans": [
                            {
                                "Node Type": "Seq Scan",
                                "Relation Name": "orders",
                                "Total Cost": 25.00,
                                "Plan Rows": 500,
                            },
                            {
                                "Node Type": "Hash",
                                "Total Cost": 15.00,
                                "Plans": [
                                    {
                                        "Node Type": "Index Scan",
                                        "Relation Name": "customers",
                                        "Total Cost": 12.50,
                                        "Plan Rows": 200,
                                    }
                                ],
                            },
                        ],
                    }
                ],
            },
            style=MQueryPlanStyle.BLUE,
            max_width=12.0,
        )
        plan.next_to(title, DOWN, buff=0.5)

        self.play(FadeIn(title))
        self.play(Create(plan), run_time=1.0)
        self.wait(0.5)

        # Animate execution: leaves scan → data flows up → root aggregates.
        exec_label = Text(
            "Executing plan...", font="Cascadia Code", font_size=20, color=GREEN
        )
        exec_label.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(exec_label))
        self.play(plan.animate.execute())
        self.wait(0.3)
        self.play(FadeOut(exec_label))
        self.wait(0.5)
