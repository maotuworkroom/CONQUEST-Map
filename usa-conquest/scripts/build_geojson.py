#!/usr/bin/env python3
"""
Build USA_GEOJSON.js from raw US states GeoJSON.
- Remove Puerto Rico
- Assign numeric id 1-51 (alphabetical, DC=51)
- Transform Alaska & Hawaii into bottom-left insets
- Output as window.USA_GEOJSON = {...}
"""
import json, math, sys

SRC = '/tmp/us-states-raw.geojson'
DST = '/Users/lmc/DoubaoWork/chats/2026-09-09/new-chat-3/usa-conquest/assets/usa_geojson.js'

# Alphabetical state list (50 states + DC last)
STATE_ORDER = [
    'Alabama','Alaska','Arizona','Arkansas','California','Colorado',
    'Connecticut','Delaware','Florida','Georgia','Hawaii','Idaho',
    'Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana',
    'Maine','Maryland','Massachusetts','Michigan','Minnesota',
    'Mississippi','Missouri','Montana','Nebraska','Nevada',
    'New Hampshire','New Jersey','New Mexico','New York',
    'North Carolina','North Dakota','Ohio','Oklahoma','Oregon',
    'Pennsylvania','Rhode Island','South Carolina','South Dakota',
    'Tennessee','Texas','Utah','Vermont','Virginia','Washington',
    'West Virginia','Wisconsin','Wyoming','District of Columbia'
]
NAME_TO_ID = {name: i+1 for i, name in enumerate(STATE_ORDER)}

def bounds_of_coords(coords):
    """Recursively find [minlon, minlat, maxlon, maxlat] from GeoJSON coords."""
    minlon, minlat = 180, 90
    maxlon, maxlat = -180, -90
    def walk(c):
        nonlocal minlon, minlat, maxlon, maxlat
        if isinstance(c[0], (int, float)):
            lon, lat = c[0], c[1]
            minlon = min(minlon, lon); maxlon = max(maxlon, lon)
            minlat = min(minlat, lat); maxlat = max(maxlat, lat)
        else:
            for sub in c: walk(sub)
    walk(coords)
    return [minlon, minlat, maxlon, maxlat]

def transform_coords(coords, fn):
    """Recursively apply fn(lon,lat) -> (lon,lat) to all coordinate pairs."""
    if isinstance(coords[0], (int, float)):
        return list(fn(coords[0], coords[1])) + list(coords[2:])
    return [transform_coords(c, fn) for c in coords]

def make_alaska_transform():
    """Scale Alaska down and place as inset at bottom-left."""
    # Alaska original roughly: lon -170..-130, lat 50..72
    # Target inset: lon -128..-118, lat 25..32
    src_cx, src_cy = -150, 61  # center
    dst_cx, dst_cy = -123, 28.5  # target center
    scale = 0.34
    def fn(lon, lat):
        # Handle Alaska's anti-meridian crossing: normalize
        if lon > 0: lon -= 360
        x = (lon - src_cx) * scale + dst_cx
        y = (lat - src_cy) * scale + dst_cy
        return (x, y)
    return fn

def make_hawaii_transform():
    """Place Hawaii as inset next to Alaska."""
    # Hawaii original roughly: lon -160..-155, lat 18..22
    # Target inset: lon -115..-108, lat 25..30
    src_cx, src_cy = -157.5, 20.2
    dst_cx, dst_cy = -111.5, 27.5
    scale = 1.4
    def fn(lon, lat):
        x = (lon - src_cx) * scale + dst_cx
        y = (lat - src_cy) * scale + dst_cy
        return (x, y)
    return fn

def main():
    with open(SRC) as f:
        data = json.load(f)

    features = []
    for feat in data['features']:
        name = feat['properties']['name']
        if name == 'Puerto Rico':
            continue
        if name not in NAME_TO_ID:
            print(f"WARNING: unknown state '{name}', skipping", file=sys.stderr)
            continue
        sid = NAME_TO_ID[name]
        geom = feat['geometry']

        # Apply inset transforms
        if name == 'Alaska':
            geom['coordinates'] = transform_coords(geom['coordinates'], make_alaska_transform())
        elif name == 'Hawaii':
            geom['coordinates'] = transform_coords(geom['coordinates'], make_hawaii_transform())

        new_feat = {
            'type': 'Feature',
            'properties': {'id': sid, 'name': name},
            'geometry': geom
        }
        features.append(new_feat)

    features.sort(key=lambda f: f['properties']['id'])

    result = {
        'type': 'FeatureCollection',
        'features': features
    }

    # Verify all 51 present
    ids = sorted(f['properties']['id'] for f in features)
    assert ids == list(range(1, 52)), f"Missing IDs: {set(range(1,52)) - set(ids)}"

    js_content = f"window.USA_GEOJSON = {json.dumps(result, separators=(',', ':'))};\n"

    with open(DST, 'w') as f:
        f.write(js_content)

    print(f"Written {DST}")
    print(f"Features: {len(features)}")
    print(f"Size: {len(js_content)} bytes")

    # Print bounds for verification
    all_bounds = [180, 90, -180, -90]
    for feat in features:
        b = bounds_of_coords(feat['geometry']['coordinates'])
        all_bounds[0] = min(all_bounds[0], b[0])
        all_bounds[1] = min(all_bounds[1], b[1])
        all_bounds[2] = max(all_bounds[2], b[2])
        all_bounds[3] = max(all_bounds[3], b[3])
    print(f"Overall bounds: lon {all_bounds[0]:.1f}..{all_bounds[2]:.1f}, lat {all_bounds[1]:.1f}..{all_bounds[3]:.1f}")

if __name__ == '__main__':
    main()
