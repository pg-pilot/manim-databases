"""MIndex: visual database index (stub)."""

from __future__ import annotations

from manim import VGroup

from manim_databases.constants import MIndexStyle


class MIndex(VGroup):
    """Visual representation of a database index.

    Will support:
        - Hash and B-tree backed indexes
        - Animated key lookup with pointer traversal to a target row
          in a paired :class:`~manim_databases.m_table.m_table.MTable`
        - Index scan vs sequential scan side-by-side comparison
        - Selectivity visualization (highlight matching keys)

    Parameters
    ----------
    name : str
        Index name (e.g., ``idx_orders_status``).
    keys : list, optional
        Initial keys to populate.
    backing : {"hash", "btree"}, optional
        Index type. Default ``"btree"``.
    style : MIndexStyle._DefaultStyle, optional
        Style configuration.

    Notes
    -----
    Not yet implemented. Tracking issue:
    https://github.com/pg-pilot/manim-databases/issues
    """

    def __init__(
        self,
        name: str,
        keys: list = None,
        backing: str = "btree",
        style: MIndexStyle._DefaultStyle = MIndexStyle.DEFAULT,
    ):
        super().__init__()
        raise NotImplementedError(
            "MIndex is not yet implemented. "
            "See https://github.com/pg-pilot/manim-databases/issues"
        )
