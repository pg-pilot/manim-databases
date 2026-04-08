"""MBTree: animated B-tree mobject (stub)."""

from __future__ import annotations

from manim import VGroup

from manim_databases.constants import MBTreeStyle


class MBTree(VGroup):
    """Animated B-tree visualization.

    Will support:
        - Animated key insertion with node splits
        - Search path highlighting from root to leaf
        - Range scan visualization across leaf nodes
        - Configurable order (max keys per node)

    Parameters
    ----------
    order : int
        Maximum number of keys per node (B-tree order).
    keys : list, optional
        Initial keys to insert.
    style : MBTreeStyle._DefaultStyle, optional
        Style configuration.

    Notes
    -----
    Not yet implemented. Tracking issue:
    https://github.com/pg-pilot/manim-databases/issues
    """

    def __init__(
        self,
        order: int = 4,
        keys: list = None,
        style: MBTreeStyle._DefaultStyle = MBTreeStyle.DEFAULT,
    ):
        super().__init__()
        raise NotImplementedError(
            "MBTree is not yet implemented. "
            "See https://github.com/pg-pilot/manim-databases/issues"
        )
