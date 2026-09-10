# -*- coding: utf-8 -*-
"""
冰島制霸地圖 構建腳本 v2
基於日本制霸地圖 (japan-conquest/index.html) 改造，功能完全對齊。
"""
import json, re

JP = '/Users/lmc/DoubaoWork/chats/2026-09-08/new-chat/japan-conquest/index.html'
OUT = '/Users/lmc/DoubaoWork/chats/2026-09-09/new-chat-12/iceland-conquest/index.html'
GEO = '/tmp/iceland8_final.geojson'

src = open(JP, encoding='utf-8').read()

# ============================================================
# 0. 冰島 GeoJSON
# ============================================================
geo = json.load(open(GEO, encoding='utf-8'))
geo_str = json.dumps(geo, ensure_ascii=False, separators=(',', ':'))

# ============================================================
# 1. 冰島內容數據
# ============================================================
REGIONS_JS = """const REGIONS = {
  '西南':{name:'西南區', ids:[1,2]},
  '西部':{name:'西部區', ids:[3]},
  '西峽灣':{name:'西峽灣區', ids:[4]},
  '北部':{name:'北部區', ids:[5,6]},
  '東部':{name:'東部區', ids:[7]},
  '南部':{name:'南部區', ids:[8]},
};"""

PROVINCES_JS = """const PROVINCES = {
 1:{ja:'Höfuðborgarsvæðið',zh:'首都區',region:'西南',tagline:'冰島的心臟，雷克雅未克的彩色屋頂與音樂廳，北極光下的都會。',food:['羊肉湯','貝亞林斯熱狗','發酵鯊魚肉','Skyr 優格','龍蝦湯'],spots:['哈爾格林姆斯大教堂','哈帕音樂廳','太陽航海者','珍珠樓','托寧湖'],matsuri:['冰島國慶日','Iceland Airwaves','文化之夜']},
 2:{ja:'Suðurnes',zh:'南半島區',region:'西南',tagline:'凱夫拉維克國際機場的門戶，藍湖溫泉與火山裂縫交織的地熱海岸。',food:['龍蝦湯','熔岩地熱麵包','海鮮燉湯','冰島魚乾'],spots:['藍湖','古納威爾地熱區','歐亞美洲板塊橋','雷克雅內斯燈塔'],matsuri:['維京節']},
 3:{ja:'Vesturland',zh:'西部區',region:'西部',tagline:'斯奈山半島的縮影冰島，教會山與《地心探險》的入口。',food:['冰島羊肉','斯奈山海鮮','Skyr 優格','海鹽巧克力'],spots:['教會山','斯奈山冰川','Arnarstapi 懸崖','迪帕倫黑沙灘','博爾加內斯'],matsuri:['斯奈山冬至慶典']},
 4:{ja:'Vestfirðir',zh:'西峽灣區',region:'西峽灣',tagline:'冰島最偏遠的秘境，鋸齒狀峽灣、海鸚懸崖與地熱泳池。',food:['西峽灣海鮮','羊肉料理','冰島鱈魚','海鸚（傳統）'],spots:['丁揚迪瀑布','拉特拉爾角海鸚懸崖','霍恩斯特蘭迪爾自然保護區','伊薩菲厄澤','雷克侯拉爾地熱泳池'],matsuri:['Aldrei fór ég suður 音樂節','侯爾馬維克巫術節']},
 5:{ja:'Norðurland vestra',zh:'西北區',region:'北部',tagline:'犀牛石與海豹棲地，冰島的牧場、峽灣與古老草皮教堂。',food:['冰島羊肉','鱒魚','乾魚','農場乳製品'],spots:['犀牛石海蝕柱','華姆斯唐吉海豹中心','草皮教堂','科魯峽谷'],matsuri:['海豹節','鲱魚節']},
 6:{ja:'Norðurland eystra',zh:'東北區',region:'北部',tagline:'觀鯨之都與米湖仙境，神之瀑布與火山地熱的交響曲。',food:['米湖羊肉','北極紅點鮭','冰島優格','羊肉湯'],spots:['米湖','神之瀑布','黛提瀑布','胡薩維克觀鯨','阿克雷里教堂','克拉夫拉火山'],matsuri:['阿克雷里冬至節','胡薩維克鯨魚節']},
 7:{ja:'Austurland',zh:'東部區',region:'東部',tagline:'杰古沙龍冰河湖與鑽石沙灘，馴鹿漫步的寧靜東峽灣。',food:['赫本龍蝦','馴鹿肉','藍莓','冰島魚'],spots:['杰古沙龍冰河湖','鑽石沙灘','塞濟斯菲厄澤','亨吉瀑布','拉加爾湖'],matsuri:['塞濟斯菲厄澤彩虹節','都皮沃古爾藝術節']},
 8:{ja:'Suðurland',zh:'南部區',region:'南部',tagline:'黃金圈與黑沙灘，瀑布、冰川與火山交織的冰與火之地。',food:['羊肉湯','冰島熱狗','龍蝦料理','火山黑麥麵包'],spots:['黃金圈','古佛斯瀑布','塞里雅蘭瀑布','斯科加瀑布','雷尼斯黑沙灘','斯卡夫塔山','埃亞菲亞德拉火山'],matsuri:['Þorrablót 仲冬節','塞爾福斯音樂節']},
};"""

WH_PREFS_JS = """/* 有世界遺產的地區（冰島：辛格維利爾國家公園、瓦特納冰川國家公園） */
const WH_PREFS = [7, 8];"""

EN_PREF_JS = """const EN_PREF = {1:'Capital Region',2:'Southern Peninsula',3:'Western Region',4:'Westfjords',5:'Northwestern Region',6:'Northeastern Region',7:'Eastern Region',8:'Southern Region'};"""

LEVELS_JS = """const LEVELS = [
  {name:'冰島新旅人',icon:'🧭',pts:0,pct:'2.9%'},
  {name:'初訪者',icon:'✈️',pts:10,pct:'0.8%'},
  {name:'觀光客',icon:'🚌',pts:30,pct:'0.7%'},
  {name:'環島旅人',icon:'🚗',pts:70,pct:'10.7%'},
  {name:'冰島探索者',icon:'🧊',pts:130,pct:'42%'},
  {name:'文化漫遊者',icon:'🎻',pts:210,pct:'32.1%'},
  {name:'冰島通',icon:'🌋',pts:310,pct:'9.2%'},
  {name:'峽灣獵人',icon:'🦅',pts:430,pct:'1.3%'},
  {name:'冰島制霸者',icon:'🏆',pts:580,pct:'0.2%'},
  {name:'極光傳說',icon:'🌌',pts:750,pct:'0.1%'},
];"""

ACH_JS = """const ACH = [
 {id:'A01',cat:'絕景',icon:'⛲',name:'黃金圈制霸',pts:20,cond:'辛格維利爾・蓋錫爾・古佛斯皆「遊玩」以上',kind:'groups',groups:[[8],2]},
 {id:'A02',cat:'瀑布',icon:'💧',name:'南岸雙瀑',pts:16,cond:'塞里雅蘭＋斯科加皆「遊玩」以上',kind:'groups',groups:[[8],2]},
 {id:'A03',cat:'自然',icon:'🌋',name:'冰與火雙極',pts:22,cond:'首都區＋南部區皆「住宿」以上',kind:'groups',groups:[[1,8],3]},
 {id:'A04',cat:'自然',icon:'🛣️',name:'環島公路制霸',pts:30,cond:'8 個地區皆「途經」以上（Ring Road 全環）',kind:'groups',groups:[[1,2,3,4,5,6,7,8],1]},
 {id:'A05',cat:'自然',icon:'🏠',name:'全境住宿制霸',pts:40,cond:'8 個地區皆「住宿」以上',kind:'groups',groups:[[1,2,3,4,5,6,7,8],3]},
 {id:'A06',cat:'絕景',icon:'🗻',name:'西峽灣征服',pts:18,cond:'西峽灣區「住宿」以上',kind:'groups',groups:[[4],3]},
 {id:'A07',cat:'自然',icon:'🦆',name:'米湖仙境',pts:16,cond:'東北區＋東部區皆「遊玩」以上',kind:'groups',groups:[[6,7],2]},
 {id:'A08',cat:'動物',icon:'🐋',name:'觀鯨之旅',pts:15,cond:'東北區（胡薩維克）「遊玩」以上',kind:'groups',groups:[[6],2]},
 {id:'A09',cat:'地熱',icon:'💙',name:'藍湖巡禮',pts:14,cond:'南半島區「遊玩」以上',kind:'groups',groups:[[2],2]},
 {id:'A10',cat:'文化',icon:'🏛️',name:'世界遺產·辛格維利爾',pts:16,cond:'南部區「遊玩」以上',kind:'groups',groups:[[8],2]},
 {id:'A11',cat:'冰川',icon:'🧊',name:'冰川徒步',pts:20,cond:'東部區＋南部區皆「住宿」以上',kind:'groups',groups:[[7,8],3]},
 {id:'A12',cat:'極光',icon:'🌌',name:'極光獵人',pts:22,cond:'西峽灣＋西北區＋東北區皆「住宿」以上',kind:'groups',groups:[[4,5,6],3]},
 {id:'A13',cat:'極光',icon:'☀️',name:'午夜太陽',pts:14,cond:'西部區＋東北區皆「遊玩」以上',kind:'groups',groups:[[3,6],2]},
 {id:'A14',cat:'絕景',icon:'🖤',name:'黑沙灘雙星',pts:14,cond:'雷尼斯＋迪帕倫黑沙灘皆「遊玩」以上',kind:'groups',groups:[[8,3],2]},
 {id:'A15',cat:'地熱',icon:'♨️',name:'地熱溫泉三傑',pts:18,cond:'藍湖＋米湖溫泉＋地熱泳池皆「遊玩」以上',kind:'groups',groups:[[2,6,4],2]},
 {id:'A16',cat:'瀑布',icon:'💦',name:'瀑布收集者',pts:20,cond:'古佛斯＋黛提＋丁揚迪＋亨吉皆「遊玩」以上',kind:'groups',groups:[[8,6,4,7],2]},
 {id:'A17',cat:'地熱',icon:'🌋',name:'火山巡禮',pts:18,cond:'埃亞菲亞德拉＋克拉夫拉＋斯奈山皆「遊玩」以上',kind:'groups',groups:[[8,6,3],2]},
 {id:'A18',cat:'動物',icon:'🐧',name:'海鸚觀賞',pts:15,cond:'拉特拉爾角＋Ingólfshöfði 海鸚崖皆「遊玩」以上',kind:'groups',groups:[[4,8],2]},
 {id:'A19',cat:'動物',icon:'🐴',name:'冰島馬體驗',pts:12,cond:'首都區＋南部區皆「遊玩」以上',kind:'groups',groups:[[1,8],2]},
 {id:'A20',cat:'城鎮',icon:'⛪',name:'教堂巡禮',pts:14,cond:'哈爾格林姆斯＋阿克雷里＋草皮教堂皆「遊玩」以上',kind:'groups',groups:[[1,6,5],2]},
 {id:'A21',cat:'文化',icon:'🪓',name:'維京與薩迦',pts:16,cond:'博爾加內斯＋辛格維利爾＋侯爾馬維克皆「遊玩」以上',kind:'groups',groups:[[3,8,4],2]},
 {id:'A22',cat:'美食',icon:'🦈',name:'冰島美食挑戰',pts:15,cond:'發酵鯊魚＋赫本龍蝦＋羊肉湯皆「遊玩」以上',kind:'groups',groups:[[1,7,8],2]},
 {id:'A23',cat:'城鎮',icon:'🏞️',name:'東峽灣祕境',pts:14,cond:'塞濟斯菲厄澤＋亨吉瀑布皆「遊玩」以上',kind:'groups',groups:[[7],2]},
 {id:'A24',cat:'城鎮',icon:'🏙️',name:'雷克雅未克漫遊',pts:12,cond:'首都區「遊玩」以上',kind:'groups',groups:[[1],2]},
 {id:'A25',cat:'自然',icon:'🏔️',name:'高地探險',pts:18,cond:'南部區＋東北區皆「住宿」以上',kind:'groups',groups:[[8,6],3]},
 {id:'A26',cat:'自然',icon:'🚐',name:'環島七夜',pts:25,cond:'7 個地區以上達「住宿」以上',kind:'count',prefs:[1,2,3,4,5,6,7,8],level:3,n:7},
 {id:'A27',cat:'美食',icon:'🍲',name:'冰島美食家',pts:14,cond:'首都區＋南半島區＋南部區皆「遊玩」以上',kind:'groups',groups:[[1,2,8],2]},
 {id:'A28',cat:'極光',icon:'❄️',name:'冬季極夜',pts:15,cond:'西峽灣＋東北區皆「住宿」以上',kind:'groups',groups:[[4,6],3]},
 {id:'A29',cat:'自然',icon:'🌿',name:'苔原與荒野',pts:12,cond:'西部區＋西北區皆「遊玩」以上',kind:'groups',groups:[[3,5],2]},
 {id:'A30',cat:'文化',icon:'👑',name:'全境制霸（手動）',pts:40,cond:'8 個地區皆「遊玩」以上，且手動勾選',kind:'manual',prefs:[1,2,3,4,5,6,7,8],level:2},
];"""
ACH_CATS_JS = """const ACH_CATS = ['全部','絕景','地熱','冰川','瀑布','文化','美食','動物','極光','自然','城鎮'];"""

# ============================================================
# 2. i18n 字典（is / en）。key 需與最終 HTML 中字串一致；「縣」統一映射為「地區」
# ============================================================
key_map = [
 ('在縣市面板按下「☆ 想去」收藏，或在地圖上點選找靈感。', '在地區面板按下「☆ 想去」收藏，或在地圖上找靈感。'),
 ('造訪縣市：', '造訪地區：'), ('造訪縣市', '造訪地區'),

 (' 縣已評，平均 ', ' 地區已評，平均 '), (' 縣已評分', ' 地區已評分'),
 (' 縣全部造訪過', ' 地區全部造訪過'),
 ('每縣最多 ', '每地區最多 '),
 ('點星星給這座縣市打分', '點星星給這座地區打分'),
 ('還沒記錄這座縣市 — 按下方的「新增旅程」開始吧。', '還沒記錄這座地區 — 按下方的「新增旅程」開始吧。'),
 ('點選縣市，按下「新增旅程」開始記錄足跡。', '點選地區，按下「新增旅程」開始記錄足跡。'),
 ('先點選一個縣市', '先點選一個地區'),
 ('請先選擇縣市', '請先選擇地區'),
 ('勾選即認領此成就（仍需達成縣市條件）', '勾選即認領此成就（仍需達成地區條件）'),
 ('前往縣市 →', '前往地區 →'),
 ('縣市面板', '地區面板'),
 ('這座縣市', '這座地區'),
 ('點選縣市', '點選地區'),
 ('縣市', '地區'),
 (' 縣', ' 地區'),
 ('縣）', '地區）'),
 ('（縣', '（地區'),
]
def apply_key_map(d):
    out_d = {}
    for k, v in d.items():
        nk = k
        for o, n in key_map:
            nk = nk.replace(o, n)
        out_d[nk] = v
    return out_d

I18N_IS_RAW = {
"複製識別碼":"Afrita auðkenni"," 分）":" stig)","戰報":"Skýrsla","冰島制霸戰報":"Íslandssigurskýrsla","制霸足跡":"Sigurslóð","累計總分":"Heildarstig","亮眼成就":"Helstu afrek","冰島":"Ísland","制霸":"Sigra","地圖":"Kort","記錄你走過的每一寸冰島，看看你制霸了幾個地區？":"Skráðu hvern krók af Íslandi sem þú hefur ferðast — hversu mörg héruð hefur þú sigrað?","地區":"Héruð","等級":"Stig","回憶":"Minningar","建立我的地圖":"Búa til kortið mitt","查看已有地圖":"Opna kort","進入地圖":"Fara á kortið","切換":"Skipta","重新載入":"Endurhlaða","操作說明":"Hvernig virkar það","建立你的制霸地圖":"Búa til sigurkortið þitt","填寫地圖名稱與編輯密碼（可留空），系統會產生一組專屬識別碼。純靜態版沒有雲端：識別碼與密碼都只存在這台裝置的瀏覽器裡，無法重設，建議截圖備份。":"Sláðu inn nafn og breytingarlykilorð (má vera autt). Þú færð sérstakt auðkenni. Þetta er algjörlega staðbundin útgáfa — enginn ský: auðkenni og lykilorð eru aðeins geymd í þessum vafra og ekki hægt að endurstilla. Taktu skjáskot til öryggis.","點選地區，認識冰島":"Smelltu á héruð til að kynnast Íslandi","在地圖上點選地區，右側面板會顯示在地美食、景點與節慶介紹。":"Smelltu á héruð á kortinu til að sjá staðbundinn mat, áhugaverða staði og hátíðir.","記錄每一趟旅程":"Skráðu hverja ferð","為每次造訪選擇「途經／遊玩／住宿／長居」，可填寫日期、評分與心得，並勾選在該地區達成的特殊成就。":"Fyrir hverja heimsókn veldu stig — Framhjá / Ferðast / Gisting / Langdvöl — bættu við dagsetningu, einkunn og athugasemd, og merktu afrek.","累積分數、升級等級":"Fáðu stig og stígðu upp","造訪層級越高，得分越多；同地區重複造訪、大區全制霸與特殊成就，都能帶來額外加分。":"Hærra heimsóknarstig gefur fleiri stig; endurheimsóknir, svæðasigrar og sérstök afrek bæta við stigum.","分享制霸戰報":"Deildu sigurskýrslunni","點擊頂欄的戰報按鈕，產生制霸戰報文字、匯出戰報圖片；也能匯出資料檔，帶到另一台裝置繼續記錄。":"Ýttu á skýrsluhnappinn til að búa til texta- og myndskýrslu, eða flytja út gagnaskrá til að halda áfram á öðru tæki.","計分說明":"Stigagjöf","途經":"Framhjá","途經、轉乘":"Í gegnum / millilending","遊玩":"Ferðast","觀光、一日遊":"Skemmtun / dagsferð","住宿":"Gisting","過夜住宿":"Gisting yfir nótt","長居":"Langdvöl","長期居住":"Langtímabúseta","重複造訪":"Endurheimsókn","再+2":"+2 til viðbótar","同一地區多次造訪":"Fleiri en ein heimsókn í sama hérað","每個地區只要有一筆旅程就會計分，造訪層級越高、加分越多。該大區全部地區皆造訪可獲「大區制霸」加成，全數「住宿」以上再加成；特殊成就另行加分。同一地區計分以最高造訪層級為準。":"Ein skráð ferð gefur stig; hærra stig gefur fleiri stig. Heimsókn í öll héruð svæðis gefur „svæðissigur“ bónus, öll „gisting“ eða betra bætir við; sérstök afrek bæta við. Hvert hérað telur hæsta stigið.","特殊成就":"Sérstök afrek","查看全部成就":"Sjá öll afrek","黃金圈制霸":"Gullna hringinn","· 辛格維利爾・蓋錫爾・古佛斯":"· Þingvellir, Geysir, Gullfoss","冰與火雙極":"Eldur og ís","· 首都區＋南部區皆住宿":"· Höfuðborgarsvæði + Suðurland, gisting","環島公路制霸":"Hringvegurinn","· Ring Road 8 地區全環":"· Allir 8 héruð á hringveginum","完整功能":"Eiginleikar","地區幣評分":"Einkunn héruða","為每個地區加上你的主觀評價":"Gefðu hverju héraði þína eigin einkunn","進入地圖評分":"Einkunn á korti","旅遊建議":"Ferðaráð","依你的足跡推薦下一趟旅程":"Næstu áfangastaðir út frá ferðum þínum","查看建議":"Sjá ráð","上傳照片":"Ljósmyndir","把旅途照片掛到地圖上（僅存本機）":"Festu ljósmyndir við kortið (aðeins á þessu tæki)","進入地圖上傳":"Hlaða upp á korti","好友排行":"Vinastig","匯入好友資料檔，本機比拚制霸進度":"Flyttu inn gagnaskrár vina til að bera saman","打開排行":"Opna stigalista","冰島制霸地圖 · 純靜態版 — 所有資料僅存於本機瀏覽器（localStorage），不提供雲端儲存服務。":"Íslandssigurkort · Staðbundin útgáfa — öll gögn geymd í þessum vafra (localStorage); enginn skýþjónusta.","地區邊界 © National Land Survey of Iceland（GeoJSON）· 地圖渲染 Leaflet · 介面 MDUI 2":"Héruð © Landmælingar Íslands (GeoJSON) · Kort Leaflet · Viðmót MDUI 2","點選地區查看介紹 · 滾輪縮放 / 拖曳移動":"Smelltu á hérað til að skoða · hjól til að zooma / dragðu til að færa","造訪層級":"Heimsóknarstig","未造訪":"Óheimsótt","途經 +2":"Framhjá +2","遊玩 +5":"Ferðast +5","住宿 +10":"Gisting +10","長居 +20":"Langdvöl +20","點選地圖上的地區，":"Smelltu á hérað á kortinu,","查看在地美食、景點與節慶，並記錄你的旅程。":"skoðaðu mat, staði og hátíðir, og skráðu ferðir þínar.","隨機探索":"Slembikönnun","最佳層級":"Besta stig","本站得分":"Stig héraðs","紀錄":"Skráningar","分":" stig","筆":" skráningar","在地美食":"Staðbundinn matur","名所景點":"Áhugaverðir staðir","祭典行事":"Hátíðir","☆ 想去":"☆ Langar að fara","★ 已想去":"★ Á óskalista","旅途照片":"Ferðaljósmyndir","僅存本機 · 不隨資料檔匯出":"Aðeins á þessu tæki · ekki í útflutningi","旅程紀錄":"Skráðar ferðir","清除此地":"Hreinsa hérað","已鎖定編輯 — 點擊頂欄鎖頭解鎖後才能記錄旅程":"Breytingar læstar — opnaðu með lásnum í toppstikunni","新增旅程":"Bæta við ferð","建立我的制霸地圖":"Búa til sigurkortið þitt","為地圖命名並設定編輯密碼（可留空），系統會產生一組專屬識別碼。":"Nefndu kortið og stilltu breytingarlykilorð (má vera autt); þú færð sérstakt auðkenni.","地圖名稱":"Nafn korts","例：我的環島公路之旅、極光獵人的冬夜":"t.d. Hringvegurinn minn, vetrarnótt norðurljósa","編輯密碼（可留空）":"Breytingarlykilorð (má vera autt)","再次輸入密碼":"Endurtaktu lykilorð","取消":"Hætta við","建立地圖":"Búa til kort","輸入識別碼開啟這台裝置上已建立的地圖。":"Opnaðu kort sem þegar er búið til á þessu tæki með auðkenni.","識別碼　例：ISL-A3K9":"Auðkenni t.d. ISL-A3K9","純靜態版沒有雲端伺服器：識別碼無法跨裝置讀取資料，只在本機生效。":"Enginn skýþjónusta: auðkenni virka aðeins á þessu tæki.","本機已建立的地圖（點選即開啟）：":"Kort á þessu tæki (smelltu til að opna):","從資料檔匯入":"Flytja inn úr skrá","開啟地圖":"Opna kort","解鎖編輯":"Opna breytingar","輸入這張地圖的編輯密碼以解鎖編輯功能。":"Sláðu inn breytingarlykilorð til að opna.","編輯密碼":"Breytingarlykilorð","解鎖":"Opna","記錄旅程":"Skrá ferð","日期":"Dagsetning","評分":"Einkunn","心得":"Athugasemd","在這一地區達成的成就":"Afrek hér","儲存旅程":"Vista ferð","該地區已達成的成就":"Afrek sem náðst hafa hér","願望清單":"Óskalisti","把想去的地區收進清單，或回顧你的旅程足跡。":"Settu héruð sem þú vilt heimsækja á listann, eða skoðaðu tímalínu ferða.","想去":"Óskalisti","旅程時間線":"Tímalína","還沒有想去的地方 —":"Enginn óskalisti enn —","在地區面板按下「☆ 想去」收藏，或在地圖上找靈感。":"ýttu á „☆ Langar að fara“ í spjaldi héraðs eða skoðaðu kortið.","定位":"Staðsetja","取消想去":"Fjarlægja","還沒有任何旅程紀錄 —":"Engar ferðir skráðar enn —","點選地區，按下「新增旅程」開始記錄足跡。":"smelltu á hérað og ýttu á „Bæta við ferð“.","關閉":"Loka","達成條件後自動解鎖；標記「手動」的成就需自行勾選。點擊成就卡片可查看條件。":"Opnast sjálfkrafa þegar skilyrði eru uppfyllt; „handvirk“ afrek merkir þú sjálfur. Smelltu á spjald fyrir nánari upplýsingar.","成就條件":"Skilyrði","全部":"Öll","達成":"Opnuð","未達成":"Óopnuð","制霸戰報":"Sigurskýrsla","你的冰島制霸進度總覽，可複製文字、匯出圖片或匯出資料檔。":"Yfirlit yfir sigurframvindu þína — afritaðu texta, flyttu út mynd eða gagnaskrá.","複製戰報":"Afrita skýrslu","匯出圖片":"Flytja út mynd","匯出資料檔":"Flytja út gögn","刪除這張地圖":"Eyða þessu korti","依你的足跡與未完成的成就，推薦下一站。":"Næstu áfangastaðir út frá ferðum þínum og ókláruðum afrekum.","純靜態版沒有雲端：請好友「匯出資料檔」傳給你，再匯入比拚 — 排行只在你自己的瀏覽器裡計算。":"Enginn ský: biddu vini að flytja út gagnaskrá sína og flyttu inn — stigalistinn er reiknaður aðeins í þínum vafra.","匯入好友資料檔":"Flytja inn vinagögn","確定？":"Ertu viss?","確定":"Staðfesta","冰島新旅人":"Nýr ferðalangur","初訪者":"Nýliði","觀光客":"Ferðamaður","環島旅人":"Hringvegaferðalangur","冰島探索者":"Íslandslandkönnuður","文化漫遊者":"Menningarvitji","冰島通":"Íslandsþekking","峽灣獵人":"Firðaveiðari","冰島制霸者":"Íslandssigurvegari","極光傳說":"Norðurljósasaga","全境制霸（手動）":"Allt landið (handvirkt)","制霸之始":"Fyrsta skref","五地之旅":"Fimm héruð","十地之旅":"Tíu héruð","雪國之旅":"Vetrarferð","南方島嶼之旅":"Suðureyjar","城市漫遊者":"Borgarvitji","溫泉巡禮":"Laugapílagrímsferð","古城巡禮":"Gamlabæjarferð","自然愛好者":"Náttúruunnandi","歷史愛好者":"Söguáhugamaður","美食家":"Matgæðingur","旅途照片達人":"Ljósmyndameistari","長居愛好者":"Langdvölarelsari","評價高手":"Einkunnameistari","+20 分":"+20 stig","+25 分":"+25 stig","+30 分":"+30 stig","+40 分":"+40 stig","· 8 個地區皆遊玩（手動勾選）":"· Öll 8 héruð, ferðast (handvirkt)","早起的鳥兒":"Morgunfugl","夜貓子":"Náttugla","北端踏破":"Norðuroddur","南端踏破":"Suðuroddur","東端踏破":"Austuroddur","西端踏破":"Vesturoddur","離島之旅":"Eyjaferð","制霸週年":"Sigurafmæli","好友比拚":"Vinakeppni","皆「遊玩」以上":"öll „ferðast“ eða betra","皆「住宿」以上":"öll „gisting“ eða betra","皆「途經」以上":"öll „framhjá“ eða betra","「遊玩」以上":"„ferðast“ eða betra","「住宿」以上":"„gisting“ eða betra","「途經」以上":"„framhjá“ eða betra","以上":"eða betra","全境":"öll héruð","個地區":"héruð","造訪":"heimsótt","先點選一個地區":"Veldu hérað fyrst","請先選擇地區":"Veldu hérað fyrst","兩次輸入的密碼不一致":"Lykilorðin passa ekki","匯入失敗：不是有效的制霸資料檔":"Innflutningur mistókst: ekki gild skrá","匯出圖片失敗":"Myndútflutningur mistókst","密碼不正確":"Rangt lykilorð","已上傳照片（僅存本機）":"Ljósmynd bætt við (aðeins á þessu tæki)","已刪除地圖":"Korti eytt","已刪除好友":"Vinum fjarlægt","已刪除照片":"Ljósmynd fjarlægð","已刪除紀錄":"Skráning eytt","已加入好友「":"Vini bætt við: ","已匯入地圖「":"Kort flutt inn: ","已匯出戰報圖片":"Skýrslumynd flutt út","已匯出資料檔，請妥善保存":"Gagnaskrá flutt út — geymdu hana vel","已建立地圖「":"Kort búið til: ","已清除「":"Hreinsað: ","已移出願望清單":"Fjarlægt af óskalista","已複製識別碼 ":"Auðkenni afritað: ","已解鎖，可以編輯了":"Opnað — breytingar leyfðar","已記錄：":"Skráð: ","已鎖定編輯":"Breytingar læstar","已鎖定編輯，無法修改願望清單":"Breytingar læstar — óskalisti óbreyttur","建立或開啟一張地圖後，才能依足跡推薦行程":"Búðu til eða opnaðu kort fyrir ráð","建立或開啟一張地圖後，才能收集成就":"Búðu til eða opnaðu kort til að safna afrekum","戰報已複製":"Skýrsla afrituð","找不到這張地圖的資料":"Gögn kortsins finnast ekki","本機找不到 ":"Fannst ekki á þessu tæki: ","正在繪製戰報圖片…":"Bý til skýrslumynd…","每地區最多 ":"Hámark á hérað: ","沒有可匯出的戰報":"Ekkert til að flytja út","複製失敗，請手動選取戰報文字":"Afritun mistókst — veldu textann handvirkt","解鎖成就 ":"Afrek opnað: ","請填寫地圖名稱":"Sláðu inn nafn korts","請輸入識別碼":"Sláðu inn auðkenni","請選擇圖片檔案":"Veldu myndaskrá","讀取圖片失敗":"Ekki tókst að lesa mynd","（僅存本機，請備份）":" (aðeins á þessu tæki — taktu öryggisafrit)","」 識別碼 ":" (auðkenni ","已加入願望清單":"Bætt við óskalista","（可留空）":" (má vera autt)","張照片（最多 ":" ljósmyndir (hámark ","）":")","第 ":"#","個地區":"héraðið","資料已匯入，請重新載入頁面":"Gögn flutt inn — endurhlaðið síðuna","不隨資料檔匯出":"ekki í útflutningi","還沒記錄這座地區 — 按下方的「新增旅程」開始吧。":"Engar ferðir hér enn — ýttu á „Bæta við ferð“ hér að neðan.","推薦給你的下一站":"Næstu áfangastaðir","已造訪過，不妨再去一次":"Heimsótt áður — vert þess virði að fara aftur","未完成成就的候選地":"Afrakandinn fyrir ókláruð afrek","已造訪":"Heimsótt","總得分":"Heildarstig","造訪地區":"Svæði","成就":"Afrek","西南區":"Suðvestur","西部區":"Vestur","西峽灣區":"Vestfirðir","北部區":"Norður","東部區":"Austur","南部區":"Suður"," 評為 ":" einkunn "," 星":" stjörnur","（僅存於本機，請備份）":" (aðeins á þessu tæki — taktu öryggisafrit)"," 的資料（純靜態版無法跨裝置讀取）":" fannst ekki (staðbundið, enginn ský)","」 ":" — "," — 請妥善備份":" — geymdu það vel"," 張照片":" ljósmyndir"," 項：":": "," 分":" stig"," 分 · ":" stig · ","」的記錄":" skráningar"," 筆紀錄將被移除，無法復原。":" skráning(ar) verða fjarlægðar. Ekki hægt að afturkalla.","等級：":"Stig: ","總分：":"Heildarstig: "," / 8":" / 8"," / 6":" / 6","造訪地區：":"Heimsótt héruð: ","地區制霸：":"Svæði kláruð: ","成就：":"Afrek: ","地區足跡：":"Svæðaslóð: ","地區幣評分：":"Einkunn héruða: "," 地區已評，平均 ":" einkunn, meðaltal "," / 5 星":" / 5 stjörnur","亮眼成就：":"Helstu afrek: ","— 由「冰島制霸地圖」純靜態版產生，資料僅存於本機瀏覽器 —":"— Búið til af „Íslandssigurkort“ (staðbundin útgáfa); gögn aðeins í vafranum þínum —","已獲得 ":"Opnuð "," 項 · 成就加成 <b>+":"  · afrekabónus <b>+","</b> 分</span>":"</b> stig</span>","建立地圖後開始收集":"Byrjaðu að safna eftir að kort er búið til","手動勾選認領":"Merkja handvirkt","編輯旅程 · ":"Breyta ferð · ","新增旅程 · ":"Bæta við ferð · ","勾選即認領此成就（仍需達成地區條件）":"Merkja til að fá (héraskilyrði gilda enn)","尚未建立任何地圖 — 從首頁「建立我的地圖」開始。":"Engin kort enn — byrjaðu á „Búa til kortið mitt“ á forsíðu.","完成「":"Kláraðu „","」地區制霸：還差 ":" svæðissigur: vantar "," 地區":" héruð","補齊「":"Kláraðu „","」成就：還差 ":" afrek: vantar ","經典首選 — 從這裡展開你的冰島制霸":"Klassískur valkostur — byrjaðu sigur þinn hér","前往地區 →":"Fara í hérað →","名稱":"Nafn","總分":"Stig","我":"Ég","刪除":"Eyða","還沒有任何資料 — 建立你的地圖，或匯入好友的制霸資料檔開始比拚。":"Engin gögn enn — búðu til kort eða flyttu inn vinagögn til að keppa.","排行榜只在本機計算與顯示，不經由任何雲端。更新好友：請對方重新匯出資料檔，再匯入覆蓋同名好友即可。":"Stigalistinn er reiknaður aðeins á þessu tæki — enginn ský. Til að uppfæra: biddu vin að flytja út aftur og flyttu inn til að skrifa yfir.","刪除好友？":"Fjarlægja vin?","」將從排行中移除。":" verður fjarlægð(ur) af stigalistanum.","已達最高等級":"Hæsta stigi náð","距「":"Vantar ","」還差 ":" til að ná ","你的評價 ":"Þín einkunn: ","點星星給這座地區打分":"Ýttu á stjörnur til að gefa einkunn","已移除評價":"Einkunn fjarlægð","未填日期":"Engin dagsetning","刪除照片":"Fjarlægja mynd","照片 ":"Ljósmynd ","上傳":"Bæta við","找不到「":"Engin niðurstaða fyrir \"","」":"\"","的資料":" gögn","總分 ":"Stig ","造訪地區 / 8":"Heimsótt héruð / 8","地區制霸 / 6":"Svæði kláruð / 6","成就 / ":"Afrek / ","成就加成":"Afrekabónus","純靜態版沒有雲端伺服器：識別碼只在本機生效。要跨裝置繼續記錄，請用「匯出資料檔」把資料帶走，再在另一台裝置「從資料檔匯入」。":"Enginn skýþjónusta: auðkenni virka aðeins á þessu tæki. Til að halda áfram annars staðar, flyttu út gagnaskrá og flyttu hana inn á öðru tæki.","建立或開啟一張地圖後，才能依足跡推薦行程。":"Búðu til eða opnaðu kort til að fá ráð.","太厲害了 — 8 個地區全部造訪過，等下一段旅程啟程吧。":"Frábært — öll 8 héruð heimsótt. Tími til að skipuleggja næstu ferð!","覆蓋既有地圖？":"Skrifa yfir núverandi kort?"," 已存在於本機，匯入將覆蓋原有資料。確定繼續？":" er þegar á þessu tæki. Innflutningur skrifar yfir. Halda áfram?","清除「":"Hreinsa allt fyrir \"","」全部記錄？":"\"?","將刪除這座地區的全部旅程紀錄、地區幣評分與旅途照片，無法復原。":"Allar ferðir, einkunn og myndir þessa héraðs verða eytt. Ekki hægt að afturkalla.","刪除這筆旅程？":"Eyða þessari ferð?","「":"\"","」的第 ":" #","刪除這張地圖？":"Eyða þessu korti?","」的全部旅程紀錄與成就將從本機刪除，無法復原。建議先匯出備份。":"\" — öllum ferðum og afrekum verður eytt varanlega. Flyttu út öryggisafrit fyrst.","絕景":"Útsýni","祭典":"Hátíðir","地熱":"Jarðhiti","冰川":"Jöklar","瀑布":"Fossar","美食":"Matur","動物":"Dýr","極光":"Norðurljós","自然":"Náttúra","城鎮":"Bæir","文化":"Menning","搜尋地區（中文／冰島語／大區）":"Leita að héruðum (kínverska / íslenska / svæði)","搜尋地區":"Leita að héruðum","清除":"Hreinsa","回首頁":"Forsíða","編輯鎖定":"Breytingalás","查看制霸戰報":"Skoða sigurskýrslu","冰島的心臟，雷克雅未克的彩色屋頂與音樂廳，北極光下的都會。":"Hjarta Íslands — lituð þök Reykjavíkur, tónlistarhúsið og norðurljós yfir borginni.","凱夫拉維克國際機場的門戶，藍湖溫泉與火山裂縫交織的地熱海岸。":"Hlið Keflavíkurflugvallar — Bláa lónið og eldgosasprungur á jarðhitaströnd.","斯奈山半島的縮影冰島，教會山與《地心探險》的入口。":"Ísland í smámynd — Kirkjufell og inngangurinn að „Leiðangrinum að miðju jarðar“.","冰島最偏遠的秘境，鋸齒狀峽灣、海鸚懸崖與地熱泳池。":"Afskekktasta svæði Íslands — söguð firðir, lundaklettar og jarðhitarlaugar.","犀牛石與海豹棲地，冰島的牧場、峽灣與古老草皮教堂。":"Hvítserkur og selalendi — búgarðar, firðir og gamlar torfkirkjur.","觀鯨之都與米湖仙境，神之瀑布與火山地熱的交響曲。":"Hvalaskoðunarhöfuðborgin og Mývatn — Goðafoss og eldfjallajarðhiti.","杰古沙龍冰河湖與鑽石沙灘，馴鹿漫步的寧靜東峽灣。":"Jökulsárlón og Diamond Beach — hreindýr og rólegir austfirðir.","黃金圈與黑沙灘，瀑布、冰川與火山交織的冰與火之地。":"Gullni hringinn og svartar strendur — fossar, jöklar og eldfjöll.","動漫":"Anime","影劇":"Kvikmyndir","運動":"Íþróttir","溫泉":"Laugar","城堡":"Kastalar",
}
I18N_EN_RAW = {
"複製識別碼":"Copy code"," 分）":" pts)","戰報":"Report","冰島制霸戰報":"Iceland Conquest Report","制霸足跡":"Conquest Footprint","累計總分":"Total Score","亮眼成就":"Top Achievements","冰島":"Iceland","制霸":"CONQUEST","地圖":"MAP","記錄你走過的每一寸冰島，看看你制霸了幾個地區？":"Record every inch of Iceland you've traveled — how many regions have you conquered?","地區":"Regions","等級":"Level","回憶":"Memories","建立我的地圖":"Create My Map","查看已有地圖":"Open Existing Map","進入地圖":"Enter Map","切換":"Switch","重新載入":"Reload","操作說明":"How It Works","建立你的制霸地圖":"Create your map","填寫地圖名稱與編輯密碼（可留空），系統會產生一組專屬識別碼。純靜態版沒有雲端：識別碼與密碼都只存在這台裝置的瀏覽器裡，無法重設，建議截圖備份。":"Name your map and set an edit password (optional). You'll get a unique code. Fully static build — no cloud: your code and password live only in this browser and can't be reset. Screenshot them for backup.","點選地區，認識冰島":"Tap regions, explore Iceland","在地圖上點選地區，右側面板會顯示在地美食、景點與節慶介紹。":"Click a region on the map to see local food, sights and festivals in the side panel.","記錄每一趟旅程":"Log every trip","為每次造訪選擇「途經／遊玩／住宿／長居」，可填寫日期、評分與心得，並勾選在該地區達成的特殊成就。":"For each visit pick a tier — Pass Through / Sightseeing / Stay / Long Stay — add date, rating and notes, and tick achievements earned there.","累積分數、升級等級":"Earn points, level up","造訪層級越高，得分越多；同地區重複造訪、大區全制霸與特殊成就，都能帶來額外加分。":"Higher tiers earn more points; revisits, zone sweeps and special achievements add bonuses.","分享制霸戰報":"Share your conquest report","點擊頂欄的戰報按鈕，產生制霸戰報文字、匯出戰報圖片；也能匯出資料檔，帶到另一台裝置繼續記錄。":"Hit the report button to generate text and image reports, or export a data file to continue on another device.","計分說明":"Scoring","途經":"Pass","途經、轉乘":"Transit / transfer","遊玩":"Sightsee","觀光、一日遊":"Sightseeing / day trip","住宿":"Stay","過夜住宿":"Overnight stay","長居":"Long Stay","長期居住":"Extended residence","重複造訪":"Revisit","再+2":"+2 more","同一地區多次造訪":"Multiple visits to the same region","每個地區只要有一筆旅程就會計分，造訪層級越高、加分越多。該大區全部地區皆造訪可獲「大區制霸」加成，全數「住宿」以上再加成；特殊成就另行加分。同一地區計分以最高造訪層級為準。":"Any logged trip scores points; higher tiers score more. Visiting every region in a zone earns a Zone Sweep bonus, all-Stay-or-better adds another; special achievements add more. Each region counts at its best tier.","特殊成就":"Achievements","查看全部成就":"View all achievements","黃金圈制霸":"Golden Circle","· 辛格維利爾・蓋錫爾・古佛斯":"· Þingvellir, Geysir, Gullfoss","冰與火雙極":"Fire & Ice","· 首都區＋南部區皆住宿":"· Capital + South, Stay","環島公路制霸":"Ring Road","· Ring Road 8 地區全環":"· All 8 regions on Route 1","完整功能":"Features","地區幣評分":"Ratings","為每個地區加上你的主觀評價":"Rate each region your way","進入地圖評分":"Rate on map","旅遊建議":"Trip Suggestions","依你的足跡推薦下一趟旅程":"Next-destination ideas from your travels","查看建議":"View suggestions","上傳照片":"Photo Albums","把旅途照片掛到地圖上（僅存本機）":"Pin trip photos to the map (local only)","進入地圖上傳":"Upload on map","好友排行":"Friend Leaderboard","匯入好友資料檔，本機比拚制霸進度":"Import friends' data files and compare progress","打開排行":"Open leaderboard","冰島制霸地圖 · 純靜態版 — 所有資料僅存於本機瀏覽器（localStorage），不提供雲端儲存服務。":"Iceland Conquest Map · Static build — all data stays in this browser (localStorage); no cloud storage.","地區邊界 © National Land Survey of Iceland（GeoJSON）· 地圖渲染 Leaflet · 介面 MDUI 2":"Region boundaries © National Land Survey of Iceland (GeoJSON) · Map by Leaflet · UI by MDUI 2","點選地區查看介紹 · 滾輪縮放 / 拖曳移動":"Click a region to explore · scroll to zoom / drag to pan","造訪層級":"Visit Tier","未造訪":"Not visited","途經 +2":"Pass +2","遊玩 +5":"Sightsee +5","住宿 +10":"Stay +10","長居 +20":"Long Stay +20","點選地圖上的地區，":"Click a region on the map,","查看在地美食、景點與節慶，並記錄你的旅程。":"and explore local food, sights and festivals while logging your trips.","隨機探索":"Random Pick","最佳層級":"Best tier","本站得分":"Region score","紀錄":"Records","分":"pts","在地美食":"Local Food","名所景點":"Sights","祭典行事":"Festivals","☆ 想去":"☆ Want to go","★ 已想去":"★ In wishlist","旅途照片":"Trip photos","僅存本機 · 不隨資料檔匯出":"Local only · not included in exports","旅程紀錄":"Trips logged","清除此地":"Clear region","已鎖定編輯 — 點擊頂欄鎖頭解鎖後才能記錄旅程":"Editing locked — unlock via the padlock in the top bar to log trips","新增旅程":"Add Trip","建立我的制霸地圖":"Create Your Conquest Map","為地圖命名並設定編輯密碼（可留空），系統會產生一組專屬識別碼。":"Name your map and set an edit password (optional); you'll get a unique code.","地圖名稱":"Map name","例：我的環島公路之旅、極光獵人的冬夜":"e.g. My Ring Road Trip, Aurora Hunter's Winter Night","編輯密碼（可留空）":"Edit password (optional)","再次輸入密碼":"Re-enter password","取消":"Cancel","建立地圖":"Create Map","輸入識別碼開啟這台裝置上已建立的地圖。":"Open a map already created on this device by its code.","識別碼　例：ISL-A3K9":"Code e.g. ISL-A3K9","純靜態版沒有雲端伺服器：識別碼無法跨裝置讀取資料，只在本機生效。":"No cloud server: codes only work on this device.","本機已建立的地圖（點選即開啟）：":"Maps on this device (tap to open):","從資料檔匯入":"Import from file","開啟地圖":"Open Map","解鎖編輯":"Unlock Editing","輸入這張地圖的編輯密碼以解鎖編輯功能。":"Enter the edit password to unlock editing.","編輯密碼":"Edit password","解鎖":"Unlock","記錄旅程":"Log a Trip","日期":"Date","評分":"Rating","心得":"Notes","在這一地區達成的成就":"Achievements earned here","儲存旅程":"Save Trip","該地區已達成的成就":"Achievements unlocked here","願望清單":"Wishlist","把想去的地區收進清單，或回顧你的旅程足跡。":"Save regions you want to visit, or revisit your journey timeline.","想去":"Wishlist","旅程時間線":"Timeline","還沒有想去的地方 —":"No wishlist yet —","在地區面板按下「☆ 想去」收藏，或在地圖上找靈感。":"tap \"☆ Want to go\" in a region panel or explore the map.","定位":"Locate","取消想去":"Remove","還沒有任何旅程紀錄 —":"No trips logged yet —","點選地區，按下「新增旅程」開始記錄足跡。":"click a region and hit \"Add Trip\".","關閉":"Close","達成條件後自動解鎖；標記「手動」的成就需自行勾選。點擊成就卡片可查看條件。":"Auto-unlock when conditions are met; \"manual\" achievements are self-ticked. Tap a card for details.","成就條件":"Requirement","全部":"All","達成":"Unlocked","未達成":"Locked","制霸戰報":"Conquest Report","你的冰島制霸進度總覽，可複製文字、匯出圖片或匯出資料檔。":"Your conquest progress at a glance — copy text, export an image or the data file.","複製戰報":"Copy report","匯出圖片":"Export image","匯出資料檔":"Export data","刪除這張地圖":"Delete this map","依你的足跡與未完成的成就，推薦下一站。":"Next-destination ideas based on your travels and unfinished achievements.","純靜態版沒有雲端：請好友「匯出資料檔」傳給你，再匯入比拚 — 排行只在你自己的瀏覽器裡計算。":"No cloud: ask friends to export their data file and import it — rankings are computed only in your browser.","匯入好友資料檔":"Import friend data","確定？":"Are you sure?","確定":"OK","冰島新旅人":"New Traveler","初訪者":"First-Timer","觀光客":"Sightseer","環島旅人":"Ring Roader","冰島探索者":"Iceland Explorer","文化漫遊者":"Culture Wanderer","冰島通":"Iceland Connoisseur","峽灣獵人":"Fjord Hunter","冰島制霸者":"Iceland Conqueror","極光傳說":"Aurora Legend","全境制霸（手動）":"All Regions (Manual)","制霸之始":"First Step","五地之旅":"Five Regions","十地之旅":"Ten Regions","雪國之旅":"Winter Land","南方島嶼之旅":"Southern Isles","城市漫遊者":"City Roamer","溫泉巡禮":"Hot Spring Pilgrim","古城巡禮":"Old Town Pilgrim","自然愛好者":"Nature Lover","歷史愛好者":"History Buff","美食家":"Foodie","旅途照片達人":"Photo Pro","長居愛好者":"Long-Stay Lover","評價高手":"Rater Supreme","+20 分":"+20 pts","+25 分":"+25 pts","+30 分":"+30 pts","+40 分":"+40 pts","· 8 個地區皆遊玩（手動勾選）":"· All 8 regions, Sightseeing (manual)","早起的鳥兒":"Early Bird","夜貓子":"Night Owl","北端踏破":"Northern Tip","南端踏破":"Southern Tip","東端踏破":"Eastern Tip","西端踏破":"Western Tip","離島之旅":"Island Hopper","制霸週年":"Conquest Anniversary","好友比拚":"Friend Rivalry","皆「遊玩」以上":"all \"Sightseeing\" or above","皆「住宿」以上":"all \"Stay\" or above","皆「途經」以上":"all \"Pass\" or above","「遊玩」以上":"\"Sightseeing\" or above","「住宿」以上":"\"Stay\" or above","「途經」以上":"\"Pass\" or above","以上":"or above","全境":"all regions","個地區":"regions","造訪":"visited","先點選一個地區":"Pick a region first","請先選擇地區":"Select a region first","兩次輸入的密碼不一致":"Passwords don't match","匯入失敗：不是有效的制霸資料檔":"Import failed: not a valid data file","匯出圖片失敗":"Image export failed","密碼不正確":"Incorrect password","已上傳照片（僅存本機）":"Photo added (local only)","已刪除地圖":"Map deleted","已刪除好友":"Friend removed","已刪除照片":"Photo removed","已刪除紀錄":"Record deleted","已加入好友「":"Friend added: ","已匯入地圖「":"Map imported: ","已匯出戰報圖片":"Report image exported","已匯出資料檔，請妥善保存":"Data file exported — keep it safe","已建立地圖「":"Map created: ","已清除「":"Cleared: ","已移出願望清單":"Removed from wishlist","已複製識別碼 ":"Code copied: ","已解鎖，可以編輯了":"Unlocked — editing enabled","已記錄：":"Logged: ","已鎖定編輯":"Editing locked","已鎖定編輯，無法修改願望清單":"Editing locked — wishlist unchanged","建立或開啟一張地圖後，才能依足跡推薦行程":"Create or open a map for suggestions","建立或開啟一張地圖後，才能收集成就":"Create or open a map to collect achievements","戰報已複製":"Report copied","找不到這張地圖的資料":"Map data not found","本機找不到 ":"Not found on this device: ","正在繪製戰報圖片…":"Rendering report image…","每地區最多 ":"Max per region: ","沒有可匯出的戰報":"Nothing to export","複製失敗，請手動選取戰報文字":"Copy failed — select the report text manually","解鎖成就 ":"Achievement unlocked: ","請填寫地圖名稱":"Please enter a map name","請輸入識別碼":"Please enter a code","請選擇圖片檔案":"Choose an image file","讀取圖片失敗":"Could not read the image","（僅存本機，請備份）":" (local only — back it up)","」 識別碼 ":" (code ","已加入願望清單":"Added to wishlist","（可留空）":" (optional)","張照片（最多 ":" photos (max ","）":")","第 ":"#","個地區":"region","資料已匯入，請重新載入頁面":"Data imported — please reload the page","不隨資料檔匯出":"not included in exports","還沒記錄這座地區 — 按下方的「新增旅程」開始吧。":"No trips here yet — hit \"Add Trip\" below to begin.","推薦給你的下一站":"Suggested next stops","已造訪過，不妨再去一次":"Visited before — worth a return","未完成成就的候選地":"Achievement candidate","已造訪":"Visited","總得分":"Total score","造訪地區":"Zones covered","成就":"Ach.","西南區":"Southwest","西部區":"West","西峽灣區":"Westfjords","北部區":"North","東部區":"East","南部區":"South"," 評為 ":" rated "," 星":" stars","（僅存於本機，請備份）":" (local only — keep it backed up)"," 的資料（純靜態版無法跨裝置讀取）":" not found (no cloud, device-local only)","」 ":" — "," — 請妥善備份":" — keep it safe"," 張照片":" photos"," 項：":": "," 分":" pts"," 分 · ":" pts · ","」的記錄":" records"," 筆紀錄將被移除，無法復原。":" record(s) will be removed. This cannot be undone.","等級：":"Level: ","總分：":"Score: "," / 8":" / 8"," / 6":" / 6","造訪地區：":"Visited: ","地區制霸：":"Zones: ","成就：":"Achievements: ","地區足跡：":"Zone footprint: ","地區幣評分：":"Ratings: "," 地區已評，平均 ":" rated, avg "," / 5 星":" / 5 stars","亮眼成就：":"Top achievements: ","— 由「冰島制霸地圖」純靜態版產生，資料僅存於本機瀏覽器 —":"— Generated by Iceland Conquest Map (static build); data stays in your browser —","已獲得 ":"Unlocked "," 項 · 成就加成 <b>+":"  · bonus <b>+","</b> 分</span>":"</b> pts</span>","建立地圖後開始收集":"Start collecting after creating a map","手動勾選認領":"Tick to claim","編輯旅程 · ":"Edit trip · ","新增旅程 · ":"Add trip · ","勾選即認領此成就（仍需達成地區條件）":"Tick to claim (region conditions still apply)","尚未建立任何地圖 — 從首頁「建立我的地圖」開始。":"No maps yet — start from \"Create My Map\" on the home page.","完成「":"Complete the ","」地區制霸：還差 ":" zone sweep: need "," 地區":" more","補齊「":"Complete ","」成就：還差 ":" achievement: need ","經典首選 — 從這裡展開你的冰島制霸":"Classic pick — start your conquest here","前往地區 →":"Go to region →","名稱":"Name","總分":"Score","我":"Me","刪除":"Remove","還沒有任何資料 — 建立你的地圖，或匯入好友的制霸資料檔開始比拚。":"No data yet — create your map or import a friend's file to compete.","排行榜只在本機計算與顯示，不經由任何雲端。更新好友：請對方重新匯出資料檔，再匯入覆蓋同名好友即可。":"Rankings are computed and shown only on this device — no cloud. To refresh: ask your friend to re-export, then import to overwrite.","刪除好友？":"Remove friend?","」將從排行中移除。":" will be removed from the leaderboard.","已達最高等級":"Max level reached","距「":"Need ","」還差 ":" more to reach ","你的評價 ":"Your rating: ","點星星給這座地區打分":"Tap stars to rate this region","已移除評價":"Rating removed","未填日期":"No date","刪除照片":"Remove photo","照片 ":"Photo ","上傳":"Add","找不到「":"No results for \"","」":"\"","的資料":" data","總分 ":"Score ","造訪地區 / 8":"Regions / 8","地區制霸 / 6":"Zones / 6","成就 / ":"Achievements / ","成就加成":"Bonus","純靜態版沒有雲端伺服器：識別碼只在本機生效。要跨裝置繼續記錄，請用「匯出資料檔」把資料帶走，再在另一台裝置「從資料檔匯入」。":"No cloud server: codes work only on this device. To continue elsewhere, export your data file and import it on another device.","建立或開啟一張地圖後，才能依足跡推薦行程。":"Create or open a map to get suggestions.","太厲害了 — 8 個地區全部造訪過，等下一段旅程啟程吧。":"Amazing — all 8 regions visited. Time to plan the next journey!","覆蓋既有地圖？":"Overwrite existing map?"," 已存在於本機，匯入將覆蓋原有資料。確定繼續？":" already exists on this device. Importing will overwrite it. Continue?","清除「":"Clear all for \"","」全部記錄？":"\"?","將刪除這座地區的全部旅程紀錄、地區幣評分與旅途照片，無法復原。":"All trips, rating and photos for this region will be deleted. This cannot be undone.","刪除這筆旅程？":"Delete this trip?","「":"\"","」的第 ":" #","刪除這張地圖？":"Delete this map?","」的全部旅程紀錄與成就將從本機刪除，無法復原。建議先匯出備份。":"\" — all trips and achievements will be deleted permanently. Export a backup first.","絕景":"Scenery","祭典":"Festivals","地熱":"Geothermal","冰川":"Glaciers","瀑布":"Waterfalls","美食":"Food","動物":"Wildlife","極光":"Aurora","自然":"Nature","城鎮":"Towns","文化":"Culture","搜尋地區（中文／冰島語／大區）":"Search regions (Chinese / Icelandic / zone)","搜尋地區":"Search regions","清除":"Clear","回首頁":"Home","編輯鎖定":"Edit Lock","查看制霸戰報":"View conquest report","冰島的心臟，雷克雅未克的彩色屋頂與音樂廳，北極光下的都會。":"The heart of Iceland — Reykjavík's colorful rooftops, Harpa and aurora over the city.","凱夫拉維克國際機場的門戶，藍湖溫泉與火山裂縫交織的地熱海岸。":"Gateway to Keflavík Airport — the Blue Lagoon and volcanic fissures on a geothermal coast.","斯奈山半島的縮影冰島，教會山與《地心探險》的入口。":"Iceland in miniature — Kirkjufell and the gateway to \"Journey to the Center of the Earth\".","冰島最偏遠的秘境，鋸齒狀峽灣、海鸚懸崖與地熱泳池。":"Iceland's wildest frontier — jagged fjords, puffin cliffs and geothermal pools.","犀牛石與海豹棲地，冰島的牧場、峽灣與古老草皮教堂。":"Hvítserkur and seal country — farms, fjords and ancient turf churches.","觀鯨之都與米湖仙境，神之瀑布與火山地熱的交響曲。":"Whale-watching capital and Mývatn — Goðafoss and volcanic geothermal symphonies.","杰古沙龍冰河湖與鑽石沙灘，馴鹿漫步的寧靜東峽灣。":"Jökulsárlón and Diamond Beach — reindeer and the serene Eastfjords.","黃金圈與黑沙灘，瀑布、冰川與火山交織的冰與火之地。":"The Golden Circle and black sands — waterfalls, glaciers and volcanoes in the land of fire and ice.","動漫":"Anime","影劇":"Film & TV","運動":"Sports","溫泉":"Hot Springs","城堡":"Castles",
}
I18N_IS = apply_key_map(I18N_IS_RAW)
I18N_EN = apply_key_map(I18N_EN_RAW)

I18N_JS = "const I18N = {\n" \
    "  'zh-Hans':{},\n" \
    "  'is':" + json.dumps(I18N_IS, ensure_ascii=False) + ",\n" \
    "  'en':" + json.dumps(I18N_EN, ensure_ascii=False) + "\n" \
    "};"

# ============================================================
# 3. 執行替換
# ============================================================
def replace_once(s, old, new):
    if old not in s:
        print('  !! NOT FOUND:', old[:100])
        return s
    return s.replace(old, new, 1)

out = src

# ---- head ----
out = replace_once(out, '<title>日本制霸地圖 · 記錄你走過的每一寸日本</title>',
 '<title>冰島制霸地圖 · 記錄你走過的每一寸冰島</title>')
out = replace_once(out,
 '<link rel="icon" href="data:image/svg+xml,<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 100 100\'><rect width=\'100\' height=\'100\' rx=\'20\' fill=\'%23FCF8F3\'/><circle cx=\'50\' cy=\'50\' r=\'26\' fill=\'%23B02A1A\'/></svg>">',
 '<link rel="icon" href="data:image/svg+xml,<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 100 100\'><rect width=\'100\' height=\'100\' rx=\'20\' fill=\'%2302529C\'/><rect x=\'42\' y=\'0\' width=\'16\' height=\'100\' fill=\'%23FFFFFF\'/><rect x=\'0\' y=\'42\' width=\'100\' height=\'16\' fill=\'%23FFFFFF\'/><rect x=\'46\' y=\'0\' width=\'8\' height=\'100\' fill=\'%23DC1E35\'/><rect x=\'0\' y=\'46\' width=\'100\' height=\'8\' fill=\'%23DC1E35\'/></svg>">')
out = replace_once(out,
 '<meta name="description" content="純靜態的日本 47 都道府縣制霸記錄器：點選地圖、記錄旅程、累積分數、解鎖成就、升級等級。資料只存於本機瀏覽器。">',
 '<meta name="description" content="純靜態的冰島 8 地區制霸記錄器：點選地圖、記錄旅程、累積分數、解鎖成就、升級等級。資料只存於本機瀏覽器。">')

# ---- CSS 顏色 ----
css_rep = [
 ('  --mdui-color-primary:176 42 26;', '  --mdui-color-primary:2 82 156;'),
 ('  --mdui-color-primary-container:255 218 212;', '  --mdui-color-primary-container:211 229 255;'),
 ('  --mdui-color-on-primary-container:59 5 0;', '  --mdui-color-on-primary-container:0 21 45;'),
 ('  --mdui-color-inverse-primary:255 180 168;', '  --mdui-color-inverse-primary:158 202 255;'),
 ('  --mdui-color-tertiary:123 94 0;', '  --mdui-color-tertiary:0 106 80;'),
 ('  --mdui-color-tertiary-container:255 224 138;', '  --mdui-color-tertiary-container:165 242 209;'),
 ('  --mdui-color-on-tertiary-container:42 31 0;', '  --mdui-color-on-tertiary-container:0 42 31;'),
 ('  --mdui-color-surface:252 248 243;', '  --mdui-color-surface:248 250 253;'),
 ('  --mdui-color-on-surface:33 26 23;', '  --mdui-color-on-surface:27 33 40;'),
 ('  --mdui-color-surface-dim:223 211 201;', '  --mdui-color-surface-dim:214 219 227;'),
 ('  --mdui-color-surface-bright:255 248 242;', '  --mdui-color-surface-bright:250 252 255;'),
 ('  --mdui-color-surface-container-low:247 239 233;', '  --mdui-color-surface-container-low:240 243 248;'),
 ('  --mdui-color-surface-container:241 232 225;', '  --mdui-color-surface-container:234 238 244;'),
 ('  --mdui-color-surface-container-high:235 225 217;', '  --mdui-color-surface-container-high:229 233 240;'),
 ('  --mdui-color-surface-container-highest:229 219 210;', '  --mdui-color-surface-container-highest:223 228 235;'),
 ('  --mdui-color-on-surface-variant:82 68 62;', '  --mdui-color-on-surface-variant:73 80 90;'),
 ('  --mdui-color-outline:133 116 108;', '  --mdui-color-outline:121 128 138;'),
 ('  --mdui-color-outline-variant:212 196 188;', '  --mdui-color-outline-variant:204 211 219;'),
 ('  --mdui-color-background:252 248 243;', '  --mdui-color-background:248 250 253;'),
 ('  --mdui-color-on-background:33 26 23;', '  --mdui-color-on-background:27 33 40;'),
 ('  --mdui-color-inverse-surface:79 90 112;', '  --mdui-color-inverse-surface:52 60 70;'),
 ('  --mdui-color-surface-variant:229 219 210;', '  --mdui-color-surface-variant:222 228 235;'),

 ('  --paper:#FCF8F3;', '  --paper:#F8FAFD;'),
 ('  --paper-deep:#F1E8E1;', '  --paper-deep:#E9EEF5;'),
 ('  --ink:#211A17;', '  --ink:#1B2127;'),
 ('  --ink-soft:#52443E;', '  --ink-soft:#46515C;'),
 ('  --ink-faint:#85746C;', '  --ink-faint:#7C8794;'),
 ('  --vermilion:#B02A1A;', '  --vermilion:#02529C;'),
 ('  --vermilion-deep:#8C1F12;', '  --vermilion-deep:#063E77;'),
 ('  --gold:#C9A227;', '  --gold:#B98A12;'),
 ('  --gold-soft:#FFE08A;', '  --gold-soft:#F7D57A;'),
 ('  --indigo:#4F5A70;', '  --indigo:#33485C;'),
 ('  --line:#E3D5CB;', '  --line:#D8E0EA;'),
]
for o, n in css_rep:
    out = out.replace(o, n)
out = out.replace('radial-gradient(rgba(176,42,26,.07) 1px,transparent 1.4px)', 'radial-gradient(rgba(2,82,156,.07) 1px,transparent 1.4px)')
out = out.replace('background:rgba(176,42,26,.08)', 'background:rgba(2,82,156,.08)')
out = out.replace('box-shadow:0 2px 6px rgba(176,42,26,.35),inset 0 0 0 1px rgba(176,42,26,.6)', 'box-shadow:0 2px 6px rgba(2,82,156,.35),inset 0 0 0 1px rgba(2,82,156,.6)')

# ---- 國旗 ----
out = replace_once(out,
 """.brand-flag{
  width:30px;height:21px;border-radius:4px;background:#fff;
  box-shadow:inset 0 0 0 1px rgba(33,26,23,.14);
  position:relative;flex:none;
}
.brand-flag::after{
  content:'';position:absolute;left:50%;top:50%;
  width:11px;height:11px;border-radius:50%;
  background:var(--vermilion);transform:translate(-50%,-50%);
}""",
 """.brand-flag{
  width:30px;height:21px;border-radius:4px;background:#02529C;
  box-shadow:inset 0 0 0 1px rgba(27,33,39,.14);
  position:relative;flex:none;overflow:hidden;
}
.brand-flag::before{
  content:'';position:absolute;left:50%;top:0;bottom:0;
  width:6px;background:#fff;transform:translateX(-50%);
}
.brand-flag::after{
  content:'';position:absolute;left:50%;top:50%;
  width:100%;height:6px;background:#fff;transform:translate(-50%,-50%);
}
.brand-flag .cross-r{
  position:absolute;left:50%;top:0;bottom:0;width:3px;
  background:#DC1E35;transform:translateX(-50%);z-index:2;
}
.brand-flag .cross-r2{
  position:absolute;left:50%;top:50%;width:100%;height:3px;
  background:#DC1E35;transform:translate(-50%,-50%);z-index:2;
}""")
out = replace_once(out,
 """.hero-flag{
  width:84px;height:59px;border-radius:12px;background:#fff;
  box-shadow:var(--shadow-2),inset 0 0 0 1px rgba(33,26,23,.10);
  margin:0 auto 22px;position:relative;
}
.hero-flag::after{
  content:'';position:absolute;left:50%;top:50%;
  width:31px;height:31px;border-radius:50%;
  background:var(--vermilion);transform:translate(-50%,-50%);
}""",
 """.hero-flag{
  width:84px;height:59px;border-radius:12px;background:#02529C;
  box-shadow:var(--shadow-2),inset 0 0 0 1px rgba(27,33,39,.10);
  margin:0 auto 22px;position:relative;overflow:hidden;
}
.hero-flag::before{
  content:'';position:absolute;left:50%;top:0;bottom:0;
  width:16px;background:#fff;transform:translateX(-50%);
}
.hero-flag::after{
  content:'';position:absolute;left:50%;top:50%;
  width:100%;height:16px;background:#fff;transform:translate(-50%,-50%);
}
.hero-flag .cross-r{
  position:absolute;left:50%;top:0;bottom:0;width:8px;
  background:#DC1E35;transform:translateX(-50%);z-index:2;
}
.hero-flag .cross-r2{
  position:absolute;left:50%;top:50%;width:100%;height:8px;
  background:#DC1E35;transform:translate(-50%,-50%);z-index:2;
}""")
out = replace_once(out, '<span class="brand-flag"></span>', '<span class="brand-flag"><span class="cross-r"></span><span class="cross-r2"></span></span>')
out = replace_once(out, '<div class="hero-flag"></div>', '<div class="hero-flag"><span class="cross-r"></span><span class="cross-r2"></span></div>')

# ---- HTML 文案 ----
html_rep = [
 ('        <button data-lang="ja" title="日本語">日</button>', '        <button data-lang="is" title="Íslenska">Ís</button>'),
 ('<span class="brand-name">日本<b>制霸</b>地圖</span>', '<span class="brand-name">冰島<b>制霸</b>地圖</span>'),
 ('<h1>日本<span class="jp">制霸</span>地圖</h1>', '<h1>冰島<span class="jp">制霸</span>地圖</h1>'),
 ('<p class="hero-sub">記錄你走過的每一寸日本，看看你制霸了幾個縣？</p>', '<p class="hero-sub">記錄你走過的每一寸冰島，看看你制霸了幾個地區？</p>'),
 ('<div class="hero-stat"><div class="num">47</div><div class="lbl">縣市</div></div>', '<div class="hero-stat"><div class="num">8</div><div class="lbl">地區</div></div>'),
 ('<div class="step-title">點選縣市，認識日本</div>', '<div class="step-title">點選地區，認識冰島</div>'),
 ('<div class="step-desc">在地圖上點選都道府縣，右側面板會顯示在地美食、景點與祭典介紹。</div>', '<div class="step-desc">在地圖上點選地區，右側面板會顯示在地美食、景點與節慶介紹。</div>'),
 ('<div class="step-desc">為每次造訪選擇「途經／遊玩／住宿／長居」，可填寫日期、評分與心得，並勾選在該縣達成的特殊成就。</div>', '<div class="step-desc">為每次造訪選擇「途經／遊玩／住宿／長居」，可填寫日期、評分與心得，並勾選在該地區達成的特殊成就。</div>'),
 ('<div class="step-desc">造訪層級越高，得分越多；同縣重複造訪、地區全制霸與特殊成就，都能帶來額外加分。</div>', '<div class="step-desc">造訪層級越高，得分越多；同地區重複造訪、大區全制霸與特殊成就，都能帶來額外加分。</div>'),
 ('<div class="score-foot">每個縣市只要有一筆旅程就會計分，造訪層級越高、加分越多。該地區全部縣市皆造訪可獲「地區制霸」加成，全數「住宿」以上再加成；特殊成就另行加分。同一縣市計分以最高造訪層級為準。</div>', '<div class="score-foot">每個地區只要有一筆旅程就會計分，造訪層級越高、加分越多。該大區全部地區皆造訪可獲「大區制霸」加成，全數「住宿」以上再加成；特殊成就另行加分。同一地區計分以最高造訪層級為準。</div>'),
 ('<div class="score-card"><div class="sc-type">重複造訪 <span class="pts">再+2<small> 分</small></span></div><div class="sc-desc">同一縣市多次造訪</div></div>', '<div class="score-card"><div class="sc-type">重複造訪 <span class="pts">再+2<small> 分</small></span></div><div class="sc-desc">同一地區多次造訪</div></div>'),
 ('<div class="ach-card"><div class="ic">⛩️</div><div class="ac-body"><div class="ac-name">日本三景</div><div class="ac-pts">+20 分 <span>· 松島・天橋立・宮島</span></div></div></div>', '<div class="ach-card"><div class="ic">⛲</div><div class="ac-body"><div class="ac-name">黃金圈制霸</div><div class="ac-pts">+20 分 <span>· 辛格維利爾・蓋錫爾・古佛斯</span></div></div></div>'),
 ('<div class="ach-card"><div class="ic">🎆</div><div class="ac-body"><div class="ac-name">日本三大祭</div><div class="ac-pts">+25 分 <span>· 祇園・天神・神田</span></div></div></div>', '<div class="ach-card"><div class="ic">🌋</div><div class="ac-body"><div class="ac-name">冰與火雙極</div><div class="ac-pts">+22 分 <span>· 首都區＋南部區皆住宿</span></div></div></div>'),
 ('<div class="ach-card"><div class="ic">🏯</div><div class="ac-body"><div class="ac-name">十二天守</div><div class="ac-pts">+30 分 <span>· 現存天守 12 座全制霸</span></div></div></div>', '<div class="ach-card"><div class="ic">🛣️</div><div class="ac-body"><div class="ac-name">環島公路制霸</div><div class="ac-pts">+30 分 <span>· Ring Road 8 地區全環</span></div></div></div>'),
 ('<div class="ach-card"><div class="ic">🙏</div><div class="ac-body"><div class="ac-name">四國遍路</div><div class="ac-pts">+45 分 <span>· 四國四縣（手動勾選）</span></div></div></div>', '<div class="ach-card"><div class="ic">👑</div><div class="ac-body"><div class="ac-name">全境制霸</div><div class="ac-pts">+40 分 <span>· 8 個地區皆遊玩（手動勾選）</span></div></div></div>'),
 ('<div class="rm-card"><div class="rm-ic">⭐</div><h3>縣幣評分</h3><p>為每個縣市加上你的主觀評價</p>', '<div class="rm-card"><div class="rm-ic">⭐</div><h3>地區幣評分</h3><p>為每個地區加上你的主觀評價</p>'),
 ('日本制霸地圖 · 純靜態版 — 所有資料僅存於本機瀏覽器（localStorage），不提供雲端儲存服務。<br>\n      都道府縣邊界 © dataofjapan（GeoJSON）· 地圖渲染 Leaflet · 介面 MDUI 2', '冰島制霸地圖 · 純靜態版 — 所有資料僅存於本機瀏覽器（localStorage），不提供雲端儲存服務。<br>\n      地區邊界 © National Land Survey of Iceland（GeoJSON）· 地圖渲染 Leaflet · 介面 MDUI 2'),
 ('<input id="prefSearch" placeholder="搜尋縣市（中文／日文／地區）" autocomplete="off" aria-label="搜尋縣市">', '<input id="prefSearch" placeholder="搜尋地區（中文／冰島語／大區）" autocomplete="off" aria-label="搜尋地區">'),
 ('<div class="map-hint">點選縣市查看介紹 · 滾輪縮放 / 拖曳移動</div>', '<div class="map-hint">點選地區查看介紹 · 滾輪縮放 / 拖曳移動</div>'),
 ('<div>點選地圖上的都道府縣，<br>查看在地美食、景點與祭典，並記錄你的旅程。</div>', '<div>點選地圖上的地區，<br>查看在地美食、景點與節慶，並記錄你的旅程。</div>'),
 ('<div class="fl-hint">例：我的關西之旅、大阪社畜的週末</div>', '<div class="fl-hint">例：我的環島公路之旅、極光獵人的冬夜</div>'),
 ('<mdui-text-field id="lfCode" variant="outlined" label="識別碼　例：JPN-A3K9" style="width:100%"></mdui-text-field>', '<mdui-text-field id="lfCode" variant="outlined" label="識別碼　例：ISL-A3K9" style="width:100%"></mdui-text-field>'),
 ('<span class="fl-label">在這一縣達成的成就</span>', '<span class="fl-label">在這一地區達成的成就</span>'),
 ('<div class="dlg-sub">把想去的縣市收進清單，或回顧你的旅程足跡。</div>', '<div class="dlg-sub">把想去的地區收進清單，或回顧你的旅程足跡。</div>'),
 ('<div class="dlg-sub">你的日本制霸進度總覽，可複製文字、匯出圖片或匯出資料檔。</div>', '<div class="dlg-sub">你的冰島制霸進度總覽，可複製文字、匯出圖片或匯出資料檔。</div>'),
]
for o, n in html_rep:
    out = replace_once(out, o, n)

# ---- 數據塊 ----
def block_replace(s, start_marker, end_marker, new_block):
    i = s.index(start_marker)
    j = s.index(end_marker, i) + len(end_marker)
    return s[:i] + new_block + s[j:]

out = block_replace(out, 'const REGIONS = {', '};', REGIONS_JS)
out = block_replace(out, 'const PROVINCES = {', '};', PROVINCES_JS)
out = re.sub(r'/\* 有世界遺產的縣（用於「世界遺產巡禮」） \*/\nconst WH_PREFS = \[[^\]]*\];', WH_PREFS_JS, out)
out = block_replace(out, 'const EN_PREF = {', '};', EN_PREF_JS)
out = block_replace(out, 'const LEVELS = [', '];', LEVELS_JS)
out = block_replace(out, 'const ACH = [', '];', ACH_JS)
out = block_replace(out, "const ACH_CATS = [", '];', ACH_CATS_JS)

i18n_start = out.index("const I18N = {")
i18n_end = out.index("function t(s){")
out = out[:i18n_start] + I18N_JS + "\n" + out[i18n_end:]

out = replace_once(out, "const LANGS = ['zh-Hant','zh-Hans','ja','en'];", "const LANGS = ['zh-Hant','zh-Hans','is','en'];")

# ---- GeoJSON ----
out = re.sub(r'<script>window\.JAPAN_GEOJSON = .*?</script>',
             '<script>window.ICELAND_GEOJSON = ' + geo_str + ';</script>', out, flags=re.S)

# ---- JS 邏輯 ----
js_rep = [
 ("const LS_REG = 'japanMap.registry';", "const LS_REG = 'icelandMap.registry';"),
 ("const LS_ACTIVE = 'japanMap.active';", "const LS_ACTIVE = 'icelandMap.active';"),
 ("const LS_DATA = 'japanMap.data.';", "const LS_DATA = 'icelandMap.data.';"),
 ("const LS_FRIENDS = 'japanMap.friends';", "const LS_FRIENDS = 'icelandMap.friends';"),
 ("const LANG_KEY = 'jp_lang';", "const LANG_KEY = 'is_lang';"),
 ("if(LANG === 'ja') return p.ja;", "if(LANG === 'is') return p.ja;"),
 ("$('pNameJa').textContent = LANG === 'ja' ? (EN_PREF[id] || '') : p.ja;", "$('pNameJa').textContent = LANG === 'is' ? (EN_PREF[id] || '') : p.ja;"),
 ("for(let id=1; id<=47; id++){", "for(let id=1; id<=Object.keys(PROVINCES).length; id++){"),
 ("for(let id = 1; id <= 47; id++){", "for(let id = 1; id <= Object.keys(PROVINCES).length; id++){"),
 ("const vars = [zh, ja, rg, zh + '都', zh + '府', zh + '縣'];", "const vars = [zh, ja, rg, zh + '區'];"),
 ("const LABEL_MAJOR = new Set([1,2,3,4,5,6,7,13,15,16,20,22,23,27,28,30,31,34,36,37,40,42,43,44,46,47]);", "const LABEL_MAJOR = new Set([1,2,3,4,5,6,7,8]);"),
 ("map.attributionControl.addAttribution('境界 © <a href=\"https://github.com/dataofjapan/land\" target=\"_blank\" rel=\"noopener\">dataofjapan</a> · Leaflet');", "map.attributionControl.addAttribution('境界 © <a href=\"https://www.lmi.is/\" target=\"_blank\" rel=\"noopener\">NLSI</a> · Leaflet');"),
]
# PREF_IMG 正則替換
out = re.sub(r'const PREF_IMG = \{[^;]*\};', "const PREF_IMG = {1:'assets/prefs/01_capital.jpg', 2:'assets/prefs/02_sudurnes.jpg', 3:'assets/prefs/03_vesturland.jpg', 4:'assets/prefs/04_vestfirdir.jpg', 5:'assets/prefs/05_nordurland_vestra.jpg', 6:'assets/prefs/06_nordurland_eystra.jpg', 7:'assets/prefs/07_austurland.jpg', 8:'assets/prefs/08_sudurland.jpg'};", out)
for o, n in js_rep:
    out = replace_once(out, o, n)
out = replace_once(out, "c = 'JPN-';", "c = 'ISL-';")
out = replace_once(out, '   多語 i18n（繁體／簡體／日本語／English）', '   多語 i18n（繁體／簡體／冰島語／English）')
out = replace_once(out, '   資料：都道府縣（ISO 3166-2 數字碼 1-47）', '   資料：冰島地區（ISO 3166-2 數字碼 1-8）')
out = out.replace('window.JAPAN_GEOJSON', 'window.ICELAND_GEOJSON')
out = out.replace("      const t = document.createElement('span');\n      t.className = 'ac-t';\n      t.innerHTML = '<b>' + esc(a.icon + ' ' + t(a.name)) + '</b><span>' + t('勾選即認領此成就（仍需達成縣市條件）') + '</span>';\n      label.appendChild(t);", "      const sp = document.createElement('span');\n      sp.className = 'ac-t';\n      sp.innerHTML = '<b>' + esc(a.icon + ' ' + t(a.name)) + '</b><span>' + t('勾選即認領此成就（仍需達成地區條件）') + '</span>';\n      label.appendChild(sp);")

# ---- 動態文案：縣→地區 ----
dyn_rep = [
 ("t('還沒記錄這座縣市 — 按下方的「新增旅程」開始吧。')", "t('還沒記錄這座地區 — 按下方的「新增旅程」開始吧。')"),
 ("t('點星星給這座縣市打分')", "t('點星星給這座地區打分')"),
 ("t('先點選一個縣市')", "t('先點選一個地區')"),
 ("t('勾選即認領此成就（仍需達成縣市條件）')", "t('勾選即認領此成就（仍需達成地區條件）')"),
 ("t('在縣市面板按下「☆ 想去」收藏，或在地圖上點選找靈感。')", "t('在地區面板按下「☆ 想去」收藏，或在地圖上找靈感。')"),
 ("t('點選縣市，按下「新增旅程」開始記錄足跡。')", "t('點選地區，按下「新增旅程」開始記錄足跡。')"),
 ("t('請先選擇縣市')", "t('請先選擇地區')"),
 ("t('每縣最多 ')", "t('每地區最多 ')"),
 ("t('縣幣評分：')", "t('地區評分：')"),
 ("t(' 縣已評，平均 ')", "t(' 地區已評，平均 ')"),
 ("t(' 縣已評分')", "t(' 地區已評分')"),
 ("t('前往縣市 →')", "t('前往地區 →')"),
 ("t('將刪除這座縣市的全部旅程紀錄、縣幣評分與旅途照片，無法復原。')", "t('將刪除這座地區的全部旅程紀錄、地區幣評分與旅途照片，無法復原。')"),
 ("frHead('visited',t('縣市'))", "frHead('visited',t('地區'))"),
 ("missing.length + t(' 縣')", "missing.length + t(' 地區')"),
]
for o, n in dyn_rep:
    out = out.replace(o, n)
out = out.replace('縣幣評分', '地區評分')
out = out.replace('縣已評', '地區已評')

# ---- 戰報文字與數字 ----
out = replace_once(out, "lines.push(t('【日本制霸戰報】') + curData.name + '（' + curCode + '）');",
                          "lines.push(t('【冰島制霸戰報】') + curData.name + '（' + curCode + '）');")
out = replace_once(out, "lines.push(t('造訪縣市：') + s.visited + t(' / 47') + '　' + t('地區制霸：') + s.regionsDone + t(' / 8'));",
                          "lines.push(t('造訪地區：') + s.visited + t(' / 8') + '　' + t('地區制霸：') + s.regionsDone + t(' / 6'));")
out = replace_once(out, "lines.push(t('— 由「日本制霸地圖」純靜態版產生，資料僅存於本機瀏覽器 —'));",
                          "lines.push(t('— 由「冰島制霸地圖」純靜態版產生，資料僅存於本機瀏覽器 —'));")
out = replace_once(out, "'<div class=\"report-stat\"><div class=\"rs-num\">' + s.visited + '</div><div class=\"rs-lbl\">' + t('造訪縣市 / 47') + '</div></div>' +",
                          "'<div class=\"report-stat\"><div class=\"rs-num\">' + s.visited + '</div><div class=\"rs-lbl\">' + t('造訪地區 / 8') + '</div></div>' +")
out = replace_once(out, "'<div class=\"report-stat\"><div class=\"rs-num\">' + s.regionsDone + '</div><div class=\"rs-lbl\">' + t('地區制霸 / 8') + '</div></div>' +",
                          "'<div class=\"report-stat\"><div class=\"rs-num\">' + s.regionsDone + '</div><div class=\"rs-lbl\">' + t('地區制霸 / 6') + '</div></div>' +")

# ---- 戰報 Canvas ----
out = replace_once(out, "const VERM = '#9E2418', VERM_DEEP = '#7A1A10', VERM_SOFT = '#C44A3A';",
                          "const VERM = '#0A5AA8', VERM_DEEP = '#074178', VERM_SOFT = '#3A7FC4';")
out = replace_once(out, "const PAPER = '#FAF5EE', PAPER_WARM = '#F5EEE3';",
                          "const PAPER = '#F7FAFD', PAPER_WARM = '#EDF3FA';")
out = replace_once(out, "const GOLD = '#B08D1E', GOLD_LIGHT = '#D4B54E', GOLD_FAINT = '#E8D9A8';",
                          "const GOLD = '#B98A12', GOLD_LIGHT = '#D4A93E', GOLD_FAINT = '#EAD9A0';")
out = replace_once(out, "const INK = '#1E1815', INK_SOFT = '#4A3F39', INK_FAINT = '#8A7A72';",
                          "const INK = '#1B2127', INK_SOFT = '#46515C', INK_FAINT = '#7C8794';")
out = replace_once(out, "const CARD_BG = '#FFFFFF', CARD_BORDER = '#E8DDCE';",
                          "const CARD_BG = '#FFFFFF', CARD_BORDER = '#DCE4EE';")
out = replace_once(out, "center(t('日本制霸戰報'), W/2, 168, '900 58px ' + serif, VERM);",
                          "center(t('冰島制霸戰報'), W/2, 168, '900 58px ' + serif, VERM);")
out = replace_once(out, "const badgeT = t('已造訪') + '  ' + visitedIds.length + t(' / 47') + t('縣');",
                          "const badgeT = t('已造訪') + '  ' + visitedIds.length + t(' / 8') + t('地區');")
out = replace_once(out, "const GB = { minLon: 123.6, maxLon: 146.2, minLat: 24.0, maxLat: 45.7 };",
                          "const GB = { minLon: -24.7, maxLon: -13.3, minLat: 63.15, maxLat: 66.7 };")
out = replace_once(out, "ctx.fillText('123°E – 146°E  /  24°N – 46°N', mc.x + mc.w - 40, legY);",
                          "ctx.fillText('24°W – 13°W  /  63°N – 67°N', mc.x + mc.w - 40, legY);")
out = replace_once(out, "ctx.fillStyle = '#EAE0D0'; ctx.fill();", "ctx.fillStyle = '#E4EAF2'; ctx.fill();")
out = replace_once(out, "ctx.strokeStyle = '#D2C4AE'; ctx.lineWidth = 0.7; ctx.stroke();", "ctx.strokeStyle = '#C9D4E2'; ctx.lineWidth = 0.7; ctx.stroke();")
out = replace_once(out, "setShadow(14, 0, 'rgba(158,36,24,.4)');", "setShadow(14, 0, 'rgba(10,90,168,.4)');")
out = replace_once(out, "ctx.strokeStyle = 'rgba(158,36,24,.15)'; ctx.lineWidth = 0.8; ctx.stroke();", "ctx.strokeStyle = 'rgba(10,90,168,.15)'; ctx.lineWidth = 0.8; ctx.stroke();")
out = replace_once(out, "ctx.fillStyle = '#E0D4C0'; ctx.beginPath(); ctx.arc(mc.x+148, legY-5, 7, 0, Math.PI*2); ctx.fill();", "ctx.fillStyle = '#DCE4F0'; ctx.beginPath(); ctx.arc(mc.x+148, legY-5, 7, 0, Math.PI*2); ctx.fill();")
out = replace_once(out, "ctx.strokeStyle = '#D2C4AE'; ctx.lineWidth = 1; ctx.stroke();", "ctx.strokeStyle = '#C9D4E2'; ctx.lineWidth = 1; ctx.stroke();")
out = replace_once(out, "heroGrad.addColorStop(0, '#2A211C'); heroGrad.addColorStop(1, INK);", "heroGrad.addColorStop(0, '#0E2C4A'); heroGrad.addColorStop(1, '#123A5F');")
out = replace_once(out, "[s.visited, t('造訪縣市'), '/ 47'],", "[s.visited, t('造訪地區'), '/ 8'],")
out = replace_once(out, "[s.regionsDone, t('地區制霸'), '/ 8'],", "[s.regionsDone, t('地區制霸'), '/ 6'],")
out = replace_once(out, "ctx.fillStyle = '#EDE2D2'; round(x, barY, barW, barH, 3); ctx.fill();", "ctx.fillStyle = '#E4EAF2'; round(x, barY, barW, barH, 3); ctx.fill();")
out = replace_once(out, "center(t('— 由「日本制霸地圖」純靜態版產生 —'), W/2, footY+50, '400 18px ' + sans, INK_FAINT);",
                          "center(t('— 由「冰島制霸地圖」純靜態版產生 —'), W/2, footY+50, '400 18px ' + sans, INK_FAINT);")
out = replace_once(out, "center('所有資料僅存於本機瀏覽器，不提供雲端儲存服務', W/2, footY+76, '400 15px ' + sans, '#A99C94');",
                          "center('所有資料僅存於本機瀏覽器，不提供雲端儲存服務', W/2, footY+76, '400 15px ' + sans, '#A0A9B3');")

# ---- 建議與好友 ----
out = replace_once(out, "const hot = [26, 13, 27, 1, 40, 14, 28, 23];", "const hot = [8, 1, 2, 3, 6, 7, 4, 5];")
out = replace_once(out, "push(id, t('經典首選 — 從這裡展開你的日本制霸'));", "push(id, t('經典首選 — 從這裡展開你的冰島制霸'));")
out = replace_once(out, "wrap.innerHTML = '<div class=\"sug-empty\">' + t('太厲害了 — 47 縣全部造訪過，等下一段旅程啟程吧。') + '</div>';",
                          "wrap.innerHTML = '<div class=\"sug-empty\">' + t('太厲害了 — 8 個地區全部造訪過，等下一段旅程啟程吧。') + '</div>';")
out = replace_once(out, "'<td>' + r.visited + '/47</td>' +", "'<td>' + r.visited + '/8</td>' +")
out = replace_once(out, "'<td>' + r.regionsDone + '/8</td>' +", "'<td>' + r.regionsDone + '/6</td>' +")

# ---- 驗證 ----
left_japan = out.count('日本')
left_47 = len(re.findall(r'(?<![0-9])47(?![0-9])', out))
print('剩餘「日本」字樣數:', left_japan)
print('剩餘 47 字樣數:', left_47)

with open(OUT, 'w', encoding='utf-8') as fp:
    fp.write(out)
print('已寫出:', OUT, len(out), 'bytes')
