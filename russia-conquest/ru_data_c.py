# -*- coding: utf-8 -*-
# 俄羅斯制霸地圖 — 資料模組 C（地區/英文名/世遺/等級/成就/類別/標籤/主題）

# 地區（8 個聯邦管區）：key -> (名稱zh, 名稱ja, 名稱en, ids)
REGIONS_NEW = {
 '中央':    ('中央聯邦管區','中央連邦管区','Central',        [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]),
 '西北':    ('西北聯邦管區','北西連邦管区','Northwestern',    [19,20,21,22,23,24,25,26,27,28,29]),
 '南方':    ('南方聯邦管區','南部連邦管区','Southern',        [30,31,32,33,34,35]),
 '北高加索': ('北高加索聯邦管區','北カフカス連邦管区','North Caucasus',[36,37,38,39,40,41,42]),
 '伏爾加':  ('伏爾加聯邦管區','沿ヴォルガ連邦管区','Volga',    [43,44,45,46,47,48,49,50,51,52,53,54,55,56]),
 '烏拉爾':  ('烏拉爾聯邦管區','ウラル連邦管区','Ural',        [57,58,59,60,61,62]),
 '西伯利亞': ('西伯利亞聯邦管區','シベリア連邦管区','Siberian',[63,64,65,66,67,68,69,70,71,72,73]),
 '遠東':    ('遠東聯邦管區','極東連邦管区','Far Eastern',    [74,75,76,77,78,79,80,81,82,83]),
}

# 英文主體名
EN_PREF_NEW = {
 1:'Moscow City',2:'Moscow Oblast',3:'Belgorod Oblast',4:'Bryansk Oblast',5:'Vladimir Oblast',
 6:'Voronezh Oblast',7:'Ivanovo Oblast',8:'Kaluga Oblast',9:'Kostroma Oblast',10:'Kursk Oblast',
 11:'Lipetsk Oblast',12:'Oryol Oblast',13:'Ryazan Oblast',14:'Smolensk Oblast',15:'Tambov Oblast',
 16:'Tver Oblast',17:'Tula Oblast',18:'Yaroslavl Oblast',19:'Saint Petersburg City',20:'Leningrad Oblast',
 21:'Arkhangelsk Oblast',22:'Vologda Oblast',23:'Kaliningrad Oblast',24:'Republic of Karelia',25:'Komi Republic',
 26:'Murmansk Oblast',27:'Nenets Autonomous Okrug',28:'Novgorod Oblast',29:'Pskov Oblast',30:'Republic of Adygea',
 31:'Republic of Kalmykia',32:'Krasnodar Krai',33:'Astrakhan Oblast',34:'Volgograd Oblast',35:'Rostov Oblast',
 36:'Republic of Dagestan',37:'Republic of Ingushetia',38:'Kabardino-Balkar Republic',39:'Karachay-Cherkess Republic',40:'Republic of North Ossetia',
 41:'Chechen Republic',42:'Stavropol Krai',43:'Republic of Bashkortostan',44:'Mari El Republic',45:'Republic of Mordovia',
 46:'Republic of Tatarstan',47:'Udmurt Republic',48:'Chuvash Republic',49:'Kirov Oblast',50:'Nizhny Novgorod Oblast',
 51:'Orenburg Oblast',52:'Penza Oblast',53:'Samara Oblast',54:'Saratov Oblast',55:'Ulyanovsk Oblast',56:'Perm Krai',
 57:'Kurgan Oblast',58:'Sverdlovsk Oblast',59:'Tyumen Oblast',60:'Chelyabinsk Oblast',61:'Khanty-Mansi Autonomous Okrug',62:'Yamalo-Nenets Autonomous Okrug',
 63:'Altai Krai',64:'Altai Republic',65:'Irkutsk Oblast',66:'Kemerovo Oblast',67:'Krasnoyarsk Krai',68:'Novosibirsk Oblast',
 69:'Omsk Oblast',70:'Tomsk Oblast',71:'Tuva Republic',72:'Khakassia Republic',73:'Zabaikalsky Krai',74:'Amur Oblast',
 75:'Republic of Buryatia',76:'Jewish Autonomous Oblast',77:'Kamchatka Krai',78:'Magadan Oblast',79:'Primorsky Krai',
 80:'Sakha Republic',81:'Sakhalin Oblast',82:'Khabarovsk Krai',83:'Chukotka Autonomous Okrug',
}

# 有 UNESCO 世界遺產的主體
WH_PREFS_NEW = [1,2,5,18,19,20,21,22,23,24,25,28,29,30,32,36,39,46,64,65,67,71,75,77,79,80,83]

# 等級（10 級）
LEVELS_NEW = [
 {'name':'未踏之旅人','icon':'🧳','pts':0,'pct':'2.9%'},
 {'name':'旅行初心者','icon':'🚂','pts':10,'pct':'0.8%'},
 {'name':'觀光旅客','icon':'🪆','pts':30,'pct':'0.7%'},
 {'name':'俄羅斯探索者','icon':'🏰','pts':70,'pct':'10.7%'},
 {'name':'文化踐行者','icon':'⛪','pts':130,'pct':'42.0%'},
 {'name':'旅遊達人','icon':'🪕','pts':210,'pct':'32.1%'},
 {'name':'俄羅斯通','icon':'🐻','pts':310,'pct':'9.2%'},
 {'name':'聯邦獵人','icon':'🏔️','pts':430,'pct':'1.3%'},
 {'name':'俄羅斯制霸者','icon':'👑','pts':580,'pct':'0.2%'},
 {'name':'傳說的旅人','icon':'❄️','pts':750,'pct':'0.1%'},
]

# 成就類別
ACH_CATS_NEW = ['全部','絕景','節慶','美食','文化','自然','鐵路','建築','運動','影劇','文學']

# 成就（60）
ACH_NEW = [
 {'id':'A01','cat':'絕景','icon':'🏛️','name':'紅場與克里姆林宮','pts':15,'cond':'莫斯科市「遊玩」以上','kind':'groups','groups':[[1],2]},
 {'id':'A02','cat':'絕景','icon':'🖼️','name':'冬宮與涅瓦河','pts':15,'cond':'聖彼得堡市「遊玩」以上','kind':'groups','groups':[[19],2]},
 {'id':'A03','cat':'絕景','icon':'🧊','name':'貝加爾湖藍冰','pts':20,'cond':'伊爾庫茨克＋布里亞特皆「遊玩」以上','kind':'groups','groups':[[65,75],2]},
 {'id':'A04','cat':'絕景','icon':'🌋','name':'堪察加火山群','pts':18,'cond':'堪察加邊疆區「遊玩」以上','kind':'groups','groups':[[77],2]},
 {'id':'A05','cat':'絕景','icon':'⛰️','name':'阿爾泰金山','pts':18,'cond':'阿爾泰共和國「遊玩」以上','kind':'groups','groups':[[64],2]},
 {'id':'A06','cat':'絕景','icon':'🏞️','name':'俄羅斯三絕景','pts':25,'cond':'貝加爾湖・堪察加・阿爾泰皆「遊玩」以上','kind':'groups','groups':[[65,77,64],2]},
 {'id':'A07','cat':'絕景','icon':'🌌','name':'北極光之夜','pts':20,'cond':'摩爾曼斯克州「住宿」以上','kind':'groups','groups':[[26],3]},
 {'id':'A08','cat':'絕景','icon':'🏔️','name':'厄爾布魯士峰','pts':16,'cond':'卡巴爾達-巴爾卡爾「遊玩」以上','kind':'groups','groups':[[38],2]},
 {'id':'A09','cat':'絕景','icon':'🏘️','name':'金環古城巡禮','pts':18,'cond':'弗拉基米爾・雅羅斯拉夫爾・科斯特羅馬・伊萬諾沃皆「遊玩」以上','kind':'groups','groups':[[5,18,9,7],2]},
 {'id':'A10','cat':'絕景','icon':'🏖️','name':'索契黑海之濱','pts':14,'cond':'克拉斯諾達爾「遊玩」以上','kind':'groups','groups':[[32],2]},
 {'id':'A11','cat':'絕景','icon':'⛰️','name':'高加索群峰','pts':16,'cond':'卡巴爾達-巴爾卡爾＋卡拉恰伊-切爾克斯皆「遊玩」以上','kind':'groups','groups':[[38,39],2]},
 {'id':'A12','cat':'絕景','icon':'🏛️','name':'千年古城諾夫哥羅德','pts':13,'cond':'諾夫哥羅德州「遊玩」以上','kind':'groups','groups':[[28],2]},
 {'id':'A13','cat':'節慶','icon':'🎖️','name':'勝利日閱兵','pts':16,'cond':'莫斯科市「遊玩」以上','kind':'groups','groups':[[1],2]},
 {'id':'A14','cat':'節慶','icon':'✨','name':'白夜節','pts':15,'cond':'聖彼得堡市「遊玩」以上','kind':'groups','groups':[[19],2]},
 {'id':'A15','cat':'節慶','icon':'🥞','name':'謝肉節','pts':14,'cond':'莫斯科＋聖彼得堡皆「遊玩」以上','kind':'groups','groups':[[1,19],2]},
 {'id':'A16','cat':'節慶','icon':'🎆','name':'莫斯科城市日','pts':13,'cond':'莫斯科市「遊玩」以上','kind':'groups','groups':[[1],2]},
 {'id':'A17','cat':'節慶','icon':'🧊','name':'貝加爾冰上節','pts':14,'cond':'伊爾庫茨克「遊玩」以上','kind':'groups','groups':[[65],2]},
 {'id':'A18','cat':'節慶','icon':'🎇','name':'喀山城市日','pts':13,'cond':'韃靼斯坦「遊玩」以上','kind':'groups','groups':[[46],2]},
 {'id':'A19','cat':'節慶','icon':'🎪','name':'北極節','pts':13,'cond':'摩爾曼斯克「遊玩」以上','kind':'groups','groups':[[26],2]},
 {'id':'A20','cat':'美食','icon':'🍲','name':'羅宋湯巡禮','pts':13,'cond':'莫斯科＋聖彼得堡皆「遊玩」以上','kind':'groups','groups':[[1,19],2]},
 {'id':'A21','cat':'美食','icon':'🥫','name':'裏海魚子醬','pts':16,'cond':'阿斯特拉罕「遊玩」以上','kind':'groups','groups':[[33],2]},
 {'id':'A22','cat':'美食','icon':'🥟','name':'西伯利亞餃子','pts':14,'cond':'彼爾姆＋秋明皆「遊玩」以上','kind':'groups','groups':[[56,59],2]},
 {'id':'A23','cat':'美食','icon':'🥞','name':'布林餅與魚子醬','pts':14,'cond':'莫斯科「遊玩」以上','kind':'groups','groups':[[1],2]},
 {'id':'A24','cat':'美食','icon':'🍢','name':'高加索烤肉串','pts':14,'cond':'達吉斯坦＋斯塔夫羅波爾皆「遊玩」以上','kind':'groups','groups':[[36,42],2]},
 {'id':'A25','cat':'美食','icon':'🦀','name':'帝王蟹盛宴','pts':16,'cond':'堪察加＋薩哈林皆「遊玩」以上','kind':'groups','groups':[[77,81],2]},
 {'id':'A26','cat':'美食','icon':'🍪','name':'圖拉薑餅','pts':12,'cond':'圖拉州「遊玩」以上','kind':'groups','groups':[[17],2]},
 {'id':'A27','cat':'美食','icon':'🐟','name':'伏爾加河鮮湯','pts':13,'cond':'薩馬拉＋阿斯特拉罕皆「遊玩」以上','kind':'groups','groups':[[53,33],2]},
 {'id':'A28','cat':'美食','icon':'☕','name':'圖拉茶炊','pts':12,'cond':'圖拉州「遊玩」以上','kind':'groups','groups':[[17],2]},
 {'id':'A29','cat':'文化','icon':'🩰','name':'莫斯科大劇院芭蕾','pts':16,'cond':'莫斯科市「遊玩」以上','kind':'groups','groups':[[1],2]},
 {'id':'A30','cat':'文化','icon':'🎭','name':'馬林斯基劇院','pts':15,'cond':'聖彼得堡市「遊玩」以上','kind':'groups','groups':[[19],2]},
 {'id':'A31','cat':'文化','icon':'🖼️','name':'特列季亞科夫畫廊','pts':14,'cond':'莫斯科市「遊玩」以上','kind':'groups','groups':[[1],2]},
 {'id':'A32','cat':'文化','icon':'🏛️','name':'國立艾爾米塔什博物館','pts':15,'cond':'聖彼得堡市「遊玩」以上','kind':'groups','groups':[[19],2]},
 {'id':'A33','cat':'文化','icon':'🎪','name':'俄羅斯馬戲團','pts':13,'cond':'莫斯科市「遊玩」以上','kind':'groups','groups':[[1],2]},
 {'id':'A34','cat':'文化','icon':'🚀','name':'宇航雙城','pts':14,'cond':'卡盧加＋莫斯科皆「遊玩」以上','kind':'groups','groups':[[8,1],2]},
 {'id':'A35','cat':'文化','icon':'🌍','name':'世界遺產巡禮','pts':20,'cond':'8 個以上「有世界遺產」且「遊玩」以上','kind':'count','prefs':WH_PREFS_NEW,'level':2,'n':8},
 {'id':'A36','cat':'自然','icon':'🐯','name':'西伯利亞虎','pts':16,'cond':'濱海邊疆區「遊玩」以上','kind':'groups','groups':[[79],2]},
 {'id':'A37','cat':'自然','icon':'🐻❄️','name':'北極熊之島','pts':18,'cond':'楚科奇「遊玩」以上','kind':'groups','groups':[[83],2]},
 {'id':'A38','cat':'自然','icon':'🐋','name':'白鯨之歌','pts':15,'cond':'阿爾漢格爾斯克「遊玩」以上','kind':'groups','groups':[[21],2]},
 {'id':'A39','cat':'自然','icon':'🐻','name':'堪察加棕熊','pts':16,'cond':'堪察加「遊玩」以上','kind':'groups','groups':[[77],2]},
 {'id':'A40','cat':'自然','icon':'🐆','name':'雪豹之國','pts':16,'cond':'阿爾泰共和國＋圖瓦皆「遊玩」以上','kind':'groups','groups':[[64,71],2]},
 {'id':'A41','cat':'自然','icon':'🌋','name':'間歇泉谷','pts':16,'cond':'堪察加「遊玩」以上','kind':'groups','groups':[[77],2]},
 {'id':'A42','cat':'自然','icon':'🌲','name':'國家公園巡禮','pts':15,'cond':'6 個以上「有國家公園」且「遊玩」以上','kind':'count','prefs':[21,24,26,32,33,36,46,63,64,65,67,75,77,79,80,83],'level':2,'n':6},
 {'id':'A43','cat':'鐵路','icon':'🚂','name':'西伯利亞大鐵路','pts':20,'cond':'莫斯科→葉卡捷琳堡→新西伯利亞→伊爾庫茨克→海參崴皆「途經」以上','kind':'groups','groups':[[1,58,68,65,79],1]},
 {'id':'A44','cat':'鐵路','icon':'🚇','name':'莫斯科地鐵','pts':14,'cond':'莫斯科市「遊玩」以上','kind':'groups','groups':[[1],2]},
 {'id':'A45','cat':'鐵路','icon':'🛤️','name':'貝阿鐵路','pts':16,'cond':'伊爾庫茨克＋布里亞特＋哈巴羅夫斯克皆「途經」以上','kind':'groups','groups':[[65,75,82],1]},
 {'id':'A46','cat':'鐵路','icon':'🚃','name':'環貝加爾鐵路','pts':14,'cond':'伊爾庫茨克「遊玩」以上','kind':'groups','groups':[[65],2]},
 {'id':'A47','cat':'鐵路','icon':'🚄','name':'遊隼號高鐵','pts':13,'cond':'莫斯科＋聖彼得堡皆「遊玩」以上','kind':'groups','groups':[[1,19],2]},
 {'id':'A48','cat':'建築','icon':'⛪','name':'聖瓦西里大教堂','pts':14,'cond':'莫斯科市「遊玩」以上','kind':'groups','groups':[[1],2]},
 {'id':'A49','cat':'建築','icon':'💒','name':'滴血大教堂','pts':14,'cond':'聖彼得堡市「遊玩」以上','kind':'groups','groups':[[19],2]},
 {'id':'A50','cat':'建築','icon':'🪵','name':'木造建築巡禮','pts':15,'cond':'基日島（卡累利阿）＋蘇茲達爾（弗拉基米爾）皆「遊玩」以上','kind':'groups','groups':[[24,5],2]},
 {'id':'A51','cat':'建築','icon':'🕌','name':'喀山克里姆林宮','pts':14,'cond':'韃靼斯坦「遊玩」以上','kind':'groups','groups':[[46],2]},
 {'id':'A52','cat':'建築','icon':'🛕','name':'洋蔥頂教堂巡禮','pts':16,'cond':'莫斯科＋聖彼得堡＋喀山皆「遊玩」以上','kind':'groups','groups':[[1,19,46],2]},
 {'id':'A53','cat':'運動','icon':'🏒','name':'冰球聖殿','pts':14,'cond':'莫斯科＋聖彼得堡皆「遊玩」以上','kind':'groups','groups':[[1,19],2]},
 {'id':'A54','cat':'運動','icon':'⛸️','name':'花樣滑冰巡禮','pts':14,'cond':'莫斯科「遊玩」以上','kind':'groups','groups':[[1],2]},
 {'id':'A55','cat':'運動','icon':'⚽','name':'世界盃球場巡禮','pts':16,'cond':'莫斯科＋聖彼得堡＋喀山＋葉卡捷琳堡＋索契皆「遊玩」以上','kind':'groups','groups':[[1,19,46,58,32],2]},
 {'id':'A56','cat':'運動','icon':'🏃','name':'紅場馬拉松','pts':13,'cond':'莫斯科市「遊玩」以上','kind':'groups','groups':[[1],2]},
 {'id':'A57','cat':'影劇','icon':'📖','name':'戰爭與和平','pts':14,'cond':'莫斯科＋圖拉皆「遊玩」以上','kind':'groups','groups':[[1,17],2]},
 {'id':'A58','cat':'影劇','icon':'🎬','name':'安娜·卡列尼娜','pts':13,'cond':'聖彼得堡「遊玩」以上','kind':'groups','groups':[[19],2]},
 {'id':'A59','cat':'影劇','icon':'🎞️','name':'莫斯科不相信眼淚','pts':13,'cond':'莫斯科市「遊玩」以上','kind':'groups','groups':[[1],2]},
 {'id':'A60','cat':'影劇','icon':'🚂','name':'日瓦戈醫生','pts':13,'cond':'斯維爾德洛夫斯克「遊玩」以上','kind':'groups','groups':[[58],2]},
 {'id':'A61','cat':'文學','icon':'📚','name':'俄羅斯文學三巨匠','pts':18,'cond':'托爾斯泰・杜斯妥也夫斯基・契訶夫皆「遊玩」以上','kind':'groups','groups':[[17,1,54],2]},
 {'id':'A62','cat':'文學','icon':'✒️','name':'普希金足跡','pts':13,'cond':'莫斯科＋聖彼得堡皆「遊玩」以上','kind':'groups','groups':[[1,19],2]},
 {'id':'A63','cat':'文學','icon':'🎼','name':'柴可夫斯基音樂之旅','pts':14,'cond':'烏德穆爾特＋聖彼得堡皆「遊玩」以上','kind':'groups','groups':[[47,19],2]},
 {'id':'A64','cat':'文學','icon':'🐈','name':'布爾加科夫與莫斯科','pts':13,'cond':'莫斯科市「遊玩」以上','kind':'groups','groups':[[1],2]},
]

# 手動勾選成就（全俄制霸）
ACH_MANUAL_NEW = [
 {'id':'A65','cat':'全部','icon':'👑','name':'全俄制霸（手動）','pts':45,'cond':'83 個聯邦主體皆「遊玩」以上，且手動勾選','kind':'manual','prefs':list(range(1,84)),'level':2},
]

# 地圖標籤主體（主要主體）
LABEL_MAJOR_NEW = [1,2,5,9,17,18,19,20,21,22,23,24,25,26,28,29,32,33,34,35,36,38,42,43,46,50,53,56,58,59,60,63,64,65,66,67,68,69,70,71,72,73,75,77,78,79,80,81,82,83]

# 主題色（俄羅斯三色旗：白／藍／紅，主色深藍）
THEME = {
 'vermilion': '#1F4E9C',        # 主色深藍
 'vermilion-deep': '#122F63',   # 深藍陰影
 'verml_rgba': 'rgba(31,78,156,',
 'dot_bg': 'rgba(31,78,156,.07)',
 'FILLS': {0:'#F1EDE6',1:'#C9D8F0',2:'#8FAFDF',3:'#4F78C8',4:'#1F4E9C'},
 'TYPE_COLOR': {1:'#8E99A8',2:'#8FAFDF',3:'#4F78C8',4:'#C8402E'},
 'VERM': '#1F4E9C',
 'VERM_DEEP': '#122F63',
 'RUS_RED': '#C8402E',
}
