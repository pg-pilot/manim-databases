"""Scene tests for MBTree.

Render with:
    manim -ql tests/test_mbtree.py Init
"""

from manim import *

from manim_databases import MBTree, MBTreeStyle


class Init(Scene):
    def construct(self):
        tree = MBTree.from_structure(
            {
                "keys": [10, 20],
                "children": [
                    {"keys": [3, 7]},
                    {"keys": [12, 17]},
                    {"keys": [25, 30]},
                ],
            },
            style=MBTreeStyle.BLUE,
        )
        self.play(Create(tree))
        self.wait()


class FromStructureDeep(Scene):
    """Three-level tree to verify nested layout."""

    def construct(self):
        tree = MBTree.from_structure(
            {
                "keys": [50],
                "children": [
                    {
                        "keys": [20, 30],
                        "children": [
                            {"keys": [10, 15]},
                            {"keys": [22, 25]},
                            {"keys": [33, 40]},
                        ],
                    },
                    {
                        "keys": [70, 80],
                        "children": [
                            {"keys": [55, 60]},
                            {"keys": [72, 75]},
                            {"keys": [85, 90]},
                        ],
                    },
                ],
            },
            style=MBTreeStyle.PURPLE,
        )
        self.play(Create(tree))
        self.wait()


class SearchHit(Scene):
    def construct(self):
        tree = MBTree.from_structure(
            {
                "keys": [10, 20],
                "children": [
                    {"keys": [3, 7]},
                    {"keys": [12, 17]},
                    {"keys": [25, 30]},
                ],
            },
            style=MBTreeStyle.GREEN,
        )
        self.play(Create(tree))
        self.play(tree.animate.search(17))
        self.wait()


class SearchMiss(Scene):
    def construct(self):
        tree = MBTree.from_structure(
            {
                "keys": [10, 20],
                "children": [
                    {"keys": [3, 7]},
                    {"keys": [12, 17]},
                    {"keys": [25, 30]},
                ],
            },
        )
        self.play(Create(tree))
        # 99 is not present — search should walk to the rightmost leaf
        # and Indicate the whole leaf as a "not found" signal.
        self.play(tree.animate.search(99))
        self.wait()


class InsertNoSplit(Scene):
    def construct(self):
        tree = MBTree.from_structure(
            {
                "keys": [10, 20],
                "children": [
                    {"keys": [3, 7]},
                    {"keys": [12, 17]},
                    {"keys": [25, 30]},
                ],
            },
            style=MBTreeStyle.BLUE,
        )
        self.play(Create(tree))
        self.play(tree.animate.insert(15))
        self.wait()


class InsertWithSplit(Scene):
    def construct(self):
        # Start with a leaf already at max keys (3 for order 4) so the
        # next insert into it triggers a split.
        tree = MBTree.from_structure(
            {
                "keys": [10, 20],
                "children": [
                    {"keys": [3, 7]},
                    {"keys": [12, 15, 17]},
                    {"keys": [25, 30]},
                ],
            },
            style=MBTreeStyle.BLUE,
        )
        self.play(Create(tree))
        self.play(tree.animate.insert(14))
        self.wait()


class AutoBuild(Scene):
    """Build a tree by sequential insertion from a flat key list."""

    def construct(self):
        tree = MBTree(
            order=4,
            keys=[10, 20, 5, 6, 12, 30, 7, 17],
            style=MBTreeStyle.GREEN,
        )
        self.play(Create(tree))
        self.wait()
