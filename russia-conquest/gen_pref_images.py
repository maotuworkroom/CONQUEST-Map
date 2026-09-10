#!/usr/bin/env python3
"""生成俄罗斯 83 联邦主体面板图片（旅行海报风格）。
输出到 assets/prefs/NN_name.jpg，并打印 PREF_IMG 映射。
"""
import json, os, sys, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ru_data_a import P_A
from ru_data_b import P_B
from ru_data_c import EN_PREF_NEW, REGIONS_NEW

P = {}
P.update(P_A); P.update(P_B)

W, H = 900, 600
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'prefs')
os.makedirs(OUT, exist_ok=True)

# ── 8 区域配色（3 停垂直渐变，深色旅行海报风）──
REGION_PALETTE = {
    '中央':      [(26,58,108),  (45,90,158),  (74,123,196)],   # 深蓝
    '西北':      [(26,77,77),   (45,122,110), (91,168,154)],   # 青绿
    '南方':      [(139,69,19),  (196,122,58), (232,168,90)],   # 暖金
    '北高加索':  [(61,42,92),   (106,74,142), (154,122,184)],  # 山紫
    '伏爾加':    [(92,58,26),   (142,106,58), (196,160,106)],  # 琥珀
    '烏拉爾':    [(42,61,77),   (74,106,126), (122,154,176)],  # 岩蓝灰
    '西伯利亞':  [(26,61,92),   (58,106,142), (106,154,184)],  # 冰蓝
    '遠東':      [(13,42,61),   (26,77,110),  (58,122,158)],   # 太平洋深蓝
}

# ── 字体 ──
FONT_EN = '/System/Library/Fonts/Helvetica.ttc'
FONT_CJK = '/System/Library/Fonts/PingFang.ttc'
def font(path, size, idx=0):
    return ImageFont.truetype(path, size, index=idx)

f_en_big = font(FONT_EN, 54, idx=1)   # Helvetica Bold
f_en_med = font(FONT_EN, 22, idx=1)
f_en_sm  = font(FONT_EN, 13, idx=0)
f_zh     = font(FONT_CJK, 26, idx=0)
f_zh_sm  = font(FONT_CJK, 15, idx=0)
f_num    = font(FONT_EN, 28, idx=1)

# ── 工具 ──
def lerp(a, b, t):
    return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))

def make_gradient(palette, w, h):
    """3 停垂直渐变。"""
    img = Image.new('RGB', (w, h))
    px = img.load()
    c0, c1, c2 = palette
    for y in range(h):
        t = y / (h-1)
        if t < 0.5:
            col = lerp(c0, c1, t*2)
        else:
            col = lerp(c1, c2, (t-0.5)*2)
        for x in range(w):
            px[x, y] = col
    return img

def add_radial_glow(img, cx, cy, radius, color, alpha):
    """中心径向光晕。"""
    glow = Image.new('RGBA', img.size, (0,0,0,0))
    d = ImageDraw.Draw(glow)
    for r in range(radius, 0, -2):
        a = int(alpha * (1 - r/radius)**2)
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=color+(a,))
    glow = glow.filter(ImageFilter.GaussianBlur(20))
    img.paste(glow, (0,0), glow)

def extract_polygons(geometry):
    """从 Polygon/MultiPolygon 提取所有多边形坐标列表。"""
    if geometry['type'] == 'Polygon':
        return [geometry['coordinates'][0]]  # 外环
    polys = []
    for poly in geometry['coordinates']:
        polys.append(poly[0])
    return polys

def normalize_coords(polys, target_w, target_h, cx, cy):
    """将经纬度坐标归一化到画布中心区域。"""
    all_x, all_y = [], []
    for poly in polys:
        for lon, lat in poly:
            all_x.append(lon); all_y.append(lat)
    minx, maxx = min(all_x), max(all_x)
    miny, maxy = min(all_y), max(all_y)
    bw, bh = maxx-minx, maxy-miny
    scale = min(target_w/bw, target_h/bh) * 0.92
    # 纬度翻转（屏幕 y 向下）
    result = []
    for poly in polys:
        pts = []
        for lon, lat in poly:
            x = cx + (lon - (minx+maxx)/2) * scale
            y = cy - (lat - (miny+maxy)/2) * scale
            pts.append((x, y))
        result.append(pts)
    return result

def draw_silhouette(img, polys_norm, fill_alpha=18, outline_alpha=50):
    """绘制地图剪影（半透明填充 + 描边 + 柔光）。"""
    # 柔光层
    glow = Image.new('RGBA', img.size, (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    for pts in polys_norm:
        gd.polygon(pts, fill=(255,255,255,25))
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    img.paste(glow, (0,0), glow)
    # 填充层
    layer = Image.new('RGBA', img.size, (0,0,0,0))
    d = ImageDraw.Draw(layer)
    for pts in polys_norm:
        d.polygon(pts, fill=(252,248,243,fill_alpha), outline=(255,255,255,outline_alpha), width=2)
    img.paste(layer, (0,0), layer)

def draw_text_shadow(draw, pos, text, font, fill, shadow=(0,0,0,120), offset=(2,3), blur=False):
    """带阴影的文字。"""
    x, y = pos
    draw.text((x+offset[0], y+offset[1]), text, font=font, fill=shadow)
    draw.text((x, y), text, font=font, fill=fill)

def rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def draw_region_chip(draw, region_name):
    """左上角区域标签。"""
    text = region_name + '聯邦管區'
    bbox = draw.textbbox((0,0), text, font=f_zh_sm)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    pad_x, pad_y = 14, 7
    x, y = 36, 36
    rounded_rect(draw, [x, y, x+tw+pad_x*2, y+th+pad_y*2], 100,
                  fill=(0,0,0,70), outline=(255,255,255,40), width=1)
    draw.text((x+pad_x, y+pad_y-1), text, font=f_zh_sm, fill=(255,255,255,230))

def draw_id_badge(draw, num):
    """右上角编号徽章（复古邮戳风）。"""
    cx, cy, r = W-72, 72, 30
    # 外圈
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(255,255,255,60), width=2)
    draw.ellipse([cx-r+5, cy-r+5, cx+r-5, cy+r-5], outline=(255,255,255,30), width=1)
    text = f'{num:02d}'
    bbox = draw.textbbox((0,0), text, font=f_num)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.text((cx-tw/2, cy-th/2-2), text, font=f_num, fill=(255,255,255,200))

def draw_vignette(img):
    """边缘暗角。"""
    vig = Image.new('RGBA', img.size, (0,0,0,0))
    d = ImageDraw.Draw(vig)
    for i in range(60):
        a = int(2.5 * i)
        d.rectangle([i, i, W-i, H-i], outline=(0,0,0,a))
    vig = vig.filter(ImageFilter.GaussianBlur(8))
    img.paste(vig, (0,0), vig)

def add_noise(img, amount=8):
    """细微胶片颗粒。"""
    import random
    px = img.load()
    for _ in range(W*H // 40):
        x = random.randint(0, W-1)
        y = random.randint(0, H-1)
        r,g,b = px[x,y]
        delta = random.randint(-amount, amount)
        px[x,y] = (max(0,min(255,r+delta)), max(0,min(255,g+delta)), max(0,min(255,b+delta)))

def slugify(name):
    """英文名转文件名 slug。"""
    s = name.lower().replace(' ', '_').replace("'", '').replace('.', '')
    for ch in ['(', ')', ',', '/', '-']:
        s = s.replace(ch, '_')
    while '__' in s:
        s = s.replace('__', '_')
    return s.strip('_')

# ── 主流程 ──
geo = json.load(open('ru83.geojson', encoding='utf-8'))
features = {f['properties']['id']: f for f in geo['features']}

pref_img = {}
for pid in range(1, 84):
    feat = features[pid]
    ja_name, zh_name, region, tagline, food, spots, matsuri = P[pid]
    en_name = EN_PREF_NEW[pid]
    palette = REGION_PALETTE.get(region, REGION_PALETTE['中央'])

    # 背景渐变
    img = make_gradient(palette, W, H).convert('RGBA')
    # 中心光晕
    add_radial_glow(img, W//2, H//2 - 40, 380, (255,255,255), 18)

    # 地图剪影
    polys = extract_polygons(feat['geometry'])
    polys_norm = normalize_coords(polys, 460, 340, W//2, 260)
    draw_silhouette(img, polys_norm)

    d = ImageDraw.Draw(img)

    # 区域标签
    draw_region_chip(d, region)
    # 编号徽章
    draw_id_badge(d, pid)

    # 底部文字区
    text_y = H - 148
    # 装饰线
    d.line([(40, text_y-14), (40+60, text_y-14)], fill=(255,255,255,100), width=2)

    # 英文名（大）
    draw_text_shadow(d, (40, text_y), en_name, f_en_big, (255,255,255,255))
    # 计算英文名高度，放中文名
    bbox = d.textbbox((0,0), en_name, font=f_en_big)
    en_h = bbox[3] - bbox[1]
    draw_text_shadow(d, (42, text_y + en_h + 8), zh_name, f_zh, (245,238,225,235),
                     shadow=(0,0,0,100), offset=(1,2))

    # 右下角小字
    d.text((W-200, H-36), 'RUSSIAN FEDERATION · 83 SUBJECTS', font=f_en_sm, fill=(255,255,255,90))

    # 暗角 + 颗粒
    draw_vignette(img)
    img = img.convert('RGB')
    add_noise(img, amount=6)

    # 保存
    slug = slugify(en_name)
    fname = f'{pid:02d}_{slug}.jpg'
    fpath = os.path.join(OUT, fname)
    img.save(fpath, 'JPEG', quality=85, optimize=True)
    pref_img[pid] = f'assets/prefs/{fname}'
    if pid % 10 == 0 or pid == 83:
        print(f'  [{pid:02d}/83] {en_name} -> {fname}')

# 输出 PREF_IMG
print('\n=== PREF_IMG ===')
items = ', '.join(f"{k}:'{v}'" for k, v in sorted(pref_img.items()))
print(f'const PREF_IMG = {{{items}}};')
print(f'\n共 {len(pref_img)} 张图片，输出到 {OUT}')
