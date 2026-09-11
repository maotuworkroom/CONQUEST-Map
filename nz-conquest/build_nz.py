# -*- coding: utf-8 -*-
"""從日本版 index.html 構建紐西蘭制霸地圖"""
import re, json, subprocess, sys, urllib.parse
import opencc
from nz_content import *
from nz_en import NZ_EN

T2S = opencc.OpenCC('t2s')

JP = '/Users/lmc/DoubaoWork/chats/2026-09-08/new-chat/japan-conquest/index.html'
OUT = '/Users/lmc/DoubaoWork/chats/2026-09-11/new-chat-7/nz-conquest/index.html'

src = open(JP, encoding='utf-8').read()

# ============================================================
# 工具：提取 const 區塊（含結尾分號）
# ============================================================
def grab(s, name, kind='{'):
    """找 `const NAME = kind` 到配對閉合 + ';' 的區塊，回傳 (start, end, text)"""
    m = re.search(r'const\s+' + re.escape(name) + r'\s*=\s*' + re.escape(kind), s)
    if not m:
        raise SystemExit('MISSING const ' + name)
    i = m.end() - 1  # 指到 { 或 [
    depth = 0
    j = i
    while j < len(s):
        c = s[j]
        if c in '{[':
            depth += 1
        elif c in '}]':
            depth -= 1
            if depth == 0:
                semi = s.index(';', j)
                return m.start(), semi + 1
        j += 1
    raise SystemExit('unbalanced ' + name)

def cut(name, kind='{'):
    """取出並從 src 移除 const 區塊，回傳其文字"""
    global src
    m = re.search(r'const\s+' + re.escape(name) + r'\s*=\s*' + re.escape(kind), src)
    if not m:
        raise SystemExit('MISSING const ' + name)
    i = m.end() - 1
    depth = 0
    j = i
    while j < len(src):
        c = src[j]
        if c in '{[':
            depth += 1
        elif c in '}]':
            depth -= 1
            if depth == 0:
                semi = src.index(';', j)
                a, b = m.start(), semi + 1
                txt = src[a:b]
                src = src[:a] + '\n/*__' + name + '__*/\n' + src[b:]
                return txt
        j += 1
    raise SystemExit('unbalanced ' + name)

def repl(src, old, new, label=''):
    n = src.count(old)
    if n == 0:
        print('  !! not found:', label or old[:60])
        return src
    return src.replace(old, new)

# ============================================================
# 1. 抽出受保護區塊
# ============================================================
m = re.search(r'<script>window\.JAPAN_GEOJSON = .*?</script>', src, re.S)
assert m, 'geojson block'
src = src[:m.start()] + '<script>/*__NZ_GEOJSON__*/</script>' + src[m.end():]

i18n_txt = cut('I18N')
t2s_m = re.search(r'const T2S = \{.*?\};', src, re.S)
assert t2s_m, 'T2S'
t2s_txt = t2s_m.group(0)
src = src[:t2s_m.start()] + '/*__T2S__*/' + src[t2s_m.end():]
ts_fn = re.search(r'function toSimplified\(str\)\{.*?\n\}', src, re.S)
assert ts_fn, 'toSimplified'
ts_fn_txt = ts_fn.group(0)
src = src[:ts_fn.start()] + '/*__T2S_FN__*/' + src[ts_fn.end():]

data_names = ['REGIONS', 'PROVINCES', 'WH_PREFS', 'EN_PREF', 'LEVELS', 'TYPE_COLOR', 'ACH', 'ACH_CATS', 'PREF_IMG']
saved = {}
for nm in data_names:
    saved[nm] = cut(nm, '{' if nm not in ('WH_PREFS', 'LEVELS', 'ACH', 'ACH_CATS') else '[')

# LABEL_MAJOR（Set）
m = re.search(r'const LABEL_MAJOR = new Set\(\[[^\]]*\]\);', src)
assert m, 'LABEL_MAJOR'
src = src[:m.start()] + '/*__LABEL_MAJOR__*/' + src[m.end():]

# FILLS
f_txt = cut('FILLS')

# ============================================================
# 2. 內容字串替換（鍵名遷移 = RENAME）
# ============================================================
RENAMES = [
    ('縣幣評分', '大區評分'),
    ('都道府縣', '大區'),
    ('縣市', '大區'),
    ('該地區', '該島'),
    ('地區制霸', '島嶼制霸'),
    ('地區足跡', '島嶼足跡'),
    ('縣', '大區'),
    ('日本制霸地圖', '紐西蘭制霸地圖'),
    ('日本', '紐西蘭'),
    (' / 47', ' / 16'),
    (' / 8', ' / 2'),
    ('/47', '/16'),
    ('/8', '/2'),
    ('JPN-', 'NZL-'),
    ('japanMap', 'nzMap'),
    ('jp_lang', 'nz_lang'),
    ('日文', '英文'),
    ('47', '16'),
]
for old, new in RENAMES:
    src = src.replace(old, new)

# 例：建立地圖名稱
src = src.replace('例：我的關西之旅、大阪社畜的週末', '例：我的南島環島之旅、皇后鎮週末')

# ============================================================
# 3. 寫入新資料區塊
# ============================================================
def js_provinces():
    lines = ['const PROVINCES = {']
    for i in range(1, 17):
        p = PROVINCES[i]
        lines.append(' %d:{ja:%r, zh:%r, region:%r, tagline:%r, food:%r, spots:%r, matsuri:%r},'
                     % (i, p['ja'], p['zh'], p['region'], p['tagline'], p['food'], p['spots'], p['matsuri']))
    lines.append('};')
    return '\n'.join(lines)

def js_levels():
    lines = ['const LEVELS = [']
    for lv in LEVELS:
        lines.append(' {name:%r, icon:%r, pts:%d, pct:%r},' % (lv['name'], lv['icon'], lv['pts'], lv['pct']))
    lines.append('];')
    return '\n'.join(lines)

def js_ach():
    lines = ['const ACH = [']
    for a in ACH:
        if 'groups' in a:
            lines.append(' {id:%d, cat:%r, icon:%r, name:%r, cond:%r, kind:\'groups\', groups:%r, level:%d, pts:%d},'
                         % (a['id'], a['cat'], a['icon'], a['name'], a['cond'], a['groups'], a['groups'][1], a['pts']))
        elif 'prefs' in a and 'n' in a:
            lines.append(' {id:%d, cat:%r, icon:%r, name:%r, cond:%r, kind:\'count\', prefs:%r, n:%d, level:%d, pts:%d},'
                         % (a['id'], a['cat'], a['icon'], a['name'], a['cond'], a['prefs'], a['n'], a['level'], a['pts']))
        else:
            lines.append(' {id:%d, cat:%r, icon:%r, name:%r, cond:%r, kind:\'manual\', prefs:%r, level:%d, pts:%d},'
                         % (a['id'], a['cat'], a['icon'], a['name'], a['cond'], a['prefs'], a['level'], a['pts']))
    lines.append('];')
    return '\n'.join(lines)

def js_regions():
    return 'const REGIONS = {\n \'北島\': {name: \'北島\', ids: [1,2,3,4,5,6,7,8,9]},\n \'南島\': {name: \'南島\', ids: [10,11,12,13,14,15,16]},\n};'

def js_wh():
    return 'const WH_PREFS = %r;' % WH_PREFS

def js_enpref():
    return 'const EN_PREF = %r;' % EN_PREF

def js_typecolor():
    return 'const TYPE_COLOR = %r;' % TYPE_COLOR

def js_achcats():
    return 'const ACH_CATS = %r;' % ACH_CATS

def js_prefimg():
    return 'const PREF_IMG = %r;' % PREF_IMG

blocks = {
    'REGIONS': js_regions(),
    'PROVINCES': js_provinces(),
    'WH_PREFS': js_wh(),
    'EN_PREF': js_enpref(),
    'LEVELS': js_levels(),
    'TYPE_COLOR': js_typecolor(),
    'ACH': js_ach(),
    'ACH_CATS': js_achcats(),
    'PREF_IMG': js_prefimg(),
}
for nm, txt in blocks.items():
    src = src.replace('/*__' + nm + '__*/', txt, 1)

# LABEL_MAJOR / FILLS / GeoJSON
src = src.replace('/*__LABEL_MAJOR__*/', 'const LABEL_MAJOR = new Set(%r);' % LABEL_MAJOR)
nz_fills = {0: '#EDF1E7', 1: '#D8E5D3', 2: '#A9CBA4', 3: '#6FA37B', 4: '#2E6B4F'}
src = src.replace('/*__FILLS__*/', 'const FILLS = %r;' % nz_fills)
nz_geo = json.load(open('/Users/lmc/DoubaoWork/chats/2026-09-11/new-chat-7/nz-conquest/nz.geojson', encoding='utf-8'))
geo_js = 'window.NZ_GEOJSON = ' + json.dumps(nz_geo, separators=(',', ':')) + ';'
src = src.replace('<script>/*__NZ_GEOJSON__*/</script>', '<script>' + geo_js + '</script>')
# 業務 JS 中對舊 GeoJSON 變數名的引用一併替換
src = src.replace('window.JAPAN_GEOJSON', 'window.NZ_GEOJSON')

# 恢復 T2S
src = src.replace('/*__T2S__*/', t2s_txt, 1).replace('/*__T2S_FN__*/', ts_fn_txt, 1)

# ============================================================
# 4. 目標式編輯（JS / CSS / HTML）
# ============================================================
# 4.1 JS 邏輯
src = src.replace("const LANGS = ['zh-Hant','zh-Hans','ja','en'];", "const LANGS = ['zh-Hant','zh-Hans','en'];")
src = src.replace("const LANG_KEY = 'nz_lang';", "const LANG_KEY = 'nz_lang';")  # 已由 RENAME 處理
src = src.replace('id<=47', 'id<=16').replace('id <= 47', 'id <= 16')
src = src.replace("const GB = { minLon: 123.6, maxLon: 146.2, minLat: 24.0, maxLat: 45.7 };",
                  "const GB = { minLon: 166.0, maxLon: 179.0, minLat: -47.7, maxLat: -34.0 };")
src = src.replace("'123°E – 146°E  /  24°N – 46°N'", "'166°E – 179°E  /  47°S – 34°S'")
src = src.replace("const VERM = '#9E2418', VERM_DEEP = '#7A1A10', VERM_SOFT = '#C44A3A';",
                  "const VERM = '#2E6B4F', VERM_DEEP = '#1F4A35', VERM_SOFT = '#4E8A68';")
src = src.replace('rgba(158,36,24,.3)', 'rgba(46,107,79,.3)')
src = src.replace('rgba(158,36,24,.4)', 'rgba(46,107,79,.4)')
src = src.replace('rgba(158,36,24,.15)', 'rgba(46,107,79,.15)')
src = src.replace('[26,13,27,1,40,14,28,23]', '[15,16,7,9,14,3,2,6]')
src = src.replace('dataofjapan', 'Stats NZ')
src = src.replace('（GeoJSON）', '（CC BY 4.0）')

# 4.2 CSS 色板
root_block = re.search(r':root\{.*?\n\}', src, re.S)
assert root_block, ':root'
root_new = """:root{
  /* MDUI 3 色板覆寫（蕨綠主色 / 炭灰次色 / 金三色 / 羊皮紙表面） */
  --mdui-color-primary:46 107 79;
  --mdui-color-on-primary:255 255 255;
  --mdui-color-primary-container:204 232 209;
  --mdui-color-on-primary-container:0 40 23;
  --mdui-color-inverse-primary:156 205 169;
  --mdui-color-secondary:79 88 82;
  --mdui-color-on-secondary:255 255 255;
  --mdui-color-secondary-container:210 219 211;
  --mdui-color-on-secondary-container:14 25 19;
  --mdui-color-tertiary:123 94 0;
  --mdui-color-on-tertiary:255 255 255;
  --mdui-color-tertiary-container:255 223 148;
  --mdui-color-on-tertiary-container:38 26 0;
  --mdui-color-error:186 26 26;
  --mdui-color-error-container:255 218 214;
  --mdui-color-on-error-container:65 0 2;
  --mdui-color-on-error:255 255 255;
  --mdui-color-inverse-on-surface:242 246 240;
  --mdui-color-inverse-surface:66 79 69;
  --mdui-color-on-inverse-surface:242 246 240;
  --mdui-color-surface:248 249 244;
  --mdui-color-on-surface:25 32 27;
  --mdui-color-surface-variant:224 231 219;
  --mdui-color-on-surface-variant:66 79 69;
  --mdui-color-surface-dim:218 225 214;
  --mdui-color-surface-bright:248 249 244;
  --mdui-color-outline:113 126 114;
  --mdui-color-outline-variant:196 210 197;
  --mdui-color-shadow:0 0 0;
  --mdui-color-scrim:0 0 0;
  --mdui-color-surface-container-lowest:255 255 255;
  --mdui-color-surface-container-low:242 246 240;
  --mdui-color-surface-container:236 241 233;
  --mdui-color-surface-container-high:230 236 226;
  --mdui-color-surface-container-highest:224 231 219;
  /* 站點色板 */
  --paper:#F8F9F4;
  --paper-deep:#EAF0E5;
  --ink:#19201B;
  --ink-soft:#3F4A41;
  --ink-faint:#6F7B6B;
  --fern:#2E6B4F;
  --fern-deep:#1F4A35;
  --fern-soft:#4E8A68;
  --gold:#C9A227;
  --gold-soft:#FFE08A;
  --indigo:#4F5A70;
  --line:#DCE5D8;
  --radius-sm:8px;
  --radius-md:14px;
  --radius-lg:22px;
  --shadow-1:0 1px 3px rgba(25,32,27,.08),0 4px 14px rgba(25,32,27,.06);
  --shadow-2:0 10px 30px rgba(25,32,27,.12);
}"""
src = src[:root_block.start()] + root_new + src[root_block.end():]
src = src.replace('var(--vermilion-deep)', 'var(--fern-deep)')
src = src.replace('var(--vermilion-soft)', 'var(--fern-soft)')
src = src.replace('var(--vermilion)', 'var(--fern)')
src = src.replace('rgba(176,42,26,.35)', 'rgba(46,107,79,.35)')
src = src.replace('rgba(176,42,26,.6)', 'rgba(46,107,79,.6)')
src = src.replace('rgba(176,42,26,.07)', 'rgba(46,107,79,.07)')

# 圖例色
for old, new in [('#F0E7DF', '#EDF1E7'), ('#F3CDBF', '#D8E5D3'), ('#E89376', '#A9CBA4'),
                 ('#D2603F', '#6FA37B'), ('#B02A1A', '#2E6B4F')]:
    src = src.replace(old, new)

# favicon 色
src = src.replace('%23B02A1A', '%232E6B4F')

# 4.3 銀蕨徽標（hero-flag / brand-flag）
FERN = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
        '<path d="M50 92 C49 72 49 44 51 20" stroke="#2E6B4F" stroke-width="3.4" fill="none" stroke-linecap="round"/>'
        '<path d="M50 82 C41 78 33 72 27 63 C36 69 44 74 50 78 Z" fill="#2E6B4F"/>'
        '<path d="M50 82 C59 78 67 72 73 63 C64 69 56 74 50 78 Z" fill="#2E6B4F"/>'
        '<path d="M50 66 C43 63 36 58 31 50 C38 55 45 60 50 63 Z" fill="#2E6B4F"/>'
        '<path d="M50 66 C57 63 64 58 69 50 C62 55 55 60 50 63 Z" fill="#2E6B4F"/>'
        '<path d="M50 50 C45 48 40 44 37 39 C42 43 47 46 50 48 Z" fill="#2E6B4F"/>'
        '<path d="M50 50 C55 48 60 44 63 39 C58 43 53 46 50 48 Z" fill="#2E6B4F"/>'
        '<path d="M50 36 C47 35 44 33 42 29 C45 31 48 34 50 35 Z" fill="#2E6B4F"/>'
        '<path d="M50 36 C53 35 56 33 58 29 C55 31 52 34 50 35 Z" fill="#2E6B4F"/></svg>')
fern_uri = 'url("data:image/svg+xml,' + urllib.parse.quote(FERN, safe='') + '")'

def replace_css_block(css, sel, new):
    m = re.search(re.escape(sel) + r'\{.*?\n\}', css, re.S)
    if not m:
        print('  !! css block not found:', sel)
        return css
    return css[:m.start()] + new + css[m.end():]

src = replace_css_block(src, '.hero-flag::after',
    ".hero-flag::after{\n  content:'';position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);\n  width:56px;height:56px;\n  background:" + fern_uri + " center/contain no-repeat;\n}")
src = replace_css_block(src, '.brand-flag::after',
    ".brand-flag::after{\n  content:'';position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);\n  width:18px;height:18px;\n  background:" + fern_uri + " center/contain no-repeat;\n}")

# 4.4 語言切換：移除日文鈕（blanket 改名後 title 已變，需按 data-lang 移除）
src = re.sub(r'\s*<button data-lang="ja"[^>]*>.*?</button>', '', src)

# 4.5 首頁特殊成就預覽卡
teaser_old = re.search(r'<div class="ach-teaser">.*?</div>\s*\n\s*</section>', src, re.S)
teaser_new = ('<div class="ach-teaser">' + ''.join(
    '<div class="ach-card"><div class="ic">%s</div><div class="ac-body"><div class="ac-name">%s</div><div class="ac-pts">%s <span>%s</span></div></div></div>'
    % t for t in TEASER) + '</div>\n    </section>')
assert teaser_old, 'teaser'
src = src[:teaser_old.start()] + teaser_new + src[teaser_old.end():]

# 4.6 地圖說明 / 計分說明 細節
src = src.replace('同一縣市多次造訪', '同一大區多次造訪')
src = src.replace('同縣重複造訪', '同大區重複造訪')
src = src.replace('每個縣市只要有一筆旅程就會計分', '每個大區只要有一筆旅程就會計分')
src = src.replace('同一縣市計分以最高造訪層級為準', '同一大區計分以最高造訪層級為準')
src = src.replace('在該縣達成的特殊成就', '在該大區達成的特殊成就')
src = src.replace('並勾選在該縣達成的特殊成就', '並勾選在該大區達成的特殊成就')
src = src.replace('該縣市已達成的成就', '該大區已達成的成就')
src = src.replace('在縣市面板按下', '在大區面板按下')
src = src.replace('點選縣市，按下「新增旅程」', '點選大區，按下「新增旅程」')
src = src.replace('這座縣市的全部旅程紀錄', '這座大區的全部旅程紀錄')
src = src.replace('縣幣評分與旅途照片', '大區評分與旅途照片')
src = src.replace('清除此縣', '清除此大區')

# 4.7 地圖檢視
src = src.replace('點選縣市查看介紹', '點選大區查看介紹')
src = src.replace('先點選縣市，認識日本', '先點選大區，認識紐西蘭')

# 4.8 戰報
src = src.replace('造訪縣市：', '造訪大區：')
src = src.replace('大區已評，平均', '大區已評，平均')
src = src.replace('的縣市', '的大區')

# 4.9 好友排行
src = src.replace("frHead('visited',t('縣市'))", "frHead('visited',t('大區'))")
src = src.replace('還沒有任何資料 — 建立你的地圖，或匯入好友的制霸資料檔開始比拚。',
                  '還沒有任何資料 — 建立你的地圖，或匯入好友的制霸資料檔開始比拚。')

# 4.10 徽章文字
src = src.replace('建立我的地圖', '建立我的地圖')

# 4.11 移除已不存在之 日本 殘留（保險）
leftover = re.findall(r'[日県都道府]', src)
print('leftover JP tokens:', len(leftover))

# ============================================================
# 5. 建立新版 I18N（zh-Hans 由 OpenCC 統一生成；en 走 覆蓋→日版→交換）
# ============================================================
i18n_obj = re.search(r'const I18N = \{.*?\};', i18n_txt, re.S)
assert i18n_obj
i18n_body = i18n_obj.group(0)
# 拆三語 map（單行 JSON 風格）
def extract_map(s, key):
    m = re.search(r"'%s'\s*:\s*\{(.*?)\}\s*," % key, s, re.S) or re.search(r"'%s'\s*:\s*\{(.*?)\}\s*\};" % key, s, re.S)
    return m.group(1) if m else ''

zh_map_txt = extract_map(i18n_body, 'zh-Hans')
en_map_txt = extract_map(i18n_body, 'en')
def parse_js_obj(txt):
    return json.loads('{' + txt + '}')

j_zh = parse_js_obj(zh_map_txt)
j_en = parse_js_obj(en_map_txt)
print('japan zh-Hans keys:', len(j_zh), '| en keys:', len(j_en))

def en_swap(s):
    if not s:
        return s
    for old, new in [
        ('prefectures', 'regions'), ('prefecture', 'region'),
        ('Prefectures', 'Regions'), ('Prefecture', 'Region'),
        ('Japan', 'New Zealand'), ('JPN-', 'NZL-'),
        (' / 47', ' / 16'), (' / 8', ' / 2'), ('/47', '/16'), ('/8', '/2'),
        ('47 ', '16 '), ('47', '16'),
    ]:
        s = s.replace(old, new)
    return s

# 正向改名所有日版鍵
def rename_key(k):
    for old, new in [('縣幣評分', '大區評分'), ('都道府縣', '大區'), ('縣市', '大區'), ('該地區', '該島'),
                     ('地區制霸', '島嶼制霸'), ('地區足跡', '島嶼足跡'), ('縣', '大區'),
                     ('日本制霸地圖', '紐西蘭制霸地圖'), ('日本', '紐西蘭'),
                     (' / 47', ' / 16'), (' / 8', ' / 2'), ('/47', '/16'), ('/8', '/2'),
                     ('JPN-', 'NZL-'), ('jp_lang', 'nz_lang'), ('日文', '英文'), ('47', '16')]:
        k = k.replace(old, new)
    return k

new_zh, new_en = {}, {}
for k in list(j_zh.keys()) + list(j_en.keys()):
    nk = rename_key(k)
    if nk in new_en:
        continue
    if nk in NZ_EN:
        new_en[nk] = NZ_EN[nk]
    elif k in j_en:
        new_en[nk] = en_swap(j_en[k])
    elif nk == k:
        new_en[nk] = nk
    else:
        new_en[nk] = en_swap(j_en.get(k, nk))
# 額外補上 NZ_EN 中尚未收錄的鍵
for k, v in NZ_EN.items():
    if k not in new_en:
        new_en[k] = v
# zh-Hans 全量 OpenCC
for k in list(new_en.keys()):
    if k not in new_zh:
        new_zh[k] = T2S.convert(k)

def dump_js_map(d):
    return '{\n' + ''.join('  %s:%s,\n' % (json.dumps(k, ensure_ascii=False), json.dumps(v, ensure_ascii=False)) for k, v in d.items()) + '}'

i18n_new = 'const I18N = {\n  \'zh-Hans\': ' + dump_js_map(new_zh) + ',\n  \'en\': ' + dump_js_map(new_en) + '\n};'
assert src.count('/*__I18N__*/') == 1, 'I18N placeholder'
src = src.replace('/*__I18N__*/', i18n_new, 1)

# ============================================================
# 6. 鍵覆蓋檢查：最終源碼中的 t() 鍵與靜態文本是否都有 en
# ============================================================
t_keys = set(re.findall(r"t\('([^']+)'\)", src))
data_keys = set()
for i in range(1, 17):
    p = PROVINCES[i]
    data_keys.add(p['tagline'])
    data_keys.update(p['food']); data_keys.update(p['spots']); data_keys.update(p['matsuri'])
for lv in LEVELS: data_keys.add(lv['name'])
for a in ACH: data_keys.add(a['name']); data_keys.add(a['cond'])
data_keys.update(REGIONS.keys()); data_keys.update(ACH_CATS)
# 靜態文本節點（HTML 標籤間含中文者）
text_nodes = set(re.findall(r'>([^<>]{1,80})<', src))
static_keys = {t.strip() for t in text_nodes if re.search(r'[\u4e00-\u9fff]', t) and t.strip()}
# JS 內嵌中文字串（'…' 或 "…" 中含中文；過濾拼接碎片/選擇器/標籤名）
JS_NOISE = {'div', 'button', 'span', 'label', 'canvas', 'textarea', 'tr', 'td', 'th',
            'mdui-button', 'mdui-checkbox', 'mdui-chip', 'mdui-text-field', 'b', 'i', 'h3'}
js_strings = set()
for m in re.finditer(r'''["']([^"'\n]{1,120})["']''', src):
    s = m.group(1)
    if not re.search(r'[\u4e00-\u9fff]', s) or re.match(r'^#[0-9a-fA-F]{3,6}$', s):
        continue
    if "' + " in s or " + '" in s or s.startswith("' + ") or s.endswith(" + '"):
        continue
    if re.match(r'^[#\[\.]', s) or s in JS_NOISE or 'https://' in s or '/assets/' in s:
        continue
    js_strings.add(s)

all_keys = t_keys | data_keys | static_keys | js_strings
missing = [k for k in sorted(all_keys) if k not in new_en]
print('--- missing en keys (%d) ---' % len(missing))
for k in missing:
    print(repr(k))

open(OUT, 'w', encoding='utf-8').write(src)
print('WROTE', OUT, len(src), 'bytes')
