"""Row mobject — a single horizontal strip of cells in a :class:`MTable`."""

from __future__ import annotations

from typing import Any

from manim import Rectangle, Text, VGroup

from manim_databases.constants import MTableStyle
from manim_databases.utils.utils import Highlightable, set_text


class MRow(VGroup, Highlightable):
    """A single row in an :class:`~manim_databases.m_table.m_table.MTable`.

    Each row is a :class:`VGroup` of cell rectangles paired with their value
    text. The first cell is the highlight target so :meth:`highlight` paints
    the whole row uniformly.

    Parameters
    ----------
    values : list
        Cell values, one per column. Converted to strings for rendering.
    style : MTableStyle._DefaultStyle
        Style configuration controlling cell and value appearance.
    column_widths : list[float] or None
        Per-column widths. If ``None``, every cell uses ``style.cell['width']``.
    """

    def __init__(
        self,
        values: list[Any],
        style: MTableStyle._DefaultStyle = MTableStyle.DEFAULT,
        column_widths: list[float] | None = None,
    ):
        super().__init__()
        self.style = style
        self.values = list(values)
        self.cells: list[Rectangle] = []
        self.value_texts: list[Text] = []

        previous_cell: Rectangle | None = None
        for i, value in enumerate(values):
            cell_kwargs = dict(style.cell)
            if column_widths is not None:
                cell_kwargs["width"] = column_widths[i]
            cell = Rectangle(**cell_kwargs)

            if previous_cell is None:
                cell.move_to([0, 0, 0])
            else:
                # Place edge-to-edge so cell borders share a line.
                cell.next_to(previous_cell, direction=[1, 0, 0], buff=0)

            text = Text(str(value), **style.value).move_to(cell)

            self.cells.append(cell)
            self.value_texts.append(text)
            self += cell
            self += text
            previous_cell = cell

        # Highlight the entire row by enclosing all cells.
        if self.cells:
            row_box = VGroup(*self.cells)
            self._add_highlight(row_box)

    def get_cell(self, column_index: int) -> Rectangle:
        """Return the rectangle for a column position."""
        return self.cells[column_index]

    def get_value_text(self, column_index: int) -> Text:
        """Return the value text mobject for a column position."""
        return self.value_texts[column_index]

    def set_cell_value(self, column_index: int, new_value: Any) -> MRow:
        """Replace a cell's value text in place.

        Parameters
        ----------
        column_index : int
            Position of the column to update.
        new_value : Any
            New value (will be coerced to string).
        """
        old_text = self.value_texts[column_index]
        self -= old_text
        new_text = set_text(old_text, str(new_value))
        self.value_texts[column_index] = new_text
        self.values[column_index] = new_value
        self += new_text
        return self
