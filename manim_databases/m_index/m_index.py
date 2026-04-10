"""MIndex: a visual database index that composes an MBTree with an MTable."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from manim import (
    Animation,
    Arrow,
    Create,
    FadeIn,
    FadeOut,
    Succession,
    SurroundingRectangle,
    VGroup,
    Wait,
    override_animate,
)

from manim_databases.constants import MIndexStyle
from manim_databases.m_btree.m_btree import MBTree
from manim_databases.m_table.m_row import MRow
from manim_databases.m_table.m_table import MTable
from manim_databases.utils.utils import Labelable


class MIndex(VGroup, Labelable):
    """A visual database index that composes an MBTree with an MTable.

    The index holds a B-tree whose leaf keys are values from one column
    of the table.  Each leaf key has a pointer arrow to the corresponding
    :class:`MRow` in the table.

    The hero animation is :meth:`lookup` — the search walks the B-tree,
    then follows the pointer arrow to highlight the matching row.

    Parameters
    ----------
    table : MTable
        The table this index points into.  The index does **not** own or
        manage the table — it just draws arrows to its rows.
    column : str
        Column name whose values become the B-tree keys.
    name : str, optional
        Human-readable index name (e.g. ``"idx_orders_total"``).  Used
        only for labels; does not affect behaviour.
    order : int, optional
        B-tree order.  Default ``4``.
    style : MIndexStyle._DefaultStyle, optional
        Style configuration.

    Examples
    --------
    >>> table = MTable(columns=["id", "total"], rows=[[1, 120], [2, 85]])
    >>> index = MIndex.from_table(table, "total")
    >>> self.play(Create(index))
    >>> self.play(index.animate.lookup(120))
    """

    def __init__(
        self,
        table: MTable,
        column: str,
        name: str | None = None,
        order: int = 4,
        style: MIndexStyle._DefaultStyle = MIndexStyle.DEFAULT,
    ):
        super().__init__()
        self.table = table
        self.column = column
        self.index_name = name
        self.order = order
        self.style = deepcopy(style)

        col_index = table._resolve_column(column)

        # Build the B-tree from column values.
        keys = [row.values[col_index] for row in table.rows]
        self.tree = MBTree(order=order, keys=keys, style=self.style.tree)
        self += self.tree

        # Map key value → MRow for pointer arrows.
        self._key_to_row: dict[Any, MRow] = {}
        for row in table.rows:
            val = row.values[col_index]
            self._key_to_row[val] = row

        # Arrows from leaf cells to table rows.
        self._arrows: list[Arrow] = []
        self._build_arrows()

    # ── construction ─────────────────────────────────────────────────

    @classmethod
    def from_table(
        cls,
        table: MTable,
        column: str,
        name: str | None = None,
        order: int = 4,
        style: MIndexStyle._DefaultStyle = MIndexStyle.DEFAULT,
    ) -> MIndex:
        """Build an index from an existing table and column.

        This is the primary construction API.  The index is positioned to
        the left of the table with pointer arrows drawn automatically.

        Parameters
        ----------
        table : MTable
            The table to index.
        column : str
            Column name to index.
        name : str, optional
            Index name for labelling.
        order : int, optional
            B-tree order.  Default ``4``.
        style : MIndexStyle._DefaultStyle, optional
            Style configuration.
        """
        index = cls(table, column, name=name, order=order, style=style)
        index._position_beside_table()
        index._rebuild_arrows()
        return index

    # ── layout ───────────────────────────────────────────────────────

    def _position_beside_table(self) -> None:
        """Place the tree to the left of the table with a gap."""
        self.tree.next_to(self.table, direction=[-1, 0, 0], buff=self.style.gap)

    def _build_arrows(self) -> None:
        """Create arrows from leaf B-tree cells to their matching table rows."""
        if self.tree._root is None:
            return

        for bnode in self.tree._bfs():
            if not bnode.is_leaf():
                continue
            for i, key in enumerate(bnode.keys):
                row = self._key_to_row.get(key)
                if row is None:
                    continue
                arrow = self._make_arrow(bnode.node, i, row)
                self._arrows.append(arrow)
                self += arrow

    def _rebuild_arrows(self) -> None:
        """Remove all arrows and recreate them from current positions."""
        for arrow in self._arrows:
            if arrow in self.submobjects:
                self -= arrow
        self._arrows = []
        self._build_arrows()

    def _make_arrow(
        self, node, key_index: int, row: MRow
    ) -> Arrow:
        """Build an arrow from a B-tree leaf cell to a table row."""
        cell = node.cells[key_index]
        start = cell.get_right()
        end = row.get_left()
        return Arrow(
            start, end,
            **self.style.arrow,
        )

    # ── lookup ───────────────────────────────────────────────────────

    def lookup(self, value: Any) -> MIndex:
        """Perform a lookup (non-animated). Use ``.animate.lookup(value)``."""
        return self

    @override_animate(lookup)
    def _lookup_animation(
        self, value: Any, anim_args: dict | None = None
    ) -> Animation:
        """Animated lookup: search the B-tree, then follow the pointer.

        1. Walk the B-tree search path, highlighting each comparison key.
        2. Highlight the pointer arrow from the found leaf to the table row.
        3. Highlight the matching row in the table.
        4. Fade everything out.
        """
        if anim_args is None:
            anim_args = {}

        path = self.tree.get_search_path(value)
        if not path:
            return Wait(0.1, **anim_args)

        anims: list[Animation] = []

        # Phase 1: walk the B-tree path with transient overlays.
        last_index = len(path) - 1
        for i, (node, key_index) in enumerate(path):
            is_last = i == last_index
            color = (
                self.style.found_color
                if is_last and key_index is not None
                else self.style.path_highlight_color
            )
            target = node if key_index is None else node.get_key_target(key_index)
            overlay = SurroundingRectangle(
                target, color=color, stroke_width=5, buff=0.05
            )
            anims.append(
                Succession(
                    FadeIn(overlay, run_time=0.2),
                    Wait(0.25),
                    FadeOut(overlay, run_time=0.2),
                )
            )

        # Phase 2: find the pointer arrow and highlight it + the row.
        row = self._key_to_row.get(value)
        arrow = self._find_arrow_for_key(value)
        if row is not None and arrow is not None:
            # Highlight the arrow
            arrow_overlay = arrow.copy().set_color(self.style.found_color)
            arrow_overlay.set_stroke(width=arrow.get_stroke_width() + 2)
            anims.append(
                Succession(
                    FadeIn(arrow_overlay, run_time=0.2),
                    Wait(0.3),
                    FadeOut(arrow_overlay, run_time=0.2),
                )
            )
            # Highlight the row
            row_overlay = SurroundingRectangle(
                row, color=self.style.found_color, stroke_width=5, buff=0.05
            )
            anims.append(
                Succession(
                    FadeIn(row_overlay, run_time=0.2),
                    Wait(0.5),
                    FadeOut(row_overlay, run_time=0.3),
                )
            )

        if not anims:
            return Wait(0.1, **anim_args)

        return Succession(*anims, **anim_args)

    def _find_arrow_for_key(self, key: Any) -> Arrow | None:
        """Find the arrow that connects a leaf key to its table row."""
        if self.tree._root is None:
            return None
        arrow_idx = 0
        for bnode in self.tree._bfs():
            if not bnode.is_leaf():
                continue
            for k in bnode.keys:
                if k not in self._key_to_row:
                    continue
                if k == key:
                    if arrow_idx < len(self._arrows):
                        return self._arrows[arrow_idx]
                    return None
                arrow_idx += 1
        return None

    # ── insert (index update after table row insert) ─────────────────

    def insert_key(self, value: Any, row: MRow) -> MIndex:
        """Insert a key into the index pointing to the given row.

        Call this after inserting a row into the table to keep the index
        in sync.

        Parameters
        ----------
        value : Any
            The column value to insert as a B-tree key.
        row : MRow
            The table row this key points to.
        """
        self._key_to_row[value] = row
        self.tree.insert(value)
        self._rebuild_arrows()
        return self

    @override_animate(insert_key)
    def _insert_key_animation(
        self, value: Any, row: MRow, anim_args: dict | None = None
    ) -> Animation:
        """Animated index update: insert key into B-tree, draw new arrow."""
        if anim_args is None:
            anim_args = {}

        self._key_to_row[value] = row
        self.tree.insert(value)
        self._rebuild_arrows()

        # Find the new arrow and fade it in.
        new_arrow = self._find_arrow_for_key(value)
        if new_arrow is not None:
            new_arrow_copy = new_arrow.copy()
            return Succession(
                Wait(0.1),
                Create(new_arrow_copy, run_time=0.4),
                **anim_args,
            )

        return Wait(0.3, **anim_args)


__all__ = ["MIndex"]
