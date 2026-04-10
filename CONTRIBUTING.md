# Contributing

Thanks for your interest in contributing to manim-databases!

## Development setup

```bash
git clone https://github.com/pg-pilot/manim-databases.git
cd manim-databases
pip install -e '.[dev]'
```

This installs the package in editable mode with linting (`ruff`, `black`), testing (`pytest`), and docs (`sphinx`, `furo`) dependencies.

## Code quality

```bash
ruff check manim_databases/
black manim_databases/
```

## Running examples

```bash
# Low quality (480p, fast iteration)
manim -ql examples/01_table_basic.py OrdersTable

# High quality (1080p, final renders)
manim -qh examples/02_btree_search.py BTreeSearchAndInsert
```

Manim output lands in `media/videos/<file>/<quality>/`.

## Testing

Tests are Manim scenes (not pytest functions) — render them and inspect visually:

```bash
manim -ql tests/visual/btree_animated.py A04_FullSequence
```

## Project layout

```
manim_databases/
├── __init__.py              # public API exports
├── constants.py             # *Style classes (DEFAULT/BLUE/PURPLE/GREEN)
├── m_table/                 # MTable + MRow
├── m_btree/                 # MBTree + MBTreeNode
├── m_index/                 # stub
├── m_query_plan/            # stub
├── m_wal/                   # stub
├── m_replication/           # stub
├── m_lock/                  # stub
└── utils/                   # Labelable, Highlightable, set_text
```

### Conventions

- **One package per mobject:** `m_<thing>/m_<thing>.py`
- **Styles in `constants.py`:** every mobject ships with `DEFAULT`, `BLUE`, `PURPLE`, `GREEN` variants
- **Subclass `VGroup`** for composite mobjects
- **Animation override pattern:** mutating methods have a matching `@override_animate` method
- **Use `set_text(old, new)`** instead of Manim's built-in `Text.set_text`

## Adding a new mobject

1. Create the package: `m_<thing>/m_<thing>.py`
2. Add style variants in `constants.py`
3. Export from `__init__.py`
4. Add an example scene in `examples/`
5. Add a visual test scene in `tests/`
6. Update the docs: add to `docs/source/api.rst` and `docs/source/examples.rst`

## Generating preview GIFs

The README and docs use animated GIFs rendered from example scenes:

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
playback stutter.

## Building docs

```bash
cd docs
sphinx-build -b html source build
# Open build/index.html
```

## Commit conventions

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `ci`, `style`, `build`.
