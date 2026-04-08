"""MBTree placeholder example (mobject not yet implemented)."""

from manim import *

from manim_databases import MBTree


class BTreeSearch(Scene):
    def construct(self):
        # MBTree is currently a stub. When implemented, this scene will
        # build a B-tree of order 4, animate inserting keys, and highlight
        # the search path for a target key.
        tree = MBTree(order=4, keys=[10, 20, 5, 6, 12, 30, 7, 17])
        self.play(Create(tree))
