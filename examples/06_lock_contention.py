"""MLock placeholder example (mobject not yet implemented)."""

from manim import *

from manim_databases import MLock


class LockContention(Scene):
    def construct(self):
        # MLock is currently a stub. When implemented, this will show a row
        # being locked and a queue of waiters forming behind it.
        lock = MLock(target="orders.row[42]", mode="EXCLUSIVE")
        self.play(Create(lock))
