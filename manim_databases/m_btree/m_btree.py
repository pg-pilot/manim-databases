"""MBTree: animated B-tree mobject."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterator

import numpy as np
from manim import (
    Animation,
    AnimationGroup,
    FadeIn,
    FadeOut,
    Line,
    MoveToTarget,
    Succession,
    SurroundingRectangle,
    VGroup,
    Wait,
    override_animate,
)

from manim_databases.constants import MBTreeStyle
from manim_databases.m_btree.m_btree_node import MBTreeNode
from manim_databases.utils.utils import Labelable


class _BNode:
    """Internal tree-structure wrapper around an :class:`MBTreeNode`.

    Holds parent/child references for the tree algorithms. The visual
    mobject is :attr:`node`; keys are read directly from it so there is
    no state duplication.
    """

    def __init__(self, node: MBTreeNode):
        self.node = node
        self.children: list[_BNode] = []
        self.parent: _BNode | None = None

    @property
    def keys(self) -> list[Any]:
        return self.node.keys

    def is_leaf(self) -> bool:
        return not self.children


class MBTree(VGroup, Labelable):
    """An animated B-tree visualization.

    Two construction modes:

    1. **Manual structure** — primary API for educational scenes:

       >>> tree = MBTree.from_structure({
       ...     "keys": [10, 20],
       ...     "children": [
       ...         {"keys": [3, 7]},
       ...         {"keys": [12, 17]},
       ...         {"keys": [25, 30]},
       ...     ],
       ... })

    2. **Auto-build** from a flat key list (sequential insertion with
       splits, just like a real B-tree):

       >>> tree = MBTree(order=4, keys=[10, 20, 5, 6, 12, 30, 7, 17])

    Parameters
    ----------
    order : int
        Maximum number of children per node. A node with more than
        ``order - 1`` keys triggers a split.
    keys : list, optional
        Initial keys to insert sequentially.
    style : MBTreeStyle._DefaultStyle, optional
        Style configuration. Default ``MBTreeStyle.DEFAULT``.

    Notes
    -----
    Insertion with cascading splits is supported. Deletion (with merges
    and borrows) is intentionally not implemented in this version — it
    will land after insert/split is validated against real scenes.
    """

    def __init__(
        self,
        order: int = 4,
        keys: list[Any] | None = None,
        style: MBTreeStyle._DefaultStyle = MBTreeStyle.DEFAULT,
        max_width: float | None = None,
    ):
        super().__init__()
        if order < 3:
            raise ValueError(f"B-tree order must be >= 3, got {order}")

        self.order = order
        self.max_keys = order - 1
        self.style = deepcopy(style)
        self.max_width = max_width
        self._root: _BNode | None = None
        self._edges: list[Line] = []
        self._temp_mobs: list = []

        if keys:
            for k in keys:
                self.insert(k)

    # ── construction ──────────────────────────────────────────────────

    @classmethod
    def from_structure(
        cls,
        structure: dict,
        order: int = 4,
        style: MBTreeStyle._DefaultStyle = MBTreeStyle.DEFAULT,
        max_width: float | None = None,
    ) -> MBTree:
        """Build a tree from an explicit nested-dict spec.

        Each dict has ``keys`` (list) and an optional ``children`` list of
        further dicts. ``order`` defaults to ``4`` (max 3 keys per node);
        if any node in the structure has more keys than ``order - 1``,
        the structure is rejected as inconsistent.

        If ``max_width`` is provided, the tree is uniformly scaled down
        after layout so its bounding box width does not exceed that
        value. Useful for deep trees that would otherwise clip the frame.
        """
        max_node_keys = cls._max_keys_in_structure(structure)
        if max_node_keys >= order:
            raise ValueError(
                f"Structure has a node with {max_node_keys} keys, which "
                f"exceeds order {order} (max {order - 1} keys per node). "
                f"Pass a larger ``order`` argument or shrink the node."
            )

        tree = cls(order=order, style=style, max_width=max_width)
        tree._root = tree._build_subtree_from_dict(structure, parent=None)
        tree._layout_tree()
        return tree

    @staticmethod
    def _max_keys_in_structure(spec: dict) -> int:
        own = len(spec.get("keys", []))
        children = spec.get("children", [])
        if not children:
            return own
        return max(own, *(MBTree._max_keys_in_structure(c) for c in children))

    def _build_subtree_from_dict(
        self, spec: dict, parent: _BNode | None
    ) -> _BNode:
        node = MBTreeNode(spec.get("keys", []), style=self.style)
        bnode = _BNode(node)
        bnode.parent = parent
        self += node
        for child_spec in spec.get("children", []):
            bnode.children.append(
                self._build_subtree_from_dict(child_spec, parent=bnode)
            )
        return bnode

    # ── traversal helpers ────────────────────────────────────────────

    def get_root(self) -> MBTreeNode | None:
        return self._root.node if self._root else None

    def get_nodes(self) -> list[MBTreeNode]:
        """Return all nodes in BFS order (root first)."""
        return [bnode.node for bnode in self._bfs()]

    def _bfs(self) -> Iterator[_BNode]:
        if self._root is None:
            return
        queue: list[_BNode] = [self._root]
        while queue:
            current = queue.pop(0)
            yield current
            queue.extend(current.children)

    # ── layout ────────────────────────────────────────────────────────

    def _layout_tree(self, anchor_center: np.ndarray | None = None) -> None:
        """Recompute positions of all nodes, rebuild edges, fit, anchor.

        Order matters:

        1. Lay out every node around the origin.
        2. Rebuild edges so the bbox reflects the new topology.
        3. If ``self.max_width`` is set and the tree is wider than that,
           uniformly scale it down (about the origin) so it fits.
        4. Shift to ``anchor_center`` (if provided) so the user-supplied
           ``next_to(title)`` position is preserved across re-layouts
           triggered by insert/split.

        Edges must be rebuilt BEFORE the fit-and-anchor steps: otherwise
        stale edges sitting at their pre-layout positions would inflate
        the bounding box, and both the scale and the shift would be
        computed off a wrong bbox.
        """
        if self._root is None:
            return

        # 1. Position every node around the origin.
        self._layout_subtree(self._root, center_x=0.0, top_y=0.0)

        # 2. Rebuild edges so the bbox reflects the new topology.
        self._draw_edges()

        # 3. Auto-fit: scale down if we exceed ``max_width``.
        if self.max_width is not None and self.width > self.max_width:
            factor = self.max_width / self.width
            self.scale(factor, about_point=self.get_center())

        # 4. Shift the whole tree so its center matches the anchor.
        if anchor_center is not None:
            new_center = self.get_center()
            offset = anchor_center - new_center
            if not np.allclose(offset, 0):
                self.shift(offset)

    def _compute_subtree_width(self, bnode: _BNode) -> float:
        """Horizontal space needed by a subtree.

        Guards against the case where a wide parent (many keys) exceeds
        the combined width of its children — uses ``max(parent_width,
        children_total)`` so siblings never overlap a wide parent.
        """
        own_width = bnode.node.width
        if bnode.is_leaf():
            return own_width

        children_widths = [self._compute_subtree_width(c) for c in bnode.children]
        children_total = (
            sum(children_widths)
            + self.style.horizontal_gap * (len(children_widths) - 1)
        )
        return max(own_width, children_total)

    def _layout_subtree(
        self, bnode: _BNode, center_x: float, top_y: float
    ) -> None:
        bnode.node.move_to([center_x, top_y, 0])
        if bnode.is_leaf():
            return

        children_widths = [self._compute_subtree_width(c) for c in bnode.children]
        total = sum(children_widths) + self.style.horizontal_gap * (
            len(children_widths) - 1
        )
        x = center_x - total / 2
        child_y = top_y - self.style.vertical_gap
        for child, w in zip(bnode.children, children_widths):
            child_center_x = x + w / 2
            self._layout_subtree(child, child_center_x, child_y)
            x += w + self.style.horizontal_gap

    # ── temp-mob cleanup ─────────────────────────────────────────────

    def _cleanup_temp(self) -> None:
        """Remove leftover temporary mobjects from prior animations."""
        for mob in getattr(self, "_temp_mobs", []):
            if mob in self.submobjects:
                self -= mob
        self._temp_mobs = []

    # ── edges ─────────────────────────────────────────────────────────

    def _draw_edges(self) -> None:
        """Re-create all edges from parents' gap bottoms to children's tops."""
        self._cleanup_temp()
        for edge in self._edges:
            self -= edge
        self._edges = []

        for bnode in self._bfs():
            if bnode.is_leaf():
                continue
            for gap_index, child in enumerate(bnode.children):
                edge = self._make_edge(bnode.node, child.node, gap_index)
                self._edges.append(edge)
                self += edge

    def _make_edge(
        self, parent: MBTreeNode, child: MBTreeNode, gap_index: int
    ) -> Line:
        """Build an edge from a parent's gap bottom to a child's top.

        Edges are plain :class:`Line` mobjects with **no updaters**. They
        snapshot the (parent, child) positions at construction time. The
        intent was to use updaters so edges follow nodes during layout
        transitions, but in practice ``put_start_and_end_on`` interacts
        poorly with prior ``shift`` calls (e.g. ``next_to``) and leaves
        the line geometry inconsistent.

        Since ``_draw_edges`` is called from scratch on every structural
        change (after ``_layout_tree`` finalizes positions), edges are
        always at their correct post-layout positions when the user sees
        them. The trade-off: during the animated layout transition for an
        insert/split, edges sit at their destination from the start while
        cells slide into them — visually clean enough for v1.
        """
        return Line(
            parent.get_gap_bottom(gap_index),
            child.get_top(),
            **self.style.edge,
        )

    # ── search ────────────────────────────────────────────────────────

    def get_search_path(
        self, key: Any
    ) -> list[tuple[MBTreeNode, int | None]]:
        """Return ``(node, key_index)`` tuples visited during a key search.

        At each internal node, ``key_index`` is the position of the key
        whose comparison decided which child to descend into — i.e., the
        smallest key in the node that is ``>= key`` (or the last key if
        all node keys are smaller). At the terminating leaf, ``key_index``
        is the position of the matching key, or ``None`` if not found.
        """
        if self._root is None:
            return []

        path: list[tuple[MBTreeNode, int | None]] = []
        current = self._root
        while True:
            keys = current.keys
            i = 0
            while i < len(keys) and keys[i] < key:
                i += 1

            if i < len(keys) and keys[i] == key:
                path.append((current.node, i))
                return path

            if current.is_leaf():
                path.append((current.node, None))
                return path

            compare_index = i if i < len(keys) else len(keys) - 1
            path.append((current.node, compare_index))
            current = current.children[i]

    def search(self, key: Any) -> MBTree:
        """Walk the search path for a key. Non-animated; use ``.animate``."""
        return self

    @override_animate(search)
    def _search_animation(
        self, key: Any, anim_args: dict | None = None
    ) -> Animation:
        """Walk the search path with transient highlight overlays.

        We deliberately DO NOT use ``Indicate`` on the tree's own cells.
        ``Indicate`` (like all :class:`Transform` subclasses) adds its
        target to the scene as a top-level mobject, and Manim never
        cleans it up. Subsequent mutations that remove those cells from
        the tree still see them rendered via the leaked top-level ref.

        Instead we create a fresh :class:`SurroundingRectangle` overlay
        for each step of the path and ``FadeIn`` → ``Wait`` →
        ``FadeOut`` it. ``FadeOut`` has ``remover=True`` so the overlay
        is fully removed from the scene at the end of each step — no
        stale references linger.
        """
        if anim_args is None:
            anim_args = {}
        path = self.get_search_path(key)
        if not path:
            return Wait(0.1)

        hold_time = 0.25
        anims: list[Animation] = []
        last_index = len(path) - 1
        for i, (node, key_index) in enumerate(path):
            is_last = i == last_index
            color = (
                self.style.found_color
                if is_last
                else self.style.path_highlight_color
            )
            if key_index is None:
                target = node
            else:
                target = node.get_key_target(key_index)
            overlay = SurroundingRectangle(
                target, color=color, stroke_width=5, buff=0.05
            )
            anims.append(
                Succession(
                    FadeIn(overlay, run_time=0.2),
                    Wait(hold_time),
                    FadeOut(overlay, run_time=0.2),
                )
            )
        return Succession(*anims, **anim_args)

    # ── insert (with cascading splits) ───────────────────────────────

    def insert(self, key: Any) -> MBTree:
        """Insert a key into the tree, splitting nodes as needed.

        Empty tree → creates a single-node root. Otherwise descends to
        the correct leaf, inserts the key in sorted order, and cascades
        splits upward through the tree (creating a new root if the old
        root itself overflows).
        """
        if self._root is None:
            node = MBTreeNode([key], style=self.style)
            self._root = _BNode(node)
            self += node
            self._layout_tree()
            return self

        # Preserve the tree's overall position across the mutation.
        pre_center = self.get_center().copy()

        leaf = self._find_leaf_for_key(key)
        position = self._sorted_position(leaf, key)
        leaf.node.insert_key_at(position, key)

        current: _BNode | None = leaf
        while current is not None and len(current.keys) > self.max_keys:
            current = self._split_node(current)

        self._layout_tree(anchor_center=pre_center)
        return self

    @override_animate(insert)
    def _insert_animation(
        self, key: Any, anim_args: dict | None = None
    ) -> Animation:
        """Animated insert using snapshot → mutate → diff → rewind → animate.

        1. Snapshot every cell/text position keyed by key value.
        2. Run the synchronous insert (full mutation + re-layout).
        3. Diff: keys present before slide from old → new positions;
           truly new keys (the just-inserted one) fade in.
        4. Edge transitions: old edges fade out, new edges fade in.

        The animation plays in two phases:

        - **Phase 1** — existing cells slide to new positions while old
          edges fade out. For splits this produces the "tear" effect
          (left half slides left, right half slides right, median floats
          up to the parent).
        - **Phase 2** — the newly inserted key fades in at its gap, and
          new edges draw in.
        """
        if anim_args is None:
            anim_args = {}

        # First insert into an empty tree — just fade in the root node.
        if self._root is None:
            self.insert(key)
            return FadeIn(self._root.node, **anim_args)

        # -- 1. Snapshot pre-mutation positions keyed by key value -----
        old_key_pos: dict[Any, tuple[np.ndarray, np.ndarray]] = {}
        for bnode in self._bfs():
            for i, k in enumerate(bnode.keys):
                old_key_pos[k] = (
                    bnode.node.cells[i].get_center().copy(),
                    bnode.node.key_texts[i].get_center().copy(),
                )

        old_edges = [e.copy() for e in self._edges]

        # -- 2. Mutate (full insert + split cascade + re-layout) ------
        self.insert(key)

        # -- 3. Diff: classify every post-mutation cell ----------------
        move_anims: list[Animation] = []
        fade_in_anims: list[Animation] = []

        for bnode in self._bfs():
            for i, k in enumerate(bnode.keys):
                cell = bnode.node.cells[i]
                text = bnode.node.key_texts[i]
                final_cp = cell.get_center().copy()
                final_tp = text.get_center().copy()

                if k in old_key_pos:
                    # Key existed before — rewind cell+text, then slide.
                    old_cp, old_tp = old_key_pos[k]
                    if not np.allclose(old_cp, final_cp, atol=1e-3):
                        cell.move_to(old_cp)
                        cell.generate_target()
                        cell.target.move_to(final_cp)
                        move_anims.append(MoveToTarget(cell))

                        text.move_to(old_tp)
                        text.generate_target()
                        text.target.move_to(final_tp)
                        move_anims.append(MoveToTarget(text))
                else:
                    # Truly new key — fade in at its final position.
                    fade_in_anims.extend([FadeIn(cell), FadeIn(text)])

        # -- 4. Edge transitions --------------------------------------
        # Re-add old edges (copies) temporarily so they can fade out.
        for edge in old_edges:
            self += edge
            self._temp_mobs.append(edge)

        edge_out = [FadeOut(e) for e in old_edges]
        edge_in = [FadeIn(e) for e in self._edges]

        # -- 5. Assemble animation ------------------------------------
        # Everything plays simultaneously: cells slide to new positions
        # while old edges cross-fade to new edges and the new key fades
        # in at its gap. Using a single AnimationGroup (rather than
        # Succession) ensures that FadeIn.begin() is called at t=0
        # which hides new cells immediately — no premature flash.
        all_anims = move_anims + fade_in_anims + edge_out + edge_in

        if not all_anims:
            return Wait(0.5, **anim_args)

        return AnimationGroup(*all_anims, **anim_args)

    # ── insert helpers ────────────────────────────────────────────────

    def _find_leaf_for_key(self, key: Any) -> _BNode:
        current = self._root
        assert current is not None
        while not current.is_leaf():
            i = self._sorted_position(current, key)
            current = current.children[i]
        return current

    @staticmethod
    def _sorted_position(bnode: _BNode, key: Any) -> int:
        """Return the index where ``key`` would slot into ``bnode.keys``."""
        i = 0
        while i < len(bnode.keys) and bnode.keys[i] < key:
            i += 1
        return i

    def _split_node(self, bnode: _BNode) -> _BNode | None:
        """Split an overflowing node and promote the median.

        Returns the parent that may now itself be overflowing, or
        ``None`` if a brand-new root was created.
        """
        median_index = len(bnode.keys) // 2
        median_key = bnode.keys[median_index]

        # Take everything strictly to the right of the median.
        right_keys, _ = bnode.node.take_keys_after(median_index)
        # Drop the median itself from the left side.
        bnode.node.take_keys_after(median_index - 1)

        right_node = MBTreeNode(right_keys, style=self.style)
        right_bnode = _BNode(right_node)
        self += right_node

        # Reassign children: internal nodes have N+1 children for N keys.
        # The split point is one past the median index.
        if not bnode.is_leaf():
            split_at = median_index + 1
            right_bnode.children = bnode.children[split_at:]
            for child in right_bnode.children:
                child.parent = right_bnode
            bnode.children = bnode.children[:split_at]

        if bnode.parent is None:
            # Root just split — create a new root containing the median.
            new_root_node = MBTreeNode([median_key], style=self.style)
            new_root = _BNode(new_root_node)
            new_root.children = [bnode, right_bnode]
            bnode.parent = new_root
            right_bnode.parent = new_root
            self._root = new_root
            self += new_root_node
            return None

        # Insert the median into the parent at the correct position and
        # slot the new sibling in just after the original.
        parent = bnode.parent
        position = self._sorted_position(parent, median_key)
        parent.node.insert_key_at(position, median_key)
        original_index = parent.children.index(bnode)
        parent.children.insert(original_index + 1, right_bnode)
        right_bnode.parent = parent
        return parent

__all__ = ["MBTree"]
