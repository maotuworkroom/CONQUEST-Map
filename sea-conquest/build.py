#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Southeast Asia Conquest Map — build script.
Transforms the Japan static conquest map into a Southeast Asia (11 countries) version.
"""
import re, json, sys
from html.parser import HTMLParser

SRC = '/Users/lmc/DoubaoWork/chats/2026-09-08/new-chat/japan-conquest/index.html'
OUT = '/Users/lmc/DoubaoWork/chats/2026-09-09/new-chat-6/sea-conquest/index.html'

orig = open(SRC, encoding='utf-8').read()

def fail(msg):
    print('!! ' + msg)
    sys.exit(1)

def sub(s, old, new, count=1):
    n = s.count(old)
    if n == 0: fail('MISSING: ' + old[:150])
    if count is not None and n != count: fail(f'COUNT {n} != {count}: ' + old[:150])
    return s.replace(old, new)

def sub_all(s, old, new, min_count=1):
    n = s.count(old)
    if n < min_count: fail('MISSING(all): ' + old[:150])
    return s.replace(old, new)

def brace_block(s, start_marker):
    i = s.find(start_marker)
    if i == -1: fail('marker missing: ' + start_marker)
    j = s.find('{', i)
    depth, k = 0, j
    while k < len(s):
        c = s[k]
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: return i, k + 1
        k += 1
    fail('unbalanced: ' + start_marker)

def jq(o):
    return json.dumps(o, ensure_ascii=False)

# ════════════════════════════════════════════════════════════════
# 1. 內容資料
# ════════════════════════════════════════════════════════════════
REGIONS = {
    '中南半島': {'name': '中南半島', 'ids': [1, 2, 3, 4, 5]},
    '馬來半島': {'name': '馬來半島與新加坡', 'ids': [6, 7]},
    '南洋群島': {'name': '南洋群島', 'ids': [8, 9, 10, 11]},
}

COUNTRIES = {
 1: dict(ja='泰國', zh='泰國', region='中南半島',
   tagline='微笑之國：從曼谷的喧囂夜市到清邁的古城寺院，再到普吉與蘇梅的碧海白沙。',
   food=['冬陰功湯','泰式炒河粉','綠咖哩雞','芒果糯米飯','船麵'],
   spots=['大皇宮','鄭王廟','清邁古城','普吉島','拜縣'],
   matsuri=['潑水節','水燈節','清邁天燈節']),
 2: dict(ja='越南', zh='越南', region='中南半島',
   tagline='從北越的下龍灣到南越的湄公河三角洲，法式殖民風情與東方韻味在此交織。',
   food=['越南河粉','越式法包','生春捲','越南咖啡','烤肉米粉'],
   spots=['下龍灣','會安古鎮','峴港','河內三十六古街','胡志明市'],
   matsuri=['越南新年','中秋節','會安燈籠節']),
 3: dict(ja='緬甸', zh='緬甸', region='中南半島',
   tagline='萬塔之城的蒲甘、茵萊湖上的單腳漁夫，佛國祕境靜待旅人。',
   food=['緬甸茶葉沙拉','莫西湯麵','緬式咖哩','檳榔葉料理'],
   spots=['蒲甘','仰光大金塔','茵萊湖','曼德勒烏本橋'],
   matsuri=['潑水節','點燈節','蒲甘熱氣球節']),
 4: dict(ja='寮國', zh='寮國', region='中南半島',
   tagline='琅勃拉邦的晨間布施、永珍河畔的夜市，東南亞最後的寧靜角落。',
   food=['寮式烤魚','竹筒糯米飯','寮國香腸','木瓜沙拉'],
   spots=['琅勃拉邦','關西瀑布','永珍塔鑾','四千美島'],
   matsuri=['潑水節','塔鑾節','水燈節']),
 5: dict(ja='柬埔寨', zh='柬埔寨', region='中南半島',
   tagline='吳哥王朝的輝煌遺跡與洞里薩湖的水上人家，高棉的微笑穿越千年。',
   food=['高棉咖哩','柬埔寨米粉','酸湯魚','油炸蜘蛛'],
   spots=['吳哥窟','巴戎寺','塔普倫寺','洞里薩湖','金邊皇宮'],
   matsuri=['柬埔寨新年','送水節','亡人節']),
 6: dict(ja='馬來西亞', zh='馬來西亞', region='馬來半島',
   tagline='吉隆坡的雙塔、檳城的壁畫街與沙巴的熱帶雨林，多元文化交融的國度。',
   food=['椰漿飯','肉骨茶','檳城叻沙','沙嗲','貓山王榴槤'],
   spots=['雙子塔','檳城喬治市','蘭卡威','馬六甲','沙巴神山'],
   matsuri=['開齋節','屠妖節','農曆新年','九皇爺誕']),
 7: dict(ja='新加坡', zh='新加坡', region='馬來半島',
   tagline='花園城市：濱海灣的璀璨天際線、世界級美食與四季如夏的熱帶風情。',
   food=['海南雞飯','辣椒螃蟹','新加坡叻沙','咖椰吐司','沙嗲'],
   spots=['濱海灣金沙','魚尾獅公園','聖淘沙','環球影城','濱海灣花園'],
   matsuri=['農曆新年','開齋節','屠妖節','中秋節']),
 8: dict(ja='印尼', zh='印尼', region='南洋群島',
   tagline='千島之國：峇里島的度假天堂、爪哇的火山與婆羅浮屠，文化多元奔放。',
   food=['印尼炒飯','沙嗲','巴東牛肉','加多加多','峇里髒鴨餐'],
   spots=['婆羅浮屠','峇里島','科莫多島','龍目島','日惹'],
   matsuri=['峇里島加隆安','開齋節','衛塞節']),
 9: dict(ja='菲律賓', zh='菲律賓', region='南洋群島',
   tagline='七千島嶼的碧海藍天：長灘島的白沙、宿霧的鯨鯊與巴拉望的秘境。',
   food=['烤乳豬','阿斗波','哈囉哈囉','比科爾辣燉'],
   spots=['長灘島','宿霧','愛妮島','巧克力山','馬尼拉王城'],
   matsuri=['聖嬰節','阿蒂阿蒂漢節','菲律賓聖誕節']),
 10: dict(ja='汶萊', zh='汶萊', region='南洋群島',
   tagline='富裕而寧靜的和平之國：黃金清真寺、水上村落與廣袤雨林。',
   food=['汶萊沙嗲','亞參魚','炸香蕉','汶萊炒飯'],
   spots=['傑米清真寺','水上村落','烏魯淡武廊國家公園','皇家王權博物館'],
   matsuri=['開齋節','先知誕辰','汶萊國慶日']),
 11: dict(ja='東帝汶', zh='東帝汶', region='南洋群島',
   tagline='世界最年輕的國家之一：阿陶羅島的潛水天堂與高山上的純樸村落。',
   food=['烤魚','玉米粥','木薯料理','葡萄牙風味燉菜'],
   spots=['阿陶羅島','帝力耶穌像','東帝汶博物館','拉美勞山'],
   matsuri=['獨立紀念日','國慶日','復活節']),
}

EN_PREF = {1:'Thailand',2:'Vietnam',3:'Myanmar',4:'Laos',5:'Cambodia',6:'Malaysia',
           7:'Singapore',8:'Indonesia',9:'Philippines',10:'Brunei',11:'Timor-Leste'}
WH_COUNTRIES = [1,2,3,4,5,6,7,8,9]

LEVELS = [
    ('未踏之旅人','🗺️',0), ('旅行初心者','🏖️',10), ('觀光旅客','🍜',30),
    ('東南亞探索者','🛕',70), ('文化踐行者','🪷',130), ('旅遊達人','🏝️',210),
    ('南洋通','🌴',310), ('國家獵人','🦜',430), ('東南亞制霸者','👑',580),
    ('傳說中的旅人','🌟',750),
]

ACH = [
 ('A01','絕景','🏔️','下龍灣世界奇觀',15,'越南「遊玩」以上','groups',[2],None,2),
 ('A02','文化','🛕','吳哥窟朝聖',20,'柬埔寨「遊玩」以上','groups',[5],None,2),
 ('A03','城市','🏛️','曼谷大皇宮',12,'泰國「遊玩」以上','groups',[1],None,2),
 ('A04','城市','🌃','新加坡天際線',12,'新加坡「遊玩」以上','groups',[7],None,2),
 ('A05','城市','🗼','吉隆坡雙塔',12,'馬來西亞「遊玩」以上','groups',[6],None,2),
 ('A06','海島','🏖️','峇里島度假',15,'印尼「遊玩」以上','groups',[8],None,2),
 ('A07','海島','🌊','長灘島白沙',14,'菲律賓「遊玩」以上','groups',[9],None,2),
 ('A08','絕景','🎈','蒲甘萬塔之城',16,'緬甸「遊玩」以上','groups',[3],None,2),
 ('A09','文化','🏯','琅勃拉邦古城',14,'寮國「遊玩」以上','groups',[4],None,2),
 ('A10','文化','🕌','汶萊水上村落',12,'汶萊「遊玩」以上','groups',[10],None,2),
 ('A11','自然','🐠','東帝汶原始海岸',13,'東帝汶「遊玩」以上','groups',[11],None,2),
 ('A12','自然','🚂','中南半島縱貫',10,'泰國、越南、柬埔寨皆「途經」以上','groups',[1,2,5],None,1),
 ('A13','文化','🏰','東南亞三大古城',18,'曼谷・琅勃拉邦・會安（泰國、寮國、越南）皆「遊玩」以上','groups',[1,4,2],None,2),
 ('A14','文化','🕉️','三大聖地巡禮',18,'仰光大金塔・吳哥窟・婆羅浮屠（緬甸、柬埔寨、印尼）皆「遊玩」以上','groups',[3,5,8],None,2),
 ('A15','文化','🏛️','世界遺產巡禮',20,'5 個世界遺產國「遊玩」以上','count','WH',5,2),
 ('A16','美食','🍜','街頭小吃之王',16,'泰國、越南、馬來西亞、新加坡皆「遊玩」以上','groups',[1,2,6,7],None,2),
 ('A17','美食','🍈','榴槤控',14,'馬來西亞、泰國、印尼皆「遊玩」以上','groups',[6,1,8],None,2),
 ('A18','美食','☕','咖啡國度',13,'越南、印尼、寮國皆「遊玩」以上','groups',[2,8,4],None,2),
 ('A19','美食','🦐','海鮮大餐',14,'泰國、越南、菲律賓、馬來西亞皆「遊玩」以上','groups',[1,2,9,6],None,2),
 ('A20','海島','⛵','跳島之旅',16,'印尼、菲律賓皆「遊玩」以上','groups',[8,9],None,2),
 ('A21','海島','🤿','潛水勝地',15,'印尼、馬來西亞、菲律賓皆「遊玩」以上','groups',[8,6,9],None,2),
 ('A22','海島','🌺','度假天堂三島',16,'普吉・峇里・蘭卡威（泰國、印尼、馬來西亞）皆「遊玩」以上','groups',[1,8,6],None,2),
 ('A23','自然','🌿','熱帶雨林',14,'馬來西亞、印尼、寮國皆「遊玩」以上','groups',[6,8,4],None,2),
 ('A24','自然','🌋','火山探險',14,'印尼、菲律賓皆「遊玩」以上','groups',[8,9],None,2),
 ('A25','自然','🏞️','世界新七大自然奇觀',16,'下龍灣・科莫多・公主港地下河（越南、印尼、菲律賓）皆「遊玩」以上','groups',[2,8,9],None,2),
 ('A26','動物','🐘','大象王國',13,'泰國、寮國、緬甸皆「遊玩」以上','groups',[1,4,3],None,2),
 ('A27','動物','🦧','人猿之島',13,'印尼、馬來西亞皆「遊玩」以上（婆羅洲）','groups',[8,6],None,2),
 ('A28','動物','🦈','與鯨鯊共游',12,'菲律賓、印尼皆「遊玩」以上','groups',[9,8],None,2),
 ('A29','文化','🏛️','殖民風情',13,'越南、緬甸、印尼皆「遊玩」以上','groups',[2,3,8],None,2),
 ('A30','城市','🌆','南洋都會巡禮',15,'泰國、新加坡、馬來西亞、越南皆「遊玩」以上','groups',[1,7,6,2],None,2),
 ('A31','文化','💦','潑水節三國',14,'泰國、緬甸、寮國皆「遊玩」以上','groups',[1,3,4],None,2),
 ('A32','美食','🥭','熱帶水果王國',12,'泰國、越南、馬來西亞、菲律賓皆「遊玩」以上','groups',[1,2,6,9],None,2),
 ('A33','影劇','🏺','古墓奇兵・吳哥',12,'柬埔寨「遊玩」以上（吳哥窟）','groups',[5],None,2),
 ('A34','影劇','🦍','金剛・骷髏島',13,'越南「遊玩」以上（峰牙／下龍灣取景）','groups',[2],None,2),
 ('A35','影劇','🎬','海灘・PP島',12,'泰國「遊玩」以上（PP島取景）','groups',[1],None,2),
 ('A36','影劇','💍','瘋狂亞洲富豪・新加坡',12,'新加坡「遊玩」以上','groups',[7],None,2),
 ('A37','影劇','🍝','美食祈禱戀愛・峇里島',12,'印尼「遊玩」以上（峇里島取景）','groups',[8],None,2),
 ('A38','城市','🌙','夜生活探索者',13,'泰國、新加坡、越南皆「遊玩」以上','groups',[1,7,2],None,2),
 ('A39','文化','🏆','中南半島五國',25,'中南半島五國（泰國、越南、緬甸、寮國、柬埔寨）皆「遊玩」以上','groups',[1,2,3,4,5],None,2),
 ('A40','海島','🌏','南洋群島大滿貫',25,'南洋群島四國（印尼、菲律賓、汶萊、東帝汶）皆「遊玩」以上','groups',[8,9,10,11],None,2),
 ('A41','文化','👑','東協大滿貫',60,'東南亞 11 國皆「遊玩」以上，且手動勾選','manual','ALL',None,2),
 ('A42','城市','🏝️','住宿大師',18,'累計 8 國「住宿」以上','count','ALL',8,3),
 ('A43','自然','🐉','湄公河之旅',10,'泰國、寮國、柬埔寨、越南皆「途經」以上（湄公河流域）','groups',[1,4,5,2],None,1),
 ('A44','城市','🚋','鐵道漫遊',12,'泰國、越南、馬來西亞皆「途經」以上（火車之旅）','groups',[1,2,6],None,1),
]
ACH_CATS = ['全部','絕景','文化','美食','自然','海島','城市','動物','影劇']

def ach_js(ach):
    lines = []
    for (aid, cat, icon, name, pts, cond, kind, extra, n, lv) in ach:
        if kind == 'groups':
            body = f"{{id:'{aid}',cat:'{cat}',icon:'{icon}',name:'{name}',pts:{pts},cond:'{cond}',kind:'groups',groups:[[{','.join(map(str, extra))}],{lv}]}}"
        elif kind == 'count':
            prefs = 'WH_PREFS' if extra == 'WH' else '[1,2,3,4,5,6,7,8,9,10,11]'
            body = f"{{id:'{aid}',cat:'{cat}',icon:'{icon}',name:'{name}',pts:{pts},cond:'{cond}',kind:'count',prefs:{prefs},level:{lv},n:{n}}}"
        else:
            body = f"{{id:'{aid}',cat:'{cat}',icon:'{icon}',name:'{name}',pts:{pts},cond:'{cond}',kind:'manual',prefs:[1,2,3,4,5,6,7,8,9,10,11],level:{lv}}}"
        lines.append('  ' + body)
    return 'const ACH = [\n' + ',\n'.join(lines) + ',\n];'

def provinces_js():
    lines = []
    for i in sorted(COUNTRIES):
        c = COUNTRIES[i]
        lines.append('  ' + str(i) + ': ' + jq(c) + ',')
    return 'const PROVINCES = {\n' + '\n'.join(lines) + '\n};'

def regions_js():
    return 'const REGIONS = ' + jq(REGIONS) + ';'

# ════════════════════════════════════════════════════════════════
# 2. i18n 英譯（新增/變更的 key）
# ════════════════════════════════════════════════════════════════
NEW_EN = {}

def add_en(d, s, v):
    assert s not in d, 'dup en key: ' + s
    d[s] = v

# 國家名／地區
for k, v in EN_PREF.items():
    add_en(NEW_EN, COUNTRIES[k]['zh'], v)
add_en(NEW_EN, '中南半島', 'Mainland Southeast Asia')
add_en(NEW_EN, '馬來半島與新加坡', 'Malay Peninsula & Singapore')
add_en(NEW_EN, '南洋群島', 'Maritime Southeast Asia')

# taglines
TAG_EN = {
 1:'Land of smiles: from Bangkok night markets and Chiang Mai temples to Phuket and Samui beaches.',
 2:'From Ha Long Bay to the Mekong Delta, French colonial charm meets oriental soul.',
 3:"Bagan's sea of pagodas and Inle Lake's leg-rowers — a hidden Buddhist land.",
 4:'Morning alms in Luang Prabang, night markets by the Mekong — Southeast Asia’s calmest corner.',
 5:'The glories of Angkor and the floating villages of Tonlé Sap — Khmer smiles across centuries.',
 6:'Twin Towers, Penang street art and Sabah rainforest — a kaleidoscope of cultures.',
 7:'A garden city: Marina Bay skyline, world-class food, eternal summer.',
 8:'Island nation: Bali escapes, Javan volcanoes and Borobudur.',
 9:'Seven thousand islands: Boracay’s white sand, Cebu’s whale sharks, Palawan’s secrets.',
 10:'A wealthy, peaceful sultanate of golden mosques, water villages and rainforest.',
 11:"One of the world's youngest nations: Atauro diving and highland villages.",
}
for k, v in TAG_EN.items():
    add_en(NEW_EN, COUNTRIES[k]['tagline'], v)

FOOD_EN = {
 1:['Tom Yum Goong','Pad Thai','Green Curry Chicken','Mango Sticky Rice','Boat Noodles'],
 2:['Pho','Bánh Mì','Fresh Spring Rolls','Vietnamese Coffee','Bún Chả'],
 3:['Tea Leaf Salad','Mohinga','Burmese Curry','Betel Leaf Delicacies'],
 4:['Laotian Grilled Fish','Sticky Rice in Bamboo','Lao Sausage','Papaya Salad'],
 5:['Khmer Curry','Num Banh Chok','Sour Fish Soup','Fried Tarantulas'],
 6:['Nasi Lemak','Bak Kut Teh','Penang Laksa','Satay','Musang King Durian'],
 7:['Hainanese Chicken Rice','Chilli Crab','Singapore Laksa','Kaya Toast','Satay'],
 8:['Nasi Goreng','Satay','Rendang','Gado-Gado','Bali Bebek Betutu'],
 9:['Lechon','Adobo','Halo-Halo','Bicol Express'],
 10:['Bruneian Satay','Asam Fish','Fried Banana','Bruneian Fried Rice'],
 11:['Grilled Fish','Corn Porridge','Cassava Dishes','Portuguese-Style Stew'],
}
SPOTS_EN = {
 1:['Grand Palace','Wat Arun','Chiang Mai Old Town','Phuket','Pai'],
 2:['Ha Long Bay','Hoi An Ancient Town','Da Nang','Hanoi Old Quarter','Ho Chi Minh City'],
 3:['Bagan','Shwedagon Pagoda','Inle Lake','U Bein Bridge'],
 4:['Luang Prabang','Kuang Si Falls','That Luang, Vientiane','Si Phan Don'],
 5:['Angkor Wat','Bayon Temple','Ta Prohm','Tonlé Sap','Royal Palace, Phnom Penh'],
 6:['Petronas Twin Towers','George Town, Penang','Langkawi','Malacca','Mount Kinabalu'],
 7:['Marina Bay Sands','Merlion Park','Sentosa','Universal Studios','Gardens by the Bay'],
 8:['Borobudur','Bali','Komodo Island','Lombok','Yogyakarta'],
 9:['Boracay','Cebu','El Nido','Chocolate Hills','Intramuros, Manila'],
 10:['Jame’Asr Hassanil Bolkiah Mosque','Water Village (Kampong Ayer)','Ulu Temburong National Park','Royal Regalia Museum'],
 11:['Atauro Island','Cristo Rei, Dili','Timor-Leste Museum','Mount Ramelau'],
}
MATSURI_EN = {
 1:['Songkran','Loy Krathong','Yi Peng (Chiang Mai)'],
 2:['Tết','Mid-Autumn Festival','Hoi An Lantern Festival'],
 3:['Thingyan (Water Festival)','Tazaungdaing Festival','Bagan Balloon Festival'],
 4:['Pi Mai (Lao New Year)','That Luang Festival','Lai Heua Fai'],
 5:['Khmer New Year','Water Festival (Bon Om Touk)','Pchum Ben'],
 6:['Hari Raya Aidilfitri','Deepavali','Chinese New Year','Nine Emperor Gods Festival'],
 7:['Chinese New Year','Hari Raya Puasa','Deepavali','Mid-Autumn Festival'],
 8:['Galungan (Bali)','Hari Raya Idul Fitri','Waisak'],
 9:['Sinulog Festival','Ati-Atihan Festival','Filipino Christmas'],
 10:['Hari Raya Aidilfitri','Mawlid (Prophet’s Birthday)','Brunei National Day'],
 11:['Independence Day','National Day','Easter'],
}
for k, lst in FOOD_EN.items():
    for zh, en in zip(COUNTRIES[k]['food'], lst):
        NEW_EN.setdefault(zh, en)
for k, lst in SPOTS_EN.items():
    for zh, en in zip(COUNTRIES[k]['spots'], lst):
        NEW_EN.setdefault(zh, en)
for k, lst in MATSURI_EN.items():
    for zh, en in zip(COUNTRIES[k]['matsuri'], lst):
        NEW_EN.setdefault(zh, en)

# 等級
LV_EN = ['Untrodden Traveler','First-Time Traveler','Sightseer','Southeast Asia Explorer',
         'Culture Practitioner','Travel Expert','SEA Connoisseur','Country Hunter',
         'Southeast Asia Conqueror','Legendary Traveler']
for (zh, _, _), en in zip(LEVELS, LV_EN):
    add_en(NEW_EN, zh, en)

# 成就
ACH_EN = {
 'A01':('Ha Long Bay Wonder','Visit Vietnam (level 2+)'),
 'A02':('Angkor Wat Pilgrimage','Visit Cambodia (level 2+)'),
 'A03':('Grand Palace, Bangkok','Visit Thailand (level 2+)'),
 'A04':('Singapore Skyline','Visit Singapore (level 2+)'),
 'A05':('Petronas Twin Towers','Visit Malaysia (level 2+)'),
 'A06':('Bali Escape','Visit Indonesia (level 2+)'),
 'A07':('Boracay White Sands','Visit Philippines (level 2+)'),
 'A08':('Bagan, City of Temples','Visit Myanmar (level 2+)'),
 'A09':('Luang Prabang Old Town','Visit Laos (level 2+)'),
 'A10':('Brunei Water Village','Visit Brunei (level 2+)'),
 'A11':('Timor-Leste Wild Coast','Visit Timor-Leste (level 2+)'),
 'A12':('Mainland Crossing','Thailand, Vietnam & Cambodia (level 1+)'),
 'A13':('Three Ancient Cities of SEA','Bangkok · Luang Prabang · Hoi An — Thailand, Laos & Vietnam (level 2+)'),
 'A14':('Three Great Sanctuaries','Shwedagon · Angkor · Borobudur — Myanmar, Cambodia & Indonesia (level 2+)'),
 'A15':('World Heritage Trail','Reach level 2+ in 5 countries with World Heritage sites'),
 'A16':('Street Food King','Thailand, Vietnam, Malaysia & Singapore (level 2+)'),
 'A17':('Durian Addict','Malaysia, Thailand & Indonesia (level 2+)'),
 'A18':('Coffee Nations','Vietnam, Indonesia & Laos (level 2+)'),
 'A19':('Seafood Feast','Thailand, Vietnam, Philippines & Malaysia (level 2+)'),
 'A20':('Island Hopping','Indonesia & Philippines (level 2+)'),
 'A21':('Diving Hotspots','Indonesia, Malaysia & Philippines (level 2+)'),
 'A22':('Three Paradise Isles','Phuket · Bali · Langkawi — Thailand, Indonesia & Malaysia (level 2+)'),
 'A23':('Tropical Rainforest','Malaysia, Indonesia & Laos (level 2+)'),
 'A24':('Volcano Adventure','Indonesia & Philippines (level 2+)'),
 'A25':('New 7 Wonders of Nature','Ha Long · Komodo · Puerto Princesa — Vietnam, Indonesia & Philippines (level 2+)'),
 'A26':('Kingdom of Elephants','Thailand, Laos & Myanmar (level 2+)'),
 'A27':('Island of the Great Apes','Indonesia & Malaysia — Borneo (level 2+)'),
 'A28':('Swimming with Whale Sharks','Philippines & Indonesia (level 2+)'),
 'A29':('Colonial Charm','Vietnam, Myanmar & Indonesia (level 2+)'),
 'A30':('Metropolis Tour of SEA','Thailand, Singapore, Malaysia & Vietnam (level 2+)'),
 'A31':('Water Festival Trio','Thailand, Myanmar & Laos (level 2+)'),
 'A32':('Tropical Fruit Kingdom','Thailand, Vietnam, Malaysia & Philippines (level 2+)'),
 'A33':('Tomb Raider · Angkor','Cambodia (level 2+) — Angkor'),
 'A34':('Kong · Skull Island','Vietnam (level 2+) — Phong Nha / Ha Long'),
 'A35':('The Beach · Phi Phi','Thailand (level 2+) — Phi Phi'),
 'A36':('Crazy Rich Asians · Singapore','Singapore (level 2+)'),
 'A37':('Eat Pray Love · Bali','Indonesia (level 2+) — Bali'),
 'A38':('Nightlife Explorer','Thailand, Singapore & Vietnam (level 2+)'),
 'A39':('Mainland Southeast Asia 5','All 5 mainland countries (level 2+)'),
 'A40':('Maritime Southeast Asia Sweep','All 4 maritime countries (level 2+)'),
 'A41':('ASEAN Grand Slam','All 11 SEA countries (level 2+), manually claimed'),
 'A42':('Stay Master','Reach level 3+ (stay) in 8 countries'),
 'A43':('Mekong Journey','Thailand, Laos, Cambodia & Vietnam (level 1+) — Mekong'),
 'A44':('Railway Wander','Thailand, Vietnam & Malaysia (level 1+) — rail trips'),
}
for row, en_pair in zip(ACH, [ACH_EN[a[0]] for a in ACH]):
    NEW_EN.setdefault(row[3], en_pair[0])
    NEW_EN.setdefault(row[5], en_pair[1])

# 新增/變更的 UI 字串
UI_EN = {
 '東南亞':'Southeast Asia',
 '地圖':'Map',
 '制霸':'Conquest',
 '東南亞制霸地圖':'Southeast Asia Conquest Map',
 '東南亞制霸戰報':'Southeast Asia Conquest Report',
 '記錄你走過的每一寸東南亞':'Track every inch of Southeast Asia you have walked',
 '看看你制霸了幾個國家？':'How many countries have you conquered?',
 '國家':'Countries',
 '國家評分':'Country Ratings',
 '本站得分':'Country score',
 '國界 © Natural Earth · Leaflet':'Borders © Natural Earth · Leaflet',
 '國家評分：':'Country rating: ',
 '點選國家，認識東南亞':'Pick a country to explore Southeast Asia',
 '在地圖上點選國家，右側面板會顯示在地美食、景點與節慶介紹。':'Click a country on the map; the side panel shows local food, sights and festivals.',
 '同一國家多次造訪':'Visiting the same country multiple times',
 '同國重複造訪':'Repeated visits to the same country',
 '每個國家只要有一筆旅程就會計分，造訪層級越高、加分越多。該地區全部國家皆造訪可獲「地區制霸」加成，全數「住宿」以上再加成；特殊成就另行加分。同一國家計分以最高造訪層級為準。':'Every country scores as soon as it has one trip; higher visit levels earn more. Conquering all countries in a region grants a bonus, with extra bonus if all are level 3+ (stay); special achievements add more. A country is scored at its highest visit level.',
 '點選國家查看介紹 · 滾輪縮放 / 拖曳移動':'Click a country to explore · scroll to zoom / drag to move',
 '搜尋國家':'Search countries',
 '點選地圖上的國家，':'Click a country on the map,',
 '查看在地美食、景點與節慶，並記錄你的旅程。':'to discover local food, sights and festivals, and record your trips.',
 '節慶活動':'Festivals',
 '清除此國':'Clear this country',
 '在這一國達成的成就':'Achievements unlocked in this country',
 '把想去的國家收進清單，或回顧你的旅程足跡。':'Save countries you want to visit, or review your travel footprints.',
 '你的東南亞制霸進度總覽，可複製文字、匯出圖片或匯出資料檔。':'An overview of your Southeast Asia conquest — copy text, export image or export data.',
 '例：我的泰越之旅、南洋島民的週末':'e.g. My Thailand–Vietnam trip, a weekend of an island dweller',
 '識別碼　例：SEA-A3K9':'Code  e.g. SEA-A3K9',
 '先點選一個國家':'Select a country first',
 '點選國家，按下「新增旅程」開始記錄足跡。':'Pick a country and press “Add trip” to start recording.',
 '還沒記錄這個國家 — 按下方的「新增旅程」開始吧。':'No trips recorded here yet — hit “Add trip” below to start.',
 '每國最多 ':'Max ',
 ' 國已評，平均 ':' rated, avg ',
 '點星星給這個國家打分':'Tap the stars to rate this country',
 '前往國家 →':'Go to country →',
 '在國家面板按下「☆ 想去」收藏，或在地圖上點選找靈感。':'Press “☆ Want to go” on a country panel, or click the map for inspiration.',
 '勾選即認領此成就（仍需達成國家條件）':'Check to claim this achievement (country conditions still apply)',
 '造訪國家':'Visited',
 '造訪國家：':'Visited countries: ',
 '造訪國家 / ':'Countries / ',
 '地區制霸 / ':'Regions / ',
 ' / ':' / ',
 ' 國':' more',
 '國':' countries',
 '太厲害了 — 11 國全部造訪過，等下一段旅程啟程吧。':'Amazing — all 11 countries visited. Time to plan the next journey!',
 '— 由「東南亞制霸地圖」純靜態版產生，資料僅存於本機瀏覽器 —':'— Generated by the Southeast Asia Conquest Map (pure static). Data stays in your local browser. —',
 '— 由「東南亞制霸地圖」純靜態版產生 —':'— Generated by the Southeast Asia Conquest Map (pure static) —',
 ' 國已評分':' rated',
 '經典首選 — 從這裡展開你的東南亞制霸':'Top picks — start your Southeast Asia conquest here',
 '純靜態的東南亞 11 國制霸記錄器：點選地圖、記錄旅程、累積分數、解鎖成就、升級等級。資料只存於本機瀏覽器。':'A pure-static Southeast Asia conquest tracker: click the map, record trips, score points, unlock achievements, level up. Data stays in your local browser.',
 '平均 ':' avg ',
 '識別碼 ':' Code ',
 '地區足跡':'Region Footprints',
 '當前制霸等級':'Current Conquest Level',
 '解鎖成就':'Achievements Unlocked',
 '查看制霸戰報':'View Conquest Report',
 '地區制霸':'Region Conquest',
 '清除':'Clear',
 '回首頁':'Back to Home',
 '編輯鎖定':'Edit Locked',
 '請先選擇國家':'Please select a country first',
 '【東南亞制霸戰報】':'[Southeast Asia Conquest Report]',
 '將刪除這個國家的全部旅程紀錄、國家評分與旅途照片，無法復原。':'All trips, rating and photos for this country will be deleted permanently.',
 '】（':' ) (',
 '）的全部旅程紀錄與成就將從本機刪除，無法復原。建議先匯出備份。':') and all its trips and achievements will be deleted from this device permanently. This cannot be undone — export a backup first.',
}
for k, v in UI_EN.items():
    NEW_EN.setdefault(k, v)

# 首頁成就預覽卡片（靜態文字）
CARD_EN = {
 '下龍灣世界奇觀':'Ha Long Bay Wonder',
 '吳哥窟朝聖':'Angkor Wat Pilgrimage',
 '南洋都會巡禮':'Metropolis Tour of SEA',
 '東協大滿貫':'ASEAN Grand Slam',
}
for k, v in CARD_EN.items():
    NEW_EN.setdefault(k, v)

# zh-Hans 顯式覆寫（T2S 之外的慣用詞）
ZH_HANS_OVERRIDE = {
 '寮國':'老挝',
 '寮式烤魚':'老挝烤鱼',
 '寮國香腸':'老挝香肠',
}

T2S_SUPPLEMENT = {
 '亞':'亚','節':'节','慶':'庆','緬':'缅','嶼':'屿','峽':'峡','檳':'槟','峴':'岘','鑾':'銮',
 '囉':'啰','髒':'脏','鴨':'鸭','豬':'猪','爾':'尔','燉':'炖','參':'参','風':'风','鄭':'郑',
 '邁':'迈','會':'会','鎮':'镇','烏':'乌','橋':'桥','關':'关','吳':'吴','倫':'伦','薩':'萨',
 '雙':'双','喬':'乔','蘭':'兰','濱':'滨','獅':'狮','聖':'圣','環':'环','羅':'罗','長':'长',
 '霧':'雾','愛':'爱','傑':'杰','魯':'鲁','權':'权','館':'馆','穌':'稣','勞':'劳','潑':'泼',
 '燈':'灯','麵':'面','捲':'卷','葉':'叶','腸':'肠','雞':'鸡','漿':'浆','陰':'阴','遺':'遗',
 '跡':'迹','樓':'楼','觀':'观','動':'动','鐵':'铁','綠':'绿','飯':'饭','車':'车','龍':'龙',
 '鱷':'鳄','龜':'龟','願':'愿','單':'单','練':'练','確':'确','認':'认','選':'选','擇':'择',
 '準':'准','層':'层','級':'级','達':'达','標':'标','檢':'检','驗':'验','彙':'汇','總':'总',
 '結':'结','論':'论','題':'题','號':'号','歷':'历','繼':'继','續':'续','雜':'杂','誌':'志',
 '儲':'储','點':'点','擊':'击','輸':'输','記':'记','錄':'录','匯':'汇','檔':'档','製':'制',
 '圖':'图','縮':'缩','數':'数','圓':'圆','狀':'态','氣':'气','溫':'温','東':'东','灣':'湾',
 '國':'国','島':'岛','縣':'县','遊':'游','評':'评','個':'个','馬':'马','來':'来','賓':'宾',
 '賽':'赛','藍':'蓝','賣':'卖','買':'买','廣':'广','場':'场','樂':'乐','區':'区','園':'园',
 '萬':'万','歲':'岁','導':'导','夢':'梦','戰':'战','報':'报','億':'亿','麼':'么','鯨':'鲸',
 '魚':'鱼','鳥':'鸟','鶯':'莺','鷹':'鹰','鶴':'鹤','鵝':'鹅','鵬':'鹏','鳩':'鸠','鴿':'鸽',
 '鵲':'鹊','鷺':'鹭','鷗':'鸥','鸚':'鹦','鳳':'凤','聽':'听','開':'开','門':'门','間':'间',
 '問':'问','聞':'闻','閒':'闲','関':'关','關':'关','齊':'齐','齋':'斋','齒':'齿','齡':'龄',
 '齲':'龋','齣':'出','齧':'啮','龕':'龛','龜':'龟','電':'电','雲':'云','雷':'雷','霜':'霜',
 '露':'露','霸':'霸','靈':'灵','鬱':'郁','麥':'麦','麪':'面','麵':'面','麼':'么','鹹':'咸',
 '麗':'丽','鹵':'卤','鹼':'碱','鹽':'盐','鹿':'鹿','塵':'尘','塵':'尘','墊':'垫','壘':'垒',
 '壤':'壤','壓':'压','壞':'坏','壩':'坝','牆':'墙','壯':'壮','壺':'壶','壼':'壶','壽':'寿',
 '夥':'伙','夢':'梦','奪':'夺','奮':'奋','奧':'奥','獎':'奖','娑':'娑','婚':'婚','媽':'妈',
 '嫻':'娴','嬌':'娇','孃':'娘','寧':'宁','寬':'宽','審':'审','寫':'写','寶':'宝','將':'将',
 '專':'专','尋':'寻','對':'对','導':'导','小':'小','塵':'尘','層':'层','屬':'属','巒':'峦',
 '嶺':'岭','嶽':'岳','巖':'岩','巹':'卺','幣':'币','幫':'帮','幹':'干','廣':'广','廢':'废',
 '廟':'庙','廠':'厂','廳':'厅','彈':'弹','強':'强','歸':'归','當':'当','彙':'汇','徹':'彻',
 '徵':'征','德':'德','徹':'彻','從':'从','復':'复','慣':'惯','慮':'虑','慶':'庆','憂':'忧',
 '憶':'忆','憐':'怜','憫':'悯','憑':'凭','戲':'戏','戶':'户','房':'房','所':'所','扇':'扇',
 '才':'才','撲':'扑','撐':'撑','撿':'捡','據':'据','擴':'扩','擾':'扰','擱':'搁','擺':'摆',
 '攏':'拢','攜':'携','攝':'摄','支':'支','收':'收','改':'改','攻':'攻','放':'放','政':'政',
 '故':'故','效':'效','敵':'敌','數':'数','整':'整','斃':'毙','斷':'断','於':'于','時':'时',
 '晉':'晋','曉':'晓','暫':'暂','曆':'历','書':'书','會':'会','月':'月','有':'有','服':'服',
 '朗':'朗','望':'望','朝':'朝','期':'期','木':'木','未':'未','本':'本','朱':'朱','朴':'朴',
 '村':'村','東':'东','松':'松','板':'板','析':'析','果':'果','枝':'枝','林':'林','杯':'杯',
 '東':'东','析':'析','果':'果','枝':'枝','林':'林','杯':'杯','析':'析','果':'果','枝':'枝',
 '並':'并','備':'备','僅':'仅','別':'别','劇':'剧','勝':'胜','囂':'嚣','宮':'宫','幾':'几','態':'态','戀':'恋','湯':'汤','滿':'满','漢':'汉','潛':'潜','瀏':'浏','無':'无','熱':'热','獨':'独','獲':'获','畫':'画','碼':'码','祕':'秘','禮':'礼','稱':'称','積':'积','紀':'纪','純':'纯','統':'统','織':'织','萊':'莱','複':'复','覽':'览','該':'该','識':'识','輯':'辑','轉':'转','這':'这','還':'还','項':'项','啟':'启','舊':'旧','於':'于','區':'区','與':'与','為':'为','稱':'称','報':'报','戰':'战','層':'层','級':'级','數':'数','據':'据','經':'经','濟':'济','點':'点','觀':'观','園':'园','島':'岛','節':'节','慶':'庆','風':'风','車':'车','門':'门','問':'问','開':'开','間':'间','會':'会','過':'过','對':'对','應':'应','當':'当','樣':'样','來':'来','裡':'里','兩':'两','邊':'边','這':'这','後':'后','時':'时','書':'书','話':'话','說':'说','記':'记','許':'许','評':'评','設':'设','試':'试','調':'调','請':'请','讓':'让','認':'认','誤':'误','證':'证','錄':'录','驗':'验','長':'长','門':'门','問':'问','開':'开','間':'间','雲':'云','電':'电','頭':'头','題':'题','額':'额','項':'项','顯':'显','風':'风','飛':'飞','飯':'饭','飲':'饮','館':'馆','馬':'马','魚':'鱼','鳥':'鸟','龍':'龙','龜':'龟','點':'点','齊':'齐','齒':'齿','麗':'丽','麥':'麦','黃':'黄','鴻':'鸿','鳳':'凤','鬆':'松','髮':'发','驚':'惊','駕':'驾','體':'体','驗':'验','類':'类','願':'愿','頻':'频','領':'领','順':'顺','預':'预','頓':'顿','頑':'顽','頂':'顶','響':'响','露':'露','霧':'雾','難':'难','離':'离','雞':'鸡','雜':'杂','雖':'虽','雙':'双','隨':'随','際':'际','階':'阶','陽':'阳','隊':'队','闡':'阐','關':'关','閱':'阅','閒':'闲','閃':'闪','鐵':'铁','鑑':'鉴','釋':'释','鄰':'邻','鄧':'邓','適':'适','遺':'遗','遷':'迁','達':'达','辦':'办','輪':'轮','輩':'辈','輔':'辅','載':'载','軟':'软','軒':'轩','贏':'赢','購':'购','贈':'赠','賺':'赚','贍':'赡','賴':'赖','質':'质','賜':'赐','賣':'卖','賢':'贤','賞':'赏','賓':'宾','賀':'贺','費':'费','買':'买','貴':'贵','財':'财','貢':'贡','負':'负','譜':'谱','談':'谈','諒':'谅','課':'课','詳':'详','詞':'词','詢':'询','詩':'诗','訓':'训','計':'计','視':'视','補':'补','術':'术','衛':'卫','裝':'装','衝':'冲','艱':'艰','臨':'临','臉':'脸','肅':'肃','耀':'耀','繞':'绕','績':'绩','緩':'缓','紅':'红','築':'筑','競':'竞','穩':'稳','盤':'盘','監':'监','盃':'杯','異':'异','燦':'灿','營':'营','燒':'烧','燈':'灯','熱':'热','潛':'潜','漢':'汉','溝':'沟','氣':'气','權':'权','檢':'检','樂':'乐','棟':'栋','望':'望','斷':'断','數':'数','徵':'征','彈':'弹','廠':'厂','廢':'废','幣':'币','屆':'届','將':'将','尋':'寻','婦':'妇','奧':'奥','壯':'壮','夥':'伙','夢':'梦','塗':'涂','聖':'圣','場':'场','學':'学','寧':'宁','媒':'媒','博':'博','卓':'卓','協':'协','醫':'医','動':'动','勵':'励','勁':'劲','劍':'剑','創':'创','傘':'伞','倉':'仓','蘭':'兰','爭':'争','隱':'隐','盡':'尽','誌':'志','況':'况','傳':'传','聲':'声','釋':'释','祕':'秘','巒':'峦','牆':'墙','環':'环','極':'极','濃':'浓','鮮':'鲜','業':'业','專':'专','實':'实','寶':'宝','貝':'贝','亞':'亚','準':'准','歸':'归','歲':'岁','兩':'两','邊':'边','麼':'么','嗎':'吗','現':'现','處':'处','餘':'余','郵':'邮','體':'体','觸':'触','覺':'觉','歡':'欢','靈':'灵','調':'调','設':'设','試':'试','誤':'误','說':'说','語':'语','話':'话','讀':'读','寫':'写','錯':'错','聽':'听','頁':'页','雙':'双','單':'单','離':'离','線':'线','繫':'系','聯':'联','絡':'络','網':'网','級':'级','層':'层','報':'报','戰':'战','題':'题','標':'标','號':'号','稱':'称','態':'态','樣':'样','輸':'输','擇':'择','選':'选','導':'导','匯':'汇','檔':'档','當':'当','應':'应','對':'对','過':'过','續':'续','繼':'继','認':'认','確':'确','雲':'云','儲':'储','務':'务','覽':'览','瀏':'浏','資':'资','無':'无','畫':'画','機':'机','飛':'飞','軍':'军','車':'车','見':'见','風':'风','豐':'丰','億':'亿','們':'们','門':'门','問':'问','開':'开','間':'间','長':'长','評':'评','碼':'码','別':'别','識':'识','製':'制','複':'复','還':'还','後':'后','這':'这','會':'会','鑾':'銮','峽':'峡','嶼':'屿','檳':'槟','峴':'岘','齊':'齐','滿':'满','據':'据','歷':'历','遺':'遗','遊':'游','構':'构','邁':'迈','緬':'缅','萊':'莱','囂':'嚣','鄭':'郑','廟':'庙','宮':'宫','灣':'湾','龍':'龙','潑':'泼','燈':'灯','麵':'面','湯':'汤','陰':'阴','綠':'绿','馬':'马','慶':'庆','節':'节','與':'与','東':'东','館':'馆','溫':'温','島':'岛','園':'园','觀':'观','點':'点','縣':'县','國':'国',
}

# 防呆：從原文 i18n 抽取 en 字典
def scan_js_pairs(sec):
    """掃描 JS 物件中的 "key": "value" 對，支援 \" 轉義。"""
    out = {}
    i = 0
    n = len(sec)
    while i < n:
        if sec[i] == '"':
            # key
            j = i + 1
            buf = []
            while j < n:
                c = sec[j]
                if c == '\\':
                    buf.append(sec[j:j+2]); j += 2; continue
                if c == '"':
                    break
                buf.append(c); j += 1
            key = ''.join(buf)
            j += 1
            while j < n and sec[j] not in '":': j += 1
            if j >= n or sec[j] != ':': i = j + 1; continue
            j += 1
            while j < n and sec[j] in ' \t\n': j += 1
            if j >= n or sec[j] != '"': i = j + 1; continue
            j += 1
            buf = []
            while j < n:
                c = sec[j]
                if c == '\\':
                    buf.append(sec[j:j+2]); j += 2; continue
                if c == '"':
                    break
                buf.append(c); j += 1
            val = ''.join(buf)
            out[key] = val
            i = j + 1
        else:
            i += 1
    return out

def extract_i18n_en(html):
    i = html.find('const I18N = {')
    if i == -1: fail('no I18N')
    j = html.find("'en'", i)
    if j == -1: fail('no en section')
    k = html.find('};', j)
    return scan_js_pairs(html[j:k])

def parse_t2s(html):
    i = html.find('const T2S = {')
    j = html.find('};', i)
    sec = html[i:j]
    out = {}
    for m in re.finditer(r'"([^"]*)"\s*:\s*"([^"]*)"', sec):
        out[m.group(1)] = m.group(2)
    return out

ORIG_EN = extract_i18n_en(orig)
T2S = parse_t2s(orig)
for k, v in T2S_SUPPLEMENT.items():
    T2S.setdefault(k, v)

def to_simplified(s):
    return ''.join(T2S.get(ch, ch) for ch in s)

# ════════════════════════════════════════════════════════════════
# 3. 主流程：轉換
# ════════════════════════════════════════════════════════════════
out = orig

# ── 3.1 GeoJSON script1 ──
geojson = json.dumps(json.load(open('sea.geojson', encoding='utf-8')), ensure_ascii=False, separators=(',', ':'))
s1 = out.find('<script>')
e1 = out.find('</script>', s1) + len('</script>')
out = out[:s1] + '<script>window.SEA_GEOJSON = ' + geojson + ';</script>' + out[e1:]

# ── 3.2 I18N 佔位（內容最後再填）──
i1 = out.find('const I18N = {')
i2 = out.find('function t(')
out = out[:i1] + '__I18N_DICT__\n' + out[i2:]

# ── 3.3 資料區塊 ──
start, end = brace_block(out, 'const REGIONS = {')
out = out[:start] + regions_js() + out[end:]

start, end = brace_block(out, 'const PROVINCES = {')
out = out[:start] + provinces_js() + out[end:]

out = sub(out, 'const WH_PREFS = [1,2,3,5,9,10,13,15,16,19,21,22,23,24,26,27,28,29,30,32,34,35,40,42,46,47];',
          'const WH_PREFS = ' + jq(WH_COUNTRIES) + ';')
out = sub(out, "const LANG_KEY = 'jp_lang';", "const LANG_KEY = 'sea_lang';")
out = sub(out, "const LANGS = ['zh-Hant','zh-Hans','ja','en'];", "const LANGS = ['zh-Hant','zh-Hans','en'];")

# T2S supplement
start = out.find('const T2S = {')
end = out.find('};', start)
supp = ',\n'.join(f'"{k}":"{v}"' for k, v in T2S_SUPPLEMENT.items() if k not in parse_t2s(orig))
out = out[:end] + ',' + supp + '\n' + out[end:]

# LEVELS
start = out.find('const LEVELS = [')
end = out.find('];', start) + 2
lvs = 'const LEVELS = [\n' + ',\n'.join(f"  {{name:'{n}',icon:'{ic}',pts:{p}}}" for n, ic, p in LEVELS) + '\n];'
out = out[:start] + lvs + out[end:]

# TYPE_*
start = out.find('const TYPE_NAME')
end = out.find('const ACH = [')
types = (
 "const TYPE_NAME = {1:'途經',2:'遊玩',3:'住宿',4:'長居'};\n"
 "const TYPE_PTS = {1:2,2:5,3:10,4:20};\n"
 "const TYPE_COLOR = {1:'#94A3A0',2:'#5BAFC2',3:'#2E8CA8',4:'#0E7490'};\n"
)
out = out[:start] + types + out[end:]

# FILLS（script3 內定義）
out = sub(out, "const FILLS = {0:'#F0E7DF', 1:'#F3CDBF', 2:'#E89376', 3:'#D2603F', 4:'#B02A1A'}",
          "const FILLS = {0:'#E8E2D8',1:'#BBDDE5',2:'#7FC2D2',3:'#3E9CB4',4:'#0E7490'}")

# ACH
start = out.find('const ACH = [')
end = out.find('const ACH_CATS')
out = out[:start] + ach_js(ACH) + '\n' + out[end:]

# ACH_CATS
start = out.find('const ACH_CATS')
end = out.find('];', start) + 2
out = out[:start] + 'const ACH_CATS = ' + jq(ACH_CATS) + ';' + out[end:]

# 計數常數（加在 computeScore 前）
out = sub(out, 'function computeScore(data){',
          'const N_CTRY = Object.keys(PROVINCES).length, N_REG = Object.keys(REGIONS).length;\n'
          'function computeScore(data){')

# PREF_IMG → 11 國代表圖（與日版 assets/prefs 同構）
start, end = brace_block(out, 'const PREF_IMG = {')
SEA_IMG = "{1:'assets/countries/01_thailand.jpg', 2:'assets/countries/02_vietnam.jpg', 3:'assets/countries/03_myanmar.jpg', 4:'assets/countries/04_laos.jpg', 5:'assets/countries/05_cambodia.jpg', 6:'assets/countries/06_malaysia.jpg', 7:'assets/countries/07_singapore.jpg', 8:'assets/countries/08_indonesia.jpg', 9:'assets/countries/09_philippines.jpg', 10:'assets/countries/10_brunei.jpg', 11:'assets/countries/11_timor_leste.jpg'}"
out = out[:start] + 'const PREF_IMG = ' + SEA_IMG + ';' + out[end:]

# EN_PREF → 11 國英譯（prefName/搜索在 EN 模式使用）
start, end = brace_block(out, 'const EN_PREF = {')
SEA_ENP = "{1:'Thailand',2:'Vietnam',3:'Myanmar',4:'Laos',5:'Cambodia',6:'Malaysia',7:'Singapore',8:'Indonesia',9:'Philippines',10:'Brunei',11:'Timor-Leste'}"
out = out[:start] + 'const EN_PREF = ' + SEA_ENP + ';' + out[end:]

# ── 3.4 JS 邏輯替換 ──
out = sub_all(out, 'window.JAPAN_GEOJSON', 'window.SEA_GEOJSON')
out = sub(out, 'for(let id=1; id<=47; id++){', 'for(const id in PROVINCES){')
out = sub(out, 'for(let id = 1; id <= 47; id++){', 'for(const id in PROVINCES){')
out = sub(out, "const vars = [zh, ja, rg, zh + '都', zh + '府', zh + '縣'];",
          "const en = (EN_PREF[id] || '').toLowerCase();\n    const vars = [zh, ja, rg, en];")
out = sub(out, 'LABEL_MAJOR = new Set([1,2,3,4,5,6,7,13,15,16,20,22,23,27,28,30,31,34,36,37,40,42,43,44,46,47])',
          'LABEL_MAJOR = new Set([1,2,3,4,5,6,8,9])')
out = sub(out, 'minZoom:4.2,', 'minZoom:3,')
out = sub(out, "c = 'JPN-';", "c = 'SEA-';")
out = sub(out, "const LS_REG = 'japanMap.registry';", "const LS_REG = 'seaMap.registry';")
out = sub(out, "const LS_ACTIVE = 'japanMap.active';", "const LS_ACTIVE = 'seaMap.active';")
out = sub(out, "const LS_DATA = 'japanMap.data.';", "const LS_DATA = 'seaMap.data.';")
out = sub(out, "const LS_FRIENDS = 'japanMap.friends';", "const LS_FRIENDS = 'seaMap.friends';")
out = sub(out, "pNameJa').textContent = LANG === 'ja' ? (EN_PREF[id] || '') : p.ja;",
"pNameJa').textContent = LANG === 'en' ? p.zh : (EN_PREF[id] || '');")
out = sub(out, 'html[lang="ja"] .hero h1{gap:.05em}', '')
out = sub(out, "const GB = { minLon: 123.6, maxLon: 146.2, minLat: 24.0, maxLat: 45.7 };",
          "const GB = { minLon: 92.0, maxLon: 141.2, minLat: -11.2, maxLat: 28.8 };")
out = sub(out, "map.attributionControl.addAttribution('境界 © <a href=\"https://github.com/dataofjapan/land\" target=\"_blank\" rel=\"noopener\">dataofjapan</a> · Leaflet');",
          "map.attributionControl.addAttribution(t('國界 © Natural Earth · Leaflet'));")
out = sub(out, 'const hot = [26, 13, 27, 1, 40, 14, 28, 23];', 'const hot = [1, 2, 6, 8, 5, 7, 3, 9];')
out = sub(out, "t('經典首選 — 從這裡展開你的日本制霸')", "t('經典首選 — 從這裡展開你的東南亞制霸')")
out = sub(out, "missing.length + t(' 縣')", "missing.length + t(' 國')")
out = sub(out, "t('前往縣市 →')", "t('前往國家 →')")
out = sub(out, "t('太厲害了 — 47 縣全部造訪過，等下一段旅程啟程吧。')",
          "t('太厲害了 — 11 國全部造訪過，等下一段旅程啟程吧。')")
out = sub(out, "t('造訪縣市：') + s.visited + t(' / 47') + '　' + t('地區制霸：') + s.regionsDone + t(' / 8')",
          "t('造訪國家：') + s.visited + t(' / ') + N_CTRY + '　' + t('地區制霸：') + s.regionsDone + t(' / ') + N_REG")
out = sub(out, "t('縣幣評分：') + ratedIds.length + t(' 縣已評，平均 ')", "t('國家評分：') + ratedIds.length + t(' 國已評，平均 ')")
out = sub(out, "t('造訪縣市 / 47')", "t('造訪國家 / ') + N_CTRY")
out = sub(out, "t('地區制霸 / 8')", "t('地區制霸 / ') + N_REG")
out = sub(out, "t('— 由「日本制霸地圖」純靜態版產生，資料僅存於本機瀏覽器 —')",
          "t('— 由「東南亞制霸地圖」純靜態版產生，資料僅存於本機瀏覽器 —')")
out = sub(out, "t('— 由「日本制霸地圖」純靜態版產生 —')",
          "t('— 由「東南亞制霸地圖」純靜態版產生 —')")
out = sub(out, "t(' 縣已評分')", "t(' 國已評分')")
out = sub(out, "t('每縣最多 ')", "t('每國最多 ')")
out = sub_all(out, "t('先點選一個縣市')", "t('先點選一個國家')")
out = sub(out, "t('還沒記錄這座縣市 — 按下方的「新增旅程」開始吧。')",
          "t('還沒記錄這個國家 — 按下方的「新增旅程」開始吧。')")
out = sub_all(out, "t('點星星給這座縣市打分')", "t('點星星給這個國家打分')")
out = sub(out, "t('在縣市面板按下「☆ 想去」收藏，或在地圖上點選找靈感。')",
          "t('在國家面板按下「☆ 想去」收藏，或在地圖上點選找靈感。')")
# 修復：openRecordDialog 成就勾選區 const t 遮蔽翻譯函數 t（日版原生 bug）
out = sub(out, "const t = document.createElement('span');",
          "const tEl = document.createElement('span');")
out = sub(out, "t.className = 'ac-t';", "tEl.className = 'ac-t';")
out = sub(out, "label.appendChild(t);", "label.appendChild(tEl);")
out = sub(out, "t('勾選即認領此成就（仍需達成縣市條件）')",
          "t('勾選即認領此成就（仍需達成國家條件）')")
out = sub(out, "frHead('visited',t('縣市')", "frHead('visited',t('國家')")
out = sub(out, "r.visited + '/47</td>'", "r.visited + '/' + N_CTRY + '</td>'")
out = sub(out, "r.regionsDone + '/8</td>'", "r.regionsDone + '/' + N_REG + '</td>'")
out = sub(out, "[s.visited, t('造訪縣市'), '/ 47']", "[s.visited, t('造訪國家'), '/ ' + N_CTRY]")
out = sub(out, "[s.regionsDone, t('地區制霸'), '/ 8']", "[s.regionsDone, t('地區制霸'), '/ ' + N_REG]")
out = sub(out, "badgeT = t('已造訪') + '  ' + visitedIds.length + t(' / 47') + t('縣');",
          "badgeT = t('已造訪') + '  ' + visitedIds.length + t(' / ') + N_CTRY + t('國');")
out = sub(out, "const VERM = '#9E2418', VERM_DEEP = '#7A1A10', VERM_SOFT = '#C44A3A';",
          "const VERM = '#0E7490', VERM_DEEP = '#0A5C74', VERM_SOFT = '#2E8CA8';")
out = sub_all(out, 'rgba(158,36,24,.4)', 'rgba(14,116,144,.4)')
out = sub_all(out, "'#EAE0D0'", "'#EAE2D2'")
out = sub_all(out, "'#D2C4AE'", "'#D9CBB6'")
out = sub_all(out, "'#E0D4C0'", "'#E8E2D8'")
out = sub(out, "center(t('日本制霸戰報'), W/2, 168, '900 58px ' + serif, VERM);",
          "center(t('東南亞制霸戰報'), W/2, 168, '900 58px ' + serif, VERM);")
out = sub(out, "'123°E – 146°E  /  24°N – 46°N'", "'92°E – 141°E  /  11°S – 29°N'")
# prefName ja 分支
out = sub(out, "function prefName(id){\n  const p = PROVINCES[id];\n  if(LANG === 'ja') return p.ja;\n  if(LANG === 'en') return EN_PREF[id] || p.zh;\n  return t(p.zh);\n}",
          "function prefName(id){\n  const p = PROVINCES[id];\n  if(LANG === 'en') return EN_PREF[id] || p.zh;\n  return t(p.zh);\n}")

# ── 3.5 CSS 替換 ──
new_root = '''\
:root{
  /* MDUI 3 色板覆寫（南洋青主色 / 陶土次色 / 金沙三色 / 沙紙表面） */
  --mdui-color-primary:14 116 144;
  --mdui-color-on-primary:255 255 255;
  --mdui-color-primary-container:190 233 244;
  --mdui-color-on-primary-container:0 42 54;
  --mdui-color-inverse-primary:145 214 232;
  --mdui-color-secondary:140 84 58;
  --mdui-color-on-secondary:255 255 255;
  --mdui-color-secondary-container:250 218 202;
  --mdui-color-on-secondary-container:57 21 10;
  --mdui-color-tertiary:146 106 11;
  --mdui-color-on-tertiary:255 255 255;
  --mdui-color-tertiary-container:255 224 138;
  --mdui-color-on-tertiary-container:42 31 0;
  --mdui-color-surface:251 247 241;
  --mdui-color-on-surface:33 26 23;
  --mdui-color-surface-dim:222 212 199;
  --mdui-color-surface-bright:255 250 245;
  --mdui-color-surface-container-lowest:255 255 255;
  --mdui-color-surface-container-low:246 238 231;
  --mdui-color-surface-container:240 230 222;
  --mdui-color-surface-container-high:234 223 214;
  --mdui-color-surface-container-highest:228 217 207;
  --mdui-color-on-surface-variant:82 68 62;
  --mdui-color-outline:133 116 108;
  --mdui-color-outline-variant:212 196 188;
  --mdui-color-background:251 247 241;
  --mdui-color-on-background:33 26 23;
  --mdui-color-error:186 26 26;
  --mdui-color-on-error:255 255 255;
  --mdui-color-error-container:255 218 214;
  --mdui-color-on-error-container:65 0 2;
  --mdui-color-inverse-surface:79 90 112;
  --mdui-color-inverse-on-surface:255 255 255;
  --mdui-color-surface-variant:228 217 207;

  /* 站點自有 token */
  --paper:#FBF7F1;
  --paper-deep:#F0E8DE;
  --ink:#211A17;
  --ink-soft:#52443E;
  --ink-faint:#85746C;
  --vermilion:#0E7490;
  --vermilion-deep:#0A5C74;
  --gold:#C9A227;
  --gold-soft:#FFE08A;
  --indigo:#8C543A;
  --line:#E6D9C8;
'''
i_css_s = out.find(':root{')
i_css_e = out.find('*{box-sizing')
out = out[:i_css_s] + new_root + '\n' + out[i_css_e:]

# 全站硬編碼紅 → 青
out = sub_all(out, 'rgba(176,42,26,.07)', 'rgba(14,116,144,.07)')
out = sub_all(out, 'rgba(176,42,26,.08)', 'rgba(14,116,144,.08)')
out = sub_all(out, 'rgba(176,42,26,.12)', 'rgba(14,116,144,.12)')
out = sub_all(out, 'rgba(176,42,26,.35)', 'rgba(14,116,144,.35)')
out = sub_all(out, 'rgba(176,42,26,.6)', 'rgba(14,116,144,.6)')
out = sub_all(out, '#FFF1ED', '#EAF6F9')
out = sub_all(out, '#FFE7DF', '#D9EEF4')
out = sub_all(out, '#F0C9C0', '#BFDDE6')
out = sub_all(out, '#e0c7bb', '#BCD8E0')
out = sub_all(out, 'rgba(79,90,112,.12)', 'rgba(140,84,58,.14)')
out = sub_all(out, 'color:#4F5A70', 'color:#8C543A')
out = sub_all(out, '#B02A1A', '#0E7490')
out = sub_all(out, "fill='%23B02A1A'", "fill='%230E7490'")
# 圖例色（HTML 內聯）
out = sub_all(out, '#F0E7DF', '#E8E2D8')
out = sub_all(out, '#F3CDBF', '#BBDDE5')
out = sub_all(out, '#E89376', '#7FC2D2')
out = sub_all(out, '#D2603F', '#3E9CB4')

# 旗標 → 南洋三色
brand_flag = '''.brand-flag{
  width:30px;height:21px;border-radius:4px;background:#fff;
  box-shadow:inset 0 0 0 1px rgba(33,26,23,.14);
  position:relative;flex:none;
}
.brand-flag::after{
  content:'';position:absolute;left:50%;top:50%;
  width:11px;height:11px;border-radius:50%;
  background:var(--vermilion);transform:translate(-50%,-50%);
}'''
brand_flag_new = '''.brand-flag{
  width:30px;height:21px;border-radius:4px;
  background:linear-gradient(180deg,#0E7490 0 34%,#F2C879 34% 66%,#C0503C 66% 100%);
  box-shadow:inset 0 0 0 1px rgba(33,26,23,.14);
  position:relative;flex:none;
}'''
out = sub(out, brand_flag, brand_flag_new)

hero_flag = '''.hero-flag{
  width:84px;height:59px;border-radius:12px;background:#fff;
  box-shadow:var(--shadow-2),inset 0 0 0 1px rgba(33,26,23,.10);
  margin:0 auto 22px;position:relative;
}
.hero-flag::after{
  content:'';position:absolute;left:50%;top:50%;
  width:31px;height:31px;border-radius:50%;
  background:var(--vermilion);transform:translate(-50%,-50%);
}'''
hero_flag_new = '''.hero-flag{
  width:84px;height:59px;border-radius:12px;
  background:linear-gradient(180deg,#0E7490 0 34%,#F2C879 34% 66%,#C0503C 66% 100%);
  box-shadow:var(--shadow-2),inset 0 0 0 1px rgba(33,26,23,.10);
  margin:0 auto 22px;position:relative;
}'''
out = sub(out, hero_flag, hero_flag_new)

# ── 3.6 HTML 靜態文字 ──
out = sub(out, '<title>日本制霸地圖 · 記錄你走過的每一寸日本</title>',
          '<title>東南亞制霸地圖 · 記錄你走過的每一寸東南亞</title>')
out = sub(out, '<meta name="description" content="純靜態的日本 47 都道府縣制霸記錄器：點選地圖、記錄旅程、累積分數、解鎖成就、升級等級。資料只存於本機瀏覽器。">',
          '<meta name="description" content="純靜態的東南亞 11 國制霸記錄器：點選地圖、記錄旅程、累積分數、解鎖成就、升級等級。資料只存於本機瀏覽器。">')
out = sub(out, '<span class="brand-name">日本<b>制霸</b>地圖</span>',
          '<span class="brand-name">東南亞<b>制霸</b>地圖</span>')
out = sub(out, '<h1>日本<span class="jp">制霸</span>地圖</h1>', '<h1>東南亞<span class="jp">制霸</span>地圖</h1>')
out = sub(out, '記錄你走過的每一寸日本，看看你制霸了幾個縣？',
          '記錄你走過的每一寸東南亞，看看你制霸了幾個國家？')
out = sub(out, '47</div><div class="lbl">縣市</div>', '11</div><div class="lbl">國家</div>')
out = sub(out, '點選縣市，認識日本', '點選國家，認識東南亞')
out = sub(out, '在地圖上點選都道府縣，右側面板會顯示在地美食、景點與祭典介紹。',
          '在地圖上點選國家，右側面板會顯示在地美食、景點與節慶介紹。')
out = sub(out, '並勾選在該縣達成的特殊成就。', '並勾選在該國達成的特殊成就。')
out = sub(out, '同縣重複造訪', '同國重複造訪')
out = sub(out, '同一縣市多次造訪', '同一國家多次造訪')
out = sub(out, '每個縣市只要有一筆旅程就會計分，造訪層級越高、加分越多。該地區全部縣市皆造訪可獲「地區制霸」加成，全數「住宿」以上再加成；特殊成就另行加分。同一縣市計分以最高造訪層級為準。',
          '每個國家只要有一筆旅程就會計分，造訪層級越高、加分越多。該地區全部國家皆造訪可獲「地區制霸」加成，全數「住宿」以上再加成；特殊成就另行加分。同一國家計分以最高造訪層級為準。')
# 首頁成就卡片
out = sub(out, '<div class="ach-card"><div class="ic">⛩️</div><div class="ac-body"><div class="ac-name">日本三景</div><div class="ac-pts">+20 分 <span>· 松島・天橋立・宮島</span></div></div></div>',
          '<div class="ach-card"><div class="ic">🏝️</div><div class="ac-body"><div class="ac-name">下龍灣世界奇觀</div><div class="ac-pts">+15 分 <span>· 越南</span></div></div></div>')
out = sub(out, '<div class="ach-card"><div class="ic">🎆</div><div class="ac-body"><div class="ac-name">日本三大祭</div><div class="ac-pts">+25 分 <span>· 祇園・天神・神田</span></div></div></div>',
          '<div class="ach-card"><div class="ic">🛕</div><div class="ac-body"><div class="ac-name">吳哥窟朝聖</div><div class="ac-pts">+20 分 <span>· 柬埔寨</span></div></div></div>')
out = sub(out, '<div class="ach-card"><div class="ic">🏯</div><div class="ac-body"><div class="ac-name">十二天守</div><div class="ac-pts">+30 分 <span>· 現存天守 12 座全制霸</span></div></div></div>',
          '<div class="ach-card"><div class="ic">🏙️</div><div class="ac-body"><div class="ac-name">南洋都會巡禮</div><div class="ac-pts">+15 分 <span>· 曼谷・新加坡・吉隆坡</span></div></div></div>')
out = sub(out, '<div class="ach-card"><div class="ic">🙏</div><div class="ac-body"><div class="ac-name">四國遍路</div><div class="ac-pts">+45 分 <span>· 四國四縣（手動勾選）</span></div></div></div>',
          '<div class="ach-card"><div class="ic">👑</div><div class="ac-body"><div class="ac-name">東協大滿貫</div><div class="ac-pts">+60 分 <span>· 11 國全制霸（手動勾選）</span></div></div></div>')
out = sub_all(out, '縣幣評分', '國家評分')
out = sub(out, '為每個縣市加上你的主觀評價', '為每個國家加上你的主觀評價')
out = sub(out, '日本制霸地圖 · 純靜態版 — 所有資料僅存於本機瀏覽器（localStorage），不提供雲端儲存服務。',
          '東南亞制霸地圖 · 純靜態版 — 所有資料僅存於本機瀏覽器（localStorage），不提供雲端儲存服務。')
out = sub(out, '都道府縣邊界 © dataofjapan（GeoJSON）· 地圖渲染 Leaflet · 介面 MDUI 2',
          '國家邊界 © Natural Earth（公有領域 GeoJSON）· 地圖渲染 Leaflet · 介面 MDUI 2')
out = sub(out, '點選縣市查看介紹 · 滾輪縮放 / 拖曳移動', '點選國家查看介紹 · 滾輪縮放 / 拖曳移動')
out = sub_all(out, '搜尋縣市', '搜尋國家')
out = sub_all(out, '（中文／日文／地區）', '（中文／英文／地區）')
out = sub_all(out, '點選縣市', '點選國家')
out = sub(out, '點選地圖上的都道府縣，', '點選地圖上的國家，')
out = sub(out, '查看在地美食、景點與祭典，並記錄你的旅程。', '查看在地美食、景點與節慶，並記錄你的旅程。')
out = sub_all(out, '祭典行事', '節慶活動')
out = sub_all(out, '清除此縣', '清除此國')
out = sub(out, '例：我的關西之旅、大阪社畜的週末', '例：我的泰越之旅、南洋島民的週末')
out = sub(out, '識別碼　例：JPN-A3K9', '識別碼　例：SEA-A3K9')
out = sub(out, '在這一縣達成的成就', '在這一國達成的成就')
out = sub(out, '把想去的縣市收進清單，或回顧你的旅程足跡。', '把想去的國家收進清單，或回顧你的旅程足跡。')
out = sub(out, '你的日本制霸進度總覽，可複製文字、匯出圖片或匯出資料檔。',
          '你的東南亞制霸進度總覽，可複製文字、匯出圖片或匯出資料檔。')
out = sub(out, '<button data-lang="ja" title="日本語">日</button>', '')
out = sub(out, "t('【日本制霸戰報】')", "t('【東南亞制霸戰報】')")
out = sub_all(out, "t('請先選擇縣市')", "t('請先選擇國家')")
out = sub(out, "t('將刪除這座縣市的全部旅程紀錄、國家評分與旅途照片，無法復原。')",
          "t('將刪除這個國家的全部旅程紀錄、國家評分與旅途照片，無法復原。')")
out = sub_all(out, '適用於該縣', '適用於該國')
out = sub_all(out, '造訪縣市', '造訪國家', min_count=0)

# ── 3.6b 註釋清理 ──
out = sub_all(out, '// 選中的縣市', '// 選中的國家')
out = sub_all(out, '// 每縣最佳層級', '// 每國最佳層級')
out = sub_all(out, '// 每縣基礎分', '// 每國基礎分')
out = sub_all(out, '// 每縣重複加成', '// 每國重複加成')
out = sub_all(out, '// 縣名標籤：縮放 6 以上才顯示', '// 國名標籤：縮放 6 以上才顯示')
out = sub_all(out, '// 未造訪縣（柔和米色）', '// 未造訪國（柔和米色）')
out = sub_all(out, '// 已造訪縣（朱紅 + 外發光 + 白描邊）', '// 已造訪國（南洋青 + 外發光 + 白描邊）')
out = sub_all(out, '// 已造訪縣名標註（按面積篩選，避免小縣重疊）', '// 已造訪國名標註（按面積篩選，避免小國重疊）')
out = sub_all(out, '// 收集可標註的縣（按面積排序，大的先標，小的跳過重疊）', '// 收集可標註的國（按面積排序，大的先標，小的跳過重疊）')
out = sub_all(out, '// 標註，跳過與已有標註重疊的小縣', '// 標註，跳過與已有標註重疊的小國')
out = sub_all(out, '   縣市搜尋', '   國家搜尋')
out = sub_all(out, '多語 i18n（繁體／簡體／日本語／English）', '多語 i18n（繁體／簡體／English）')
out = sub_all(out, '資料：都道府縣（ISO 3166-2 數字碼 1-47）', '資料：東南亞 11 國（Natural Earth）')
out = sub(out, '有世界遺產的縣（用於「世界遺產巡禮」）', '有世界遺產的國家（用於「世界遺產巡禮」）')

# ── 3.7 殘留檢查 ──
for kw in ['日本', '都道府縣', '縣市', 'JPN-', 'japanMap', 'jp_lang', 'dataofjapan', '日文']:
    n = out.count(kw)
    if n:
        # 找出位置
        idxs = [m.start() for m in re.finditer(re.escape(kw), out)]
        print(f'[殘留] {kw}: {n} 處 @ {idxs[:8]}')
        for i in idxs[:5]:
            print('   ...', out[max(0,i-60):i+60].replace('\n', ' | '))

# 縣（單字）殘留（排除已替換的）
resid = [m.start() for m in re.finditer('縣', out)]
print('縣 殘留總數:', len(resid))

# ── 3.8 收集使用的 key ──
js_keys = set()
for m in re.finditer(r"t\('([^']*)'\)", out):
    js_keys.add(m.group(1))
for m in re.finditer(r't\("([^"]*)"\)', out):
    js_keys.add(m.group(1))

class TextCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.texts = set()
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'template'):
            self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'template') and self.skip:
            self.skip -= 1
    def handle_data(self, data):
        if self.skip:
            return
        t = data.strip()
        if t:
            self.texts.add(t)

body = out[out.find('<body'):out.rfind('</body>')]
tc = TextCollector()
tc.feed(body)
static_keys = tc.texts

# data-i18n-title 屬性鍵
title_keys = set(re.findall(r'data-i18n-title="([^"]+)"', out))

used = js_keys | static_keys | title_keys

# 數據鍵（以資料值作為 t() 鍵的內容）
LEVELS_EN = {
 '未踏之旅人':'Uncharted Traveler', '旅行初心者':'First-time Voyager', '觀光旅客':'Sightseeing Tourist',
 '東南亞探索者':'SEA Explorer', '文化踐行者':'Culture Devotee', '旅遊達人':'Travel Pro',
 '南洋通':'Nanyang Veteran', '國家獵人':'Country Hunter', '東南亞制霸者':'SEA Conqueror',
 '傳說中的旅人':'Legendary Traveler',
}
for k, v in LEVELS_EN.items():
    NEW_EN.setdefault(k, v)

ACH_CATS_EN = {
 '全部':'All', '絕景':'Scenery', '文化':'Culture', '美食':'Food', '自然':'Nature',
 '海島':'Islands', '城市':'Cities', '動物':'Wildlife', '影劇':'Film & TV',
}
for k, v in ACH_CATS_EN.items():
    NEW_EN.setdefault(k, v)

TYPE_NAME_PY = {1:'途經',2:'遊玩',3:'住宿',4:'長居'}
def data_keys():
    keys = set()
    for r in REGIONS.values():
        keys.add(r['name'])
    for c in COUNTRIES.values():
        keys.add(c['ja']); keys.add(c['zh']); keys.add(c['tagline'])
        for x in c['food'] + c['spots'] + c['matsuri']:
            keys.add(x)
    for n, ic, p in LEVELS:
        keys.add(n)
    for v in TYPE_NAME_PY.values():
        keys.add(v)
    for a in ACH:
        keys.add(a[3]); keys.add(a[5])
    for cat in ACH_CATS:
        keys.add(cat)
    return keys

used = used | data_keys()

# 生成 i18n 字典
zh_hans = {}
for k in used:
    zh_hans[k] = ZH_HANS_OVERRIDE.get(k, to_simplified(k))

en = {}
fallback_used = []
for k in sorted(used):
    if k in NEW_EN:
        en[k] = NEW_EN[k]
    elif k in ORIG_EN:
        en[k] = ORIG_EN[k]
    else:
        # fallback transform
        v = ORIG_EN.get(k)
        if v is None:
            v = k
            fallback_used.append(k)
        v = v.replace('Prefectures', 'Countries').replace('prefectures', 'countries')
        v = v.replace('Prefecture', 'Country').replace('prefecture', 'country')
        v = v.replace('Japan', 'Southeast Asia').replace('prefs', 'countries').replace('pref.', 'ctry.')
        en[k] = v

def dict_js(d):
    items = ',\n'.join(f'  "{k}": "{v}"' for k, v in sorted(d.items()))
    return '{\n' + items + '\n}'

i18n_block = (
    'const I18N = {\n'
    "  'zh-Hans': " + dict_js(zh_hans) + ',\n'
    "  'en': " + dict_js(en) + ',\n'
    '};'
)
out = out.replace('__I18N_DICT__', i18n_block, 1)

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(out)

print('OK 寫入', OUT)
print('used keys:', len(used), '| en:', len(en), '| zh-Hans:', len(zh_hans))
print('fallback(無原文/無新增翻譯):', len(fallback_used), fallback_used[:20])
