"""Trace the boundary of a union of pixel rows; retain holes, remove seams."""
PX_Y, TOP = 64, 896


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
