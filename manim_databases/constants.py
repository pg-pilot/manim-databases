"""Style configurations for all manim-databases mobjects.

Each mobject has its own ``*Style`` class with ``DEFAULT``, ``BLUE``, ``PURPLE``,
and ``GREEN`` variants. Subclass ``_DefaultStyle`` to build custom styles.
"""

from __future__ import annotations

from manim import (
    BLUE_B,
    BLUE_D,
    BOLD,
    GRAY,
    GREEN_B,
    GREEN_D,
    PURPLE_B,
    PURPLE_D,
    WHITE,
    YELLOW,
    ManimColor,
)


class MTableStyle:
    """Style configuration for :class:`~manim_databases.m_table.m_table.MTable`.

    Attributes
    ----------
    DEFAULT : MTableStyle._DefaultStyle
        Clean default style with white outlines.
    BLUE : MTableStyle._BlueStyle
        Blue accent variant.
    PURPLE : MTableStyle._PurpleStyle
        Purple accent variant.
    GREEN : MTableStyle._GreenStyle
        Green accent variant.
    """

    class _DefaultStyle:
        """Default table style — white outlines, neutral text."""

        def __init__(self):
            self.cell: dict = {
                "color": WHITE,
                "stroke_width": 4,
                "width": 2.0,
                "height": 0.6,
            }
            self.header_cell: dict = {
                "color": WHITE,
                "stroke_width": 4,
                "width": 2.0,
                "height": 0.7,
                "fill_opacity": 0.15,
            }
            self.value: dict = {
                "color": WHITE,
                "font": "Cascadia Code",
                "font_size": 22,
                "disable_ligatures": True,
            }
            self.header: dict = {
                "color": WHITE,
                "font": "Cascadia Code",
                "font_size": 22,
                "disable_ligatures": True,
                "weight": BOLD,
            }
            self.primary_key_color: ManimColor = YELLOW
            self.row_highlight_color: ManimColor = GRAY

    class _BlueStyle(_DefaultStyle):
        """Blue accent style."""

        def __init__(self):
            super().__init__()
            self.cell: dict = {
                "color": BLUE_B,
                "fill_color": BLUE_D,
                "stroke_width": 4,
                "fill_opacity": 0.2,
                "width": 2.0,
                "height": 0.6,
            }
            self.header_cell: dict = {
                "color": BLUE_B,
                "fill_color": BLUE_D,
                "stroke_width": 4,
                "fill_opacity": 0.5,
                "width": 2.0,
                "height": 0.7,
            }

    class _PurpleStyle(_DefaultStyle):
        """Purple accent style."""

        def __init__(self):
            super().__init__()
            self.cell: dict = {
                "color": PURPLE_B,
                "fill_color": PURPLE_D,
                "stroke_width": 4,
                "fill_opacity": 0.2,
                "width": 2.0,
                "height": 0.6,
            }
            self.header_cell: dict = {
                "color": PURPLE_B,
                "fill_color": PURPLE_D,
                "stroke_width": 4,
                "fill_opacity": 0.5,
                "width": 2.0,
                "height": 0.7,
            }

    class _GreenStyle(_DefaultStyle):
        """Green accent style."""

        def __init__(self):
            super().__init__()
            self.cell: dict = {
                "color": GREEN_B,
                "fill_color": GREEN_D,
                "stroke_width": 4,
                "fill_opacity": 0.2,
                "width": 2.0,
                "height": 0.6,
            }
            self.header_cell: dict = {
                "color": GREEN_B,
                "fill_color": GREEN_D,
                "stroke_width": 4,
                "fill_opacity": 0.5,
                "width": 2.0,
                "height": 0.7,
            }

    DEFAULT = _DefaultStyle()
    BLUE = _BlueStyle()
    PURPLE = _PurpleStyle()
    GREEN = _GreenStyle()


class MBTreeStyle:
    """Style configuration for :class:`~manim_databases.m_btree.m_btree.MBTree`."""

    class _DefaultStyle:
        def __init__(self):
            self.node: dict = {
                "color": WHITE,
                "stroke_width": 4,
                "width": 1.6,
                "height": 0.6,
            }
            self.key: dict = {
                "color": WHITE,
                "font": "Cascadia Code",
                "font_size": 22,
                "disable_ligatures": True,
                "weight": BOLD,
            }
            self.edge: dict = {
                "color": GRAY,
                "stroke_width": 5,
            }

    DEFAULT = _DefaultStyle()


class MIndexStyle:
    """Style configuration for :class:`~manim_databases.m_index.m_index.MIndex`."""

    class _DefaultStyle:
        def __init__(self):
            self.entry: dict = {
                "color": WHITE,
                "stroke_width": 4,
                "width": 2.5,
                "height": 0.5,
            }
            self.key: dict = {
                "color": WHITE,
                "font": "Cascadia Code",
                "font_size": 20,
                "disable_ligatures": True,
            }
            self.pointer: dict = {
                "color": GRAY,
                "stroke_width": 4,
            }

    DEFAULT = _DefaultStyle()


class MQueryPlanStyle:
    """Style configuration for :class:`~manim_databases.m_query_plan.m_query_plan.MQueryPlan`."""

    class _DefaultStyle:
        def __init__(self):
            self.node: dict = {
                "color": WHITE,
                "stroke_width": 4,
                "width": 3.0,
                "height": 1.0,
            }
            self.label: dict = {
                "color": WHITE,
                "font": "Cascadia Code",
                "font_size": 20,
                "disable_ligatures": True,
                "weight": BOLD,
            }
            self.cost: dict = {
                "color": YELLOW,
                "font": "Cascadia Code",
                "font_size": 16,
                "disable_ligatures": True,
            }
            self.edge: dict = {
                "color": GRAY,
                "stroke_width": 4,
            }

    DEFAULT = _DefaultStyle()


class MWalStyle:
    """Style configuration for :class:`~manim_databases.m_wal.m_wal.MWal`."""

    class _DefaultStyle:
        def __init__(self):
            self.entry: dict = {
                "color": WHITE,
                "stroke_width": 4,
                "width": 1.0,
                "height": 0.5,
            }
            self.lsn: dict = {
                "color": WHITE,
                "font": "Cascadia Code",
                "font_size": 16,
                "disable_ligatures": True,
            }

    DEFAULT = _DefaultStyle()


class MReplicationTopologyStyle:
    """Style for :class:`~manim_databases.m_replication.m_replication_topology.MReplicationTopology`."""

    class _DefaultStyle:
        def __init__(self):
            self.primary_node: dict = {
                "color": YELLOW,
                "stroke_width": 6,
                "radius": 0.5,
            }
            self.replica_node: dict = {
                "color": WHITE,
                "stroke_width": 4,
                "radius": 0.4,
            }
            self.replication_edge: dict = {
                "color": GRAY,
                "stroke_width": 5,
            }

    DEFAULT = _DefaultStyle()


class MLockStyle:
    """Style configuration for :class:`~manim_databases.m_lock.m_lock.MLock`."""

    class _DefaultStyle:
        def __init__(self):
            self.lock_icon: dict = {
                "color": YELLOW,
                "stroke_width": 4,
            }
            self.waiter: dict = {
                "color": GRAY,
                "stroke_width": 3,
            }

    DEFAULT = _DefaultStyle()
