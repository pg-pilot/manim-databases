"""MWal: animated write-ahead log (stub)."""

from __future__ import annotations

from manim import VGroup

from manim_databases.constants import MWalStyle


class MWal(VGroup):
    """Animated write-ahead log as an append-only sequence.

    Will support:
        - LSN-labeled entries appearing left to right
        - Different entry types (INSERT, UPDATE, DELETE, COMMIT, CHECKPOINT)
        - Checkpoint markers
        - Replay animation (cursor walking through entries)
        - Visual link between WAL entries and the
          :class:`~manim_databases.m_table.m_table.MTable` rows they describe

    Parameters
    ----------
    initial_lsn : int
        Starting log sequence number.
    style : MWalStyle._DefaultStyle, optional
        Style configuration.

    Notes
    -----
    Not yet implemented. Tracking issue:
    https://github.com/pg-pilot/manim-databases/issues
    """

    def __init__(
        self,
        initial_lsn: int = 0,
        style: MWalStyle._DefaultStyle = MWalStyle.DEFAULT,
    ):
        super().__init__()
        raise NotImplementedError(
            "MWal is not yet implemented. "
            "See https://github.com/pg-pilot/manim-databases/issues"
        )
