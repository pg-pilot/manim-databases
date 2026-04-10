"""MBTreeNode: a single B-tree node, rendered as a horizontal strip of keys."""

from __future__ import annotations

from typing import Any

import numpy as np
from manim import DL, DR, Rectangle, Text, VGroup

from manim_databases.constants import MBTreeStyle
from manim_databases.utils.utils import Highlightable


class MBTreeNode(VGroup, Highlightable):
    """A single B-tree node — a horizontal strip of cells, one per key.

    A node with N keys has N cells and N+1 child slots (gaps), labeled
    ``0`` through ``N``. Edges from a parent node attach to specific gaps:

    - gap 0  → before the first key
    - gap i  → between key (i-1) and key i
    - gap N  → after the last key

    Use :meth:`get_gap_bottom` to retrieve the (x, y, z) attachment point
    for an edge originating from a given gap. The point lies on the bottom
    edge of the node so that downward edges look natural.

    Parameters
    ----------
    keys : list
        Initial keys, in sorted order. Each is converted to a string for
        rendering. The order is the caller's responsibility — this class
        does not sort.
    style : MBTreeStyle._DefaultStyle
        Style configuration controlling cell and key appearance.
    """

    def __init__(
        self,
        keys: list[Any],
        style: MBTreeStyle._DefaultStyle = MBTreeStyle.DEFAULT,
    ):
        super().__init__()
        self.style = style
        self.keys: list[Any] = list(keys)
        self.cells: list[Rectangle] = []
        self.key_texts: list[Text] = []

        for i, key in enumerate(self.keys):
            cell, text = self._build_cell(key)
            if i == 0:
                cell.move_to([0, 0, 0])
            else:
                cell.next_to(self.cells[-1], direction=[1, 0, 0], buff=0)
            text.move_to(cell)
            self.cells.append(cell)
            self.key_texts.append(text)
            self += cell
            self += text

        if self.cells:
            self._add_highlight(VGroup(*self.cells))

    # ── helpers ───────────────────────────────────────────────────────

    def _build_cell(self, key: Any) -> tuple[Rectangle, Text]:
        cell = Rectangle(**self.style.node)
        text = Text(str(key), **self.style.key).move_to(cell)
        return cell, text

    # ── public API ────────────────────────────────────────────────────

    def get_gap_bottom(self, gap_index: int) -> np.ndarray:
        """Return the bottom-edge attachment point for a child slot.

        Parameters
        ----------
        gap_index : int
            Index in ``[0, len(self.keys)]``. ``0`` is before the first key,
            ``len(self.keys)`` is after the last key, and intermediate values
            are between adjacent cells.
        """
        if not self.cells:
            return self.get_bottom()

        n = len(self.cells)
        if gap_index < 0 or gap_index > n:
            raise IndexError(
                f"gap_index {gap_index} out of range for node with {n} cells"
            )

        if gap_index == 0:
            return self.cells[0].get_corner(DL)
        if gap_index == n:
            return self.cells[-1].get_corner(DR)
        # Between cells[gap_index - 1] and cells[gap_index] — they share a
        # border, so either corner works.
        return self.cells[gap_index - 1].get_corner(DR)

    def get_key_target(self, key_index: int) -> VGroup:
        """Return a VGroup of (cell, text) for animating a single key.

        Useful for ``Indicate``-style highlights of a specific key during
        search animations.
        """
        return VGroup(self.cells[key_index], self.key_texts[key_index])

    def insert_key_at(self, position: int, key: Any) -> tuple[Rectangle, Text]:
        """Insert a key at the given position and reflow cells around the
        node's existing center.

        After this call, every cell in the node is repositioned left-to-right
        anchored on the same center, so the node grows symmetrically and
        existing cells slide instead of overlapping. The new cell is also
        scaled to match the size of existing cells (so a post-construction
        ``.scale()`` on the parent tree doesn't break the layout).
        """
        old_center = (
            self.get_center().copy()
            if self.cells
            else np.array([0.0, 0.0, 0.0])
        )

        cell, text = self._build_cell(key)

        # Match the scale of existing cells if the parent tree was scaled
        # after construction.
        if self.cells:
            ref = self.cells[0]
            if cell.width > 0 and not np.isclose(ref.width, cell.width):
                factor = ref.width / cell.width
                cell.scale(factor)
                text.scale(factor)

        self.keys.insert(position, key)
        self.cells.insert(position, cell)
        self.key_texts.insert(position, text)
        self += cell
        self += text

        self._reflow_around(old_center)
        return cell, text

    def take_keys_after(self, position: int) -> tuple[list[Any], VGroup]:
        """Remove all keys at index ``> position`` and return them.

        After removal, the remaining cells reflow around the original
        node center so the node shrinks symmetrically.

        Returns
        -------
        (removed_keys, removed_mobjects) : (list, VGroup)
            The removed key values and the mobjects (cells + texts) that
            were detached from this node.
        """
        if position < 0 or position >= len(self.cells):
            return [], VGroup()

        old_center = self.get_center().copy()

        removed_keys = self.keys[position + 1 :]
        removed_cells = self.cells[position + 1 :]
        removed_texts = self.key_texts[position + 1 :]

        self.keys = self.keys[: position + 1]
        self.cells = self.cells[: position + 1]
        self.key_texts = self.key_texts[: position + 1]

        removed_mobjects = VGroup(*removed_cells, *removed_texts)
        for m in removed_mobjects:
            self -= m

        self._reflow_around(old_center)
        return removed_keys, removed_mobjects

    def _reflow_around(self, center: np.ndarray) -> None:
        """Position all cells left-to-right, centered on ``center``.

        Reads the cell width from the first existing cell so the layout
        is correct even if the parent tree has been scaled.
        """
        if not self.cells:
            return
        cell_w = self.cells[0].width
        n = len(self.cells)
        total_w = n * cell_w
        cx, cy = float(center[0]), float(center[1])
        start_x = cx - total_w / 2
        for i, cell in enumerate(self.cells):
            cell.move_to([start_x + cell_w * (i + 0.5), cy, 0])
            self.key_texts[i].move_to(cell)
