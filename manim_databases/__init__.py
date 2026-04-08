"""manim-databases: a Manim plugin for animating database concepts.

Public API:
    - :class:`MTable`: animated database table
    - :class:`MBTree`: B-tree with insertion and search animations (stub)
    - :class:`MIndex`: visual index structure (stub)
    - :class:`MQueryPlan`: execution plan tree (stub)
    - :class:`MWal`: write-ahead log (stub)
    - :class:`MReplicationTopology`: primary/replica topology (stub)
    - :class:`MLock`: lock visualization (stub)

Style classes are exported alongside their mobjects (``MTableStyle``, etc.).
"""

from importlib.metadata import PackageNotFoundError, version

from manim_databases.constants import (
    MBTreeStyle,
    MIndexStyle,
    MLockStyle,
    MQueryPlanStyle,
    MReplicationTopologyStyle,
    MTableStyle,
    MWalStyle,
)
from manim_databases.m_btree.m_btree import MBTree
from manim_databases.m_index.m_index import MIndex
from manim_databases.m_lock.m_lock import MLock
from manim_databases.m_query_plan.m_query_plan import MQueryPlan
from manim_databases.m_replication.m_replication_topology import MReplicationTopology
from manim_databases.m_table.m_table import MTable
from manim_databases.m_wal.m_wal import MWal

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    __version__ = "0.1.0"

__all__ = [
    "MTable",
    "MTableStyle",
    "MBTree",
    "MBTreeStyle",
    "MIndex",
    "MIndexStyle",
    "MQueryPlan",
    "MQueryPlanStyle",
    "MWal",
    "MWalStyle",
    "MReplicationTopology",
    "MReplicationTopologyStyle",
    "MLock",
    "MLockStyle",
]
