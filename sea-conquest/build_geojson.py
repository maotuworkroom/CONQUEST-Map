#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract Southeast Asia countries from Natural Earth 50m, simplify, and emit
a minified GeoJSON FeatureCollection for embedding in the SEA conquest map."""
import json, math, sys

SRC = 'ne50m_countries.geojson'
OUT = 'sea.geojson'

# numeric id -> ADM0_A3
ID_MAP = {
    1: 'THA',   # 泰國
    2: 'VNM',   # 越南
    3: 'MMR',   # 緬甸
    4: 'LAO',   # 寮國
    5: 'KHM',   # 柬埔寨
    6: 'MYS',   # 馬來西亞
    7: 'SGP',   # 新加坡
    8: 'IDN',   # 印尼
    9: 'PHL',   # 菲律賓
    10: 'BRN',  # 汶萊
    11: 'TLS',  # 東帝汶
}
A3_TO_ID = {v: k for k, v in ID_MAP.items()}

EPS = 0.012  # degrees; ~1.3km at equator — keeps coastlines lively, cuts size a lot

def dp(points, eps):
    """Iterative Douglas-Peucker on a closed ring (list of [lon, lat])."""
    if len(points) < 4:
        return points
    # mark kept points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        a, b = stack.pop()
        if b <= a + 1:
            continue
        ax, ay = points[a]
        bx, by = points[b]
        dx, dy = bx - ax, by - ay
        denom = dx * dx + dy * dy
        maxd = -1.0
        imax = -1
        for i in range(a + 1, b):
            px, py = points[i]
            if denom == 0:
                d = (px - ax) ** 2 + (py - ay) ** 2
            else:
                t = ((px - ax) * dx + (py - ay) * dy) / denom
                t = max(0.0, min(1.0, t))
                cx, cy = ax + t * dx, ay + t * dy
                d = (px - cx) ** 2 + (py - cy) ** 2
            if d > maxd:
                maxd = d
                imax = i
        if maxd > eps * eps and imax != -1:
            keep[imax] = True
            stack.append((a, imax))
            stack.append((imax, b))
    return [pt for i, pt in enumerate(points) if keep[i]]

def simplify_ring(ring):
    out = dp(ring, EPS)
    if len(out) >= 4:
        out = out  # keep as-is (already closed)
    return out

def simplify_coords(coords):
    """coords: list of rings (Polygon) or list of list of rings (MultiPolygon)."""
    if coords and isinstance(coords[0][0][0], (int, float)):
        # Polygon: list of rings
        return [simplify_ring(r) for r in coords]
    # MultiPolygon: list of polygons, each list of rings
    return [[simplify_ring(r) for r in poly] for poly in coords]

def main():
    with open(SRC, 'r', encoding='utf-8') as f:
        data = json.load(f)
    feats = []
    for f in data['features']:
        a3 = f['properties'].get('ADM0_A3')
        if a3 not in A3_TO_ID:
            continue
        g = f['geometry']
        feats.append({
            'type': 'Feature',
            'properties': {'id': A3_TO_ID[a3]},
            'geometry': {
                'type': g['type'],
                'coordinates': simplify_coords(g['coordinates'])
            }
        })
    # sort by id for determinism
    feats.sort(key=lambda x: x['properties']['id'])
    fc = {'type': 'FeatureCollection', 'features': feats}

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(fc, f, ensure_ascii=False, separators=(',', ':'))
    size = len(json.dumps(fc, ensure_ascii=False, separators=(',', ':')))
    print('features:', len(feats), 'ids:', [x['properties']['id'] for x in feats])
    print('minified size: %.1f KB' % (size / 1024))

    # bounds
    minx = miny = 1e9
    maxx = maxy = -1e9
    def rings_of(coords):
        if coords and isinstance(coords[0][0][0], (int, float)):
            return coords  # Polygon: list of rings
        out = []
        for poly in coords:
            out.extend(poly)
        return out
    for f in feats:
        for ring in rings_of(f['geometry']['coordinates']):
            for lon, lat in ring:
                minx = min(minx, lon); maxx = max(maxx, lon)
                miny = min(miny, lat); maxy = max(maxy, lat)
    print('bounds: lon %.2f..%.2f  lat %.2f..%.2f' % (minx, maxx, miny, maxy))

if __name__ == '__main__':
    main()
