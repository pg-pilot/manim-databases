"""Nine stock prices, three shapes: array.find(), nested Map, composite index.

Companion animation for the "hand-rolled Maps were secretly teaching me
composite indexes" story. Every act reuses the same data — closing prices
for three tickers over three days — so the viewer sees one dataset under
three lookups, phrased as questions anyone can ask:

1. ``array.find()`` — "MSFT on Tuesday?" A cursor walks the list one row
   at a time with a compare counter, then the "and this ran once for every
   price" multiplier.
2. ``Map`` — one hop for a flat map; two hops for the nested
   ``Map<ticker, Map<day, price>>``; and the expensive question
   ("every stock on Tuesday") that has to visit every ticker.
3. ``INDEX (ticker, day)`` — an :class:`MBTree` keyed by the composite
   value. Both columns: one search path. Leading column alone: one path.
   Trailing column alone: no path — sweep every key.

The closing card states the equivalence: the nested map is the same shape
as the composite index, and the leading-column rule is the ticker walk.

Square frame for social feeds. Run with:
    manim -ql -r 480,480 examples/07_nested_map_vs_composite_index.py NestedMapVsCompositeIndex
    manim -r 1080,1080 --fps 30 examples/07_nested_map_vs_composite_index.py NestedMapVsCompositeIndex
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


TICKERS = ["AAPL", "MSFT", "NVDA"]
DAYS = ["Mon", "Tue", "Wed"]  # alphabetical == chronological, so keys sort right
# Order of the list in act 1 — deliberately unsorted, target last.
LIST_ORDER = [
    ("NVDA", "Tue"),
    ("AAPL", "Mon"),
    ("MSFT", "Wed"),
    ("NVDA", "Mon"),
    ("AAPL", "Wed"),
    ("MSFT", "Mon"),
    ("AAPL", "Tue"),
    ("NVDA", "Wed"),
    ("MSFT", "Tue"),
]
TARGET = ("MSFT", "Tue")
CODE_SIZE = 22


def tree_key(ticker, day):
    return f"{ticker}\n{day}"


class Ep1TreeStyle(MBTreeStyle._DefaultStyle):
    """MBTree style on the same palette, with two-line (ticker / day) keys."""

    def __init__(self):
        super().__init__()
        self.node = {
            "color": BLUE,
            "fill_color": SURFACE,
            "fill_opacity": 1,
            "stroke_width": 4,
            "width": 1.05,
            "height": 1.0,
        }
        self.key = {
            "color": TXT,
            "font": FONT,
            "font_size": 24,
            "disable_ligatures": True,
            "weight": BOLD,
            "line_spacing": 0.6,
        }
        self.edge = {"color": OVERLAY, "stroke_width": 4}
        self.horizontal_gap = 0.3
        self.vertical_gap = 1.8
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

    def cell(self, label, width, height=0.46, color=OVERLAY, font_size=24):
        box = Rectangle(
            width=width,
            height=height,
            color=color,
            stroke_width=4,
            fill_color=SURFACE,
            fill_opacity=1,
        )
        text = Text(label, font=FONT, font_size=font_size, color=TXT)
        text.move_to(box)
        return VGroup(box, text)

    def fit_width(self, labels, font_size=24, pad=0.4):
        """Cell width that fits the widest label — derived, never guessed."""
        return max(Text(s, font=FONT, font_size=font_size).width for s in labels) + pad

    def price_list(self):
        """The nine prices as rows of (ticker | day), stacked like a table."""
        tw = self.fit_width(TICKERS)
        dw = self.fit_width(DAYS)
        return VGroup(
            *[
                VGroup(self.cell(t, tw), self.cell(d, dw)).arrange(RIGHT, buff=0)
                for t, d in LIST_ORDER
            ]
        ).arrange(DOWN, buff=0.03)

    def header(self, title, code):
        t = Text(title, font=FONT, font_size=34, color=BLUE)
        c = Text(nolig(code), font=FONT, font_size=CODE_SIZE, color=GREEN)
        group = VGroup(t, c).arrange(DOWN, buff=0.22)
        group.to_edge(UP, buff=0.4)
        return group

    def set_code(self, header, code):
        new = Text(nolig(code), font=FONT, font_size=CODE_SIZE, color=GREEN)
        new.move_to(header[1])
        header[1].become(new)
        return FadeIn(header[1], run_time=0.4)

    def new_counter(self, text, color=YELLOW):
        self.counter = Text(text, font=FONT, font_size=30, color=color)
        self.counter.to_edge(DOWN, buff=0.5)
        return self.counter

    def tick(self, text, color=YELLOW):
        """Swap the counter text instantly; returns a no-op animation so it
        can sit inside a ``self.play(...)`` alongside the cursor move."""
        new = Text(text, font=FONT, font_size=30, color=color)
        new.move_to(self.counter)
        self.counter.become(new)
        return self.counter.animate.set_opacity(1)

    def cursor_for(self, mob):
        return SurroundingRectangle(mob, color=YELLOW, stroke_width=6, buff=0.05)

    def mark_found(self, mob):
        return SurroundingRectangle(mob, color=GREEN, stroke_width=6, buff=0.05)

    def note(self, text, color=PEACH, font_size=24):
        n = Text(text, font=FONT, font_size=font_size, color=color)
        n.next_to(self.counter, UP, buff=0.3)
        return n

    def clear(self):
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.5)
        self.counter = None

    def between_header_and_counter(self, header, mob):
        """Centre ``mob`` in the band between the header and the counter."""
        top = header.get_bottom()[1]
        bottom = self.counter.get_top()[1]
        mob.set_y((top + bottom) / 2)

    # ── act 1: array.find() ─────────────────────────────────────────

    def act_find(self):
        header = self.header("1. array.find()", "prices.find(p => p.id === 'MSFT:Tue')")
        rows = self.price_list()
        counter = self.new_counter("compares: 0")
        self.between_header_and_counter(header, rows)
        rows.shift(RIGHT * 1.6)
        question = Text('"MSFT on\nTuesday?"', font=FONT, font_size=28, color=TXT)
        question.next_to(rows, LEFT, buff=0.9)

        self.play(FadeIn(header), FadeIn(rows), FadeIn(counter), FadeIn(question))
        self.wait(0.8)

        cursor = self.cursor_for(rows[0])
        self.play(Create(cursor), run_time=0.3)
        for i, key in enumerate(LIST_ORDER):
            self.play(
                cursor.animate.move_to(rows[i]),
                self.tick(f"compares: {i + 1}"),
                run_time=0.22,
            )
            if key == TARGET:
                found = self.mark_found(rows[i])
                self.play(FadeOut(cursor), FadeIn(found), run_time=0.3)
                break
        self.wait(0.8)

        multiplier = Text(
            "…and it ran once\nfor every price:\n\n9 × 9 = 81",
            font=FONT,
            font_size=24,
            color=PEACH,
        ).move_to(question)
        self.play(
            FadeOut(question),
            FadeIn(multiplier, shift=UP * 0.2),
            self.tick("O(n) inside O(n)", PEACH),
        )
        self.wait(2.0)
        self.clear()

    # ── act 2: Map, then nested Map ─────────────────────────────────

    def act_map(self):
        header = self.header("2. Map", "prices.get('MSFT:Tue')")
        rows = self.price_list()
        counter = self.new_counter("hops: 0")
        self.between_header_and_counter(header, rows)
        rows.shift(RIGHT * 1.6)
        self.play(FadeIn(header), FadeIn(rows), FadeIn(counter))

        target_row = rows[LIST_ORDER.index(TARGET)]
        key = Text("'MSFT:Tue'", font=FONT, font_size=26, color=YELLOW)
        key.next_to(rows, LEFT, buff=0.9).match_y(rows)
        arrow = Arrow(key.get_right(), target_row.get_left(), color=YELLOW, buff=0.15)
        self.play(FadeIn(key))
        self.play(GrowArrow(arrow), self.tick("hops: 1"), run_time=0.5)
        found = self.mark_found(target_row)
        self.play(FadeIn(found), run_time=0.3)
        self.wait(1.2)
        self.play(FadeOut(rows), FadeOut(key), FadeOut(arrow), FadeOut(found))

        # nested: Map<ticker, Map<day, price>>
        self.play(self.set_code(header, "Map<ticker, Map<day, price>>"))
        tw = self.fit_width(TICKERS)
        dw = self.fit_width(DAYS)
        grid = VGroup()
        outer_cells, inner_rows = [], []
        for t in TICKERS:
            outer = self.cell(t, tw, height=0.6, color=BLUE)
            inner = VGroup(*[self.cell(d, dw, height=0.6) for d in DAYS]).arrange(
                RIGHT, buff=0.06
            )
            grid.add(VGroup(outer, inner).arrange(RIGHT, buff=1.0))
            outer_cells.append(outer)
            inner_rows.append(inner)
        grid.arrange(DOWN, buff=0.35).move_to(ORIGIN)
        arrows = VGroup(
            *[
                Arrow(o.get_right(), r.get_left(), color=OVERLAY, buff=0.1)
                for o, r in zip(outer_cells, inner_rows, strict=True)
            ]
        )
        self.play(FadeIn(grid), Create(arrows), self.tick("hops: 0"))
        self.wait(0.6)

        # query 1: both keys — two hops
        self.play(self.set_code(header, "m.get('MSFT').get('Tue')"))
        cursor = self.cursor_for(outer_cells[1])
        self.play(Create(cursor), self.tick("hops: 1"), run_time=0.3)
        self.wait(0.3)
        self.play(
            cursor.animate.move_to(inner_rows[1][1]), self.tick("hops: 2"), run_time=0.4
        )
        found = self.mark_found(inner_rows[1][1])
        self.play(FadeOut(cursor), FadeIn(found), run_time=0.3)
        cheap = self.note('cheap: "MSFT", or "MSFT on Tue"', GREEN)
        self.play(FadeIn(cheap, shift=UP * 0.2))
        self.wait(1.5)
        self.play(FadeOut(found), FadeOut(cheap))

        # query 2: trailing key alone — walk every ticker
        self.play(
            self.set_code(header, "for ([t, byDay] of m) byDay.get('Tue')"),
            self.tick("hops: 0"),
        )
        hops = 0
        cursor = self.cursor_for(outer_cells[0])
        self.play(Create(cursor), run_time=0.2)
        for i in range(len(TICKERS)):
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
            self.play(FadeIn(self.mark_found(inner_rows[i][1])), run_time=0.15)
        self.play(FadeOut(cursor), run_time=0.2)
        costly = self.note('costly: "every stock on Tue"', PEACH)
        self.play(
            FadeIn(costly, shift=UP * 0.2),
            self.tick("hops: 6 = 2 × every ticker", PEACH),
        )
        self.wait(2.2)
        self.clear()

    # ── act 3: composite index ──────────────────────────────────────

    def act_index(self):
        header = self.header("3. Composite index", "INDEX (ticker, day)")
        tree = MBTree.from_structure(
            {
                "keys": [tree_key("AAPL", "Wed"), tree_key("MSFT", "Wed")],
                "children": [
                    {"keys": [tree_key("AAPL", "Mon"), tree_key("AAPL", "Tue")]},
                    {"keys": [tree_key("MSFT", "Mon"), tree_key("MSFT", "Tue")]},
                    {
                        "keys": [
                            tree_key("NVDA", "Mon"),
                            tree_key("NVDA", "Tue"),
                            tree_key("NVDA", "Wed"),
                        ]
                    },
                ],
            },
            order=4,
            style=Ep1TreeStyle(),
            max_width=config.frame_width - 0.8,
        )
        tree.move_to(UP * 0.5)
        counter = self.new_counter("nodes: 0")
        self.play(FadeIn(header), Create(tree), FadeIn(counter))
        self.wait(0.6)

        # query 1: both columns — one search path
        self.play(self.set_code(header, "WHERE ticker='MSFT' AND day='Tue'"))
        target = tree_key(*TARGET)
        path = tree.get_search_path(target)
        self.play(tree.animate.search(target), self.tick(f"nodes: {len(path)}"))
        node, idx = path[-1]
        found = self.mark_found(node.get_key_target(idx))
        self.play(FadeIn(found), run_time=0.3)
        cheap = self.note("cheap: one path down the tree", GREEN)
        self.play(FadeIn(cheap, shift=UP * 0.2))
        self.wait(1.5)
        self.play(FadeOut(found), FadeOut(cheap))

        # query 2: leading column alone — one path
        self.play(self.set_code(header, "WHERE ticker='MSFT'"), self.tick("nodes: 0"))
        first = tree_key("MSFT", "Mon")
        path = tree.get_search_path(first)
        self.play(tree.animate.search(first), self.tick(f"nodes: {len(path)}"))
        founds = [
            self.mark_found(node.get_key_target(i))
            for node in tree.get_nodes()
            for i, key in enumerate(node.keys)
            if key.startswith("MSFT")
        ]
        self.play(*[FadeIn(f) for f in founds], run_time=0.4)
        cheap = self.note("cheap: leading column — one path", GREEN)
        self.play(FadeIn(cheap, shift=UP * 0.2))
        self.wait(1.5)
        self.play(*[FadeOut(f) for f in founds], FadeOut(cheap))

        # query 3: trailing column alone — no path, sweep every key
        self.play(self.set_code(header, "WHERE day='Tue'"), self.tick("compares: 0"))
        all_keys = [
            (node, i, key)
            for node in tree.get_nodes()
            for i, key in enumerate(node.keys)
        ]
        cursor = self.cursor_for(all_keys[0][0].get_key_target(0))
        self.play(Create(cursor), run_time=0.2)
        for n, (node, i, key) in enumerate(all_keys):
            target_mob = node.get_key_target(i)
            self.play(
                cursor.animate.move_to(target_mob),
                self.tick(f"compares: {n + 1}"),
                run_time=0.22,
            )
            if key.endswith("Tue"):
                self.play(FadeIn(self.mark_found(target_mob)), run_time=0.12)
        self.play(FadeOut(cursor), run_time=0.2)
        costly = self.note("costly: day alone — sweep every key", PEACH)
        pg18 = VGroup(
            Text(
                "(PG 18 skip scan: one probe per ticker —",
                font=FONT,
                font_size=20,
                color=MAUVE,
            ),
            Text("the ticker walk, automated)", font=FONT, font_size=20, color=MAUVE),
        ).arrange(DOWN, buff=0.08)
        pg18.next_to(costly, UP, buff=0.25)
        self.play(FadeIn(costly, shift=UP * 0.2), self.tick("every key visited", PEACH))
        self.play(FadeIn(pg18))
        self.wait(2.5)
        self.clear()

    # ── closing card ────────────────────────────────────────────────

    def closing(self):
        top = Text("Map<ticker, Map<day, price>>", font=FONT, font_size=30, color=TEAL)
        eq = Text("is the same shape as", font=FONT, font_size=22, color=TXT)
        bottom = Text("INDEX (ticker, day)", font=FONT, font_size=30, color=TEAL)
        cheap = Text(
            'cheap:   "MSFT"  ·  "MSFT on Tue"', font=FONT, font_size=24, color=GREEN
        )
        costly = Text(
            'costly:  "every stock on Tue"', font=FONT, font_size=24, color=PEACH
        )
        card = VGroup(top, eq, bottom).arrange(DOWN, buff=0.3)
        legend = VGroup(cheap, costly).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        VGroup(card, legend).arrange(DOWN, buff=0.8).move_to(ORIGIN)
        self.play(FadeIn(card, shift=UP * 0.2))
        self.wait(0.6)
        self.play(FadeIn(legend))
        self.wait(3.0)
