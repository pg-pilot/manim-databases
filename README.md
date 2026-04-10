# manim-databases

A [Manim](https://www.manim.community/) plugin for animating database concepts: tables, B-trees, indexes, query execution plans, WAL, replication topologies, lock contention, and more.

Built for educators, content creators, and database tooling developers who want to explain how databases actually work.

![MTable preview](assets/previews/mtable.gif)

> **Status:** Early alpha. `MTable` and `MBTree` are functional; other mobjects are stubs being filled in. The public API is stable but expect new mobjects with each release.

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
            ],
            primary_key="id",
            style=MTableStyle.BLUE,
        )

        self.play(Create(table))
        self.play(table.animate.insert_row([3, "carol", "shipped", 200]))
        self.play(table.animate.update_cell(1, "status", "shipped"))
        self.play(table.animate.delete_row(0))
```

```bash
manim -ql my_scene.py OrdersTable
```

### MBTree

![MBTree preview](assets/previews/mbtree.gif)

```python
from manim import *
from manim_databases import MBTree, MBTreeStyle

class BTreeDemo(Scene):
    def construct(self):
        tree = MBTree.from_structure(
            {
                "keys": [10, 20],
                "children": [
                    {"keys": [3, 7]},
                    {"keys": [12, 17]},
                    {"keys": [25, 30]},
                ],
            },
            order=4,
            style=MBTreeStyle.BLUE,
        )
        self.play(Create(tree))
        self.play(tree.animate.search(17))    # highlights search path
        self.play(tree.animate.insert(15))    # smooth insert
        self.play(tree.animate.insert(14))    # triggers a leaf split
```

## Mobjects

| Mobject | Status | Description |
|---|---|---|
| `MTable` | Implemented | Animated database table with typed columns, primary key, insert/delete/update |
| `MBTree` | Implemented | B-tree with search path highlighting, animated insert with cascading splits |
| `MIndex` | Implemented | B-tree index with lookup animation and pointer arrows to table rows |
| `MQueryPlan` | Stub | Execution plan tree (SeqScan, IndexScan, HashJoin, etc.) with cost flow |
| `MWal` | Stub | Append-only write-ahead log sequence |
| `MReplicationTopology` | Stub | Primary/replica graph with write propagation and lag |
| `MLock` | Stub | Row/table lock visualization with contention |

## Documentation

Full docs at [manim-databases.readthedocs.io](https://manim-databases.readthedocs.io/) — includes installation, quickstart, API reference, and examples.

## Contributing

Issues and PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the dev workflow.

## License

MIT — see [LICENSE](LICENSE).
