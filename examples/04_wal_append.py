"""MWal placeholder example (mobject not yet implemented)."""

from manim import *

from manim_databases import MWal


class WalAppend(Scene):
    def construct(self):
        # MWal is currently a stub. When implemented, this will animate WAL
        # entries being appended left-to-right with LSN labels.
        wal = MWal(initial_lsn=0)
        self.play(Create(wal))
