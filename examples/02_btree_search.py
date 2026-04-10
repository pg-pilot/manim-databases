"""MBTree basics: build a B-tree, search a key, insert a key that splits.

Walks through three concepts in sequence:

1. A static B-tree of order 4, manually constructed.
2. Searching for an existing key — the search animation highlights each
   key compared along the path from root to leaf.
3. Inserting a key that triggers a leaf split, with the median promoted
   to the parent. This is the integration test for layout + edge updates
   after a structural change.

Run with:
    manim -ql examples/02_btree_search.py BTreeSearchAndInsert
"""

from manim import *

from manim_databases import MBTree, MBTreeStyle


class BTreeSearchAndInsert(Scene):
    def construct(self):
        title = Text("B-tree (order 4)", font="Cascadia Code", font_size=32)
        title.to_edge(UP, buff=0.6)

        # Manual structure — exact tree shape we want to explain.
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

        self.play(FadeIn(title), Create(tree))
        self.wait(0.8)

        # 1. Search for an existing key — highlights the comparison key
        #    at each node on the path.
        search_label = Text(
            "search(17)", font="Cascadia Code", font_size=24, color=YELLOW
        )
        search_label.to_edge(DOWN, buff=0.8)
        self.play(FadeIn(search_label))
        self.play(tree.animate.search(17))
        self.wait(0.5)
        self.play(FadeOut(search_label))

        # 2. Insert a key that fits in an existing leaf without splitting.
        insert_label = Text(
            "insert(15)", font="Cascadia Code", font_size=24, color=GREEN
        )
        insert_label.to_edge(DOWN, buff=0.8)
        self.play(FadeIn(insert_label))
        self.play(tree.animate.insert(15))
        self.wait(0.5)
        self.play(FadeOut(insert_label))

        # 3. Insert a key that triggers a leaf split. After step 2 the
        #    middle leaf is [12, 15, 17] — already at the order-4 max of
        #    3 keys. Inserting 14 overflows it, splitting into two leaves
        #    and promoting the median up into the root.
        split_label = Text(
            "insert(14)  →  split",
            font="Cascadia Code",
            font_size=24,
            color=PURPLE_B,
        )
        split_label.to_edge(DOWN, buff=0.8)
        self.play(FadeIn(split_label))
        self.play(tree.animate.insert(14))
        self.wait(1.5)
