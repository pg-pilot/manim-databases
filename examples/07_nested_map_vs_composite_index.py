"""The same nine points, three shapes: array.find(), nested Map, composite index.

Companion animation for the "hand-rolled Maps were secretly teaching me
composite indexes" story. Every act reuses the same data — series A/B/C
at times 1/2/3 — so the viewer sees one dataset under three lookups:

1. ``array.find()`` — a cursor walks the array one cell at a time with a
   compare counter, then the "and this ran once per point" multiplier.
2. ``Map`` — one hop for a flat map; two hops for the nested
   ``Map<series, Map<ts, Point[]>>``; and the expensive question
   ("every series at time 2") that has to visit every outer entry.
3. ``INDEX (series_id, ts)`` — an :class:`MBTree` keyed by the composite
   value. Both columns: one search path. Leading column alone: one path,
   then neighbours. Trailing column alone: no path — sweep every key.

The closing card states the equivalence: the nested map *is* the composite
index, and the leading-column rule is the outer-map walk.

Square frame for social feeds. Run with:
    manim -ql -r 480,480  examples/07_nested_map_vs_composite_index.py NestedMapVsCompositeIndex
    manim -qh -r 1080,1080 examples/07_nested_map_vs_composite_index.py NestedMapVsCompositeIndex
"""

from manim import *

from manim_databases import MBTree, MBTreeStyle

# Derive frame units from whatever pixel size the CLI chose, so ``-r W,H``
# gives a correctly proportioned frame (square for 1080x1080).
config.frame_width = config.frame_height * config.pixel_width / config.pixel_height

# Catppuccin Mocha
BG = "#1e1e2e"
TXT = "#cdd6f4"
BLUE = "#89b4fa"
GREEN = "#a6e3a1"
PEACH = "#fab387"
MAUVE = "#cba6f7"
YELLOW = "#f9e2af"
TEAL = "#94e2d5"
SURFACE = "#313244"
OVERLAY = "#45475a"

FONT = "Cascadia Code"  # registered by manim_databases on import


def nolig(code: str) -> str:
    """Break Cascadia Code ligatures (=>, ===) with hair spaces.

    ``Text(disable_ligatures=True)`` trips Manim's glyph-count check on
    exactly these sequences, and zero-width characters are ignored by the
    shaper, so a (barely visible) hair space is inserted instead.
    """
    out = []
    for ch in code:
        if out and ch in "=>" and out[-1] in "=":
            out.append("\u200a")
        out.append(ch)
    return "".join(out)


SERIES = ["A", "B", "C"]
TIMES = [1, 2, 3]
# Insertion order of the array in act 1 — deliberately unsorted, target last.
ARRAY_ORDER = ["C2", "A1", "B3", "C1", "A3", "B1", "A2", "C3", "B2"]
TARGET = "B2"


class Ep1TreeStyle(MBTreeStyle._DefaultStyle):
    """MBTree style on the same palette as the rest of the scene."""

    def __init__(self):
        super().__init__()
        self.node = {
            "color": BLUE,
            "fill_color": SURFACE,
            "fill_opacity": 1,
            "stroke_width": 4,
            "width": 0.8,
            "height": 0.8,
        }
        self.key = {
            "color": TXT,
            "font": FONT,
            "font_size": 28,
            "disable_ligatures": True,
            "weight": BOLD,
        }
        self.edge = {"color": OVERLAY, "stroke_width": 4}
        self.path_highlight_color = YELLOW
        self.found_color = GREEN


class NestedMapVsCompositeIndex(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.counter = None
        self.act_find()
        self.act_map()
        self.act_index()
        self.closing()

    # ── building blocks ──────────────────────────────────────────────

    def cell(self, label, size=0.7, color=OVERLAY, font_size=28):
        box = Rectangle(
            width=size,
            height=size,
            color=color,
            stroke_width=4,
            fill_color=SURFACE,
            fill_opacity=1,
        )
        text = Text(label, font=FONT, font_size=font_size, color=TXT)
        text.move_to(box)
        return VGroup(box, text)

    def header(self, title, code):
        t = Text(title, font=FONT, font_size=34, color=BLUE)
        c = Text(nolig(code), font=FONT, font_size=26, color=GREEN)
        group = VGroup(t, c).arrange(DOWN, buff=0.25)
        group.to_edge(UP, buff=0.45)
        return group

    def set_code(self, header, code):
        new = Text(nolig(code), font=FONT, font_size=26, color=GREEN)
        new.move_to(header[1])
        header[1].become(new)
        return FadeIn(header[1], run_time=0.4)

    def new_counter(self, text, color=YELLOW):
        self.counter = Text(text, font=FONT, font_size=30, color=color)
        self.counter.to_edge(DOWN, buff=0.6)
        return self.counter

    def tick(self, text, color=YELLOW):
        """Swap the counter text instantly; returns a no-op animation so it
        can sit inside a ``self.play(...)`` alongside the cursor move."""
        new = Text(text, font=FONT, font_size=30, color=color)
        new.move_to(self.counter)
        self.counter.become(new)
        return self.counter.animate.set_opacity(1)

    def cursor_for(self, mob):
        return SurroundingRectangle(mob, color=YELLOW, stroke_width=6, buff=0.06)

    def mark_found(self, mob):
        return SurroundingRectangle(mob, color=GREEN, stroke_width=6, buff=0.06)

    def note(self, text, color=PEACH, font_size=24):
        n = Text(text, font=FONT, font_size=font_size, color=color)
        n.next_to(self.counter, UP, buff=0.35)
        return n

    def clear(self):
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.5)
        self.counter = None

    # ── act 1: array.find() ─────────────────────────────────────────

    def act_find(self):
        header = self.header("1. array.find()", "points.find(p => p.id === 'B2')")
        cells = VGroup(*[self.cell(k) for k in ARRAY_ORDER]).arrange(RIGHT, buff=0.06)
        cells.move_to(ORIGIN)
        counter = self.new_counter("compares: 0")

        self.play(FadeIn(header), FadeIn(cells), FadeIn(counter))
        self.wait(0.6)

        cursor = self.cursor_for(cells[0])
        self.play(Create(cursor), run_time=0.3)
        found = None
        for i, key in enumerate(ARRAY_ORDER):
            self.play(
                cursor.animate.move_to(cells[i]),
                self.tick(f"compares: {i + 1}"),
                run_time=0.22,
            )
            if key == TARGET:
                found = self.mark_found(cells[i])
                self.play(FadeOut(cursor), FadeIn(found), run_time=0.3)
                break
        self.wait(0.8)

        multiplier = self.note("…and it ran once per point:  9 × 9 = 81")
        self.play(
            FadeIn(multiplier, shift=UP * 0.2), self.tick("O(n) inside O(n)", PEACH)
        )
        self.wait(2.0)
        self.clear()

    # ── act 2: Map, then nested Map ─────────────────────────────────

    def act_map(self):
        header = self.header("2. Map", "points.get('B2')")
        cells = VGroup(*[self.cell(k) for k in ARRAY_ORDER]).arrange(RIGHT, buff=0.06)
        cells.move_to(ORIGIN)
        counter = self.new_counter("hops: 0")
        self.play(FadeIn(header), FadeIn(cells), FadeIn(counter))

        target_cell = cells[ARRAY_ORDER.index(TARGET)]
        key = Text("'B2'", font=FONT, font_size=28, color=YELLOW)
        key.next_to(cells, UP, buff=0.9)
        arrow = Arrow(key.get_bottom(), target_cell.get_top(), color=YELLOW, buff=0.1)
        self.play(FadeIn(key))
        self.play(GrowArrow(arrow), self.tick("hops: 1"), run_time=0.5)
        found = self.mark_found(target_cell)
        self.play(FadeIn(found), run_time=0.3)
        self.wait(1.2)
        self.play(FadeOut(cells), FadeOut(key), FadeOut(arrow), FadeOut(found))

        # nested: Map<series, Map<ts, Point[]>>
        self.play(self.set_code(header, "Map<series, Map<ts, Point[]>>"))
        rows = VGroup()
        outer_cells, inner_rows = [], []
        for s in SERIES:
            outer = self.cell(s, color=BLUE)
            inner = VGroup(*[self.cell(str(t)) for t in TIMES]).arrange(
                RIGHT, buff=0.06
            )
            row = VGroup(outer, inner).arrange(RIGHT, buff=1.1)
            rows.add(row)
            outer_cells.append(outer)
            inner_rows.append(inner)
        rows.arrange(DOWN, buff=0.35).move_to(ORIGIN)
        arrows = VGroup(
            *[
                Arrow(o.get_right(), r.get_left(), color=OVERLAY, buff=0.1)
                for o, r in zip(outer_cells, inner_rows, strict=True)
            ]
        )
        self.play(FadeIn(rows), Create(arrows), self.tick("hops: 0"))
        self.wait(0.6)

        # query 1: both keys — two hops
        self.play(self.set_code(header, "m.get('B').get(2)"))
        cursor = self.cursor_for(outer_cells[1])
        self.play(Create(cursor), self.tick("hops: 1"), run_time=0.3)
        self.wait(0.3)
        self.play(
            cursor.animate.move_to(inner_rows[1][1]), self.tick("hops: 2"), run_time=0.4
        )
        found = self.mark_found(inner_rows[1][1])
        self.play(FadeOut(cursor), FadeIn(found), run_time=0.3)
        cheap = self.note("cheap: series, or series + ts", GREEN)
        self.play(FadeIn(cheap, shift=UP * 0.2))
        self.wait(1.5)
        self.play(FadeOut(found), FadeOut(cheap))

        # query 2: trailing key alone — walk every outer entry
        self.play(
            self.set_code(header, "for ([s, byTs] of m) byTs.get(2)"),
            self.tick("hops: 0"),
        )
        hops = 0
        founds = []
        cursor = self.cursor_for(outer_cells[0])
        self.play(Create(cursor), run_time=0.2)
        for i in range(len(SERIES)):
            hops += 1
            self.play(
                cursor.animate.move_to(outer_cells[i]),
                self.tick(f"hops: {hops}"),
                run_time=0.3,
            )
            hops += 1
            self.play(
                cursor.animate.move_to(inner_rows[i][1]),
                self.tick(f"hops: {hops}"),
                run_time=0.3,
            )
            f = self.mark_found(inner_rows[i][1])
            founds.append(f)
            self.play(FadeIn(f), run_time=0.15)
        self.play(FadeOut(cursor), run_time=0.2)
        costly = self.note("costly: ts alone — visit every series", PEACH)
        self.play(
            FadeIn(costly, shift=UP * 0.2), self.tick("hops: 6 = 2 × #series", PEACH)
        )
        self.wait(2.2)
        self.clear()

    # ── act 3: composite index ──────────────────────────────────────

    def act_index(self):
        header = self.header("3. Composite index", "INDEX (series_id, ts)")
        tree = MBTree.from_structure(
            {
                "keys": ["A3", "B3"],
                "children": [
                    {"keys": ["A1", "A2"]},
                    {"keys": ["B1", "B2"]},
                    {"keys": ["C1", "C2", "C3"]},
                ],
            },
            order=4,
            style=Ep1TreeStyle(),
        )
        tree.move_to(ORIGIN)
        counter = self.new_counter("nodes: 0")
        self.play(FadeIn(header), Create(tree), FadeIn(counter))
        self.wait(0.6)

        # query 1: both columns — one search path
        self.play(self.set_code(header, "WHERE series_id='B' AND ts=2"))
        path = tree.get_search_path("B2")
        self.play(tree.animate.search("B2"), self.tick(f"nodes: {len(path)}"))
        node, idx = path[-1]
        found = self.mark_found(node.get_key_target(idx))
        self.play(FadeIn(found), run_time=0.3)
        cheap = self.note("cheap: one path down the tree", GREEN)
        self.play(FadeIn(cheap, shift=UP * 0.2))
        self.wait(1.5)
        self.play(FadeOut(found), FadeOut(cheap))

        # query 2: leading column alone — one path, then neighbours
        self.play(self.set_code(header, "WHERE series_id='B'"), self.tick("nodes: 0"))
        path = tree.get_search_path("B1")
        self.play(tree.animate.search("B1"), self.tick(f"nodes: {len(path)}"))
        founds = []
        for node in tree.get_nodes():
            for i, text in enumerate(node.key_texts):
                if text.text.startswith("B"):
                    founds.append(self.mark_found(node.get_key_target(i)))
        self.play(*[FadeIn(f) for f in founds], run_time=0.4)
        cheap = self.note("cheap: leading column — one path", GREEN)
        self.play(FadeIn(cheap, shift=UP * 0.2))
        self.wait(1.5)
        self.play(*[FadeOut(f) for f in founds], FadeOut(cheap))

        # query 3: trailing column alone — no path, sweep every key
        self.play(self.set_code(header, "WHERE ts=2"), self.tick("compares: 0"))
        all_keys = [
            (node, i) for node in tree.get_nodes() for i in range(len(node.key_texts))
        ]
        cursor = self.cursor_for(all_keys[0][0].get_key_target(0))
        self.play(Create(cursor), run_time=0.2)
        founds = []
        for n, (node, i) in enumerate(all_keys):
            target = node.get_key_target(i)
            self.play(
                cursor.animate.move_to(target),
                self.tick(f"compares: {n + 1}"),
                run_time=0.22,
            )
            if node.key_texts[i].text.endswith("2"):
                f = self.mark_found(target)
                founds.append(f)
                self.play(FadeIn(f), run_time=0.12)
        self.play(FadeOut(cursor), run_time=0.2)
        costly = self.note("costly: ts alone — sweep every key", PEACH)
        pg18 = VGroup(
            Text(
                "(PG 18 skip scan: one probe per series —",
                font=FONT,
                font_size=20,
                color=MAUVE,
            ),
            Text(
                "the outer-map walk, automated)", font=FONT, font_size=20, color=MAUVE
            ),
        ).arrange(DOWN, buff=0.08)
        pg18.next_to(costly, UP, buff=0.25)
        self.play(FadeIn(costly, shift=UP * 0.2), self.tick("every key visited", PEACH))
        self.play(FadeIn(pg18))
        self.wait(2.5)
        self.clear()

    # ── closing card ────────────────────────────────────────────────

    def closing(self):
        top = Text("Map<series, Map<ts, Point[]>>", font=FONT, font_size=30, color=TEAL)
        eq = Text("is the same shape as", font=FONT, font_size=22, color=TXT)
        bottom = Text("INDEX (series_id, ts)", font=FONT, font_size=30, color=TEAL)
        cheap = Text(
            "cheap:   series  ·  series + ts", font=FONT, font_size=24, color=GREEN
        )
        costly = Text("costly:  ts alone", font=FONT, font_size=24, color=PEACH)
        card = VGroup(top, eq, bottom).arrange(DOWN, buff=0.3)
        legend = VGroup(cheap, costly).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        VGroup(card, legend).arrange(DOWN, buff=0.8).move_to(ORIGIN)
        self.play(FadeIn(card, shift=UP * 0.2))
        self.wait(0.6)
        self.play(FadeIn(legend))
        self.wait(3.0)
