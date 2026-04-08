"""MTable: animated database table mobject."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from manim import (
    DOWN,
    Animation,
    ApplyMethod,
    FadeIn,
    FadeOut,
    Indicate,
    Rectangle,
    Succession,
    Text,
    VGroup,
    Write,
    override_animate,
)

from manim_databases.constants import MTableStyle
from manim_databases.m_table.m_row import MRow
from manim_databases.utils.utils import Labelable


class MTable(VGroup, Labelable):
    """An animated database table.

    Renders columns and rows as a grid of cells with optional primary-key
    highlighting and animated CRUD operations.

    Parameters
    ----------
    columns : list[str]
        Column names, displayed as the header row.
    rows : list[list], optional
        Initial row values. Each inner list must have ``len(columns)`` items.
    primary_key : str or None, optional
        Name of the primary key column. When set, the column is tinted with
        ``style.primary_key_color`` to make it visually distinct.
    style : MTableStyle._DefaultStyle, optional
        Style configuration. Default ``MTableStyle.DEFAULT``.

    Examples
    --------
    >>> table = MTable(
    ...     columns=["id", "name", "status"],
    ...     rows=[[1, "alice", "active"], [2, "bob", "pending"]],
    ...     primary_key="id",
    ...     style=MTableStyle.BLUE,
    ... )
    >>> self.play(Create(table))
    >>> self.play(table.animate.insert_row([3, "carol", "active"]))
    >>> self.play(table.animate.update_cell(1, "status", "active"))
    >>> self.play(table.animate.delete_row(0))
    """

    def __init__(
        self,
        columns: list[str],
        rows: list[list[Any]] = None,
        primary_key: str | None = None,
        style: MTableStyle._DefaultStyle = MTableStyle.DEFAULT,
    ):
        super().__init__()
        if rows is None:
            rows = []

        self.columns = list(columns)
        self.style = deepcopy(style)
        self.primary_key = primary_key
        self.primary_key_index = (
            columns.index(primary_key) if primary_key in columns else None
        )

        self._column_widths = self._compute_column_widths(columns, rows)

        self.header: VGroup = self._build_header()
        self += self.header

        self.rows: list[MRow] = []
        for row_values in rows:
            self._append_row_internal(row_values)

        if self.primary_key_index is not None:
            self._tint_primary_key_column()

        self.move_to([0, 0, 0])

    # ── construction helpers ──────────────────────────────────────────

    def _compute_column_widths(
        self, columns: list[str], rows: list[list[Any]]
    ) -> list[float]:
        """Use a single uniform width for now.

        Future versions can autosize per column based on the longest value.
        """
        return [self.style.cell["width"]] * len(columns)

    def _build_header(self) -> VGroup:
        header_group = VGroup()
        previous_cell: Rectangle | None = None
        self.header_cells: list[Rectangle] = []
        self.header_texts: list[Text] = []

        for i, name in enumerate(self.columns):
            cell_kwargs = dict(self.style.header_cell)
            cell_kwargs["width"] = self._column_widths[i]
            cell = Rectangle(**cell_kwargs)

            if previous_cell is None:
                cell.move_to([0, 0, 0])
            else:
                cell.next_to(previous_cell, direction=[1, 0, 0], buff=0)

            text = Text(str(name), **self.style.header).move_to(cell)
            self.header_cells.append(cell)
            self.header_texts.append(text)
            header_group += cell
            header_group += text
            previous_cell = cell

        return header_group

    def _append_row_internal(self, values: list[Any]) -> MRow:
        """Add a row to the geometry without animations.

        New rows are created at the original (unscaled) style size and then
        scaled to match the existing geometry. This is necessary because the
        table may have been scaled or transformed after construction, and
        ``self.style.cell['width']`` no longer reflects the on-screen size.
        """
        if len(values) != len(self.columns):
            raise ValueError(
                f"Row has {len(values)} values but table has "
                f"{len(self.columns)} columns"
            )

        row = MRow(values, style=self.style, column_widths=self._column_widths)

        # Scale the new row to match the current geometry of existing rows
        # (or the header if this is the first data row). Without this, a
        # post-construction ``.scale()`` call leaves new rows at the original
        # size, breaking the column alignment.
        reference_cell = (
            self.rows[0].cells[0] if self.rows else self.header_cells[0]
        )
        new_cell = row.cells[0]
        if new_cell.width > 0 and reference_cell.width != new_cell.width:
            row.scale(reference_cell.width / new_cell.width)

        self._position_row_below_last(row)
        self.rows.append(row)
        self += row
        return row

    def _position_row_below_last(self, row: MRow) -> None:
        """Snap a new row directly under the last existing row (or header)."""
        anchor = self.rows[-1] if self.rows else self.header
        row.next_to(anchor, DOWN, buff=0)

    def _tint_primary_key_column(self) -> None:
        """Color the primary key column header to mark it visually.

        The stroke width is kept the same as the surrounding cells. A wider
        stroke would visually leak onto the top edge of adjacent data cells
        because borders are shared at ``buff=0``.
        """
        if self.primary_key_index is None:
            return
        pk_color = self.style.primary_key_color
        header_cell = self.header_cells[self.primary_key_index]
        header_cell.set_stroke(pk_color, width=header_cell.stroke_width)
        self.header_texts[self.primary_key_index].set_color(pk_color)

    # ── public API ────────────────────────────────────────────────────

    def insert_row(self, values: list[Any]) -> MTable:
        """Append a row to the bottom of the table.

        Parameters
        ----------
        values : list
            Cell values matching ``self.columns`` length.
        """
        self._append_row_internal(values)
        return self

    @override_animate(insert_row)
    def _insert_row_animation(
        self, values: list[Any], anim_args: dict = None
    ) -> Animation:
        if anim_args is None:
            anim_args = {}
        self.insert_row(values)
        return Write(self.rows[-1], **anim_args)

    def delete_row(self, row_index: int) -> MTable:
        """Remove a row by position and shift everything below upward."""
        if not 0 <= row_index < len(self.rows):
            raise IndexError(f"Row index {row_index} out of range")

        # Capture the removed row's actual height *before* removing it so the
        # shift amount stays correct under any post-construction transforms.
        shift_amount = self.rows[row_index].height

        removed = self.rows.pop(row_index)
        self -= removed

        below = VGroup(*self.rows[row_index:])
        if len(below) > 0:
            below.shift([0, shift_amount, 0])
        return self

    @override_animate(delete_row)
    def _delete_row_animation(
        self, row_index: int, anim_args: dict = None
    ) -> Animation:
        if anim_args is None:
            anim_args = {}
        if not 0 <= row_index < len(self.rows):
            raise IndexError(f"Row index {row_index} out of range")

        shift_amount = self.rows[row_index].height
        removed = self.rows.pop(row_index)
        self -= removed

        below = VGroup(*self.rows[row_index:])
        anims = [FadeOut(removed)]
        if len(below) > 0:
            anims.append(ApplyMethod(below.shift, [0, shift_amount, 0]))
        return Succession(*anims, **anim_args, group=VGroup(self, removed))

    def update_cell(
        self, row_index: int, column: int | str, new_value: Any
    ) -> MTable:
        """Replace a cell value in place.

        Parameters
        ----------
        row_index : int
            Row position.
        column : int or str
            Column position or column name.
        new_value : Any
            New value (coerced to string for display).
        """
        col_index = self._resolve_column(column)
        self.rows[row_index].set_cell_value(col_index, new_value)
        return self

    @override_animate(update_cell)
    def _update_cell_animation(
        self,
        row_index: int,
        column: int | str,
        new_value: Any,
        anim_args: dict = None,
    ) -> Indicate:
        if anim_args is None:
            anim_args = {}
        self.update_cell(row_index, column, new_value)
        col_index = self._resolve_column(column)
        return Indicate(self.rows[row_index].value_texts[col_index], **anim_args)

    def highlight_row(self, row_index: int) -> MTable:
        """Apply a highlight stroke to a row."""
        self.rows[row_index].highlight()
        return self

    @override_animate(highlight_row)
    def _highlight_row_animation(
        self, row_index: int, anim_args: dict = None
    ) -> Animation:
        if anim_args is None:
            anim_args = {}
        return self.rows[row_index]._highlight_animation(anim_args=anim_args)

    def unhighlight_row(self, row_index: int) -> MTable:
        """Remove the highlight from a row."""
        self.rows[row_index].unhighlight()
        return self

    def get_row(self, row_index: int) -> MRow:
        """Return the :class:`MRow` at a given position."""
        return self.rows[row_index]

    def get_cell_value(self, row_index: int, column: int | str) -> Any:
        """Return the current value of a cell."""
        col_index = self._resolve_column(column)
        return self.rows[row_index].values[col_index]

    def __getitem__(self, row_index: int) -> MRow:
        return self.rows[row_index]

    def __len__(self) -> int:
        return len(self.rows)

    # ── internals ─────────────────────────────────────────────────────

    def _resolve_column(self, column: int | str) -> int:
        if isinstance(column, int):
            return column
        try:
            return self.columns.index(column)
        except ValueError as exc:
            raise KeyError(f"Unknown column: {column!r}") from exc
