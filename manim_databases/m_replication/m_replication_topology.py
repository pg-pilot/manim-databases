"""MReplicationTopology: primary/replica graph (stub)."""

from __future__ import annotations

from manim import VGroup

from manim_databases.constants import MReplicationTopologyStyle


class MReplicationTopology(VGroup):
    """Animated database replication topology.

    Will support:
        - Primary node + N replica nodes
        - Sync vs async replication modes (different edge styles)
        - Animated write propagation from primary to replicas
        - Replication lag visualization (delayed pulse on slower replicas)
        - Failover animation (primary → replica promotion)
        - Cascading replication (replica-of-a-replica)

    Parameters
    ----------
    primary : str
        Name of the primary node.
    replicas : list[str]
        Names of replica nodes.
    style : MReplicationTopologyStyle._DefaultStyle, optional
        Style configuration.

    Notes
    -----
    Not yet implemented. Tracking issue:
    https://github.com/pg-pilot/manim-databases/issues
    """

    def __init__(
        self,
        primary: str,
        replicas: list[str],
        style: MReplicationTopologyStyle._DefaultStyle = MReplicationTopologyStyle.DEFAULT,
    ):
        super().__init__()
        raise NotImplementedError(
            "MReplicationTopology is not yet implemented. "
            "See https://github.com/pg-pilot/manim-databases/issues"
        )
