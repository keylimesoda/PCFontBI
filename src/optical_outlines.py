"""Conservative outline styling for small, antialiased terminal text.

Build the union of each glyph's rows before applying a continuous oblique.
This removes interior contour boundaries and preserves the source silhouette.
Bold gains are limited by the available counter space.
"""
from __future__ import annotations

import math
from fontTools.pens.ttGlyphPen import TTGlyphPen

PX_X, PX_Y, TOP, ADVANCE = 53, 64, 896, 424
ANGLE = 6.0
UPRIGHT = frozenset("-_=+|")
BUSY = frozenset("MmWw@&%")


def source_runs(rows):
    result = []
    for byte in rows:
        row = []
        x = 0
        while x < 8:
            if not byte & (1 << (7-x)):
                x += 1
                continue
            start = x
            while x < 8 and byte & (1 << (7-x)):
                x += 1
            row.append((start * PX_X, x * PX_X))
        result.append(row)
    return result


def styled_runs(rows, style, character=None):
    result = source_runs(rows)
    italic = "Italic" in style and character not in UPRIGHT
    bold = "Bold" in style
    if italic and character == "j":
        for y in (2, 3):
            result[y] = [(lo-26, hi-26) for lo, hi in result[y]]
    if italic and character == "f" and result[11]:
        lo, hi = result[11][0]
        result[11][0] = (lo+26, hi)
    if bold:
        gain = 4 if character in BUSY else 7
        expanded = []
        for row in result:
            out = []
            for i, (lo, hi) in enumerate(row):
                # Keep at least one original source pixel between neighboring
                # strokes. Small existing counters therefore never get thinner.
                left = min(gain, max(0, (lo-row[i-1][1]-PX_X)//2)) if i else min(gain, lo)
                right = min(gain, max(0, (row[i+1][0]-hi-PX_X)//2)) if i+1 < len(row) else min(gain, ADVANCE-hi)
                out.append((lo-left, hi+right))
            expanded.append(out)
        result = expanded
    return result


def row_contours(rows):
    """Exact rectangle union on a compressed coordinate grid, including holes."""
    xs = sorted({v for row in rows for run in row for v in run})
    if not xs:
        return []
    occupied = {(i, y) for y, row in enumerate(rows) for i in range(len(xs)-1)
                if any(lo <= xs[i] and xs[i+1] <= hi for lo, hi in row)}
    edges = set()
    for i, y in occupied:
        x0, x1 = xs[i:i+2]
        low, high = TOP-(y+1)*PX_Y, TOP-y*PX_Y
        if (i-1, y) not in occupied: edges.add(((x0, low), (x0, high)))
        if (i, y-1) not in occupied: edges.add(((x0, high), (x1, high)))
        if (i+1, y) not in occupied: edges.add(((x1, high), (x1, low)))
        if (i, y+1) not in occupied: edges.add(((x1, low), (x0, low)))
    outgoing = {}
    for a, b in edges:
        outgoing.setdefault(a, set()).add(b)
    loops = []
    while edges:
        start, point = min(edges)
        previous = start
        loop = [start]
        edges.remove((start, point))
        outgoing[start].remove(point)
        while point != start:
            loop.append(point)
            dx, dy = point[0]-previous[0], point[1]-previous[1]
            def turn(q):
                ux, uy = q[0]-point[0], q[1]-point[1]
                cross, dot = dx*uy-dy*ux, dx*ux+dy*uy
                return (0 if cross < 0 else 1 if dot > 0 else 2 if cross > 0 else 3, q)
            nxt = min(outgoing[point], key=turn)
            edges.remove((point, nxt))
            outgoing[point].remove(nxt)
            previous, point = point, nxt
        # Collinear vertices are not design features; remove them so a stem is
        # one continuous edge when sheared and rasterized.
        simplified = []
        for i, b in enumerate(loop):
            a, c = loop[i-1], loop[(i+1) % len(loop)]
            if (b[0]-a[0])*(c[1]-b[1]) != (b[1]-a[1])*(c[0]-b[0]):
                simplified.append(b)
        loops.append(simplified)
    return loops


def optical_glyph(rows, style_name, character=None, *, keep_structural=False):
    style = "Regular" if keep_structural else style_name
    contours = row_contours(styled_runs(rows, style, character))
    shear = math.tan(math.radians(ANGLE)) if "Italic" in style and character not in UPRIGHT else 0
    pen = TTGlyphPen(None)
    for contour in contours:
        points = [(round(x+shear*(y-384)), y) for x, y in contour]
        pen.moveTo(points[0])
        for point in points[1:]:
            pen.lineTo(point)
        pen.closePath()
    return pen.glyph()
