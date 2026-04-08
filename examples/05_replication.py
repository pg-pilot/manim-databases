"""MReplicationTopology placeholder example (mobject not yet implemented)."""

from manim import *

from manim_databases import MReplicationTopology


class ReplicationTopology(Scene):
    def construct(self):
        # MReplicationTopology is currently a stub. When implemented, this
        # will show a primary with multiple replicas and animate write
        # propagation with replication lag.
        topology = MReplicationTopology(
            primary="primary",
            replicas=["replica-1", "replica-2", "replica-3"],
        )
        self.play(Create(topology))
