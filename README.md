# manim-databases

A [Manim](https://www.manim.community/) plugin for animating database concepts: tables, B-trees, indexes, query execution plans, WAL, replication topologies, lock contention, and more.

Built for educators, content creators, and database tooling developers who want to explain how databases actually work.

![MTable preview](assets/previews/mtable.gif)

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
| `MBTree` | ✅ Implemented | B-tree with manual `from_structure` build, search path highlighting, animated insert with cascading splits |
| `MIndex` | 🚧 Stub | Hash or B-tree index with key→row pointer animation |
| `MQueryPlan` | 🚧 Stub | Execution plan tree (SeqScan, IndexScan, HashJoin, etc.) with cost flow |
| `MWal` | 🚧 Stub | Append-only write-ahead log sequence |
| `MReplicationTopology` | 🚧 Stub | Primary/replica graph with write propagation and lag |
| `MLock` | 🚧 Stub | Row/table lock visualization with contention |

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

        # Search animation highlights each compared key on the path.
        self.play(tree.animate.search(17))

        # Insertion handles cascading splits and re-layouts the tree.
        self.play(tree.animate.insert(15))
        self.play(tree.animate.insert(14))  # triggers a leaf split
```

## Styles

Each mobject ships with `DEFAULT`, `BLUE`, `PURPLE`, and `GREEN` style variants:

```python
MTable(columns=[...], rows=[...], style=MTableStyle.PURPLE)
```

You can also subclass `_DefaultStyle` to build your own.

## Examples

See the [`examples/`](examples/) directory for runnable scenes per mobject.

### Generating preview GIFs

The README and docs use animated GIFs rendered from the example scenes. To
regenerate them after changing a mobject:

```bash
# 1. Render at 1080p60
manim -qh examples/01_table_basic.py OrdersTable

# 2. Convert to optimized GIF (25fps for clean centisecond-aligned timing)
mkdir -p assets/previews
ffmpeg -i media/videos/01_table_basic/1080p60/OrdersTable.mp4 \
  -vf "fps=25,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5" \
  -loop 0 \
  assets/previews/mtable.gif
```

`fps=25` is the sweet spot for GIFs — the format stores frame delays in
centiseconds (1/100s), so only fps values that divide 100 cleanly avoid
playback stutter. 15fps quantizes to ~14.3 or ~16.7fps and looks janky;
25fps is exactly 4 centiseconds per frame.

## Documentation

Full docs at [manim-databases.readthedocs.io](https://manim-databases.readthedocs.io/).

## Contributing

Issues and PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the dev workflow.

## License

MIT — see [LICENSE](LICENSE).
