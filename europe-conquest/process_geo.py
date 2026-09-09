import json
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

gj = json.load(open('johan.geo.json'))
by_id = {f['id']: f for f in gj['features']}

# 目标顺序：id 1-44
ORDER = ['ISL','NOR','SWE','FIN','DNK','GBR','IRL','FRA','NLD','BEL','LUX','CHE',
         'DEU','AUT','POL','CZE','SVK','HUN','PRT','ESP','ITA','GRC','MLT','CYP',
         'HRV','SVN','SRB','BIH','MNE','MKD','ALB','BGR','ROU','EST','LVA','LTU',
         'UKR','MDA','BLR','RUS','TUR','GEO','ARM','AZE']

CLIP = {  # 裁剪到欧洲部分（经度范围）
    'RUS': (-35.0, 70.0),
    'TUR': (-35.0, 48.0),
}

def clip_geom(geom, lon_min, lon_max):
    box = shape({'type':'Polygon','coordinates':[[[lon_min,-90],[lon_max,-90],[lon_max,90],[lon_min,90],[lon_min,-90]]]})
    g = geom.intersection(box)
    if g.is_empty: return None
    return g

out = []
for i, code in enumerate(ORDER, 1):
    f = by_id[code]
    geom = shape(f['geometry'])
    if code in CLIP:
        lon_min, lon_max = CLIP[code]
        geom = clip_geom(geom, lon_min, lon_max)
        if geom is None:
            print('CLIP FAIL', code); continue
    # 简化（容差 0.02 度 ≈ 2km）
    geom = geom.simplify(0.02, preserve_topology=True)
    out.append({'type':'Feature','properties':{'id':i},'geometry':mapping(geom)})

fc = {'type':'FeatureCollection','features':out}
raw = json.dumps(fc, separators=(',',':'))
print('countries:', len(out), '| json bytes:', len(raw.encode('utf-8')))
open('europe.geojson','w').write(raw)
