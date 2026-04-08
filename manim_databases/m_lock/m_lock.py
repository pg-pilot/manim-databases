"""MLock: animated lock visualization (stub)."""

from __future__ import annotations

from manim import VGroup

from manim_databases.constants import MLockStyle


class MLock(VGroup):
    """Animated database lock with contention visualization.

    Will support:
        - Row-level and table-level lock granularity
        - Lock modes (SHARE, EXCLUSIVE, ROW EXCLUSIVE, etc.)
        - Animated waiter queue when contention occurs
        - Deadlock detection cycle visualization
        - Integration with :class:`~manim_databases.m_table.m_table.MTable`
          to lock specific rows

    Parameters
    ----------
    target : str
        Name of the locked resource (e.g., ``"orders.row[42]"``).
    mode : str
        Lock mode (e.g., ``"EXCLUSIVE"``).
    style : MLockStyle._DefaultStyle, optional
        Style configuration.

    Notes
    -----
    Not yet implemented. Tracking issue:
    https://github.com/pg-pilot/manim-databases/issues
    """

    def __init__(
        self,
        target: str,
        mode: str = "EXCLUSIVE",
        style: MLockStyle._DefaultStyle = MLockStyle.DEFAULT,
    ):
        super().__init__()
        raise NotImplementedError(
            "MLock is not yet implemented. "
            "See https://github.com/pg-pilot/manim-databases/issues"
        )
