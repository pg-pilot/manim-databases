"""Static-frame debug scenes for MBTree.

Each scene builds the tree up to a specific state and adds it to the scene
without animation, so a single ``manim -s`` render produces a clean PNG of
that exact state. Used for visual debugging — render and inspect the PNGs
to find bugs that are hard to reason about from the code alone.

Render all states with::

    bash tests/visual/render.sh

Or render a single state::

    .venv/bin/manim -ql -s tests/visual/btree_states.py S01_InitialTree
"""

from manim import *

from manim_databases import MBTree, MBTreeStyle


_STRUCTURE = {
    "keys": [10, 20],
    "children": [
        {"keys": [3, 7]},
        {"keys": [12, 17]},
        {"keys": [25, 30]},
    ],
}


def _build_titled_tree() -> tuple[Text, MBTree]:
    """Mirror the example: title + tree below it."""
    title = Text("B-tree (order 4)", font="Cascadia Code", font_size=32)
    title.to_edge(UP, buff=0.6)
    tree = MBTree.from_structure(_STRUCTURE, style=MBTreeStyle.BLUE)
    tree.next_to(title, DOWN, buff=0.6)
    return title, tree


class S01_InitialTree(Scene):
    """Tree as built by from_structure + next_to. No mutations."""

    def construct(self):
        title, tree = _build_titled_tree()
        self.add(title, tree)


class S02_AfterInsert15(Scene):
    """After a single insert(15) — leaf [12, 17] becomes [12, 15, 17]."""

    def construct(self):
        title, tree = _build_titled_tree()
        tree.insert(15)
        self.add(title, tree)


class S03_AfterInsert14Split(Scene):
    """After insert(15) then insert(14) — the latter triggers a split."""

    def construct(self):
        title, tree = _build_titled_tree()
        tree.insert(15)
        tree.insert(14)
        self.add(title, tree)


class S04_AutoBuildSequential(Scene):
    """Tree built by sequential insertion of a flat key list."""

    def construct(self):
        title = Text("auto-built", font="Cascadia Code", font_size=32)
        title.to_edge(UP, buff=0.6)
        tree = MBTree(
            order=4,
            keys=[10, 20, 5, 6, 12, 30, 7, 17],
            style=MBTreeStyle.GREEN,
        )
        tree.next_to(title, DOWN, buff=0.6)
        self.add(title, tree)


class S06_PostNextToInsert(Scene):
    """Diagnostic: call insert(14) AFTER next_to, with no animation.

    Isolates whether the synchronous ``insert`` works correctly when
    the tree has been positioned via ``next_to`` after construction.
    If this renders correctly, the bug is in ``_insert_animation``.
    If it renders incorrectly, the bug is in ``insert`` itself.
    """

    def construct(self):
        title = Text("post next_to insert", font="Cascadia Code", font_size=32)
        title.to_edge(UP, buff=0.6)
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
        tree.next_to(title, DOWN, buff=0.6)
        # Mutate AFTER positioning. This is what _insert_animation does
        # via the deferred callback.
        tree.insert(14)
        self.add(title, tree)


class S07_TwoSyncInserts(Scene):
    """Diagnostic: two consecutive SYNCHRONOUS inserts.

    If this renders correctly, the bug is in the animation framework
    (tree.animate.insert) leaking state. If it ALSO breaks, the bug is
    in the synchronous insert() called twice in a row.
    """

    def construct(self):
        title = Text("two sync inserts", font="Cascadia Code", font_size=32)
        title.to_edge(UP, buff=0.6)
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
        tree.next_to(title, DOWN, buff=0.6)
        tree.insert(15)
        tree.insert(14)
        self.add(title, tree)


class S05_DeepThreeLevel(Scene):
    """Three-level tree to verify nested layout and edges.

    Uses ``max_width`` so the tree auto-fits within the frame — without
    it, the outermost leaves (10 and 90) would clip off-screen.
    """

    def construct(self):
        title = Text("deep tree", font="Cascadia Code", font_size=32)
        title.to_edge(UP, buff=0.6)
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
            max_width=config.frame_width - 1.0,
        )
        tree.next_to(title, DOWN, buff=0.6)
        self.add(title, tree)
