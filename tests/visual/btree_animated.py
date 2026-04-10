"""Animated debug scenes for MBTree.

Each scene runs ONE animation and pauses. Render with ``-ql`` (low quality
for speed) to check that the animation looks right at intermediate frames.

Render with::

    bash tests/visual/render_animated.sh
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
    title = Text("B-tree (order 4)", font="Cascadia Code", font_size=32)
    title.to_edge(UP, buff=0.6)
    tree = MBTree.from_structure(_STRUCTURE, style=MBTreeStyle.BLUE)
    tree.next_to(title, DOWN, buff=0.6)
    return title, tree


class A01_Search17(Scene):
    """Just the search animation — should highlight the comparison path."""

    def construct(self):
        title, tree = _build_titled_tree()
        self.add(title, tree)
        self.wait(0.5)
        self.play(tree.animate.search(17))
        self.wait(0.5)


class A02_Insert15NoSplit(Scene):
    """Insert that fits without splitting."""

    def construct(self):
        title, tree = _build_titled_tree()
        self.add(title, tree)
        self.wait(0.5)
        self.play(tree.animate.insert(15))
        self.wait(0.5)


class A03_Insert14WithSplit(Scene):
    """Pre-load the leaf to 3 keys, then insert one more to trigger split."""

    def construct(self):
        title = Text("B-tree (order 4)", font="Cascadia Code", font_size=32)
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
        self.add(title, tree)
        self.wait(0.5)
        self.play(tree.animate.insert(14))
        self.wait(0.5)


class A04_FullSequence(Scene):
    """The full example: search → insert no-split → insert with split."""

    def construct(self):
        title, tree = _build_titled_tree()
        self.add(title, tree)
        self.wait(0.5)
        self.play(tree.animate.search(17))
        self.wait(0.3)
        self.play(tree.animate.insert(15))
        self.wait(0.3)
        self.play(tree.animate.insert(14))
        self.wait(0.5)


class A05_TwoInsertsNoSearch(Scene):
    """Diagnostic: two consecutive inserts WITHOUT a preceding search.

    If this renders correctly at the end, the bug is in the search
    animation leaking references. If it ALSO breaks, the bug is in
    consecutive insert calls leaking references.
    """

    def construct(self):
        title, tree = _build_titled_tree()
        self.add(title, tree)
        self.wait(0.5)
        self.play(tree.animate.insert(15))
        self.wait(0.3)
        self.play(tree.animate.insert(14))
        self.wait(0.5)


class A07_SyncInsertBetweenPlays(Scene):
    """Diagnostic: SYNC insert between two play() calls.

    If this breaks the same way A05 does, the bug is caused by play()
    freezing the scene state such that mutations between plays don't
    propagate. If this works, the bug is specific to tree.animate.insert.
    """

    def construct(self):
        title, tree = _build_titled_tree()
        self.add(title, tree)
        self.wait(0.5)
        # First mutation happens INSIDE a play via the animate builder
        self.play(tree.animate.insert(15))
        self.wait(0.3)
        # Second mutation happens OUTSIDE any play, directly on the tree
        tree.insert(14)
        # Then trigger a render via a no-op play
        self.wait(0.5)


class A08_BothSyncBetweenPlays(Scene):
    """Diagnostic: BOTH inserts sync, with plays between."""

    def construct(self):
        title, tree = _build_titled_tree()
        self.add(title, tree)
        self.wait(0.5)
        tree.insert(15)
        self.wait(0.3)
        tree.insert(14)
        self.wait(0.5)


class A06_SearchOnly(Scene):
    """Diagnostic: just a search, then a wait. After completion, are
    the highlighted cells still in the scene as stale references?"""

    def construct(self):
        title, tree = _build_titled_tree()
        self.add(title, tree)
        self.wait(0.5)
        self.play(tree.animate.search(17))
        self.wait(1.0)
