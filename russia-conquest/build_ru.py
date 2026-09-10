# -*- coding: utf-8 -*-
# 俄羅斯制霸地圖 — 主構建腳本（基於日本版遷移）
import re, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import opencc
from ru_data_a import P_A
from ru_data_b import P_B
from ru_data_c import REGIONS_NEW, EN_PREF_NEW, WH_PREFS_NEW, LEVELS_NEW, ACH_CATS_NEW, ACH_NEW, ACH_MANUAL_NEW, LABEL_MAJOR_NEW, THEME
from ru_i18n import UI_JA, UI_EN, ACH_JA, ACH_EN, LEVELS_JA, LEVELS_EN, TYPE_NAME_JA, TYPE_NAME_EN, ACH_CATS_JA, ACH_CATS_EN

BASE = '/Users/lmc/DoubaoWork/chats/2026-09-08/new-chat/japan-conquest/index.html'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')

P = {}
P.update(P_A); P.update(P_B)
assert len(P) == 83, len(P)
assert set(P.keys()) == set(range(1,84))

converter = opencc.OpenCC('t2s')

# ---------- 工具 ----------
def js_str(s):
    return json.dumps(s, ensure_ascii=False)

# ---------- 生成資料塊 ----------
def gen_regions():
    lines = ['const REGIONS = {']
    for k, (name, ja, en, ids) in REGIONS_NEW.items():
        lines.append("  %s:{name:%s, ids:[%s]},  // %s" % (js_str(k), js_str(name), ','.join(map(str, ids)), ja))
    lines.append('};')
    return '\n'.join(lines)

def gen_provinces():
    lines = ['const PROVINCES = {']
    for pid in sorted(P):
        p = P[pid]
        tag = p[3][0]; foods = p[4]; spots = p[5]; mats = p[6]
        lines.append(" %d:{ja:%s,zh:%s,region:%s,tagline:%s,food:[%s],spots:[%s],matsuri:[%s]}," % (
            pid, js_str(p[0]), js_str(p[1]), js_str(p[2]), js_str(tag),
            ','.join(js_str(x[0]) for x in foods),
            ','.join(js_str(x[0]) for x in spots),
            ','.join(js_str(x[0]) for x in mats)))
    lines.append('};')
    return '\n'.join(lines)

def gen_wh():
    return 'const WH_PREFS = [' + ','.join(map(str, WH_PREFS_NEW)) + '];'

def gen_en():
    return 'const EN_PREF = {' + ','.join('%d:%s' % (k, js_str(v)) for k, v in sorted(EN_PREF_NEW.items())) + '};'

def gen_levels():
    lines = ['const LEVELS = [']
    for lv in LEVELS_NEW:
        lines.append("  {name:%s,icon:%s,pts:%d,pct:%s}," % (js_str(lv['name']), js_str(lv['icon']), lv['pts'], js_str(lv['pct'])))
    lines.append('];')
    return '\n'.join(lines)

def gen_ach():
    lines = ['const ACH = [']
    for a in ACH_NEW:
        extra = ''
        if a['kind'] == 'groups':
            g = a['groups'][0]
            extra = 'groups:[[%s],%d]' % (','.join(map(str, g)), a['groups'][1])
        elif a['kind'] == 'count':
            extra = 'prefs:[%s],level:%d,n:%d' % (','.join(map(str, a['prefs'])), a['level'], a['n'])
        lines.append("{id:%s,cat:%s,icon:%s,name:%s,pts:%d,cond:%s,kind:%s,%s}," % (
            js_str(a['id']), js_str(a['cat']), js_str(a['icon']), js_str(a['name']), a['pts'], js_str(a['cond']), js_str(a['kind']), extra))
    for a in ACH_MANUAL_NEW:
        lines.append("{id:%s,cat:%s,icon:%s,name:%s,pts:%d,cond:%s,kind:%s,prefs:[%s],level:%d}," % (
            js_str(a['id']), js_str(a['cat']), js_str(a['icon']), js_str(a['name']), a['pts'], js_str(a['cond']), js_str(a['kind']),
            ','.join(map(str, a['prefs'])), a['level']))
    lines.append('];')
    return '\n'.join(lines)

def gen_cats():
    return 'const ACH_CATS = [' + ','.join(js_str(c) for c in ACH_CATS_NEW) + '];'

def gen_fills():
    f = THEME['FILLS']
    return 'const FILLS = {' + ','.join('%d:%s' % (k, js_str(v)) for k, v in sorted(f.items())) + '};'

def gen_type_color():
    f = THEME['TYPE_COLOR']
    return 'const TYPE_COLOR = {' + ','.join('%d:%s' % (k, js_str(v)) for k, v in sorted(f.items())) + '};'

def gen_label():
    return 'const LABEL_MAJOR = new Set([' + ','.join(map(str, LABEL_MAJOR_NEW)) + ']);'

# ---------- 術語／數字／品牌替換詞表 ----------
TERM = [
    ('都道府縣', '聯邦主體'),
    ('縣幣評分', '主體幣評分'),
    ('縣已評分', '主體已評分'),
    ('縣已評，平均', '主體已評，平均'),
    ('縣已評', '主體已評'),
    ('個縣市', '個聯邦主體'),
    ('座縣市', '個聯邦主體'),
    ('每縣最多 ', '每主體最多 '),
    ('清除此縣', '清除此主體'),
    ('全縣制霸', '全俄制霸'),
    ('全縣', '全境'),
    ('該縣市', '該聯邦主體'),
    ('該縣', '該主體'),
    ('這座縣市', '這個聯邦主體'),
    ('此縣', '此主體'),
    ('一座縣市', '一個聯邦主體'),
    ('在這一縣', '在這個主體'),
    ('縣市', '聯邦主體'),
    ('縣', '主體'),
]
NUM_PHRASES = [
    ('太厲害了 — 47 縣全部造訪過', '太厲害了 — 83 個聯邦主體全部造訪過'),
    ('47 縣全部', '83 個聯邦主體全部'),
    ('47 縣', '83 個聯邦主體'),
    ('47 都道府縣', '83 個聯邦主體'),
    ('47 縣市', '83 聯邦主體'),
    ('數字碼 1-47', '數字碼 1-83'),
]
DICT_NUM = [
    (' / 47', ' / 83'),
    ('縣市 / 47', '聯邦主體 / 83'),
    ('/47</td>', '/83</td>'),
]
BRAND = [
    ('日本制霸地圖', '俄羅斯制霸地圖'),
    ('日本', '俄羅斯'),
    ('日文', '俄文'),
]
JS_SPEC = [
    ('id<=47', 'id<=83'),
    ('id <= 47', 'id <= 83'),
    ("'/ 47'", "'/ 83'"),
    ("t('造訪縣市 / 47')", "t('造訪聯邦主體 / 83')"),
    ("' / 47'", "' / 83'"),
    ("'/47</td>'", "'/83</td>'"),
    ('minZoom:4.2', 'minZoom:2.5'),
    ('window.JAPAN_GEOJSON', 'window.RUS_GEOJSON'),
    ('japanMap', 'rusMap'),
    ('jp_lang', 'ru_lang'),
    ("'JPN-'", "'RUS-'"),
    ('JPN-A3K9', 'RUS-A3K9'),
    ('dataofjapan', 'russian-geo-data'),
    ('const GB = { minLon: 123.6, maxLon: 146.2, minLat: 24.0, maxLat: 45.7 }',
     'const GB = { minLon: 19.68, maxLon: 190.30, minLat: 41.19, maxLat: 81.86 }'),
    ('rgba(158,36,24,.4)', 'rgba(31,78,156,.4)'),
    ('rgba(158,36,24,.3)', 'rgba(31,78,156,.3)'),
    ('rgba(158,36,24,.15)', 'rgba(31,78,156,.15)'),
    ('rgba(158,36,24,0)', 'rgba(31,78,156,0)'),
    ('#9E2418', '#1F4E9C'),
    ('#7A1A10', '#122F63'),
    ('#C44A3A', '#4F78C8'),
    ('rgba(176,42,26', 'rgba(31,78,156'),
    ('#B02A1A', '#1F4E9C'),
    ('#8C1F12', '#122F63'),
    # 修復日本版遺留 bug：局部變數 t 遮蔽全域 t()，導致含手動成就的主體無法開啟記錄對話框
    ("const t = document.createElement('span');\n      t.className = 'ac-t';",
     "const sp = document.createElement('span');\n      sp.className = 'ac-t';"),
    ('      label.appendChild(t);', '      label.appendChild(sp);'),
    ('      t.innerHTML = ', '      sp.innerHTML = '),
]

# ---------- 生成 I18N ----------
def build_i18n():
    """返回 (zh_hant, zh_hans, ja, en)。以日本版全量鍵集 + 術語映射為骨架，
    內容鍵另行加入；ja/en 缺譯時回落到日本版原翻譯。"""
    jp = json.load(open('/tmp/rugeo/jp_i18n.json', encoding='utf-8'))
    jp_keys = list(jp['zhHans'].keys())
    zh_hant = {}
    zh_hans = {}
    ja = {}
    en = {}
    def add(k, j=None, e=None):
        if k in zh_hant: return
        zh_hant[k] = k
        zh_hans[k] = converter.convert(k)
        if j is not None: ja[k] = j
        if e is not None: en[k] = e
    def ru_key(jp_k):
        for a, b in NUM_PHRASES: jp_k = jp_k.replace(a, b)
        for a, b in TERM: jp_k = jp_k.replace(a, b)
        for a, b in BRAND: jp_k = jp_k.replace(a, b)
        for a, b in DICT_NUM: jp_k = jp_k.replace(a, b)
        return jp_k
    # 1) 俄版自寫 UI 鍵（優先，衝突時勝出）
    for k, j in UI_JA.items():
        add(k, j, UI_EN.get(k))
    # 2) 日本版全量鍵（術語映射後），翻譯缺則回落日本原譯
    for k in jp_keys:
        rk = ru_key(k)
        add(rk, UI_JA.get(rk) or jp['ja'].get(k), UI_EN.get(rk) or jp['en'].get(k))
    # 2) 內容鍵：tagline / food / spots / matsuri
    for pid in P:
        p = P[pid]
        add(p[3][0], p[3][1], p[3][2])
        for f in p[4]: add(f[0], f[1], f[2])
        for s in p[5]: add(s[0], s[1], s[2])
        for m in p[6]: add(m[0], m[1], m[2])
    # 3) 地區名
    for k, (name, jname, ename, ids) in REGIONS_NEW.items():
        add(name, jname, ename)
    # 4) 等級名
    for lv in LEVELS_NEW:
        n = lv['name']
        add(n, LEVELS_JA.get(n), LEVELS_EN.get(n))
    # 5) 造訪類型名
    for k, v in TYPE_NAME_JA.items():
        add(k, v, TYPE_NAME_EN.get(k))
    # 6) 成就類別
    for c in ACH_CATS_NEW:
        add(c, ACH_CATS_JA.get(c), ACH_CATS_EN.get(c))
    # 7) 成就名與條件
    for a in ACH_NEW + ACH_MANUAL_NEW:
        add(a['name'], ACH_JA.get(a['name']), ACH_EN.get(a['name']))
        add(a['cond'], ACH_JA.get(a['cond']), ACH_EN.get(a['cond']))
    # 8) 已知 JS 呼叫與 dict 鍵的文本差異（日本版遺留），補齊該變體鍵
    add('在聯邦主體面板按下「☆ 想去」收藏，或在地圖上點選找靈感。',
        '連邦構成主体パネルで「☆ 行きたい」を押して保存するか、地図上をクリックしてインスピレーションを探しましょう。',
        'Press "☆ Want to go" on a federal subject panel to save it, or click the map for inspiration.')
    # 9) 動態/拼接片段鍵（日本版同樣缺失、靠回落顯示中文；俄版補齊翻譯）
    DYNA = [
        ('識別碼 ', '識別コード ', 'ID '),
        ('【俄羅斯制霸戰報】', '【ロシア制覇レポート】', '【Russia Conquest Report】'),
        ('」（', '」（', '」('),
        ('）的全部旅程紀錄與成就將從本機刪除，無法復原。建議先匯出備份。',
         '）に含まれるすべての旅程記録と実績はこの端末から削除され、復元できません。事前にエクスポートすることをおすすめします。',
         '） — all journey records and achievements for this map will be deleted from this device and cannot be restored. Export a backup first.'),
        ('當前制霸等級', '現在の制覇レベル', 'Current level'),
        ('造訪聯邦主體', '訪問した連邦構成主体', 'Subjects visited'),
        ('地區制霸', '地域制覇', 'Regions'),
        ('解鎖成就', '達成した実績', 'Achievements'),
        ('地區足跡', '地域の足跡', 'Region footprints'),
        (' 主體已評分', ' 主体を評価済み', ' rated'),
        ('平均 ', '平均 ', 'Avg. '),
        ('— 由「俄羅斯制霸地圖」純靜態版產生 —',
         '— 「ロシア制覇地図」の純スタティック版によって生成 —',
         '— Generated by the pure static "Russia Conquest Map" —'),
    ]
    for k, j, e in DYNA:
        add(k, j, e)
    # 9) 檢查缺漏
    miss_ja = [k for k in zh_hant if k not in ja]
    miss_en = [k for k in zh_hant if k not in en]
    if miss_ja: print('WARN missing ja:', miss_ja[:30])
    if miss_en: print('WARN missing en:', miss_en[:30])
    return zh_hant, zh_hans, ja, en

zh_hant, zh_hans, ja, en = build_i18n()

def gen_i18n():
    def fmt(d):
        return ','.join('%s:%s' % (js_str(k), js_str(v)) for k, v in d.items())
    return ('const I18N = {\n'
            "  'zh-Hant':{" + fmt(zh_hant) + '},\n'
            "  'zh-Hans':{" + fmt(zh_hans) + '},\n'
            "  'ja':{" + fmt(ja) + '},\n'
            "  'en':{" + fmt(en) + '}\n'
            '};')

# ---------- 載入基礎 ----------
html = open(BASE, encoding='utf-8').read()

GJ_START = '<script>window.JAPAN_GEOJSON = '
gj_pos = html.find(GJ_START)
assert gj_pos >= 0
script_end = html.find('</script>', gj_pos)
head = html[:gj_pos]
tail = html[script_end + len('</script>'):]

# ---------- 1) GeoJSON ----------
geo = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ru83.geojson'), encoding='utf-8'))
geojson_script = '<script>window.RUS_GEOJSON = ' + json.dumps(geo, ensure_ascii=False, separators=(',', ':')) + ';</script>'

# ---------- 2) tail 資料塊替換 ----------
def replace_const(src, const_name, new_text, end_pat=None):
    i = src.find('const ' + const_name)
    assert i >= 0, const_name
    if end_pat is None:
        end_pat = ';'
    m = re.search(end_pat, src[i:])
    assert m, const_name
    return src[:i] + new_text + src[i + m.end():]

tail = replace_const(tail, 'REGIONS', gen_regions(), end_pat=r'\n\};')
tail = replace_const(tail, 'PROVINCES', gen_provinces(), end_pat=r'\n\};')
tail = replace_const(tail, 'WH_PREFS', gen_wh(), end_pat=';')
tail = replace_const(tail, 'EN_PREF', gen_en(), end_pat=';')
# I18N dict: from 'const I18N = {' to the '\n};' that precedes 'const LEVELS'
i18n_start = tail.find('const I18N = {')
i18n_end = tail.find('\n};', i18n_start) + 3
tail = tail[:i18n_start] + gen_i18n() + tail[i18n_end:]
tail = replace_const(tail, 'LEVELS', gen_levels(), end_pat=r'\n\];')
tail = replace_const(tail, 'TYPE_COLOR', gen_type_color(), end_pat=';')
tail = replace_const(tail, 'ACH', gen_ach(), end_pat=r'\n\];')
tail = replace_const(tail, 'ACH_CATS', gen_cats(), end_pat=';')
tail = replace_const(tail, 'FILLS', gen_fills(), end_pat=';')
tail = replace_const(tail, 'LABEL_MAJOR', gen_label(), end_pat=';')
# 从 assets/prefs/ 扫描生成 PREF_IMG 映射
import glob as _glob
_pref_img_items = []
for _fp in sorted(_glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'prefs', '*.jpg'))):
    _bn = os.path.basename(_fp)
    _pid = int(_bn.split('_')[0])
    _pref_img_items.append(f"{_pid}:'assets/prefs/{_bn}'")
_pref_img_str = 'const PREF_IMG = {' + ', '.join(_pref_img_items) + '};'
tail = replace_const(tail, 'PREF_IMG', _pref_img_str, end_pat=';')

# ---------- 3) 術語／數字／品牌替換（head 與 tail，排除 T2S） ----------
def apply_static(seg, exclude_start=None, exclude_end=None):
    if exclude_start is not None:
        pre = seg[:exclude_start]
        mid = seg[exclude_start:exclude_end]
        post = seg[exclude_end:]
    else:
        pre, mid, post = seg, '', ''
    for a, b in NUM_PHRASES: pre = pre.replace(a, b); post = post.replace(a, b)
    for a, b in JS_SPEC: pre = pre.replace(a, b); post = post.replace(a, b)
    for a, b in TERM: pre = pre.replace(a, b); post = post.replace(a, b)
    for a, b in BRAND: pre = pre.replace(a, b); post = post.replace(a, b)
    return pre + mid + post

# head: 不含 T2S/dict/data，直接全量替換
head = apply_static(head)

# tail: 排除 T2S 區段（T2S 在 tail 開頭附近？T2S 在 695874，位於 EN_PREF 之後 —— 即 head 與 tail 之間？
# 注意：T2S 位於原始檔 geojson script 之後、I18N 之前，而我們的 tail 從 </script> 開始，
# 包含 REGIONS..EN_PREF..T2S..I18N..LEVELS..main JS。因此 T2S 在 tail 內。
t2s_i = tail.find('const T2S = {')
t2s_j = tail.find('\n};', t2s_i) + 3
tail = apply_static(tail, t2s_i, t2s_j)

# ---------- 4) head 額外品牌替換（flag CSS / favicon / meta / hero） ----------
RUS_FLAG_SVG = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 900 600'><rect width='900' height='200' fill='%23FFFFFF'/><rect y='200' width='900' height='200' fill='%230039A6'/><rect y='400' width='900' height='200' fill='%23D52B1E'/></svg>"
RUS_ICON_SVG = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='20' fill='%23FFFFFF'/><rect y='20' width='100' height='20' fill='%230039A6'/><rect y='40' width='100' height='20' fill='%23D52B1E'/><rect y='60' width='100' height='20' fill='%23FFFFFF'/></svg>"
head = head.replace("<title>日本制霸地圖 · 記錄你走過的每一寸日本</title>",
                    "<title>俄羅斯制霸地圖 · 記錄你走過的每一寸俄羅斯</title>")
head = head.replace("<circle cx='50' cy='50' r='26' fill='%23B02A1A'/>",
                    "<rect y='20' width='100' height='20' fill='%230039A6'/><rect y='40' width='100' height='20' fill='%23D52B1E'/>")
head = head.replace('純靜態的日本 47 都道府縣制霸記錄器',
                    '純靜態的俄羅斯 83 個聯邦主體制霸記錄器')
# hero-flag / brand-flag ::after → 三色旗
head = head.replace(""".brand-flag::after{
  content:'';position:absolute;left:50%;top:50%;
  width:11px;height:11px;border-radius:50%;
  background:var(--vermilion);transform:translate(-50%,-50%);
}""", """.brand-flag::after{
  content:'';position:absolute;left:0;top:0;width:100%;height:100%;
  border-radius:3px;background:linear-gradient(#fff 0 33.3%,#0039A6 33.3% 66.6%,#D52B1E 66.6% 100%);
}""")
head = head.replace(""".hero-flag::after{
  content:'';position:absolute;left:50%;top:50%;
  width:31px;height:31px;border-radius:50%;
  background:var(--vermilion);transform:translate(-50%,-50%);
}""", """.hero-flag::after{
  content:'';position:absolute;left:0;top:0;width:100%;height:100%;
  border-radius:10px;background:linear-gradient(#fff 0 33.3%,#0039A6 33.3% 66.6%,#D52B1E 66.6% 100%);
}""")
# 主題色變數
head = head.replace('--vermilion:#B02A1A', '--vermilion:#1F4E9C')
head = head.replace('--vermilion-deep:#8C1F12', '--vermilion-deep:#122F63')

# hero 文案
head = head.replace('<h1 class="hero-title">日本制霸地圖</h1>', '<h1 class="hero-title">俄羅斯制霸地圖</h1>')
head = head.replace('<div class="hero-stat"><div class="num">47</div><div class="lbl">聯邦主體</div></div>',
                    '<div class="hero-stat"><div class="num">83</div><div class="lbl">聯邦主體</div></div>')
head = head.replace('記錄你走過的每一寸日本，看看你制霸了幾個縣？', '記錄你走過的每一寸俄羅斯，看看你制霸了幾個聯邦主體？')

# ---------- 5) 拼裝 ----------
out = head + geojson_script + tail
open(OUT, 'w', encoding='utf-8').write(out)
print('written:', OUT, len(out))
