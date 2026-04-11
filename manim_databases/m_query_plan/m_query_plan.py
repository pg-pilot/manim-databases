"""MQueryPlan: animated query execution plan tree."""

from __future__ import annotations

from collections.abc import Iterator
from copy import deepcopy

from manim import (
    DOWN,
    Animation,
    Arrow,
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


# ── leak-free execute animation ──────────────────────────────────────


class _ExecuteFlow(Animation):
    """Progressively light up plan nodes from leaves to root.

    A single Animation on the plan VGroup that manages overlay opacities
    directly in ``interpolate_mobject``.  Avoids AnimationGroup /
    Succession whose ``_setup_scene`` adds all overlays at t=0.

    Timeline (mapped to alpha 0→1):

    - **Active phase** (0 → 0.75): each level gets a slice.  Within a
      level's slice, the first half fades in node overlays, the second
      half flashes the upward edges yellow.
    - **Hold phase** (0.75 → 0.88): everything stays lit.
    - **Fade-out phase** (0.88 → 1.0): all overlays fade to 0 and are
      removed from the plan VGroup.
    """

    _ACTIVE = 0.75
    _HOLD_END = 0.88

    def __init__(self, plan: MQueryPlan, **kwargs):
        kwargs.setdefault("run_time", 3.0)
        self._plan = plan
        self._levels = plan._leaves_bottom_up()
        self._n_levels = max(len(self._levels), 1)

        # Pre-create overlays (invisible) and add to plan VGroup.
        self._level_overlays: list[list[SurroundingRectangle]] = []
        self._all_overlays: list[SurroundingRectangle] = []
        for level_nodes in self._levels:
            level_ovs = []
            for pnode in level_nodes:
                ov = SurroundingRectangle(
                    pnode.box,
                    color=plan.style.execute_color,
                    stroke_width=4,
                    buff=0.05,
                    corner_radius=0.1,
                )
                ov.set_stroke(opacity=0)
                plan += ov
                level_ovs.append(ov)
                self._all_overlays.append(ov)
            self._level_overlays.append(level_ovs)

        # Collect edges per level (child→parent arrows to flash).
        self._level_edges: list[list[Arrow]] = []
        self._edge_base_colors: dict[int, object] = {}
        for level_nodes in self._levels:
            edges = []
            for pnode in level_nodes:
                if pnode.parent is not None:
                    edge = plan._find_edge(pnode, pnode.parent)
                    if edge is not None:
                        self._edge_base_colors[id(edge)] = edge.get_color()
                        edges.append(edge)
            self._level_edges.append(edges)

        super().__init__(plan, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        active = self._ACTIVE
        hold_end = self._HOLD_END

        if alpha <= active:
            # ── Active phase: light up level by level ────────────────
            for i in range(self._n_levels):
                level_start = (i / self._n_levels) * active
                level_mid = ((i + 0.5) / self._n_levels) * active
                level_end = ((i + 1) / self._n_levels) * active

                # Node overlays: fade in during [level_start, level_mid].
                if i < len(self._level_overlays):
                    if alpha < level_start:
                        t = 0.0
                    elif alpha < level_mid:
                        t = (alpha - level_start) / (level_mid - level_start)
                    else:
                        t = 1.0
                    for ov in self._level_overlays[i]:
                        ov.set_stroke(opacity=t)

                # Edge flash: glow yellow during [level_mid, level_end].
                if i < len(self._level_edges):
                    for edge in self._level_edges[i]:
                        base_color = self._edge_base_colors[id(edge)]
                        if level_mid <= alpha < level_end:
                            progress = (alpha - level_mid) / (
                                level_end - level_mid
                            )
                            # Flash up then back: peak at progress=0.5.
                            intensity = 1.0 - abs(2.0 * progress - 1.0)
                            edge.set_color(
                                self._plan.style.flow_color
                            )
                            edge.set_stroke(
                                width=self._plan.style.edge["stroke_width"]
                                + 3 * intensity,
                            )
                        else:
                            edge.set_color(base_color)
                            edge.set_stroke(
                                width=self._plan.style.edge["stroke_width"],
                            )

        elif alpha <= hold_end:
            # ── Hold phase: everything stays fully lit ───────────────
            for ov in self._all_overlays:
                ov.set_stroke(opacity=1.0)
            # Restore edge colors.
            for edges in self._level_edges:
                for edge in edges:
                    edge.set_color(self._edge_base_colors[id(edge)])
                    edge.set_stroke(
                        width=self._plan.style.edge["stroke_width"]
                    )

        else:
            # ── Fade-out phase: all overlays fade together ───────────
            t = (alpha - hold_end) / (1.0 - hold_end)
            for ov in self._all_overlays:
                ov.set_stroke(opacity=1.0 - t)

    def clean_up_from_scene(self, scene) -> None:
        # Ensure final state and remove overlays from the plan VGroup.
        self.interpolate_mobject(1.0)
        for ov in self._all_overlays:
            if ov in self._plan.submobjects:
                self._plan -= ov


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

        Uses a custom :class:`_ExecuteFlow` animation that directly
        manages overlay opacities — avoiding Succession/AnimationGroup
        whose ``_setup_scene`` adds all overlays to the scene at t=0.

        Nodes light up level-by-level from leaves to root and stay lit.
        Between levels, edges briefly glow to show data flowing upward.
        Once the root lights up, everything holds then fades out.
        """
        if anim_args is None:
            anim_args = {}
        if self._root is None:
            return Wait(0.1, **anim_args)

        return _ExecuteFlow(self, **anim_args)


__all__ = ["MQueryPlan"]
