# manim-databases

A [Manim](https://www.manim.community/) plugin for animating database concepts: tables, B-trees, indexes, query execution plans, WAL, replication topologies, lock contention, and more.

Built for educators, content creators, and database tooling developers who want to explain how databases actually work.

> **Status:** Early alpha. `MTable` is functional; other mobjects are stubs being filled in. The public API is stable but expect new mobjects with each release.

## Installation

```bash
pip install manim-databases
```

You'll also need a working Manim installation. See the [Manim install guide](https://docs.manim.community/en/stable/installation.html).

## Quick Start

```python
from manim import *
from manim_databases import MTable, MTableStyle

class OrdersTable(Scene):
    def construct(self):
        table = MTable(
            columns=["id", "customer", "status", "total"],
            rows=[
                [1, "alice", "shipped", 120],
                [2, "bob",   "pending", 85],
                [3, "carol", "shipped", 200],
            ],
            primary_key="id",
            style=MTableStyle.BLUE,
        )

        self.play(Create(table))
        self.wait()

        # Animate a row insert
        self.play(table.animate.insert_row([4, "dave", "shipped", 55]))
        self.wait()

        # Update a value
        self.play(table.animate.update_cell(1, "status", "shipped"))
        self.wait()

        # Delete a row
        self.play(table.animate.delete_row(0))
        self.wait()
```

Render with:

```bash
manim -ql my_scene.py OrdersTable
```

## Mobjects

| Mobject | Status | Description |
|---|---|---|
| `MTable` | ✅ Implemented | Animated database table with typed columns, primary key, insert/delete/update |
| `MBTree` | 🚧 Stub | B-tree with key insertion, node splits, search path highlighting |
| `MIndex` | 🚧 Stub | Hash or B-tree index with key→row pointer animation |
| `MQueryPlan` | 🚧 Stub | Execution plan tree (SeqScan, IndexScan, HashJoin, etc.) with cost flow |
| `MWal` | 🚧 Stub | Append-only write-ahead log sequence |
| `MReplicationTopology` | 🚧 Stub | Primary/replica graph with write propagation and lag |
| `MLock` | 🚧 Stub | Row/table lock visualization with contention |

## Styles

Each mobject ships with `DEFAULT`, `BLUE`, `PURPLE`, and `GREEN` style variants:

```python
MTable(columns=[...], rows=[...], style=MTableStyle.PURPLE)
```

You can also subclass `_DefaultStyle` to build your own.

## Examples

See the [`examples/`](examples/) directory for runnable scenes per mobject.

## Documentation

Full docs at [manim-databases.readthedocs.io](https://manim-databases.readthedocs.io/).

## Contributing

Issues and PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the dev workflow.

## License

MIT — see [LICENSE](LICENSE).
