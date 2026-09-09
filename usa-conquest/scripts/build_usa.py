#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build USA Conquest Map index.html from the Japan Conquest Map source.
Reads  /Users/lmc/DoubaoWork/chats/2026-09-08/new-chat/japan-conquest/index.html
Writes /Users/lmc/DoubaoWork/chats/2026-09-09/new-chat-3/usa-conquest/index.html
"""
import json, re, sys

SRC = '/Users/lmc/DoubaoWork/chats/2026-09-08/new-chat/japan-conquest/index.html'
DST = '/Users/lmc/DoubaoWork/chats/2026-09-09/new-chat-3/usa-conquest/index.html'

lines = open(SRC, encoding='utf-8').read().split('\n')
head_orig = '\n'.join(lines[0:1099])          # lines 1..1099
geo_line  = lines[1099]                        # line 1100 (inline Japan GeoJSON)
cdn       = '\n'.join(lines[1100:1102])        # leaflet + mdui CDN
data_inner= '\n'.join(lines[1103:1400])        # data script body (idx 1103..1399)
logic_orig= '\n'.join(lines[1401:])            # app logic (idx 1401..)

# ============================================================
# 1. US content data
# ============================================================
# region key -> (display name, ids)
REGIONS_DEF = {
    '東北':   ('東北部', [7,19,21,29,39,45,30,32,38]),
    '中西部': ('中西部', [13,14,22,35,49,15,16,23,25,27,34,41]),
    '南部':   ('南部',   [8,9,10,20,33,40,46,48,51,1,17,24,42,4,18,36,43]),
    '西部':   ('西部',   [3,6,12,26,28,31,44,50,2,5,11,37,47]),
}

# id -> {ja, zh, region, tag, tagja, tagen, food[], spots[], matsuri[]}
S = {}
def st(id, ja, zh, region, tag, tagja, tagen, food, spots, matsuri):
    S[id] = dict(ja=ja, zh=zh, region=region, tag=tag, tagja=tagja, tagen=tagen,
                 food=food, spots=spots, matsuri=matsuri)

st(1,'アラバマ','阿拉巴馬','南部','南方的心臟地帶，火箭之城亨茨維爾與墨西哥灣的海岸。',
   '南部の中心、ロケット都市ハンツビルとメキシコ湾岸。',
   "Heart of the South — the rocket city of Huntsville and the Gulf Coast.",
   ['南方烤肉','蝦仁玉米粥','炸綠番茄','山核桃派'],
   ['太空與火箭中心','蒙哥馬利民權紀念館','墨西哥灣海岸','橡樹山莊園'],
   ['蒙哥馬利爵士音樂節','沙德拉克龍蝦節'])
st(2,'アラスカ','阿拉斯加','西部','極光與冰川的曠野，美國最北的荒野之境。',
   'オーロラと氷河の荒野、アメリカ最北の大自然。',
   "America's northern wilderness of auroras and glaciers.",
   ['帝王蟹','煙燻鮭魚','馴鹿香腸','啤酒燉肉'],
   ['德納利國家公園','冰川灣國家公園','費爾班克斯極光','門登霍爾冰川'],
   ['艾迪塔羅德狗拉雪橇大賽','午夜太陽節'])
st(3,'アリゾナ','亞利桑那','西部','大峽谷與仙人掌的紅色大地，美國西南的荒野之美。',
   'グランドキャニオンとサボテンの赤い大地、南西部の荒野美。',
   "Grand Canyon and saguaro country — the wild beauty of the Southwest.",
   ['墨西哥捲餅','索諾蘭熱狗','炸麵包','仙人掌料理'],
   ['大峽谷國家公園','羚羊峽谷','紀念碑谷','塞多納紅岩'],
   ['菲尼克斯火鳥節','斯科茨代爾藝術節'])
st(4,'アーカンソー','阿肯色','南部','鑽石坑與溫泉之城，歐扎克山丘的南方秘境。',
   'ダイヤモンド坑と温泉都市、オザークの丘陵の秘境。',
   "Diamond mines and hot springs — a hidden corner of the Ozarks.",
   ['起司蘸醬','炸鯰魚','山核桃派','烤雞'],
   ['鑽石坑州立公園','熱泉國家公園','水晶橋美國藝術博物館','歐扎克山'],
   ['小石城河岸節','阿肯色州博覽會'])
st(5,'カリフォルニア','加利福尼亞','西部','從好萊塢到優勝美地，陽光、衝浪與矽谷的黃金之州。',
   'ハリウッドからヨセミテへ、太陽とサーフィンとシリコンバレーの黄金州。',
   "From Hollywood to Yosemite — the Golden State of sun, surf and Silicon Valley.",
   ['酪梨吐司','墨西哥捲餅','In-N-Out 漢堡','納帕葡萄酒'],
   ['優勝美地國家公園','金門大橋','好萊塢標誌','迪士尼樂園'],
   ['玫瑰遊行','科切拉音樂節'])
st(6,'コロラド','科羅拉多','西部','落磯山脈與丹佛高原，滑雪與精釀啤酒之州。',
   'ロッキー山脈とデンバー高原、スキーとクラフトビールの州。',
   "Rocky Mountains and Denver's high plains — skiing and craft beer.",
   ['綠辣椒燉菜','落磯山牡蠣','精釀啤酒','野牛漢堡'],
   ['落磯山國家公園','大沙丘國家公園','紅岩露天劇場','派克斯峰'],
   ['大美國啤酒節','丹佛藝術節'])
st(7,'コネチカット','康乃狄克','東北','新英格蘭的古老殖民地，耶魯大學與海岸小鎮。',
   'ニューイングランドの古い植民地、イェール大学と海辺の町。',
   "An old New England colony — Yale and seaside towns.",
   ['紐黑文白蛤披薩','龍蝦捲','燕麥奶昔'],
   ['耶魯大學','神秘水族館','馬克吐溫之家','海灘小鎮'],
   ['紐黑文披薩節','馬克吐溫國際影展'])
st(8,'デラウェア','德拉瓦','南部','美國第一個州，稅務天堂與大西洋海灘。',
   'アメリカ最初の州、税金の楽園と大西洋のビーチ。',
   "America's first state — tax-free shopping and Atlantic beaches.",
   ['螃蟹濃湯','蘋果派','炸雞'],
   ['瑞和柏斯海灘','溫特圖爾莊園','紐卡斯爾歷史區'],
   ['威明頓花展','德拉瓦州博覽會'])
st(9,'フロリダ','佛羅里達','南部','陽光之州，迪士尼世界與邁阿密海灘的樂園。',
   'サンシャイン州、ディズニーワールドとマイアミビーチの楽園。',
   "The Sunshine State — Disney World and Miami Beach.",
   ['石蟹','古巴三明治','青檸派','柳橙汁'],
   ['迪士尼世界','大沼澤地國家公園','邁阿密南海灘','甘迺迪太空中心'],
   ['邁阿密國際嘉年華','勞德代爾堡國際影展'])
st(10,'ジョージア','喬治亞','南部','桃州與可口可樂的故鄉，亞特蘭大的南方之都。',
   'ピーチ州、コカ・コーラ発祥の地、アトランタの南部の都。',
   "Peach State and home of Coca-Cola — Atlanta, the South's capital.",
   ['桃子派','雞肉鬆餅','亞特蘭大烤肉','可口可樂'],
   ['CNN 中心','奧林匹克百年公園','薩凡納歷史區','石山公園'],
   ['亞特蘭大爵士音樂節','桃節'])
st(11,'ハワイ','夏威夷','西部','火山與威基基海灘，太平洋上的熱帶樂園。',
   '火山とワイキキビーチ、太平洋の熱帯の楽園。',
   "Volcanoes and Waikiki — a tropical Pacific paradise.",
   ['夏威夷蓋飯','羅科莫科','卡盧阿烤豬','彩虹刨冰'],
   ['夏威夷火山國家公園','珍珠港','威基基海灘','哈納公路'],
   ['梅里王節','檀香山馬拉松'])
st(12,'アイダホ','愛達荷','西部','馬鈴薯之州，鋸齒山脈與蛇河的荒野。',
   'じゃがいも州、ソートゥース山脈とスネーク川の荒野。',
   "Potato state — the Sawtooths and the Snake River wilderness.",
   ['烤馬鈴薯','彩虹鱒魚','蕎麥煎餅','冰激凌馬鈴薯'],
   ['鋸齒國家休閒區','月面火山口','蛇河峽谷','黃石公園西口'],
   ['愛達荷馬鈴薯節','愛達荷州博覽會'])
st(13,'イリノイ','伊利諾','中西部','芝加哥的摩天大樓與深盤披薩，林肯之鄉。',
   'シカゴの摩天楼とディープディッシュピザ、リンカーンの故郷。',
   "Chicago's skyline and deep-dish pizza — Lincoln's homeland.",
   ['深盤披薩','芝加哥熱狗','義大利牛肉三明治','爆米花'],
   ['千禧公園','威利斯大厦','芝加哥藝術學院','海軍碼頭'],
   ['芝加哥美食節','芝加哥藍調音樂節'])
st(14,'インディアナ','印第安納','中西部','印地500賽車與玉米田，美國中西部的中心。',
   'インディ500とトウモロコシ畑、中西部の中心。',
   "Indy 500 and cornfields — the heart of the Midwest.",
   ['玉米粥','豬肉嫩排','糖奶油派'],
   ['印地安納波利斯賽車場','印第安納沙丘國家公園','印地安納波利斯動物園'],
   ['印地安納波利斯 500'])
st(15,'アイオワ','愛荷華','中西部','玉米之州，州博覽會與無盡的農田。',
   'トウモロコシ州、州博覧会と果てしない農地。',
   "Corn country — the State Fair and endless farmland.",
   ['玉米熱狗','豬里脊三明治','乳酪凝塊','蘋果派'],
   ['愛荷華州博覽會','岩架州立公園','密西西比河'],
   ['愛荷華州博覽會'])
st(16,'カンザス','堪薩斯','中西部','堪薩斯城烤肉與大草原，美國的地理中心。',
   'カンザスシティのバーベキューと大草原、アメリカの地理的中心。',
   "Kansas City BBQ and prairies — America's geographic center.",
   ['堪薩斯城烤肉','炸雞','桃子酥'],
   ['堪薩斯州議會大廈','女巫之家','花卉山公園','多德城'],
   ['堪薩斯城烤肉節'])
st(17,'ケンタッキー','肯塔基','南部','肯塔基德比與波本威士忌，藍草之鄉。',
   'ケンタッキーダービーとバーボンウイスキー、ブルーグラスの郷。',
   "Kentucky Derby and bourbon — the Bluegrass State.",
   ['肯塔基炸雞','波本威士忌','德比派','熱布朗三明治'],
   ['丘吉爾唐斯賽馬場','猛獁洞穴國家公園','波本小徑','藍草音樂公園'],
   ['肯塔基德比','波本美食節'])
st(18,'ルイジアナ','路易斯安那','南部','新奧爾良爵士樂與狂歡節，法國區的南方魔幻。',
   'ニューオーリンズのジャズとマルディグラ、フレンチクォーターの魔法。',
   "New Orleans jazz and Mardi Gras — the magic of the French Quarter.",
   ['秋葵濃湯','克里奧爾料理','貝奈特餅','小龍蝦飯'],
   ['法國區','傑克遜廣場','沼澤生態遊','花園區'],
   ['狂歡節','新奧爾良爵士音樂節'])
st(19,'メイン','緬因','東北','龍蝦與燈塔的海岸之州，阿卡迪亞國家公園。',
   'ロブスターと灯台の海辺の州、アカディア国立公園。',
   "Lobsters and lighthouses — Acadia's coast.",
   ['龍蝦捲','蛤蜊濃湯','藍莓派'],
   ['阿卡迪亞國家公園','波特蘭燈塔','巴爾港'],
   ['緬因龍蝦節'])
st(20,'メリーランド','馬里蘭','南部','藍蟹之州，安納波利斯與切薩皮克灣。',
   'ブルークラブの州、アナポリスとチェサピーク湾。',
   "Blue crabs, Annapolis and the Chesapeake Bay.",
   ['馬里蘭藍蟹','蟹餅','舊灣調味料'],
   ['國家水族館','安納波利斯','巴爾的摩內港','阿薩蒂格島'],
   ['馬里蘭文藝復興節','螃蟹節'])
st(21,'マサチューセッツ','麻薩諸塞','東北','波士頓茶黨與哈佛大學，新英格蘭的歷史之心。',
   'ボストン茶会事件とハーバード、ニューイングランドの歴史の中心。',
   "Boston Tea Party and Harvard — New England's historic heart.",
   ['蛤蜊濃湯','波士頓烤豆','奶油麵包捲','楓糖甜甜圈'],
   ['自由之路','哈佛大學','芬威球場','鱈魚角'],
   ['波士頓馬拉松','波士頓愛國者節'])
st(22,'ミシガン','密西根','中西部','五大湖與汽車之都底特律，櫻桃與湖岸風景。',
   '五大湖と自動車の都デトロイト、さくらんぼと湖岸の風景。',
   "Great Lakes and Motor City Detroit — cherries and shoreline.",
   ['康尼熱狗','底特律方形披薩','櫻桃派'],
   ['麥基諾島','底特律文藝復興中心','睡熊沙丘國家湖岸','底特律河'],
   ['國家櫻桃節','底特律電子音樂節'])
st(23,'ミネソタ','明尼蘇達','中西部','萬湖之州，明尼阿波利斯與雙城文化。',
   '湖の州、ミネアポリスとツインシティーズの文化。',
   "Land of 10,000 Lakes — Minneapolis and Twin Cities culture.",
   ['熱菜砂鍋','野米湯','盧特菲斯克','芝士凝塊'],
   ['明尼哈哈瀑布','美國購物中心','邊界水域獨木舟區','瓦爾登湖'],
   ['明尼蘇達州博覽會','雙城國際影展'])
st(24,'ミシシッピ','密西西比','南部','藍調音樂的故鄉，密西西比河與南方小鎮。',
   'ブルース発祥の地、ミシシッピ川と南部の小さな町。',
   "Birthplace of the blues — the Mississippi River and Southern towns.",
   ['鯰魚料理','秋葵濃湯','脆炸雞'],
   ['比洛克西海岸','維克斯堡國家軍事公園','三角洲藍調博物館','納奇茲歷史步道'],
   ['三角洲藍調音樂節'])
st(25,'ミズーリ','密蘇里','中西部','聖路易斯拱門與堪薩斯城烤肉，密西西比河畔。',
   'セントルイスの大アーチとカンザスシティのBBQ、ミシシッピ川沿い。',
   "Gateway Arch and Kansas City BBQ on the Mississippi.",
   ['聖路易斯排骨','烤豬排','冰淇淋蛋糕','烤肋排'],
   ['大拱門','布蘭森','銀元城','聖路易斯動物園'],
   ['聖路易斯爵士音樂節'])
st(26,'モンタナ','蒙大拿','西部','冰川國家公園與大天空之州，黃石的北方入口。',
   'グレイシャー国立公園とビッグスカイ州、イエローストーンの北の玄関。',
   "Glacier National Park and Big Sky — Yellowstone's northern gate.",
   ['野牛肉','煙燻鹿肉','莓果派','牧場豆'],
   ['冰川國家公園','黃石國家公園北口','平頭湖'],
   ['蒙大拿州博覽會'])
st(27,'ネブラスカ','內布拉斯加','中西部','玉米殼之州，開闊平原與先驅者之路。',
   'コーンハスカー州、開けた平原と開拓者の道。',
   "Cornhusker State — open plains and pioneer trails.",
   ['Runza 肉餡麵包','玉米','烤牛排','起司凝塊'],
   ['斯科茨布拉夫國家紀念碑','亨利多利動物園','先驅者村','內布拉斯加歷史協會'],
   ['內布拉斯加博覽會'])
st(28,'ネバダ','內華達','西部','拉斯維加斯與大盆地，沙漠中的不夜城。',
   'ラスベガスとグレートベースン、砂漠の眠らない街。',
   "Las Vegas and the Great Basin — the desert that never sleeps.",
   ['豪華自助餐','蝦雞尾酒','地道墨西哥菜','牛排晚餐'],
   ['拉斯維加斯大道','胡佛水壩','紅岩峽谷','大峽谷西緣'],
   ['拉斯維加斯電子音樂節','燃燒人節'])
st(29,'ニューハンプシャー','新罕布夏','東北','楓葉與白山山脈，新英格蘭的戶外天堂。',
   '紅葉とホワイト山脈、ニューイングランドのアウトドア天国。',
   "Fall foliage and the White Mountains — New England outdoors.",
   ['楓糖漿','蘋果酒甜甜圈','龍蝦'],
   ['白山國家森林','弗蘭科尼亞山口','朴茨茅斯港','湖區'],
   ['新罕布夏楓糖節'])
st(30,'ニュージャージー','紐澤西','東北','澤西海岸與自由女神對岸，花園之州。',
   'ジャージー海岸と自由の女神の対岸、ガーデン州。',
   "Jersey Shore and the Statue of Liberty's neighbor — the Garden State.",
   ['豬肉捲','鹽水太妃糖','披薩派'],
   ['大西洋城木板路','自由州立公園','開普梅','六旗大冒險'],
   ['澤西海岸熱狗節'])
st(31,'ニューメキシコ','新墨西哥','西部','聖塔菲藝術與綠辣椒，西南原住民文化。',
   'サンタフェの芸術とグリーンチリ、南西部の先住民文化。',
   "Santa Fe art and green chile — Native Southwest culture.",
   ['綠辣椒燉菜','墨西哥玉米餅','藍玉米捲','納瓦霍炸麵包'],
   ['卡爾斯巴德洞穴國家公園','白沙國家公園','陶斯普韋布洛','阿爾伯克基熱氣球節'],
   ['國際熱氣球節','聖塔菲西班牙市場'])
st(32,'ニューヨーク','紐約','東北','紐約市與尼亞加拉大瀑布，世界的十字路口。',
   'ニューヨーク市とナイアガラの滝、世界の交差点。',
   "New York City and Niagara Falls — the crossroads of the world.",
   ['紐約披薩','貝果','起司蛋糕','熱狗'],
   ['自由女神像','時代廣場','中央公園','尼亞加拉大瀑布'],
   ['梅西感恩節大遊行','時代廣場跨年'])
st(33,'ノースカロライナ','北卡羅來納','南部','藍嶺山脈與外灘群島，從海灘到高山。',
   'ブルーリッジ山脈とアウターバンクス、ビーチから高山へ。',
   "Blue Ridge and the Outer Banks — from beaches to peaks.",
   ['卡羅來納烤肉','Krispy Kreme 甜甜圈','油炸牡蠣','葡萄汁'],
   ['大煙山國家公園','藍嶺公園大道','外灘燈塔','夏洛特賽車道'],
   ['夏洛特賽車節','藍嶺美食節'])
st(34,'ノースダコタ','北達科他','中西部','西奧多·羅斯福的荒原，大平原之州。',
   'セオドア・ルーズベルトの荒野、大平原の州。',
   "Theodore Roosevelt's badlands — the Great Plains state.",
   ['野牛漢堡','雪諾','起司凝塊'],
   ['西奧多·羅斯福國家公園','法戈','邁諾特','國際和平花園'],
   ['北達科他州博覽會'])
st(35,'オハイオ','俄亥俄','中西部','搖滾名人堂與七位總統，中西部的搖滾之都。',
   'ロックの殿堂と7人の大統領、中西部のロックの都。',
   "Rock & Roll Hall of Fame and seven presidents — Ohio.",
   ['辛辛那提辣椒','高級烤芝士','波蘭香腸','冰激凌蘇打'],
   ['搖滾名人堂','辛辛那提動物園','霍克馬洛克','七葉樹州立公園'],
   ['搖滾名人堂音樂節','辛辛那提美食節'])
st(36,'オクラホマ','奧克拉荷馬','南部','牛仔與原住民文化，66號公路的心臟地帶。',
   'カウボーイと先住民文化、ルート66の心臓部。',
   "Cowboys and Native heritage — the heart of Route 66.",
   ['雞肉炸牛排','烤肉','山核桃','炸秋葵'],
   ['國家牛仔博物館','塔爾薩','俄克拉荷馬城國家紀念館','66號公路'],
   ['俄克拉荷馬牛仔節'])
st(37,'オレゴン','奧勒岡','西部','火山口湖與海岸線，波特蘭的咖啡與綠意。',
   'クレーターレイクと海岸線、ポートランドのコーヒーと緑。',
   "Crater Lake and coastline — Portland's coffee and green.",
   ['馬里恩莓派','波特蘭食物車','風琴土豆','精釀啤酒'],
   ['火山口湖國家公園','哥倫比亞河峽谷','波特蘭日本花園','坎農海灘'],
   ['波特蘭玫瑰節'])
st(38,'ペンシルベニア','賓夕法尼亞','東北','費城獨立廳與阿米什社區，美國建國之地。',
   'フィラデルフィア独立記念館とアーミッシュ、建国の地。',
   "Independence Hall and the Amish — where America was born.",
   ['費城起司牛排','軟椒鹽卷餅','刮刮餅','荷蘭蘋果派'],
   ['獨立廳','自由鐘','赫希巧克力世界','匹茲堡'],
   ['費城花展','費城美食節'])
st(39,'ロードアイランド','羅德島','東北','美國最小的州，紐波特豪宅與海灘。',
   'アメリカ最小の州、ニューポートの豪邸とビーチ。',
   "America's smallest state — Newport mansions and beaches.",
   ['咖啡牛奶','蛤蜊派','紐波特龍蝦'],
   ['紐波特豪宅','普羅維登斯','布洛克島','懸崖步道'],
   ['紐波特爵士音樂節'])
st(40,'サウスカロライナ','南卡羅來納','南部','查爾斯頓南方魅力與希爾頓黑德海灘。',
   'チャールストンの南部の魅力とヒルトンヘッドのビーチ。',
   "Charleston charm and Hilton Head beaches.",
   ['什錦飯','低地料理','炸秋葵','海鮮鍋'],
   ['查爾斯頓歷史區','希爾頓黑德島','麥爾托海灘','雷文內爾橋'],
   ['查爾斯頓美食美酒節'])
st(41,'サウスダコタ','南達科他','中西部','拉什莫爾山與惡地國家公園，總統與荒野。',
   'ラシュモア山とバッドランズ国立公園、大統領と荒野。',
   "Mount Rushmore and Badlands — presidents and wilderness.",
   ['水牛漢堡','印第安炸麵包','雲杉果'],
   ['拉什莫爾山','惡地國家公園','風洞國家公園','蘇福爾斯'],
   ['斯特吉斯摩托車集會'])
st(42,'テネシー','田納西','南部','納什維爾鄉村音樂與孟菲斯藍調，音樂之州。',
   'ナッシュビルのカントリーとメンフィスのブルース、音楽の州。',
   "Nashville country and Memphis blues — the Music State.",
   ['納什維爾辣炸雞','孟菲斯烤肉','貓王三明治'],
   ['鄉村音樂名人堂','大煙山國家公園','格雷斯蘭','百老匯大街'],
   ['CMT 音樂節','孟菲斯五月節'])
st(43,'テキサス','德克薩斯','南部','德州烤肉與牛仔文化，阿拉莫的孤星之州。',
   'テキサスBBQとカウボーイ文化、アラモのローンスター州。',
   "Texas BBQ and cowboy culture — the Lone Star State.",
   ['德州烤肉','墨西哥捲餅','恰克牛排','德州辣椒'],
   ['阿拉莫','太空中心休斯頓','大彎國家公園','聖安東尼奧河濱步道'],
   ['休斯頓牛仔節','奧斯汀 SXSW'])
st(44,'ユタ','猶他','西部','五座國家公園與紅岩奇景，鹽湖城的摩門聖地。',
   '5つの国立公園と赤い岩、ソルトレイクシティのモルモンの聖地。',
   "Five national parks and red rock — Salt Lake City's Mormon heart.",
   ['炸雞牛排','綠辣椒','摩門捲','蜂蜜'],
   ['拱門國家公園','布萊斯峽谷','錫安國家公園','鹽湖城聖殿廣場'],
   ['桑丹斯電影節','鹽湖城先驅者日'])
st(45,'バーモント','佛蒙特','東北','楓糖漿與綠山山脈，秋葉最美的州。',
   'メープルシロップとグリーン山脈、紅葉が最も美しい州。',
   "Maple syrup and the Green Mountains — the prettiest autumn.",
   ['楓糖漿','切達乾酪','蘋果酒','楓糖核桃冰淇淋'],
   ['斯托滑雪場','尚普蘭湖','伯靈頓','綠山國家森林'],
   ['楓糖狂歡節','佛蒙特楓糖節'])
st(46,'バージニア','維吉尼亞','南部','總統之州，威廉斯堡與藍嶺山脈。',
   '大統領の州、ウィリアムズバーグとブルーリッジ山脈。',
   "State of presidents — Williamsburg and the Blue Ridge.",
   ['維吉尼亞火腿','花生','藍蟹','蘋果酒'],
   ['雪蘭多國家公園','威廉斯堡','藍嶺公園大道','里士滿'],
   ['弗吉尼亞葡萄酒節','里士滿歷史節'])
st(47,'ワシントン','華盛頓','西部','西雅圖咖啡與雷尼爾山，翡翠之州。',
   'シアトルのコーヒーとレーニア山、エメラルド州。',
   "Seattle coffee and Mount Rainier — the Evergreen State.",
   ['海鮮濃湯','咖啡','蘋果派','煙燻鮭魚'],
   ['雷尼爾山國家公園','奧林匹克國家公園','太空針塔','派克市場'],
   ['西雅圖國際影展','華盛頓蘋果節'])
st(48,'ウェストバージニア','西維吉尼亞','南部','山脈之州，新河峽谷與戶外探險。',
   '山の州、ニューリバーゴージとアウトドア冒険。',
   "Mountain State — New River Gorge and outdoor adventure.",
   ['佩珀羅尼捲','山毛櫸火腿','炸雞'],
   ['新河峽谷大橋','雪尼多國家森林','哈珀斯費里','黑水瀑布'],
   ['山地州博覽會'])
st(49,'ウィスコンシン','威斯康辛','中西部','起司與啤酒之州，密爾瓦基與五大湖。',
   'チーズとビールの州、ミルウォーキーと五大湖。',
   "Cheese and beer — Milwaukee and the Great Lakes.",
   ['起司凝塊','德式香腸','奶油乳酪','薄脆披薩'],
   ['密爾瓦基美術館','魔鬼湖州立公園','威斯康辛州議會大廈'],
   ['密爾瓦基夏季音樂節','起司節'])
st(50,'ワイオミング','懷俄明','西部','黃石國家公園與大提頓，牛仔之州。',
   'イエローストーンとグランドティトン、カウボーイの州。',
   "Yellowstone and Grand Teton — cowboy country.",
   ['野牛漢堡','煙燻鹿肉','牧場豆','黃石鱒魚'],
   ['黃石國家公園','大提頓國家公園','魔鬼塔','傑克遜霍爾'],
   ['夏安邊疆日','傑克遜霍爾藝術節'])
st(51,'コロンビア特別区','哥倫比亞特區','南部','美國首都，史密森尼博物館與國家廣場。',
   'アメリカの首都、スミソニアン博物館とナショナルモール。',
   "America's capital — Smithsonian museums and the National Mall.",
   ['半煙燻香腸','木莓肉餅','媽媽米','羊肉三明治'],
   ['國家廣場','白宮','國會大廈','史密森尼博物館'],
   ['國家櫻花節','七月四日國慶煙火'])

EN_NAMES = {1:'Alabama',2:'Alaska',3:'Arizona',4:'Arkansas',5:'California',6:'Colorado',
7:'Connecticut',8:'Delaware',9:'Florida',10:'Georgia',11:'Hawaii',12:'Idaho',13:'Illinois',
14:'Indiana',15:'Iowa',16:'Kansas',17:'Kentucky',18:'Louisiana',19:'Maine',20:'Maryland',
21:'Massachusetts',22:'Michigan',23:'Minnesota',24:'Mississippi',25:'Missouri',26:'Montana',
27:'Nebraska',28:'Nevada',29:'New Hampshire',30:'New Jersey',31:'New Mexico',32:'New York',
33:'North Carolina',34:'North Dakota',35:'Ohio',36:'Oklahoma',37:'Oregon',38:'Pennsylvania',
39:'Rhode Island',40:'South Carolina',41:'South Dakota',42:'Tennessee',43:'Texas',44:'Utah',
45:'Vermont',46:'Virginia',47:'Washington',48:'West Virginia',49:'Wisconsin',50:'Wyoming',
51:'District of Columbia'}

WH_PREFS = [2,3,4,5,6,9,11,12,14,17,19,22,23,25,26,28,31,33,34,35,37,40,41,42,43,44,46,47,48,50]

# levels: (name, icon, pts, pct, ja, en)
LEVELS = [
 ('初到美洲','🗽',0,'2.9%','アメリカ到着','Fresh in America'),
 ('東岸旅人','🍎',10,'0.8%','東海岸の旅人','East Coast Traveler'),
 ('公路行者','🛣️',30,'0.7%','ロードトリッパー','Road Tripper'),
 ('國家公園愛好者','🏞️',70,'10.7%','国立公園ラバー','National Park Lover'),
 ('美食獵人','🍔',130,'42%','グルメハンター','Foodie Hunter'),
 ('音樂旅人','🎸',210,'32.1%','音楽の旅人','Music Traveler'),
 ('美國通','🦅',310,'9.2%','アメリカ通','America Connoisseur'),
 ('州際獵人','🤠',430,'1.3%','州ハンター','State Hunter'),
 ('美國制霸者','🎇',580,'0.2%','アメリカ制覇者','America Conqueror'),
 ('傳說的旅人','🌟',750,'0.1%','伝説の旅人','Legendary Traveler'),
]

# achievements: (id, cat, icon, name_zh, name_ja, name_en, pts, kind, data)
#   kind 'groups': data=(ids_list, minLevel)   (single inner group)
#   kind 'count':  data=(prefs, level, n)
#   kind 'manual': data=(prefs, level)
ALL_IDS = list(range(1,52))
ACH = [
 ('A01','絕景','🏞️','國家公園巡禮','国立公園巡り','National Park Pilgrimage',20,'count',(WH_PREFS,2,5)),
 ('A02','絕景','🏜️','大峽谷與紅岩','グランドキャニオンと赤い岩','Grand Canyon & Red Rocks',18,'groups',([3,44],2)),
 ('A03','絕景','🌋','火山國度','火山の国','Volcanic Lands',15,'groups',([11,37],2)),
 ('A04','絕景','❄️','阿拉斯加極光','アラスカのオーロラ','Alaskan Aurora',18,'groups',([2],3)),
 ('A05','絕景','⛰️','優勝美地','ヨセミテ','Yosemite',12,'groups',([5],2)),
 ('A06','絕景','🍁','新英格蘭紅葉','ニューイングランドの紅葉','New England Foliage',16,'groups',([19,29,45,7],2)),
 ('A07','自然','🐻','黃石三州','イエローストーン三州','Yellowstone Tri-State',16,'groups',([50,26,12],2)),
 ('A08','自然','🌊','五大湖之旅','五大湖の旅','Great Lakes Journey',16,'groups',([22,49,13,35],2)),
 ('A09','自然','🏔️','落磯山脈','ロッキー山脈','Rocky Mountains',14,'groups',([6,26,50],2)),
 ('A10','自然','🐊','沼澤濕地','沼沢地','Swamps & Wetlands',12,'groups',([9,18],2)),
 ('A11','自然','🌾','大平原','大平原','Great Plains',14,'groups',([34,41,15,16],2)),
 ('A12','自然','🏜️','沙漠奇景','砂漠の絶景','Desert Wonders',16,'groups',([31,28,44,3],2)),
 ('A13','公路旅行','🛣️','66號公路','ルート66','Route 66',18,'groups',([13,25,36,31,3],2)),
 ('A14','公路旅行','🌉','美西縱貫','アメリカ西海岸縦断','West Coast Traverse',18,'groups',([47,37,5,28,3],2)),
 ('A15','公路旅行','🗽','美東縱貫','アメリカ東海岸縦断','East Coast Traverse',18,'groups',([19,21,32,38,46],2)),
 ('A16','公路旅行','🛤️','藍嶺公園大道','ブルーリッジ・パークウェイ','Blue Ridge Parkway',12,'groups',([46,33],2)),
 ('A17','美食','🍖','南方烤肉','南部バーベキュー','Southern BBQ',16,'groups',([42,43,16,25],2)),
 ('A18','美食','🦞','龍蝦盛宴','ロブスター三昧','Lobster Feast',14,'groups',([19,21,39],2)),
 ('A19','美食','🌮','西南風味','南西部フレーバー','Southwest Flavors',14,'groups',([43,31,3],2)),
 ('A20','文化','🏛️','美國建國之地','アメリカ建国の地','Birthplace of America',16,'groups',([21,38,46,20],2)),
 ('A21','文化','🗽','自由與獨立','自由と独立','Liberty & Independence',15,'groups',([32,38],2)),
 ('A22','文化','🏛️','華盛頓特區','ワシントンD.C.','Washington D.C.',12,'groups',([51],2)),
 ('A23','文化','🚀','太空探索','宇宙探査','Space Exploration',14,'groups',([1,9,43],2)),
 ('A24','音樂','🎸','鄉村之都','カントリーの都','Country Capital',10,'groups',([42],2)),
 ('A25','音樂','🎺','爵士藍調','ジャズとブルース','Jazz & Blues',14,'groups',([18,42],2)),
 ('A26','音樂','🎹','搖滾名人堂','ロックの殿堂','Rock & Roll Hall of Fame',10,'groups',([35],2)),
 ('A27','音樂','🎤','音樂之城三連星','音楽の都トリオ','Music City Trio',16,'groups',([42,18,35],2)),
 ('A28','運動','🏈','超級碗','スーパーボウル','Super Bowl',14,'groups',([43,9,5],2)),
 ('A29','影劇','🎬','好萊塢','ハリウッド','Hollywood',12,'groups',([5],2)),
 ('A30','影劇','🏰','迪士尼雙城','ディズニー二大リゾート','Disney Double',16,'groups',([9,5],2)),
 ('A31','影劇','🎰','賭城之夜','ラスベガスの夜','Vegas Night',12,'groups',([28],3)),
 ('A32','歷史','🏛️','南方歷史','南部の歴史','Southern History',12,'groups',([10,40,46],2)),
 ('A33','歷史','🤠','牛仔與邊疆','カウボーイと辺境','Cowboys & Frontier',14,'groups',([43,36,50,41],2)),
 ('A34','歷史','🏰','殖民十三州','13植民地','Thirteen Colonies',25,'groups',([7,8,20,21,29,30,32,33,38,39,40,46,51],2)),
 ('A35','歷史','🦅','總統之路','大統領の道','Presidential Trail',12,'groups',([46,35,43,13],2)),
 ('A36','文化','🎇','完全制霸','完全制覇','Complete Conquest',60,'manual',(ALL_IDS,1)),
 ('A37','文化','🚗','五州之旅','五州の旅','Five States',8,'count',(ALL_IDS,1,5)),
 ('A38','文化','🚗','十州之旅','十州の旅','Ten States',14,'count',(ALL_IDS,1,10)),
 ('A39','文化','🚗','二十州之旅','二十州の旅','Twenty States',22,'count',(ALL_IDS,1,20)),
 ('A40','文化','🚗','三十州之旅','三十州の旅','Thirty States',30,'count',(ALL_IDS,1,30)),
]

ACH_CATS = ['全部','絕景','美食','文化','自然','運動','音樂','歷史','影劇','公路旅行']

# extended traditional->simplified mapping (chars missing from original T2S)
T2S_EXT = {}
for ch in '羅薩喬亞遜維爾紐澤蘇納達頓蘭華懷緬岡賓猶倫楓漿捲餅塊鱈鰻龍蝦燈貓蘋濃熱雞蓋盧豬鱒蕎盤藝碼賽獁徑傑歡節復黨櫻鍋鯰煙燻覽殼餡驅壩緣險燉韋蠣灘邁樹釀軟廳茲懸錦橋惡匯彎濱錫滿鮭櫸宮慶臟帶檸穀禮峽極勝葉磯脈濕貫嶺獨搖滾級萊塢賭統劃':
    T2S_EXT[ch] = ch  # placeholder, filled below
T2S_EXT.update({
 '羅':'罗','薩':'萨','喬':'乔','亞':'亚','遜':'逊','維':'维','爾':'尔','紐':'纽','澤':'泽',
 '蘇':'苏','納':'纳','達':'达','頓':'顿','蘭':'兰','華':'华','懷':'怀','緬':'缅','岡':'冈',
 '賓':'宾','猶':'犹','倫':'伦','楓':'枫','漿':'浆','捲':'卷','餅':'饼','塊':'块','鱈':'鳕',
 '鰻':'鳗','龍':'龙','蝦':'虾','燈':'灯','貓':'猫','蘋':'苹','濃':'浓','熱':'热','雞':'鸡',
 '蓋':'盖','盧':'卢','豬':'猪','鱒':'鳟','蕎':'荞','盤':'盘','藝':'艺','碼':'码','賽':'赛',
 '獁':'犸','徑':'径','傑':'杰','歡':'欢','節':'节','復':'复','黨':'党','櫻':'樱','鍋':'锅',
 '鯰':'鲶','煙':'烟','燻':'熏','覽':'览','殼':'壳','餡':'馅','驅':'驱','壩':'坝','緣':'缘',
 '險':'险','燉':'炖','韋':'韦','蠣':'蛎','灘':'滩','邁':'迈','樹':'树','釀':'酿','軟':'软',
 '廳':'厅','茲':'兹','懸':'悬','錦':'锦','橋':'桥','惡':'恶','匯':'汇','彎':'弯','濱':'滨',
 '錫':'锡','滿':'满','鮭':'鲑','櫸':'榉','宮':'宫','慶':'庆','臟':'脏','帶':'带','檸':'柠',
 '穀':'谷','禮':'礼','峽':'峡','極':'极','勝':'胜','葉':'叶','磯':'矶','脈':'脉','濕':'湿',
 '貫':'贯','嶺':'岭','獨':'独','搖':'摇','滾':'滚','級':'级','萊':'莱','塢':'坞','賭':'赌',
 '統':'统','劃':'划','麼':'么','們':'们','巖':'岩','灣':'湾','騎':'骑','鵝':'鹅','鶴':'鹤',
 '諸':'诸','該':'该','還':'还','複':'复','製':'制','彙':'汇','檔':'档','絕':'绝','標':'标',
 '註':'注','譯':'译','錄':'录','階':'阶','攔':'拦','嚴':'严','勵':'励','綁':'绑','遺':'遗',
 '產':'产','觀':'观','點':'点','選':'选','單':'单','連':'连','遠':'远','鎮':'镇','鎖':'锁',
 '頭':'头','觸':'触','暫':'暂','確':'确','誤':'误','讀':'读','課':'课','議':'议','貼':'贴',
})

# ============================================================
# 2. helpers
# ============================================================
def js_str(o):
    return json.dumps(o, ensure_ascii=False)

def to_simplified(s, t2s):
    return ''.join(t2s.get(c, c) for c in s)

def usify(s):
    s = s.replace('都道府縣','州').replace('縣市','州').replace('縣','州')
    s = s.replace('日本','美國').replace('JAPAN_GEOJSON','USA_GEOJSON').replace('JPN','USA')
    s = s.replace('japanMap','usaMap').replace('jp_lang','us_lang').replace('dataofjapan','PublicaMundi')
    s = s.replace(' / 47',' / 51').replace('/47','/51').replace('47','51')
    s = s.replace(' / 8',' / 4').replace('/8','/4')
    return s

# ============================================================
# 3. parse original I18N
# ============================================================
def parse_js_obj(text):
    """Parse a JS object literal with double-quoted string keys/values."""
    pairs = re.findall(r'"((?:[^"\\]|\\.)*)"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
    out = {}
    for k, v in pairs:
        try:
            out[json.loads('"' + k + '"')] = json.loads('"' + v + '"')
        except Exception:
            pass
    return out

m_i18n = re.search(r'const I18N = \{(.*?)\n\};', data_inner, re.S)
assert m_i18n, 'I18N block not found'
i18n_blk = m_i18n.group(0)
ORIG_I18N = {}
for lang in ['zh-Hans','ja','en']:
    lm = re.search(r"'" + lang + r"':\{(.*?)\}", i18n_blk, re.S)
    assert lm, lang
    ORIG_I18N[lang] = parse_js_obj(lm.group(1))

# parse original T2S
m_t2s = re.search(r'const T2S = \{(.*?)\};', data_inner, re.S)
assert m_t2s
T2S_ORIG = parse_js_obj(m_t2s.group(1))
T2S = dict(T2S_ORIG)
T2S.update(T2S_EXT)

# ============================================================
# 4. build new I18N
# ============================================================
def build_cond(ids, lv):
    names = [S[i]['zh'] for i in ids]
    LV = {1:'途經',2:'遊玩',3:'住宿',4:'長居'}
    if len(ids) == 1:
        return names[0] + '「' + LV[lv] + '」以上'
    if len(ids) == 2:
        return names[0] + '＋' + names[1] + '皆「' + LV[lv] + '」以上'
    return '・'.join(names) + '皆「' + LV[lv] + '」以上'

def cond_ja(ids, lv):
    names = [S[i]['ja'] for i in ids]
    LV = {1:'通過',2:'観光',3:'宿泊',4:'長期滞在'}
    if len(ids) == 1:
        return names[0] + '「' + LV[lv] + '」以上'
    if len(ids) == 2:
        return names[0] + 'と' + names[1] + '、すべて「' + LV[lv] + '」以上'
    return '・'.join(names) + '、すべて「' + LV[lv] + '」以上'

def cond_en(ids, lv):
    names = [EN_NAMES[i] for i in ids]
    LV = {1:'Pass',2:'Sightseeing',3:'Stay',4:'Long Stay'}
    if len(ids) == 1:
        return names[0] + ' "' + LV[lv] + '" or above'
    if len(ids) == 2:
        return names[0] + ' & ' + names[1] + ' both "' + LV[lv] + '" or above'
    return ', '.join(names) + ' all "' + LV[lv] + '" or above'

# collect new keys: {key: {'zh-Hans':v,'ja':v,'en':v}}
NEW = {}
def add_key(key, zh_s, ja, en):
    NEW[key] = {'zh-Hans': zh_s, 'ja': ja, 'en': en}

# region names
for rk, (nm, ids) in REGIONS_DEF.items():
    add_key(nm, to_simplified(nm, T2S),
            {'東北部':'北東部','中西部':'中西部','南部':'南部','西部':'西部'}[nm],
            {'東北部':'Northeast','中西部':'Midwest','南部':'South','西部':'West'}[nm])

# level names
for (nm, icon, pts, pct, ja, en) in LEVELS:
    add_key(nm, to_simplified(nm, T2S), ja, en)

# achievement names + conds
for (aid, cat, icon, nm, nmja, nmen, pts, kind, data) in ACH:
    add_key(nm, to_simplified(nm, T2S), nmja, nmen)
    if kind == 'groups':
        ids, lv = data
        cond = build_cond(ids, lv)
        add_key(cond, to_simplified(cond, T2S), cond_ja(ids, lv), cond_en(ids, lv))
    elif kind == 'count':
        prefs, lv, n = data
        if prefs == WH_PREFS:
            cond = '主要國家公園 5 州「遊玩」以上'
            add_key(cond, '主要国家公园 5 州「游玩」以上',
                    '主要国立公園 5 州「観光」以上',
                    '5 states with major national parks "Sightseeing" or above')
        else:
            cond = str(n) + ' 州以上「途經」以上'
            add_key(cond, str(n) + ' 州以上「途经」以上',
                    str(n) + '州以上「通過」以上',
                    str(n) + '+ states "Pass" or above')
    elif kind == 'manual':
        cond = '51 州皆「途經」以上，且手動勾選'
        add_key(cond, '51 州皆「途经」以上，且手动勾选',
                '51州すべて「通過」以上、かつ手動チェック',
                'All 51 states "Pass" or above (manual)')

# categories
add_key('音樂','音乐','音楽','Music')
add_key('公路旅行','公路旅行','ロードトリップ','Road Trip')
add_key('歷史','历史','歴史','History')

# taglines
for i in range(1, 52):
    st = S[i]
    add_key(st['tag'], to_simplified(st['tag'], T2S), st['tagja'], st['tagen'])

# state names (for t(p.zh) in wishlist / timeline / reports)
for i in range(1, 52):
    st = S[i]
    add_key(st['zh'], to_simplified(st['zh'], T2S), st['ja'], EN_NAMES[i])
add_key('造訪州', '造访州', '訪問州', 'Visited')

# new UI keys
add_key('搜尋州（中文／英文／日文／地區）','搜索州（中文／英文／日文／地区）',
        '州を検索（中文／英文／日本語／地域）','Search states (中文 / English / 日本語 / region)')
add_key('· 主要國家公園 5 州','· 主要国家公园 5 州','· 主要国立公園 5 州','· 5 states with major national parks')
add_key('· 芝加哥到洛杉磯','· 芝加哥到洛杉矶','· シカゴからロサンゼルスへ','· Chicago to Los Angeles')
add_key('· 十三州殖民先驅','· 十三州殖民先驱','· 13植民地の先駆け','· The original 13 colonies')
add_key('· 51 州全制霸（手動勾選）','· 51 州全制霸（手动勾选）','· 51州すべて制覇（手動チェック）','· All 51 states (manual)')

# overrides for keys whose mechanical translation is wrong
OVERRIDES = {
 'zh-Hans': {
   '美國':'美国',
   '州':'州',
   '州市':'州市',
 },
 'ja': {
   '美國':'アメリカ',
   '州':'州',
 },
 'en': {
   '美國':'America',
   '州':'state',
 },
}

def transform_dict(d, lang):
    out = {}
    for k, v in d.items():
        nk = usify(k)
        nv = usify(v)
        if lang == 'zh-Hans':
            nv = (nv.replace('都道府县市','州').replace('都道府县','').replace('都道府','')
                    .replace('县市','州').replace('县','州'))
            nv = to_simplified(nv, T2S)
        elif lang == 'ja':
            nv = nv.replace('都道府県','州').replace('県','州')
        elif lang == 'en':
            nv = (nv.replace('Prefectures','States').replace('prefectures','states')
                    .replace('Prefecture','State').replace('prefecture','state')
                    .replace('pref.','state').replace('Japan','America'))
        out[nk] = nv
    for k, v in OVERRIDES.get(lang, {}).items():
        out[k] = v
    for k, v in NEW.items():
        out[k] = v[lang]
    return out

I18N = {lang: transform_dict(ORIG_I18N[lang], lang) for lang in ['zh-Hans','ja','en']}

# ============================================================
# 5. serialize JS data section
# ============================================================
def js_obj(d):
    return '{' + ','.join(js_str(k) + ':' + js_str(v) for k, v in d.items()) + '}'

def prov_line(i):
    st = S[i]
    parts = ["ja:" + js_str(st['ja']), "zh:" + js_str(st['zh']), "region:" + js_str(st['region']),
             "tagline:" + js_str(st['tag']),
             "food:" + json.dumps(st['food'], ensure_ascii=False),
             "spots:" + json.dumps(st['spots'], ensure_ascii=False),
             "matsuri:" + json.dumps(st['matsuri'], ensure_ascii=False)]
    return ' ' + str(i) + ':{' + ','.join(parts) + '},'

prov_block = 'const PROVINCES = {\n' + '\n'.join(prov_line(i) for i in range(1,52)) + '\n};'

reg_block = 'const REGIONS = {\n' + '\n'.join(
    ' ' + js_str(k) + ':{name:' + js_str(v[0]) + ', ids:[' + ','.join(str(x) for x in v[1]) + ']},'
    for k, v in REGIONS_DEF.items()) + '\n};'

en_block = 'const EN_PREF = {' + ','.join(js_str(i) + ':' + js_str(EN_NAMES[i]) for i in range(1,52)) + '};'
t2s_block = 'const T2S = ' + js_obj(dict(sorted(T2S.items(), key=lambda kv: kv[0]))) + ';'

i18n_block = 'const I18N = {\n' + '\n'.join(
    ' ' + js_str(lang) + ':' + js_obj(d) + ','
    for lang, d in [('zh-Hans', I18N['zh-Hans']), ('ja', I18N['ja']), ('en', I18N['en'])]) + '\n};'

levels_block = 'const LEVELS = [\n' + '\n'.join(
    ' {name:' + js_str(nm) + ',icon:' + js_str(icon) + ',pts:' + str(pts) + ',pct:' + js_str(pct) + '},'
    for (nm, icon, pts, pct, ja, en) in LEVELS) + '\n];'

type_block = ("const TYPE_NAME = {1:'途經',2:'遊玩',3:'住宿',4:'長居'};\n"
              "const TYPE_PTS = {1:2,2:5,3:10,4:20};\n"
              "const TYPE_COLOR = {1:'#8A8DA8',2:'#E89376',3:'#D2603F',4:'#B22234'};")

def ach_line(entry):
    aid, cat, icon, nm, nmja, nmen, pts, kind, data = entry
    base = (" {id:" + js_str(aid) + ",cat:" + js_str(cat) + ",icon:" + js_str(icon)
            + ",name:" + js_str(nm) + ",pts:" + str(pts))
    if kind == 'groups':
        ids, lv = data
        cond = build_cond(ids, lv)
        return (base + ",cond:" + js_str(cond) + ",kind:'groups',groups:[[" + ','.join(str(x) for x in ids)
                + "]," + str(lv) + "]},")
    if kind == 'count':
        prefs, lv, n = data
        cond = ('主要國家公園 5 州「遊玩」以上' if prefs == WH_PREFS
                else str(n) + ' 州以上「途經」以上')
        return (base + ",cond:" + js_str(cond) + ",kind:'count',prefs:[" + ','.join(str(x) for x in prefs)
                + "],level:" + str(lv) + ",n:" + str(n) + "},")
    # manual
    prefs, lv = data
    cond = '51 州皆「途經」以上，且手動勾選'
    return (base + ",cond:" + js_str(cond) + ",kind:'manual',prefs:[" + ','.join(str(x) for x in prefs)
            + "],level:" + str(lv) + "},")

ach_block = 'const ACH = [\n' + '\n'.join(ach_line(e) for e in ACH) + '\n];'
cats_block = 'const ACH_CATS = ' + json.dumps(ACH_CATS, ensure_ascii=False) + ';'
wh_block = 'const WH_PREFS = [' + ','.join(str(x) for x in WH_PREFS) + '];'

# replace blocks in data_inner
def replace_block(text, pat, new):
    m = re.search(pat, text, re.S)
    assert m, pat[:40]
    return text[:m.start()] + new + text[m.end():]

# usify the original remainder (comments + helper functions + computeScore) FIRST,
# so freshly injected blocks are not corrupted afterwards
data = usify(data_inner)
data = replace_block(data, r'const REGIONS = \{.*?\n\};', reg_block)
data = replace_block(data, r'const PROVINCES = \{.*?\n\};', prov_block)
data = replace_block(data, r'const WH_PREFS = \[[^\]]*\];', wh_block)
data = replace_block(data, r'const EN_PREF = \{.*?\};', en_block)
data = replace_block(data, r'const T2S = \{.*?\};', t2s_block)
data = replace_block(data, r'const I18N = \{.*?\n\};', i18n_block)
data = replace_block(data, r'const LEVELS = \[.*?\n\];', levels_block)
data = replace_block(data, r'const TYPE_NAME = \{.*?\};\nconst TYPE_PTS = \{.*?\};\nconst TYPE_COLOR = \{.*?\};', type_block)
data = replace_block(data, r'const ACH = \[.*?\n\];', ach_block)
data = replace_block(data, r'const ACH_CATS = \[.*?\];', cats_block)

# ============================================================
# 6. transform head
# ============================================================
head = head_orig

# ---- favicon (US flag SVG) ----
dots = ''.join("<circle cx='{}' cy='{}' r='0.9'/>".format(2 + c*4, 2 + r*4)
               for r in range(5) for c in range(6))
flag_svg = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 60 40'>"
            "<rect width='60' height='40' fill='%23FFFFFF'/>"
            "<path d='M0 0h60v3.08H0zM0 6.15h60v3.08H0zM0 12.31h60v3.08H0zM0 18.46h60v3.08H0zM0 24.62h60v3.08H0zM0 30.77h60v3.08H0zM0 36.92h60v3.08H0z' fill='%23B22234'/>"
            "<rect width='24' height='20' fill='%233C3B6E'/><g fill='%23FFFFFF'>" + dots + "</g></svg>")
new_fav = ('<link rel="icon" href="data:image/svg+xml,' + flag_svg + '">')
head = re.sub(r'<link rel="icon"[^>]*>', new_fav, head, count=1)

# ---- MDUI color tokens (light theme) ----
css_repl = [
 ('--mdui-color-primary:176 42 26;','--mdui-color-primary:178 34 52;'),
 ('--mdui-color-primary-container:255 218 212;','--mdui-color-primary-container:255 218 220;'),
 ('--mdui-color-on-primary-container:59 5 0;','--mdui-color-on-primary-container:77 7 8;'),
 ('--mdui-color-secondary:79 90 112;','--mdui-color-secondary:60 59 110;'),
 ('--mdui-color-tertiary:123 94 0;','--mdui-color-tertiary:201 162 39;'),
 ('--mdui-color-tertiary-container:255 224 138;','--mdui-color-tertiary-container:255 232 180;'),
 ('--mdui-color-surface:252 248 243;','--mdui-color-surface:250 250 252;'),
 ('--mdui-color-on-surface:33 26 23;','--mdui-color-on-surface:27 29 46;'),
 ('--mdui-color-surface-dim:223 211 201;','--mdui-color-surface-dim:221 222 234;'),
 ('--mdui-color-surface-bright:255 248 242;','--mdui-color-surface-bright:253 253 255;'),
 ('--mdui-color-surface-container-low:247 239 233;','--mdui-color-surface-container-low:246 246 251;'),
 ('--mdui-color-surface-container:241 232 225;','--mdui-color-surface-container:240 240 248;'),
 ('--mdui-color-surface-container-high:235 225 217;','--mdui-color-surface-container-high:233 233 243;'),
 ('--mdui-color-surface-container-highest:229 219 210;','--mdui-color-surface-container-highest:228 228 240;'),
 ('--mdui-color-surface-container-high:252 248 243;','--mdui-color-surface-container-high:250 250 252;'),
 ('--mdui-color-on-surface-variant:82 68 62;','--mdui-color-on-surface-variant:74 77 106;'),
 ('--mdui-color-outline:133 116 108;','--mdui-color-outline:138 141 168;'),
 ('--mdui-color-outline-variant:212 196 188;','--mdui-color-outline-variant:223 224 234;'),
 ('--mdui-color-surface-variant:229 219 210;','--mdui-color-surface-variant:228 228 240;'),
 ('--paper:#FCF8F3;','--paper:#FAFAFC;'),
 ('--paper-deep:#F1E8E1;','--paper-deep:#EDEEF4;'),
 ('--ink:#211A17;','--ink:#1B1D2E;'),
 ('--ink-soft:#52443E;','--ink-soft:#4A4D6A;'),
 ('--ink-faint:#85746C;','--ink-faint:#8A8DA8;'),
 ('--vermilion:#B02A1A;','--vermilion:#B22234;'),
 ('--vermilion-deep:#8C1F12;','--vermilion-deep:#8C1A28;'),
 ('--indigo:#4F5A70;','--indigo:#3C3B6E;'),
 ('--line:#E3D5CB;','--line:#DFE0EA;'),
]
for a, b in css_repl:
    assert a in head, a
    head = head.replace(a, b)

# rgba + hex globals
head = head.replace('rgba(176,42,26', 'rgba(178,34,52')
head = head.replace('rgba(33,26,23', 'rgba(27,29,46')
head = head.replace('rgba(252,248,243', 'rgba(250,250,252')
head = head.replace('#FCF8F3', '#FAFAFC')
head = head.replace('#F0E7DF', '#EDEEF4')
head = head.replace('#F3CDBF', '#F3D5D9')
head = head.replace('#B02A1A', '#B22234')

# ---- brand-flag / hero-flag (US stripes + canton) ----
brand_old = """.brand-flag{
  width:30px;height:21px;border-radius:4px;background:#fff;
  box-shadow:inset 0 0 0 1px rgba(27,29,46,.14);
  position:relative;flex:none;
}
.brand-flag::after{
  content:'';position:absolute;left:50%;top:50%;
  width:11px;height:11px;border-radius:50%;
  background:var(--vermilion);transform:translate(-50%,-50%);
}"""
brand_new = """.brand-flag{
  width:30px;height:21px;border-radius:4px;overflow:hidden;
  background:repeating-linear-gradient(to bottom,#B22234 0 3px,#fff 3px 6px);
  box-shadow:inset 0 0 0 1px rgba(27,29,46,.18);
  position:relative;flex:none;
}
.brand-flag::before{
  content:'';position:absolute;left:0;top:0;bottom:0;width:12px;
  background:#3C3B6E;box-shadow:inset -1px 0 0 rgba(255,255,255,.85);
}
.brand-flag::after{display:none}"""
assert brand_old in head
head = head.replace(brand_old, brand_new)

hero_old = """.hero-flag{
  width:84px;height:59px;border-radius:12px;background:#fff;
  box-shadow:var(--shadow-2),inset 0 0 0 1px rgba(27,29,46,.10);
  margin:0 auto 22px;position:relative;
}
.hero-flag::after{
  content:'';position:absolute;left:50%;top:50%;
  width:31px;height:31px;border-radius:50%;
  background:var(--vermilion);transform:translate(-50%,-50%);
}"""
hero_new = """.hero-flag{
  width:84px;height:59px;border-radius:12px;overflow:hidden;
  background:repeating-linear-gradient(to bottom,#B22234 0 8px,#fff 8px 16px);
  box-shadow:var(--shadow-2),inset 0 0 0 1px rgba(27,29,46,.10);
  margin:0 auto 22px;position:relative;
}
.hero-flag::before{
  content:'';position:absolute;left:0;top:0;bottom:0;width:34px;
  background-color:#3C3B6E;
  background-image:radial-gradient(circle,#fff 1.1px,transparent 1.4px);
  background-size:8px 8px;background-position:4px 4px;
  box-shadow:inset -1px 0 0 rgba(255,255,255,.85);
}
.hero-flag::after{display:none}"""
assert hero_old in head
head = head.replace(hero_old, hero_new)

# ---- teaser achievement cards ----
teaser_old = """        <div class="ach-card"><div class="ic">⛩️</div><div class="ac-body"><div class="ac-name">日本三景</div><div class="ac-pts">+20 分 <span>· 松島・天橋立・宮島</span></div></div></div>
        <div class="ach-card"><div class="ic">🎆</div><div class="ac-body"><div class="ac-name">日本三大祭</div><div class="ac-pts">+25 分 <span>· 祇園・天神・神田</span></div></div></div>
        <div class="ach-card"><div class="ic">🏯</div><div class="ac-body"><div class="ac-name">十二天守</div><div class="ac-pts">+30 分 <span>· 現存天守 12 座全制霸</span></div></div></div>
        <div class="ach-card"><div class="ic">🙏</div><div class="ac-body"><div class="ac-name">四國遍路</div><div class="ac-pts">+45 分 <span>· 四國四縣（手動勾選）</span></div></div></div>"""
teaser_new = """        <div class="ach-card"><div class="ic">🏞️</div><div class="ac-body"><div class="ac-name">國家公園巡禮</div><div class="ac-pts">+20 分 <span>· 主要國家公園 5 州</span></div></div></div>
        <div class="ach-card"><div class="ic">🛣️</div><div class="ac-body"><div class="ac-name">66號公路</div><div class="ac-pts">+18 分 <span>· 芝加哥到洛杉磯</span></div></div></div>
        <div class="ach-card"><div class="ic">🗽</div><div class="ac-body"><div class="ac-name">美國建國之地</div><div class="ac-pts">+16 分 <span>· 十三州殖民先驅</span></div></div></div>
        <div class="ach-card"><div class="ic">🎇</div><div class="ac-body"><div class="ac-name">完全制霸</div><div class="ac-pts">+60 分 <span>· 51 州全制霸（手動勾選）</span></div></div></div>"""
assert teaser_old in head
head = head.replace(teaser_old, teaser_new)

# ---- search placeholder ----
assert 'placeholder="搜尋縣市（中文／日文／地區）"' in head
head = head.replace('placeholder="搜尋縣市（中文／日文／地區）"',
                    'placeholder="搜尋州（中文／英文／日文／地區）"')

# ---- usify head ----
head = usify(head)

# ============================================================
# 7. transform logic
# ============================================================
logic = logic_orig
logic = usify(logic)

logic_repl = [
 # attribution
 ('map.attributionControl.addAttribution(\'境界 © <a href="https://github.com/PublicaMundi/land" target="_blank" rel="noopener">PublicaMundi</a> · Leaflet\');',
  'map.attributionControl.addAttribution(\'州界 © <a href="https://github.com/PublicaMundi/MappingAPI" target="_blank" rel="noopener">PublicaMundi / MappingAPI</a> · Leaflet\');'),
 # zoom
 ('minZoom:4.2, maxZoom:10, zoomSnap:0.5, wheelPxPerZoomLevel:90',
  'minZoom:3.5, maxZoom:9, zoomSnap:0.5, wheelPxPerZoomLevel:90'),
 # LABEL_MAJOR
 ('const LABEL_MAJOR = new Set([1,2,3,4,5,6,7,13,15,16,20,22,23,27,28,30,31,34,36,37,40,42,43,44,46,51]);',
  'const LABEL_MAJOR = new Set([2,3,5,6,9,11,13,22,26,28,31,32,35,36,37,38,42,43,44,46,47,50]);'),

 # search vars (en support)
 ("""    const zh = p.zh.toLowerCase(), ja = p.ja.toLowerCase(), rg = REGIONS[p.region].name.toLowerCase();
    const vars = [zh, ja, rg, zh + '都', zh + '府', zh + '州'];""",
  """    const zh = p.zh.toLowerCase(), ja = p.ja.toLowerCase(), en = (EN_PREF[id] || '').toLowerCase(), rg = REGIONS[p.region].name.toLowerCase();
    const vars = [zh, ja, en, rg, zh + '州'];"""),
 # search result shows EN name instead of long ja
 ("<span class=\"ps-ja\">' + esc(p.ja) + '</span>",
  "<span class=\"ps-ja\">' + esc(EN_PREF[id] || p.ja) + '</span>"),
 # suggestion card shows EN name
 ("'<div class=\"sug-ja\">' + esc(p.ja) + '</div>'",
  "'<div class=\"sug-ja\">' + esc(EN_PREF[id] || p.ja) + '</div>'"),
 # hot suggestions
 ('const hot = [26, 13, 27, 1, 40, 14, 28, 23];',
  'const hot = [5, 32, 43, 9, 11, 28, 50, 3];'),
 # canvas palette
 ("const VERM = '#9E2418', VERM_DEEP = '#7A1A10', VERM_SOFT = '#C44A3A';",
  "const VERM = '#B22234', VERM_DEEP = '#8C1A28', VERM_SOFT = '#D0465A';"),
 ("const INK = '#1E1815', INK_SOFT = '#4A3F39', INK_FAINT = '#8A7A72';",
  "const INK = '#1B1D2E', INK_SOFT = '#4A4D6A', INK_FAINT = '#8A8DA8';"),
 ("const PAPER = '#FAF5EE', PAPER_WARM = '#F5EEE3';",
  "const PAPER = '#FAFAFC', PAPER_WARM = '#EDEEF4';"),
 ("const GOLD = '#B08D1E', GOLD_LIGHT = '#D4B54E', GOLD_FAINT = '#E8D9A8';",
  "const GOLD = '#C9A227', GOLD_LIGHT = '#DDB94A', GOLD_FAINT = '#F0E3B8';"),
 ("const CARD_BG = '#FFFFFF', CARD_BORDER = '#E8DDCE';",
  "const CARD_BG = '#FFFFFF', CARD_BORDER = '#E3E4EE';"),
 # lightenFill paper color
 ('Math.round(r + (252-r)*amt) + \',\' + Math.round(g + (248-g)*amt) + \',\' + Math.round(b + (243-b)*amt)',
  'Math.round(r + (250-r)*amt) + \',\' + Math.round(g + (250-g)*amt) + \',\' + Math.round(b + (252-b)*amt)'),
 # FILLS map ramp -> US palette
 ("const FILLS = {0:'#F0E7DF', 1:'#F3CDBF', 2:'#E89376', 3:'#D2603F', 4:'#B02A1A'};",
  "const FILLS = {0:'#EDEEF4', 1:'#F3D5D9', 2:'#E89376', 3:'#D2603F', 4:'#B22234'};"),
 # GB bounds
 ('const GB = { minLon: 123.6, maxLon: 146.2, minLat: 24.0, maxLat: 45.7 };',
  'const GB = { minLon: -136.6, maxLon: -66.5, minLat: 25.0, maxLat: 49.5 };'),
 # coordinate label
 ("ctx.fillText('123°E – 146°E  /  24°N – 46°N', mc.x + mc.w - 40, legY);",
  "ctx.fillText('-136°W – -66°W  /  25°N – 50°N', mc.x + mc.w - 40, legY);"),
 # fix latent shadowing bug: local `const t` shadows i18n function t() in manual-ach checkbox render
 ("""      const t = document.createElement('span');
      t.className = 'ac-t';
      t.innerHTML = '<b>' + esc(a.icon + ' ' + t(a.name)) + '</b><span>' + t('勾選即認領此成就（仍需達成州條件）') + '</span>';
      label.appendChild(t);""",
  """      const tEl = document.createElement('span');
      tEl.className = 'ac-t';
      tEl.innerHTML = '<b>' + esc(a.icon + ' ' + t(a.name)) + '</b><span>' + t('勾選即認領此成就（仍需達成州條件）') + '</span>';
      label.appendChild(tEl);"""),
]
for a, b in logic_repl:
    assert a in logic, a[:70]
    logic = logic.replace(a, b)

# PREF_IMG (regex, arbitrary spacing)
def pref_img_line(m):
    entries = []
    for i in range(1, 52):
        fname = 'dc' if i == 51 else re.sub(r'[^a-z]', '', EN_NAMES[i].lower())
        entries.append(" %d:'assets/states/%02d_%s.jpg'" % (i, i, fname))
    return 'const PREF_IMG = {' + ','.join(entries) + '};'
logic = re.sub(r'const PREF_IMG = \{.*?\};', pref_img_line, logic, count=1, flags=re.S)

# ============================================================
# 8. assemble & write
# ============================================================
out = (head + '\n\n' + '<script src="assets/usa_geojson.js"></script>' + '\n' + cdn +
       '\n<script>\n' + data + '\n</script>\n' + logic)

open(DST, 'w', encoding='utf-8').write(out)

print('OK written', DST)
print('states:', len(S), 'regions:', len(REGIONS_DEF), 'ach:', len(ACH), 'levels:', len(LEVELS))
print('I18N keys -> zh-Hans:', len(I18N['zh-Hans']), 'ja:', len(I18N['ja']), 'en:', len(I18N['en']))
print('T2S entries:', len(T2S))
