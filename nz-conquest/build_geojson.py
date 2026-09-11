# -*- coding: utf-8 -*-
"""Build compact NZ regional-council GeoJSON from ECAN ArcGIS export (Stats NZ data)."""
import json
from shapely.geometry import shape, mapping

gj = json.load(open('nz_raw.geojson'))

# 官方顺序：Stats NZ REGC2023 编码 01-16
ORDER = [
    ('Northland Region', 'Northland'),
    ('Auckland Region', 'Auckland'),
    ('Waikato Region', 'Waikato'),
    ('Bay of Plenty Region', 'Bay of Plenty'),
    ('Gisborne Region', 'Gisborne'),
    ("Hawke's Bay Region", "Hawke's Bay"),
    ('Taranaki Region', 'Taranaki'),
    ('Manawatu-Wanganui Region', 'Manawatū-Whanganui'),
    ('Wellington Region', 'Wellington'),
    ('Tasman Region', 'Tasman'),
    ('Nelson Region', 'Nelson'),
    ('Marlborough Region', 'Marlborough'),
    ('West Coast Region', 'West Coast'),
    ('Canterbury Region', 'Canterbury'),
    ('Otago Region', 'Otago'),
    ('Southland Region', 'Southland'),
]

by_name = {}
for f in gj['features']:
    nm = f['properties'].get('NAME')
    if nm:
        by_name.setdefault(nm, f)

missing = [o[0] for o in ORDER if o[0] not in by_name]
print('missing:', missing)

def simplify_geom(geom, tol):
    g = shape(geom)
    g = g.simplify(tol, preserve_topology=True)
    # 避免退化（空几何）
    if g.is_empty:
        return None
    # 确保 MultiPolygon 形式统一
    if g.geom_type == 'Polygon':
        g = g
    return mapping(g)

TOL = 0.005  # ≈ 500m
out = []
for i, (src_name, short) in enumerate(ORDER, 1):
    f = by_name[src_name]
    g = simplify_geom(f['geometry'], TOL)
    if g is None:
        print('SIMPLIFY FAIL', src_name)
        continue
    out.append({'type': 'Feature', 'properties': {'id': i, 'name': short}, 'geometry': g})

fc = {'type': 'FeatureCollection', 'features': out}
raw = json.dumps(fc, separators=(',', ':'))
print('regions:', len(out), '| json bytes:', len(raw.encode('utf-8')))
open('nz.geojson', 'w').write(raw)
