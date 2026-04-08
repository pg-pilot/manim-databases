"""MQueryPlan: animated query execution plan tree (stub)."""

from __future__ import annotations

from manim import VGroup

from manim_databases.constants import MQueryPlanStyle


class MQueryPlan(VGroup):
    """Animated query execution plan as a tree of operators.

    Will support:
        - Standard operator nodes: SeqScan, IndexScan, BitmapHeapScan,
          NestedLoopJoin, HashJoin, MergeJoin, Sort, Aggregate, Limit
        - Cost annotations (startup cost, total cost, rows, width)
        - Animated data flow upward through the plan tree
        - Side-by-side plan comparison (e.g., index vs seq scan)

    Parameters
    ----------
    plan : dict
        Plan tree as a nested dict mirroring PostgreSQL ``EXPLAIN (FORMAT JSON)``.
        Each node has at least ``Node Type`` and may have ``Plans`` (children),
        ``Total Cost``, ``Plan Rows``, etc.
    style : MQueryPlanStyle._DefaultStyle, optional
        Style configuration.

    Examples
    --------
    >>> plan = {
    ...     "Node Type": "Hash Join",
    ...     "Total Cost": 1234.56,
    ...     "Plans": [
    ...         {"Node Type": "Seq Scan", "Total Cost": 100.0},
    ...         {"Node Type": "Index Scan", "Total Cost": 50.0},
    ...     ],
    ... }
    >>> mplan = MQueryPlan(plan)

    Notes
    -----
    Not yet implemented. Tracking issue:
    https://github.com/pg-pilot/manim-databases/issues
    """

    def __init__(
        self,
        plan: dict,
        style: MQueryPlanStyle._DefaultStyle = MQueryPlanStyle.DEFAULT,
    ):
        super().__init__()
        raise NotImplementedError(
            "MQueryPlan is not yet implemented. "
            "See https://github.com/pg-pilot/manim-databases/issues"
        )
