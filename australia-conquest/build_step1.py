# -*- coding: utf-8 -*-
"""Australia Conquest — Step 1: structural transplant from Japan version.
Replaces data blocks (REGIONS/PROVINCES/ACH/LEVELS/...), theme, branding,
geoJSON and global texts. I18N dict left as placeholder, injected in step 2.
"""
import re, json, math, urllib.parse, io

BASE = '/Users/lmc/DoubaoWork/chats/2026-09-09/new-chat-5/australia-conquest'
SRC = BASE + '/index.html'
OUT = BASE + '/index.html'

html = open(SRC, encoding='utf-8').read()

# ---------------------------------------------------------------- helpers
def star_path(cx, cy, r, points, rot=-90):
    pts = []
    for i in range(points * 2):
        ang = math.radians(rot + i * 180.0 / points)
        rr = r if i % 2 == 0 else r * 0.45
        pts.append("%.2f,%.2f" % (cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    return "M" + " L".join(pts) + " Z"

def flag_svg(w=300, h=200):
    """Simplified Australian flag (blue ensign + union jack + southern cross)."""
    p = []
    p.append("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 %d %d'>" % (w, h))
    p.append("<rect width='%d' height='%d' fill='#00247D'/>" % (w, h))
    # union jack upper-left quarter (0..150, 0..100)
    p.append("<path d='M0,0 L150,100 M150,0 L0,100' stroke='#fff' stroke-width='18'/>")
    p.append("<path d='M0,0 L150,100 M150,0 L0,100' stroke='#CF142B' stroke-width='8'/>")
    p.append("<path d='M0,50 L150,50 M75,0 L75,100' stroke='#fff' stroke-width='14'/>")
    p.append("<path d='M0,50 L150,50 M75,0 L75,100' stroke='#CF142B' stroke-width='6'/>")
    # commonwealth star (7-point, under the union jack) + southern cross (4 large 7-point + 1 small 5-point)
    for (cx, cy, r, n) in [(75,60,12,7),(232,148,15,7),(252,112,10,7),(272,166,10,7),(288,128,8,7),(258,186,5,5)]:
        p.append("<path d='%s' fill='#fff'/>" % star_path(cx, cy, r, n))
    p.append("</svg>")
    return "".join(p)

def data_uri(svg):
    return "data:image/svg+xml," + urllib.parse.quote(svg, safe="")

FLAG = flag_svg()
# favicon: 100x100 cream rounded tile with centered 60x40 flag
FAVICON = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>"
           "<rect width='100' height='100' rx='20' fill='#FCF8F3'/>"
           "<svg x='20' y='30' width='60' height='40' viewBox='0 0 300 200'>"
           + FLAG[FLAG.index("<rect"):FLAG.rindex("</svg>")] + "</svg></svg>")
FAVICON_URI = data_uri(FAVICON)
FLAG_URI = data_uri(FLAG)

def count(s, sub):
    return s.count(sub)

# ---------------------------------------------------------------- data blocks
REGIONS_NEW = """const REGIONS = {
  '東部':{name:'東部地方', ids:[1,2,3,8]},
  '南部':{name:'南部地方', ids:[4,6]},
  '西部':{name:'西部地方', ids:[5]},
  '北部':{name:'北部地方', ids:[7]},
};"""

PROVINCES_NEW = """const PROVINCES = {
 1:{ja:'ニューサウスウェールズ',zh:'新南威爾斯',region:'東部',tagline:'悉尼歌劇院與港灣大橋，澳洲的門戶與都會活力。',food:['悉尼岩蠔','肉派','拉明頓蛋糕','澳式早午餐'],spots:['悉尼歌劇院','悉尼港灣大橋','邦迪海灘','藍山國家公園','獵人谷酒莊'],matsuri:['悉尼跨年煙火','繽紛悉尼燈光節','悉尼同性戀狂歡節']},
 2:{ja:'ビクトリア',zh:'維多利亞',region:'東部',tagline:'墨爾本的咖啡文化與大洋路十二門徒，文藝之都的悠閒步調。',food:['墨爾本咖啡','早午餐拼盤','肉派','雅拉谷葡萄酒'],spots:['大洋路十二門徒','聯邦廣場','菲利普島企鵝歸巢','皇家植物園','雅拉谷酒莊'],matsuri:['澳洲網球公開賽','墨爾本盃賽馬節','墨爾本國際喜劇節']},
 3:{ja:'クイーンズランド',zh:'昆士蘭',region:'東部',tagline:'大堡礁與黃金海岸，陽光之州的熱帶樂園。',food:['澳洲和牛','昆士蘭芒果','泥蟹','大堡礁海鮮'],spots:['大堡礁','黃金海岸','凱恩斯熱帶雨林','惠森迪群島','庫蘭達雨林'],matsuri:['黃金海岸美食節','凱恩斯節','布里斯本節']},
 4:{ja:'南オーストラリア',zh:'南澳大利亞',region:'南部',tagline:'巴羅莎谷葡萄酒與袋鼠島荒野，美食美酒之都。',food:['棺材灣生蠔','巴羅莎谷設拉子','袋鼠島蜂蜜','肉派濃湯'],spots:['巴羅莎谷酒莊','袋鼠島','弗林德斯山脈','阿德萊德中央市場','阿德萊德山'],matsuri:['阿德萊德藝穗節','巴羅莎葡萄酒節','阿德萊德盃']},
 5:{ja:'西オーストラリア',zh:'西澳大利亞',region:'西部',tagline:'寧格羅礁與羅特尼斯島，西部曠野與碧海藍天。',food:['西澳岩石龍蝦','瑪格麗特河葡萄酒','淡水螯蝦','印度洋海鮮'],spots:['羅特尼斯島','寧格羅礁','波浪岩','金伯利峽谷','國王公園'],matsuri:['弗里曼特爾街頭藝術節','珀斯邊緣藝術節','瑪格麗特河美食節']},
 6:{ja:'タスマニア',zh:'塔斯馬尼亞',region:'南部',tagline:'搖籃山與塔斯曼尼亞荒野，世界盡頭的島嶼秘境。',food:['塔州生蠔','扇貝派','革木蜂蜜','塔州威士忌'],spots:['搖籃山','塔斯曼半島','亞瑟港','酒杯灣','莎拉曼卡市集'],matsuri:['霍巴特夏日節','暗黑冬夜節','塔州美食節']},
 7:{ja:'ノーザンテリトリー',zh:'北領地',region:'北部',tagline:'烏魯魯與卡卡杜，紅土中心的原住民聖地。',food:['巴拉蒙迪烤魚','袋鼠肉排','灌木叢美食','北領地芒果'],spots:['烏魯魯巨石','卡卡杜國家公園','國王峽谷','達爾文港','凱瑟琳峽谷'],matsuri:['烏魯魯原野星光','達爾文節','明迪海灘日落市集']},
 8:{ja:'首都特別地域',zh:'首都領地',region:'東部',tagline:'堪培拉的國會山與國家美術館，澳洲的心臟與設計之都。',food:['堪培拉松露','農場直送早午餐','首都精釀啤酒','澳式拉花咖啡'],spots:['澳洲國會大廈','澳洲戰爭紀念館','國家美術館','國家植物園','蒂德賓比拉保護區'],matsuri:['堪培拉松露節','堪培拉熱氣球節','國家多元文化節']},
};"""

WH_PREFS_NEW = "const WH_PREFS = [1,2,3,4,5,6,7];"
EN_PREF_NEW = "const EN_PREF = {1:'New South Wales',2:'Victoria',3:'Queensland',4:'South Australia',5:'Western Australia',6:'Tasmania',7:'Northern Territory',8:'Australian Capital Territory'};"

LEVELS_NEW = """const LEVELS = [
  {name:'未踏之旅人',icon:'🧳',pts:0,pct:'2.9%'},
  {name:'旅行初心者',icon:'🌸',pts:10,pct:'0.8%'},
  {name:'觀光旅客',icon:'🏖️',pts:30,pct:'0.7%'},
  {name:'澳洲探索者',icon:'🦘',pts:70,pct:'10.7%'},
  {name:'文化踐行者',icon:'🎭',pts:130,pct:'42%'},
  {name:'旅遊達人',icon:'🌏',pts:210,pct:'32.1%'},
  {name:'澳洲通',icon:'🇦🇺',pts:310,pct:'9.2%'},
  {name:'州領地獵人',icon:'🦜',pts:430,pct:'1.3%'},
  {name:'澳洲制霸者',icon:'👑',pts:580,pct:'0.2%'},
  {name:'傳說的旅人',icon:'🌟',pts:750,pct:'0.1%'},
];"""

TYPE_COLOR_NEW = "const TYPE_COLOR = {1:'#8A8DA8',2:'#E89376',3:'#D2603F',4:'#00247D'};"

ACH_NEW = """const ACH = [
 {id:'A01',cat:'絕景',icon:'🏛️',name:'悉尼歌劇院',pts:15,cond:'新南威爾斯「遊玩」以上',kind:'groups',groups:[[1],2]},
 {id:'A02',cat:'絕景',icon:'🏜️',name:'烏魯魯巨石',pts:20,cond:'北領地「遊玩」以上',kind:'groups',groups:[[7],2]},
 {id:'A03',cat:'絕景',icon:'🐠',name:'大堡礁',pts:20,cond:'昆士蘭「遊玩」以上',kind:'groups',groups:[[3],2]},
 {id:'A04',cat:'絕景',icon:'🌊',name:'十二門徒',pts:16,cond:'維多利亞「遊玩」以上',kind:'groups',groups:[[2],2]},
 {id:'A05',cat:'絕景',icon:'🏔️',name:'搖籃山',pts:14,cond:'塔斯馬尼亞「遊玩」以上',kind:'groups',groups:[[6],2]},
 {id:'A06',cat:'自然',icon:'🌏',name:'澳洲三大自然奇觀',pts:25,cond:'大堡礁・烏魯魯・十二門徒皆「遊玩」以上',kind:'groups',groups:[[3,7,2],2]},
 {id:'A07',cat:'自然',icon:'⛰️',name:'內陸荒野雙雄',pts:16,cond:'金伯利峽谷・弗林德斯山脈皆「遊玩」以上',kind:'groups',groups:[[5,4],2]},
 {id:'A08',cat:'自然',icon:'🌳',name:'世界遺產雨林',pts:15,cond:'丹翠雨林所在之昆士蘭「遊玩」以上',kind:'groups',groups:[[3],2]},
 {id:'A09',cat:'自然',icon:'🌌',name:'南極光',pts:20,cond:'塔斯馬尼亞「住宿」以上',kind:'groups',groups:[[6],3]},
 {id:'A10',cat:'自然',icon:'⛷️',name:'高山滑雪',pts:15,cond:'澳洲阿爾卑斯山脈所在之新南威爾斯＋維多利亞皆「遊玩」以上',kind:'groups',groups:[[1,2],2]},
 {id:'A11',cat:'海岸',icon:'🏄',name:'東岸衝浪三灘',pts:16,cond:'邦迪・黃金海岸・拜倫灣皆「遊玩」以上',kind:'groups',groups:[[1,3],2]},
 {id:'A12',cat:'公路旅行',icon:'🚗',name:'大洋路自駕',pts:15,cond:'維多利亞「遊玩」以上',kind:'groups',groups:[[2],2]},
 {id:'A13',cat:'海岸',icon:'🤿',name:'寧格羅礁浮潛',pts:18,cond:'西澳大利亞「遊玩」以上',kind:'groups',groups:[[5],2]},
 {id:'A14',cat:'海岸',icon:'🍷',name:'酒杯灣',pts:14,cond:'塔斯馬尼亞「遊玩」以上',kind:'groups',groups:[[6],2]},
 {id:'A15',cat:'海岸',icon:'🦩',name:'粉紅湖',pts:16,cond:'希利爾湖・邦邦加湖皆「遊玩」以上',kind:'groups',groups:[[5,4],2]},
 {id:'A16',cat:'動物',icon:'🦘',name:'袋鼠島野生動物',pts:15,cond:'南澳大利亞「遊玩」以上',kind:'groups',groups:[[4],2]},
 {id:'A17',cat:'動物',icon:'🐧',name:'菲利普島企鵝歸巢',pts:14,cond:'維多利亞「遊玩」以上',kind:'groups',groups:[[2],2]},
 {id:'A18',cat:'動物',icon:'😺',name:'羅特尼斯島短尾矮袋鼠',pts:15,cond:'西澳大利亞「遊玩」以上',kind:'groups',groups:[[5],2]},
 {id:'A19',cat:'動物',icon:'🐊',name:'卡卡杜野生動物',pts:16,cond:'北領地「遊玩」以上',kind:'groups',groups:[[7],2]},
 {id:'A20',cat:'動物',icon:'🐨',name:'國寶動物園巡禮',pts:15,cond:'塔龍加・墨爾本動物園・孤松考拉皆「遊玩」以上',kind:'groups',groups:[[1,2,3],2]},
 {id:'A21',cat:'美食',icon:'🍳',name:'澳式早午餐雙城',pts:13,cond:'悉尼・墨爾本皆「遊玩」以上',kind:'groups',groups:[[1,2],2]},
 {id:'A22',cat:'美食',icon:'🍷',name:'葡萄酒三谷',pts:16,cond:'獵人谷・雅拉谷・巴羅莎谷皆「遊玩」以上',kind:'groups',groups:[[1,2,4],2]},
 {id:'A23',cat:'美食',icon:'🦪',name:'生蠔三港',pts:15,cond:'悉尼岩蠔・棺材灣・塔州皆「遊玩」以上',kind:'groups',groups:[[1,4,6],2]},
 {id:'A24',cat:'美食',icon:'🦞',name:'海鮮市場巡禮',pts:14,cond:'悉尼魚市場・阿德萊德中央市場・維多利亞女王市場皆「遊玩」以上',kind:'groups',groups:[[1,4,2],2]},
 {id:'A25',cat:'美食',icon:'🥧',name:'澳式肉派之旅',pts:12,cond:'悉尼・墨爾本・阿德萊德皆「遊玩」以上',kind:'groups',groups:[[1,2,4],2]},
 {id:'A26',cat:'美食',icon:'🍺',name:'精釀啤酒與咖啡',pts:12,cond:'悉尼・墨爾本・布里斯本皆「遊玩」以上',kind:'groups',groups:[[1,2,3],2]},
 {id:'A27',cat:'祭典',icon:'🎆',name:'悉尼跨年煙火',pts:16,cond:'新南威爾斯「遊玩」以上',kind:'groups',groups:[[1],2]},
 {id:'A28',cat:'祭典',icon:'✨',name:'繽紛悉尼燈光節',pts:14,cond:'新南威爾斯「遊玩」以上',kind:'groups',groups:[[1],2]},
 {id:'A29',cat:'祭典',icon:'🎾',name:'澳洲網球公開賽',pts:14,cond:'維多利亞「遊玩」以上',kind:'groups',groups:[[2],2]},
 {id:'A30',cat:'祭典',icon:'🏇',name:'墨爾本盃賽馬節',pts:14,cond:'維多利亞「遊玩」以上',kind:'groups',groups:[[2],2]},
 {id:'A31',cat:'祭典',icon:'🎪',name:'阿德萊德藝穗節',pts:13,cond:'南澳大利亞「遊玩」以上',kind:'groups',groups:[[4],2]},
 {id:'A32',cat:'祭典',icon:'🎈',name:'堪培拉熱氣球節',pts:12,cond:'首都領地「遊玩」以上',kind:'groups',groups:[[8],2]},
 {id:'A33',cat:'祭典',icon:'🌅',name:'明迪海灘日落市集',pts:12,cond:'北領地「遊玩」以上',kind:'groups',groups:[[7],2]},
 {id:'A34',cat:'文化',icon:'🖼️',name:'國家美術館巡禮',pts:15,cond:'新南威爾斯美術館・維多利亞國立美術館・澳洲國家美術館皆「遊玩」以上',kind:'groups',groups:[[1,2,8],2]},
 {id:'A35',cat:'文化',icon:'🏛️',name:'首都文化三館',pts:14,cond:'國會大廈・戰爭紀念館・國家美術館皆「遊玩」以上',kind:'groups',groups:[[8],2]},
 {id:'A36',cat:'文化',icon:'🪃',name:'原住民文化巡禮',pts:18,cond:'烏魯魯・卡卡杜・金伯利皆「遊玩」以上',kind:'groups',groups:[[7,5],2]},
 {id:'A37',cat:'文化',icon:'🏺',name:'世界遺產巡禮',pts:20,cond:'5 個以上「有世界遺產」且「遊玩」以上',kind:'count',prefs:WH_PREFS,level:2,n:5},
 {id:'A38',cat:'文化',icon:'🌲',name:'國家公園巡禮',pts:16,cond:'6 個以上「有國家公園」且「遊玩」以上',kind:'count',prefs:[1,2,3,4,5,6,7,8],level:2,n:6},
 {id:'A39',cat:'文化',icon:'🏛️',name:'殖民歷史巡禮',pts:14,cond:'岩石區・舊墨爾本監獄・亞瑟港皆「遊玩」以上',kind:'groups',groups:[[1,2,6],2]},
 {id:'A40',cat:'運動',icon:'🏉',name:'澳式足球',pts:13,cond:'墨爾本板球場「遊玩」以上',kind:'groups',groups:[[2],2]},
 {id:'A41',cat:'運動',icon:'🏏',name:'板球聖地三場',pts:14,cond:'悉尼板球場・墨爾本板球場・布里斯本板球場皆「遊玩」以上',kind:'groups',groups:[[1,2,3],2]},
 {id:'A42',cat:'運動',icon:'🤿',name:'海底世界雙礁',pts:18,cond:'大堡礁・寧格羅礁皆「遊玩」以上',kind:'groups',groups:[[3,5],2]},
 {id:'A43',cat:'影劇',icon:'⚡',name:'雷神索爾・悉尼',pts:12,cond:'新南威爾斯「遊玩」以上',kind:'groups',groups:[[1],2]},
 {id:'A44',cat:'影劇',icon:'🌊',name:'海王・黃金海岸',pts:12,cond:'昆士蘭「遊玩」以上',kind:'groups',groups:[[3],2]},
 {id:'A45',cat:'影劇',icon:'🕶️',name:'駭客任務・悉尼',pts:13,cond:'新南威爾斯「遊玩」以上',kind:'groups',groups:[[1],2]},
 {id:'A46',cat:'影劇',icon:'🚗',name:'瘋狂麥斯・南澳',pts:13,cond:'南澳大利亞「遊玩」以上',kind:'groups',groups:[[4],2]},
 {id:'A47',cat:'公路旅行',icon:'🛣️',name:'東海岸公路之旅',pts:16,cond:'悉尼→布里斯本→凱恩斯皆「遊玩」以上',kind:'groups',groups:[[1,3],2]},
 {id:'A48',cat:'公路旅行',icon:'🏜️',name:'紅土中心公路之旅',pts:16,cond:'愛麗絲泉→烏魯魯→國王峽谷皆「遊玩」以上',kind:'groups',groups:[[7],2]},
 {id:'A49',cat:'公路旅行',icon:'🏝️',name:'塔斯曼尼亞環島自駕',pts:15,cond:'塔斯馬尼亞「遊玩」以上',kind:'groups',groups:[[6],2]},
 {id:'A50',cat:'公路旅行',icon:'🛻',name:'西部曠野四驅',pts:16,cond:'金伯利峽谷所在之西澳大利亞「遊玩」以上',kind:'groups',groups:[[5],2]},
 {id:'A51',cat:'絕景',icon:'🏙️',name:'三大都會夜景',pts:16,cond:'悉尼・墨爾本・布里斯本皆「遊玩」以上',kind:'groups',groups:[[1,2,3],2]},
 {id:'A52',cat:'海岸',icon:'⛱️',name:'城市海灘',pts:13,cond:'邦迪・聖科達・科特斯洛皆「遊玩」以上',kind:'groups',groups:[[1,2,5],2]},
];"""

ACH_CATS_NEW = "const ACH_CATS = ['全部','絕景','祭典','美食','文化','自然','海岸','動物','運動','影劇','公路旅行'];"

LABEL_MAJOR_NEW = "const LABEL_MAJOR = new Set([1,2,3,4,5,6,7,8]);"
PREF_IMG_NEW = "const PREF_IMG = {1:'assets/prefs/01_nsw.jpg', 2:'assets/prefs/02_vic.jpg', 3:'assets/prefs/03_qld.jpg', 4:'assets/prefs/04_sa.jpg', 5:'assets/prefs/05_wa.jpg', 6:'assets/prefs/06_tas.jpg', 7:'assets/prefs/07_nt.jpg', 8:'assets/prefs/08_act.jpg'};"

I18N_PLACEHOLDER = "const I18N = {'zh-Hans':{},'ja':{},'en':{}};"

# ---------------------------------------------------------------- replacements (ordered: long & specific first)
repl = []

# ---- head / branding
repl.append(("<title>日本制霸地圖 · 記錄你走過的每一寸日本</title>",
             "<title>澳洲制霸地圖 · 記錄你走過的每一寸澳洲</title>"))
repl.append((re.compile(r'<link rel="icon" href="data:image/svg\+xml,[^"]*">'),
             '<link rel="icon" href="%s">' % FAVICON_URI))
repl.append(('純靜態的日本 47 都道府縣制霸記錄器：點選地圖、記錄旅程、累積分數、解鎖成就、升級等級。資料只存於本機瀏覽器。',
             '純靜態的澳洲 8 個州與領地制霸記錄器：點選地圖、記錄旅程、累積分數、解鎖成就、升級等級。資料只存於本機瀏覽器。'))
repl.append(('日本<span class="jp">制霸</span>地圖', '澳洲<span class="jp">制霸</span>地圖'))
repl.append(('<p class="hero-sub">記錄你走過的每一寸日本，看看你制霸了幾個縣？</p>',
             '<p class="hero-sub">記錄你走過的每一寸澳洲，看看你制霸了幾個州與領地？</p>'))
repl.append(('<div class="hero-stat"><div class="num">47</div><div class="lbl">縣市</div></div>',
             '<div class="hero-stat"><div class="num">8</div><div class="lbl">州與領地</div></div>'))
repl.append(('日本<b>制霸</b>地圖', '澳洲<b>制霸</b>地圖'))
repl.append(('日本制霸地圖 · 純靜態版', '澳洲制霸地圖 · 純靜態版'))

# ---- theme colors (vermilion red -> flag blue)
repl.append(("--vermilion:#B02A1A;", "--vermilion:#00247D;"))
repl.append(("--vermilion-deep:#8C1F12;", "--vermilion-deep:#001433;"))
repl.append(("background-image:radial-gradient(rgba(176,42,26,.07) 1px,transparent 1.4px);",
             "background-image:radial-gradient(rgba(0,36,125,.08) 1px,transparent 1.4px);"))
repl.append(("rgba(176,42,26,.35)", "rgba(0,36,125,.40)"))
repl.append(("rgba(176,42,26,.6)", "rgba(0,36,125,.65)"))
repl.append(("rgba(176,42,26,.08)", "rgba(0,36,125,.08)"))
repl.append(("rgba(176,42,26,.12)", "rgba(0,36,125,.12)"))
repl.append(('<span class="sw" style="background:#B02A1A"></span>長居 +20',
             '<span class="sw" style="background:#00247D"></span>長居 +20'))

# ---- brand-flag & hero-flag CSS -> australian flag images
repl.append((re.compile(r'\.brand-flag\{[^}]*\}'), None))  # removed & rebuilt below
repl.append((re.compile(r'\.brand-flag::after\{[^}]*\}'), None))
repl.append(('.brand-name{', '.brand-flag{width:30px;height:21px;border-radius:4px;background:#fff url("%s") center/cover no-repeat;box-shadow:inset 0 0 0 1px rgba(33,26,23,.14);position:relative;flex:none}\n.brand-name{' % FLAG_URI))
repl.append((re.compile(r'\.hero-flag\{[^}]*\}'), None))
repl.append((re.compile(r'\.hero-flag::after\{[^}]*\}'), None))
repl.append(('.hero h1{', '.hero-flag{width:84px;height:59px;border-radius:12px;background:#fff url("%s") center/cover no-repeat;box-shadow:var(--shadow-2),inset 0 0 0 1px rgba(33,26,23,.10);margin:0 auto 22px;position:relative}\n.hero h1{' % FLAG_URI))

# ---- geojson
repl.append((re.compile(r'<script>window\.JAPAN_GEOJSON = \{.*?\};</script>', re.S), None))  # rebuilt below

# ---- data blocks
repl.append((re.compile(r'const REGIONS = \{.*?\n\};', re.S), REGIONS_NEW))
repl.append((re.compile(r'const PROVINCES = \{.*?\n\};', re.S), PROVINCES_NEW))
repl.append(("const WH_PREFS = [1,2,3,5,9,10,13,15,16,19,21,22,23,24,26,27,28,29,30,32,34,35,40,42,46,47];", WH_PREFS_NEW))
repl.append(("const LANG_KEY = 'jp_lang';", "const LANG_KEY = 'au_lang';"))
repl.append(("const LANGS = ['zh-Hant','zh-Hans','ja','en'];", "const LANGS = ['zh-Hant','zh-Hans','ja','en'];"))
repl.append((re.compile(r'const EN_PREF = \{.*?\};', re.S), EN_PREF_NEW))
repl.append((re.compile(r'const I18N = \{.*?\n\};', re.S), I18N_PLACEHOLDER))
repl.append((re.compile(r'const LEVELS = \[.*?\n\];', re.S), LEVELS_NEW))
repl.append(("const TYPE_COLOR = {1:'#8A7A72',2:'#E89376',3:'#D2603F',4:'#B02A1A'};", TYPE_COLOR_NEW))
repl.append((re.compile(r'const ACH = \[.*?\n\];', re.S), ACH_NEW))
repl.append(("const ACH_CATS = ['全部','絕景','祭典','溫泉','美食','文化','自然','城堡','運動','影劇','動漫'];", ACH_CATS_NEW))
repl.append(("const LS_REG = 'japanMap.registry';", "const LS_REG = 'ausMap.registry';"))
repl.append(("const LS_ACTIVE = 'japanMap.active';", "const LS_ACTIVE = 'ausMap.active';"))
repl.append(("const LS_DATA = 'japanMap.data.';", "const LS_DATA = 'ausMap.data.';"))
repl.append(("    c = 'JPN-';", "    c = 'AUS-';"))
repl.append((re.compile(r'const PREF_IMG = \{.*?\};', re.S), PREF_IMG_NEW))
repl.append(("const LABEL_MAJOR = new Set([1,2,3,4,5,6,7,13,15,16,20,22,23,27,28,30,31,34,36,37,40,42,43,44,46,47]);", LABEL_MAJOR_NEW))

# ---- hardcoded numbers in JS logic
repl.append(("  for(let id=1; id<=47; id++){", "  for(let id=1; id<=8; id++){"))
repl.append(("  for(let id = 1; id <= 47; id++){", "  for(let id = 1; id <= 8; id++){"))
repl.append(("    [s.visited, t('造訪縣市'), '/ 47'],", "    [s.visited, t('造訪州領地'), '/ 8'],"))
repl.append(("    [s.regionsDone, t('地區制霸'), '/ 8'],", "    [s.regionsDone, t('地區制霸'), '/ 4'],"))
repl.append(("'<td>' + r.visited + '/47</td>'", "'<td>' + r.visited + '/8</td>'"))

# ---- footer / credits
repl.append(('都道府縣邊界 © dataofjapan（GeoJSON）· 地圖渲染 Leaflet · 介面 MDUI 2',
             '州與領地邊界 © ABS ASGS / GeoJson-Data（GeoJSON）· 地圖渲染 Leaflet · 介面 MDUI 2'))

# ---- generic term swap in static HTML + JS strings (non-dict regions)
# NOTE: run AFTER the specific replacements below and AFTER dict replaced with placeholder;
# T2S table (line ~1180) untouched by design. The '縣'->'州' rule must NOT hit the T2S map,
# so we split the T2S region out before swapping and reattach it after.
term_map = [
    ('都道府縣', '州與領地'),
    ('縣市獵人', '州領地獵人'),
    ('縣幣評分', '州幣評分'),
    ('縣已評', '州已評'),
    ('個縣市', '個州領地'),
    ('座縣市', '座州領地'),
    ('每縣最多 ', '每州領地最多 '),
    ('清除此縣', '清除此州領地'),
    ('縣市', '州領地'),
    ('全縣', '全州'),
    ('個縣', '個州'),
    ('該縣', '該州領地'),
    ('這座縣市', '這座州領地'),
    ('在這一縣', '在這一州領地'),
    ('該縣市', '該州領地'),
    ('此縣', '此州領地'),
    ('一座縣市', '一座州領地'),
    ('縣（', '州（'),
    ('縣已', '州已'),
    ('縣「', '州「'),
    ('縣」', '州」'),
    ('縣 ', '州 '),
    ('縣？', '州？'),
    ('縣／', '州／'),
    ('縣、', '州、'),
    ('縣＋', '州＋'),
    ('縣・', '州・'),
    ('縣，', '州，'),
    ('縣。', '州。'),
    ('縣）', '州）'),
    ('縣：', '州：'),
    ('縣/', '州/'),
    ('縣）', '州）'),
    ('縣', '州'),
]
# (execution moved after the specific replacements below)

for old, new in repl:
    if isinstance(old, str):
        if old not in html:
            raise SystemExit("MISSING STRING: " + old[:80])
        html = html.replace(old, new, 1)
    else:
        m = old.search(html)
        if not m:
            raise SystemExit("MISSING REGEX: " + old.pattern[:80])
        if new is None:
            html = html[:m.start()] + html[m.end():]
        else:
            html = html[:m.start()] + new + html[m.end():]

# ---- generic term swap (after specific replacements)
t2s_start = html.find('const T2S = {')
t2s_end = html.find('};', t2s_start) + 2
t2s_region = html[t2s_start:t2s_end]
head = html[:t2s_start]
tail = html[t2s_end:]
for old, new in term_map:
    head = head.replace(old, new)
    tail = tail.replace(old, new)
html = head + t2s_region + tail

# ---- geojson injection (needs the term-swapped html to find script tag? no, plain anchor)
aus_geojson = json.load(open('/tmp/aus1.geojson', encoding='utf-8'))
feats = []
for f in aus_geojson['features']:
    code = int(f['properties']['STATE_CODE'])
    feats.append({"type": "Feature", "properties": {"id": code}, "geometry": f['geometry']})
geojson_block = '<script>window.AUS_GEOJSON = ' + json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False, separators=(',', ':')) + ';</script>'
# insert right before the leaflet script include (which follows the old geojson script tag)
anchor = '<script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js">'
if anchor not in html:
    raise SystemExit("leaflet anchor missing")
html = html.replace(anchor, geojson_block + "\n" + anchor, 1)

# ---- JS references to JAPAN_GEOJSON -> AUS_GEOJSON
html = html.replace('window.JAPAN_GEOJSON', 'window.AUS_GEOJSON')

# ---- remaining UI strings (already term-swapped; fix specifics)
html = html.replace('日本', '澳洲')
html = html.replace('識別碼　例：JPN-A3K9', '識別碼　例：AUS-A3K9')
html = html.replace('都道府縣', '州與領地')

open(OUT, 'w', encoding='utf-8').write(html)
print("OK. bytes:", len(html.encode('utf-8')))
print("AUS_GEOJSON feats:", len(feats))
