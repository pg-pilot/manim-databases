"""MQueryPlan: animated query execution plan tree."""

from __future__ import annotations

from collections.abc import Iterator
from copy import deepcopy

from manim import (
    DOWN,
    Animation,
    AnimationGroup,
    Arrow,
    FadeIn,
    FadeOut,
    ShowPassingFlash,
    Succession,
    SurroundingRectangle,
    Text,
    VGroup,
    Wait,
    override_animate,
)

from manim_databases.constants import MQueryPlanStyle
from manim_databases.utils.utils import Labelable

# ── plan node mobject ────────────────────────────────────────────────


class _PlanNodeBox(VGroup):
    """A single operator box in the query plan tree.

    Renders as a SurroundingRectangle around stacked text lines:
      - Line 1 (bold): node type  (e.g. "Hash Join")
      - Line 2 (gray): relation or index name, if present
      - Line 3 (yellow): cost / rows annotation, if present

    The box width derives from the text content — no hardcoded size.
    """

    def __init__(self, spec: dict, style: MQueryPlanStyle._DefaultStyle):
        super().__init__()
        self.spec = spec

        # Line 1: node type (always present).
        node_type = spec.get("Node Type", "???")
        self.label = Text(str(node_type), **style.label)
        lines = [self.label]

        # Line 2: relation / index name.
        relation = spec.get("Relation Name") or spec.get("Index Name")
        self.detail: Text | None = None
        if relation:
            self.detail = Text(str(relation), **style.detail)
            lines.append(self.detail)

        # Line 3: cost / rows.
        cost_parts: list[str] = []
        if "Total Cost" in spec:
            cost_parts.append(f"cost: {spec['Total Cost']:.1f}")
        if "Plan Rows" in spec:
            cost_parts.append(f"rows: {spec['Plan Rows']}")
        self.cost_text: Text | None = None
        if cost_parts:
            self.cost_text = Text("  ".join(cost_parts), **style.cost)
            lines.append(self.cost_text)

        # Stack lines vertically.
        text_group = VGroup(*lines).arrange(DOWN, buff=0.08, aligned_edge=[0, 0, 0])
        self += text_group

        # Surround with a rounded rectangle.
        self.box = SurroundingRectangle(
            text_group, buff=style.node_buff, corner_radius=0.1, **style.node
        )
        self += self.box


# ── internal tree node ───────────────────────────────────────────────


class _PNode:
    """Internal tree-structure wrapper around a :class:`_PlanNodeBox`."""

    def __init__(self, box: _PlanNodeBox):
        self.box = box
        self.children: list[_PNode] = []
        self.parent: _PNode | None = None

    def is_leaf(self) -> bool:
        return not self.children


# ── MQueryPlan ───────────────────────────────────────────────────────


class MQueryPlan(VGroup, Labelable):
    """Animated query execution plan as a tree of operators.

    Renders a top-down operator tree matching PostgreSQL's
    ``EXPLAIN (FORMAT JSON)`` output.  Each node shows its type,
    optional relation name, and cost/rows annotation.

    The hero animation is :meth:`execute` — leaf nodes highlight first
    (they scan data), then data "flows" upward through edges to parent
    nodes, cascading to the root.

    Parameters
    ----------
    plan : dict
        Plan tree as a nested dict.  Each node has at least
        ``"Node Type"`` and may have ``"Plans"`` (children),
        ``"Total Cost"``, ``"Plan Rows"``, ``"Relation Name"``, etc.
    style : MQueryPlanStyle._DefaultStyle, optional
        Style configuration.
    max_width : float or None, optional
        If set, the tree is uniformly scaled so its width does not
        exceed this value.

    Examples
    --------
    >>> plan = {
    ...     "Node Type": "Hash Join",
    ...     "Total Cost": 1234.56,
    ...     "Plans": [
    ...         {"Node Type": "Seq Scan", "Relation Name": "orders"},
    ...         {"Node Type": "Index Scan", "Relation Name": "customers"},
    ...     ],
    ... }
    >>> mplan = MQueryPlan(plan, style=MQueryPlanStyle.BLUE)
    """

    def __init__(
        self,
        plan: dict,
        style: MQueryPlanStyle._DefaultStyle = MQueryPlanStyle.DEFAULT,
        max_width: float | None = None,
    ):
        super().__init__()
        self.style = deepcopy(style)
        self.max_width = max_width
        self._edges: list[Arrow] = []

        self._root = self._build_subtree(plan, parent=None)
        self._layout_tree()

    # ── construction ─────────────────────────────────────────────────

    def _build_subtree(self, spec: dict, parent: _PNode | None) -> _PNode:
        box = _PlanNodeBox(spec, self.style)
        pnode = _PNode(box)
        pnode.parent = parent
        self += box
        for child_spec in spec.get("Plans", []):
            pnode.children.append(self._build_subtree(child_spec, parent=pnode))
        return pnode

    # ── traversal ────────────────────────────────────────────────────

    def get_nodes(self) -> list[_PlanNodeBox]:
        """Return all node boxes in BFS order."""
        return [pn.box for pn in self._bfs()]

    def _bfs(self) -> Iterator[_PNode]:
        if self._root is None:
            return
        queue: list[_PNode] = [self._root]
        while queue:
            current = queue.pop(0)
            yield current
            queue.extend(current.children)

    def _leaves_bottom_up(self) -> list[list[_PNode]]:
        """Return nodes grouped by depth, deepest first.

        Used by the execute animation to highlight leaves first, then
        cascade upward level by level.
        """
        if self._root is None:
            return []
        levels: dict[int, list[_PNode]] = {}
        queue: list[tuple[_PNode, int]] = [(self._root, 0)]
        while queue:
            node, depth = queue.pop(0)
            levels.setdefault(depth, []).append(node)
            for child in node.children:
                queue.append((child, depth + 1))
        max_depth = max(levels) if levels else 0
        return [levels.get(d, []) for d in range(max_depth, -1, -1)]

    # ── layout ───────────────────────────────────────────────────────

    def _layout_tree(self) -> None:
        """Position all nodes top-down, rebuild edges, auto-fit."""
        if self._root is None:
            return
        self._layout_subtree(self._root, center_x=0.0, top_y=0.0)
        self._draw_edges()
        if self.max_width is not None and self.width > self.max_width:
            factor = self.max_width / self.width
            self.scale(factor, about_point=self.get_center())

    def _compute_subtree_width(self, pnode: _PNode) -> float:
        own_width = pnode.box.width
        if pnode.is_leaf():
            return own_width
        children_widths = [self._compute_subtree_width(c) for c in pnode.children]
        children_total = (
            sum(children_widths)
            + self.style.horizontal_gap * (len(children_widths) - 1)
        )
        return max(own_width, children_total)

    def _layout_subtree(
        self, pnode: _PNode, center_x: float, top_y: float
    ) -> None:
        pnode.box.move_to([center_x, top_y, 0])
        if pnode.is_leaf():
            return
        children_widths = [self._compute_subtree_width(c) for c in pnode.children]
        total = sum(children_widths) + self.style.horizontal_gap * (
            len(children_widths) - 1
        )
        x = center_x - total / 2
        child_y = top_y - self.style.vertical_gap
        for child, w in zip(pnode.children, children_widths, strict=True):
            self._layout_subtree(child, x + w / 2, child_y)
            x += w + self.style.horizontal_gap

    # ── edges ────────────────────────────────────────────────────────

    def _draw_edges(self) -> None:
        """Create arrows from children to parents (data flows upward)."""
        for edge in self._edges:
            self -= edge
        self._edges = []
        for pnode in self._bfs():
            for child in pnode.children:
                arrow = Arrow(
                    child.box.get_top(),
                    pnode.box.get_bottom(),
                    **self.style.edge,
                    tip_length=self.style.arrow_tip_length,
                    buff=0.05,
                )
                self._edges.append(arrow)
                self += arrow

    def _find_edge(self, child: _PNode, parent: _PNode) -> Arrow | None:
        """Find the arrow connecting child → parent."""
        idx = 0
        for pnode in self._bfs():
            for c in pnode.children:
                if c is child and pnode is parent:
                    if idx < len(self._edges):
                        return self._edges[idx]
                    return None
                idx += 1
        return None

    # ── execute animation ────────────────────────────────────────────

    def execute(self) -> MQueryPlan:
        """Execute the plan (non-animated). Use ``.animate.execute()``."""
        return self

    @override_animate(execute)
    def _execute_animation(
        self, anim_args: dict | None = None
    ) -> Animation:
        """Animate execution flowing upward through the plan tree.

        Nodes light up level-by-level from leaves to root and **stay
        lit** — the viewer sees the active frontier build up.  After
        each level's nodes highlight, data pulses up the edges to the
        next level.  Once the root lights up, all overlays hold briefly
        then fade out together.
        """
        if anim_args is None:
            anim_args = {}
        if self._root is None:
            return Wait(0.1, **anim_args)

        levels = self._leaves_bottom_up()
        anims: list[Animation] = []
        all_overlays: list[SurroundingRectangle] = []

        for level_nodes in levels:
            # Phase A: light up every node at this level (simultaneously).
            node_fade_ins: list[Animation] = []
            for pnode in level_nodes:
                overlay = SurroundingRectangle(
                    pnode.box,
                    color=self.style.execute_color,
                    stroke_width=4,
                    buff=0.05,
                    corner_radius=0.1,
                )
                all_overlays.append(overlay)
                node_fade_ins.append(FadeIn(overlay, run_time=0.25))

            if node_fade_ins:
                anims.append(AnimationGroup(*node_fade_ins))

            # Phase B: pulse data up edges from this level to parent.
            edge_flashes: list[Animation] = []
            for pnode in level_nodes:
                if pnode.parent is not None:
                    edge = self._find_edge(pnode, pnode.parent)
                    if edge is not None:
                        flash = edge.copy()
                        flash.set_color(self.style.flow_color)
                        flash.set_stroke(width=edge.get_stroke_width() + 3)
                        edge_flashes.append(
                            ShowPassingFlash(
                                flash, time_width=0.4, run_time=0.45
                            )
                        )
            if edge_flashes:
                anims.append(AnimationGroup(*edge_flashes))

        # Hold the fully-lit state, then fade everything out.
        if all_overlays:
            anims.append(Wait(0.6))
            anims.append(
                AnimationGroup(
                    *[FadeOut(o, run_time=0.3) for o in all_overlays]
                )
            )

        if not anims:
            return Wait(0.1, **anim_args)

        return Succession(*anims, **anim_args)


__all__ = ["MQueryPlan"]
