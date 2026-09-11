/* 簡體覆寫（T2S 之外需要特別處理的詞） */
const ZH_OVERRIDES = {
  '途經、轉乘':'途经、中转','觀光、一日遊':'观光、一日游','過夜住宿':'过夜住宿','長期居住':'长期居住',
  '同省重複造訪、地區全制霸與特殊成就，都能帶來額外加分。':'同省重复到访、地区全制霸与特殊成就，都能带来额外加分。',
  '（純靜態版沒有雲端伺服器）':'（纯静态版没有云端服务器）',
};

/* 補充詞條（snack 等未在主 I18N 覆蓋的鍵） */
const EXTRA_I18N = {
  en:{
    '已清除評分':'Rating cleared',
    '已鎖定編輯 — 點擊頂欄鎖頭解鎖後才能記錄旅程':'Editing locked — unlock via the padlock in the top bar to log trips',
    '請選擇造訪層級。':'Please select a visit tier.',
    '尚未建立任何地圖 — 點擊「建立我的地圖」開始！':'No maps yet — tap "Create My Map" to get started!',
    '已匯出戰報圖片。':'Report image exported.',
    '已複製戰報！':'Report copied!',
    '請輸入地圖名稱。':'Please enter a map name.',
    '密碼不一致，請重新輸入。':'Passwords do not match — try again.',
    '找不到這組識別碼，請確認是否輸入正確。':'Code not found — please check it.',
    '已解鎖編輯。':'Editing unlocked.',
    '密碼錯誤，無法解鎖。':'Incorrect password — cannot unlock.',
    '已鎖定編輯。':'Editing locked.',
    '資料檔格式錯誤，無法匯入。':'Invalid data file.',
    '最多 5 張照片。':'Up to 5 photos.',
  },
  ar:{
    '上傳':'رفع',
    '已清除評分':'أُزيل التقييم',
    '已鎖定編輯 — 點擊頂欄鎖頭解鎖後才能記錄旅程':'التحرير مقفل — افتح القفل من الأعلى لتسجيل الرحلات',
  },
};

function t(str){
  if(!str) return str;
  const d = LANG==='zh-Hans' ? ZH_OVERRIDES : I18N[LANG];
  if(d && d[str] != null) return d[str];
  const ex = EXTRA_I18N[LANG];
  if(ex && ex[str] != null) return ex[str];
  if(LANG==='zh-Hant') return toTraditional(str);
  if(LANG==='zh-Hans') return toSimplified(str);
  return str;
}
function prefName(p){
  if(LANG==='en') return p.en;
  if(LANG==='ar') return p.ar;
  return t(p.zh);
}

/* ============ 等級 ============ */
const LEVELS = [
 {name:'未踏旅人',icon:'🏜️',pts:0},
 {name:'尼羅河旅人',icon:'🛶',pts:10},
 {name:'沙漠行者',icon:'🐪',pts:30},
 {name:'綠洲訪客',icon:'🌴',pts:70},
 {name:'金字塔旅人',icon:'🔺',pts:130},
 {name:'神廟探索者',icon:'🏺',pts:210},
 {name:'尼羅河行者',icon:'⛵',pts:310},
 {name:'法老見習',icon:'👑',pts:430},
 {name:'埃及制霸者',icon:'🦅',pts:580},
 {name:'傳說的法老',icon:'🌟',pts:750},
];

/* ============ 造訪層級 ============ */
const TYPE_NAME = {1:'途經',2:'遊玩',3:'住宿',4:'長居'};
const TYPE_PTS  = {1:2,2:5,3:10,4:20};
const TYPE_COLOR = {1:'#8A7A72',2:'#E89376',3:'#D2603F',4:'#B02A1A'};

/* ============ 成就 ============ */
const ACH_CATS = ['全部','絕景','祭典','美食','文化','自然','神廟','影劇'];
const ACH = [
 {id:'A01',cat:'絕景',icon:'🏜️',name:'金字塔奇觀',pts:15,cond:'吉薩金字塔「遊玩」以上',kind:'group',groups:[[2]],level:2},
 {id:'A02',cat:'絕景',icon:'🏛️',name:'七大奇蹟之二',pts:20,cond:'吉薩金字塔＋亞歷山大燈塔皆「遊玩」以上',kind:'group',groups:[[2,4]],level:2},
 {id:'A03',cat:'文化',icon:'🗿',name:'法老陵寢巡禮',pts:18,cond:'吉薩金字塔＋帝王谷皆「遊玩」以上',kind:'group',groups:[[2,22]],level:2},
 {id:'A04',cat:'絕景',icon:'🏞️',name:'尼羅河全覽',pts:20,cond:'開羅・盧克索・阿斯旺皆「遊玩」以上',kind:'group',groups:[[1,22,23]],level:2},
 {id:'A05',cat:'自然',icon:'🤿',name:'紅海潛水',pts:20,cond:'紅海省＋南西奈皆「遊玩」以上',kind:'group',groups:[[24,27]],level:2},
 {id:'A06',cat:'自然',icon:'🌊',name:'地中海海岸',pts:14,cond:'亞歷山大＋馬特魯皆「遊玩」以上',kind:'group',groups:[[4,6]],level:2},
 {id:'A07',cat:'自然',icon:'🌴',name:'三大綠洲',pts:20,cond:'錫瓦（馬特魯）＋哈里杰（新河谷）＋法尤姆皆「遊玩」以上',kind:'group',groups:[[6,25,16]],level:2},
 {id:'A08',cat:'文化',icon:'⛰️',name:'西奈聖山',pts:16,cond:'南西奈「住宿」以上（聖凱瑟琳修道院）',kind:'group',groups:[[27]],level:3},
 {id:'A09',cat:'神廟',icon:'🏛️',name:'神廟三傑',pts:22,cond:'卡納克＋阿布辛貝＋丹德拉皆「遊玩」以上',kind:'group',groups:[[22,23,21]],level:2},
 {id:'A10',cat:'絕景',icon:'🚢',name:'蘇伊士運河',pts:18,cond:'塞得港＋伊斯梅利亞＋蘇伊士皆「遊玩」以上',kind:'group',groups:[[13,14,15]],level:2},
 {id:'A11',cat:'自然',icon:'🌾',name:'三角洲水鄉',pts:20,cond:'三角洲地區 6 省皆「遊玩」以上',kind:'group',groups:[[7,8,9,10,11,12]],level:2},
 {id:'A12',cat:'文化',icon:'🕌',name:'開羅古城',pts:16,cond:'開羅「遊玩」以上',kind:'group',groups:[[1]],level:2},
 {id:'A13',cat:'絕景',icon:'⛵',name:'尼羅河帆船',pts:14,cond:'盧克索＋阿斯旺皆「遊玩」以上',kind:'group',groups:[[22,23]],level:2},
 {id:'A14',cat:'美食',icon:'🐟',name:'尼羅河鮮魚',pts:14,cond:'阿斯旺＋杜姆亞特＋塞得港皆「遊玩」以上',kind:'group',groups:[[23,8,13]],level:2},
 {id:'A15',cat:'自然',icon:'✨',name:'沙漠星空',pts:18,cond:'新河谷＋馬特魯＋南西奈皆「遊玩」以上',kind:'group',groups:[[25,6,27]],level:2},
 {id:'A16',cat:'自然',icon:'🐋',name:'法尤姆秘境',pts:15,cond:'法尤姆「遊玩」以上（鯨魚谷）',kind:'group',groups:[[16]],level:2},
 {id:'A17',cat:'文化',icon:'🎨',name:'貝尼哈桑岩墓',pts:13,cond:'明亞「遊玩」以上',kind:'group',groups:[[18]],level:2},
 {id:'A18',cat:'文化',icon:'🏺',name:'阿拜多斯聖城',pts:14,cond:'索哈杰「遊玩」以上',kind:'group',groups:[[20]],level:2},
 {id:'A19',cat:'神廟',icon:'🏛️',name:'埃德夫與考姆翁布',pts:15,cond:'阿斯旺「住宿」以上（雙神廟朝聖）',kind:'group',groups:[[23]],level:3},
 {id:'A20',cat:'文化',icon:'🧡',name:'努比亞文化',pts:16,cond:'阿斯旺「住宿」以上（努比亞村）',kind:'group',groups:[[23]],level:3},
 {id:'A21',cat:'文化',icon:'🔥',name:'貝都因之夜',pts:14,cond:'北西奈＋南西奈皆「遊玩」以上',kind:'group',groups:[[26,27]],level:2},
 {id:'A22',cat:'美食',icon:'🥘',name:'埃及美食巡禮',pts:15,cond:'開羅＋亞歷山大＋盧克索皆「遊玩」以上',kind:'group',groups:[[1,4,22]],level:2},
 {id:'A23',cat:'美食',icon:'☕',name:'咖啡與水煙',pts:12,cond:'開羅＋亞歷山大皆「遊玩」以上',kind:'group',groups:[[1,4]],level:2},
 {id:'A24',cat:'文化',icon:'🌿',name:'莎草紙與香水',pts:12,cond:'開羅＋法尤姆皆「遊玩」以上',kind:'group',groups:[[1,16]],level:2},
 {id:'A25',cat:'自然',icon:'🏜️',name:'黑白沙漠',pts:20,cond:'吉薩「住宿」以上（拜哈里耶出發）',kind:'group',groups:[[2]],level:3},
 {id:'A26',cat:'文化',icon:'🏆',name:'世界遺產巡禮',pts:20,cond:'埃及 7 處世界遺產所在省份中，5 省以上「遊玩」',kind:'count',prefs:WH_PREFS,n:5,level:2},
 {id:'A27',cat:'文化',icon:'🏺',name:'古埃及三都',pts:18,cond:'孟菲斯（吉薩）＋底比斯（盧克索）＋阿馬爾納（明亞）皆「遊玩」以上',kind:'group',groups:[[2,22,18]],level:2},
 {id:'A28',cat:'文化',icon:'📚',name:'燈塔與圖書館',pts:14,cond:'亞歷山大「遊玩」以上',kind:'group',groups:[[4]],level:2},
 {id:'A29',cat:'祭典',icon:'☀️',name:'阿布辛貝太陽節',pts:16,cond:'阿斯旺「遊玩」以上（2/22 或 10/22 到訪更佳）',kind:'group',groups:[[23]],level:2},
 {id:'A30',cat:'祭典',icon:'🎉',name:'盧克索奧佩特節',pts:15,cond:'盧克索「遊玩」以上',kind:'group',groups:[[22]],level:2},
 {id:'A31',cat:'文化',icon:'👑',name:'全境制霸',pts:45,cond:'埃及 27 省皆「遊玩」以上（手動）',kind:'manual',prefs:Object.keys(PROVINCES).map(Number),level:2},
 {id:'A32',cat:'影劇',icon:'🎬',name:'埃及豔后之路',pts:14,cond:'亞歷山大＋阿斯旺皆「遊玩」以上',kind:'group',groups:[[4,23]],level:2},
 {id:'A33',cat:'影劇',icon:'🕵️',name:'尼羅河謀殺案',pts:13,cond:'盧克索＋開羅皆「遊玩」以上',kind:'group',groups:[[22,1]],level:2},
 {id:'A34',cat:'影劇',icon:'🧟',name:'神鬼傳奇之旅',pts:13,cond:'開羅＋阿斯旺皆「遊玩」以上',kind:'group',groups:[[1,23]],level:2},
 {id:'A35',cat:'文化',icon:'🐱',name:'法老與貓',pts:12,cond:'東部省「遊玩」以上（布巴斯提斯）',kind:'group',groups:[[10]],level:2},
 {id:'A36',cat:'神廟',icon:'🗿',name:'拉美西斯之路',pts:16,cond:'阿布辛貝＋丹德拉＋阿拜多斯皆「遊玩」以上',kind:'group',groups:[[23,21,20]],level:2},
 {id:'A37',cat:'自然',icon:'🌵',name:'綠洲四縣',pts:18,cond:'錫瓦＋哈里杰＋法尤姆＋拜哈里耶皆「遊玩」以上',kind:'group',groups:[[6,25,16,2]],level:2},
];
const MANUAL_ACH = ACH.find(a=>a.kind==='manual');

/* ============================================================
   英文翻譯
   ============================================================ */
const I18N = {};
I18N.en = {
 '建立我的地圖':'Create My Map','查看已有地圖':'Open My Maps','進入地圖':'Open Map','切換':'Switch',
 '操作說明':'How it works','建立你的制霸地圖':'Create your conquest map',
 '填寫地圖名稱與編輯密碼（可留空），系統會產生一組專屬識別碼。純靜態版沒有雲端：識別碼與密碼都只存在這台裝置的瀏覽器裡，無法重設，建議截圖備份。':'Give your map a name and an edit password (optional); the site generates a unique code. This is a fully static site with no cloud: the code and password live only in this browser and cannot be reset — screenshot them for backup.',
 '點選省份，認識埃及':'Tap a governorate to explore Egypt',
 '在地圖上點選省份，右側面板會顯示在地美食、景點與節慶介紹。':'Select a governorate on the map and the side panel shows its local food, sights and festivals.',
 '記錄每一趟旅程':'Log every trip','為每次造訪選擇「途經／遊玩／住宿／長居」，可填寫日期、評分與心得，並勾選在該省達成的特殊成就。':'For every visit choose Passing / Sightseeing / Stay / Long-term, add a date, rating and notes, and tick achievements earned in that governorate.',
 '累積分數、升級等級':'Earn points, level up','造訪層級越高，得分越多；同省重複造訪、地區全制霸與特殊成就，都能帶來額外加分。':'The deeper your visit, the more points you earn; repeat visits, full region conquest and special achievements all add bonus points.',
 '分享制霸戰報':'Share your conquest report','點擊頂欄的戰報按鈕，產生制霸戰報文字、匯出戰報圖片；也能匯出資料檔，帶到另一台裝置繼續記錄。':'Hit the report button in the top bar to generate a text report, export it as an image, or export your data file to continue on another device.',
 '計分說明':'Scoring','途經':'Passing','途經、轉乘':'Passing through, transfer','遊玩':'Sightseeing','觀光、一日遊':'Sightseeing, day trip','住宿':'Stay','過夜住宿':'Overnight stay','長居':'Long-term','長期居住':'Long-term living','重複造訪':'Repeat visit','再+2':'+2 more','同一省份多次造訪':'Multiple visits to the same governorate',
 '每個省份只要有一筆旅程就會計分，造訪層級越高、加分越多。該地區全部省份皆造訪可獲「地區制霸」加成，全數「住宿」以上再加成；特殊成就另行加分。同一省份計分以最高造訪層級為準。':'A governorate scores as soon as it has one logged trip; higher tiers earn more. Conquer all governorates of a region for a region bonus, and an extra bonus if all are Stay or deeper; special achievements add separately. A governorate counts at its best tier only.',
 '特殊成就':'Achievements','查看全部成就':'View all achievements',
 '金字塔奇觀':'Pyramid Wonder','· 吉薩金字塔':'· Giza Pyramids','神廟三傑':'Temple Trinity','· 卡納克・阿布辛貝・丹德拉':'· Karnak · Abu Simbel · Dendera','紅海潛水':'Red Sea Diving','· 赫爾格達・沙姆沙伊赫':'· Hurghada · Sharm El Sheikh','世界遺產巡禮':'World Heritage Tour','· 埃及 7 處世界遺產':'· Egypt\'s 7 UNESCO sites',
 '完整功能':'Features','省份評分':'Rate governorates','為每個省份加上你的主觀評價':'Add your own star rating to every governorate','進入地圖評分':'Rate on the map','旅遊建議':'Travel suggestions','依你的足跡推薦下一趟旅程':'Suggestions based on your footsteps and unfinished achievements','查看建議':'See suggestions','上傳照片':'Upload photos','把旅途照片掛到地圖上（僅存本機）':'Pin your trip photos onto the map (local only)','進入地圖上傳':'Upload on the map','好友排行':'Friend leaderboard','匯入好友資料檔，本機比拚制霸進度':'Import friends\' data files and compare conquest progress locally','打開排行':'Open leaderboard',
 '埃及制霸地圖 · 純靜態版 — 所有資料僅存於本機瀏覽器（localStorage），不提供雲端儲存服務。':'Egypt Conquest Map · Static version — all data stays in your browser (localStorage); no cloud storage is provided.','省份邊界 © geoBoundaries（ODbL）· 地圖渲染 Leaflet · 介面 MDUI 2':'Governorate boundaries © geoBoundaries (ODbL) · Map by Leaflet · UI by MDUI 2',
 '點選省份查看介紹 · 滾輪縮放 / 拖曳移動':'Tap a governorate for details · Scroll to zoom / drag to pan','造訪層級':'Visit tiers','未造訪':'Not visited','途經 +2':'Passing +2','遊玩 +5':'Sightseeing +5','住宿 +10':'Stay +10','長居 +20':'Long-term +20',
 '點選地圖上的省份，':'Tap a governorate on the map,','查看在地美食、景點與節慶，並記錄你的旅程。':'to see local food, sights and festivals, and log your trips.','隨機探索':'Explore randomly',
 '最佳層級':'Best tier','本站得分':'Points here','紀錄':'Trips','分':'pts','筆':'trips','在地美食':'Local food','名所景點':'Sights','節慶行事':'Festivals','☆ 想去':'☆ Want to go','★ 已想去':'★ Want to go','旅途照片':'Trip photos','僅存本機 · 不隨資料檔匯出':'Local only · not exported with data files','旅程紀錄':'Trip log','清除此省':'Clear this governorate','已鎖定編輯 — 點擊頂欄鎖頭解鎖後才能記錄旅程':'Editing locked — unlock with the lock icon in the top bar before logging trips','新增旅程':'Add Trip',
 '建立我的制霸地圖':'Create My Conquest Map','為地圖命名並設定編輯密碼（可留空），系統會產生一組專屬識別碼。':'Name your map and set an edit password (optional); a unique code will be generated.','地圖名稱':'Map name','例：我的尼羅河之旅、開羅社畜的週末':'e.g. My Nile Journey, Weekend in Cairo','編輯密碼（可留空）':'Edit password (optional)','再次輸入密碼':'Confirm password','取消':'Cancel','建立地圖':'Create Map',
 '查看已有地圖':'Open My Maps','輸入識別碼開啟這台裝置上已建立的地圖。':'Enter a code to open a map created on this device.','識別碼　例：EGY-A3K9':'Code · e.g. EGY-A3K9','純靜態版沒有雲端伺服器：識別碼無法跨裝置讀取資料，只在本機生效。':'Static site, no cloud: a code only works on this device.','本機已建立的地圖（點選即開啟）：':'Maps created on this device (tap to open):','從資料檔匯入':'Import from file','開啟地圖':'Open Map',
 '解鎖編輯':'Unlock editing','輸入這張地圖的編輯密碼以解鎖編輯功能。':'Enter this map\'s edit password to unlock editing.','編輯密碼':'Edit password','解鎖':'Unlock',
 '記錄旅程':'Log Trip','日期':'Date','評分':'Rating','心得':'Notes','在這一省達成的成就':'Achievements earned in this governorate','儲存旅程':'Save Trip','該省已達成的成就':'Achievements already earned here',
 '願望清單':'Wishlist','把想去的省份收進清單，或回顧你的旅程足跡。':'Save governorates you want to visit, or revisit your timeline.','想去':'Want to go','旅程時間線':'Timeline','還沒有想去的地方 —':'No places on your wishlist yet —','在省份面板按下「☆ 想去」收藏，或在地圖上找靈感。':'Tap "☆ Want to go" on a governorate panel, or browse the map for ideas.','定位':'Locate','取消想去':'Remove','還沒有任何旅程紀錄 —':'No trips logged yet —','點選省份，按下「新增旅程」開始記錄足跡。':'Tap a governorate and hit "Add Trip" to start your footprint.','關閉':'Close',
 '達成條件後自動解鎖；標記「手動」的成就需自行勾選。點擊成就卡片可查看條件。':'Achievements unlock automatically when met; "manual" ones need to be ticked. Tap a card to see its condition.','全部':'All','達成':'Done','未達成':'Locked',
 '制霸戰報':'Conquest Report','你的埃及制霸進度總覽，可複製文字、匯出圖片或匯出資料檔。':'An overview of your Egypt conquest progress — copy the text, export an image, or export your data file.','複製戰報':'Copy Report','匯出圖片':'Export Image','匯出資料檔':'Export Data','刪除這張地圖':'Delete this map','複製識別碼':'Copy Code',
 '依你的足跡與未完成的成就，推薦下一站。':'Next-stop suggestions based on your footsteps and unfinished achievements.',
 '純靜態版沒有雲端：請好友「匯出資料檔」傳給你，再匯入比拚 — 排行只在你自己的瀏覽器裡計算。':'No cloud here: ask friends to export their data file and send it to you, then import it — the ranking is computed only in your browser.','匯入好友資料檔':'Import friend\'s file',
 '確定？':'Are you sure?','確定':'Confirm',
 '等級':'Level','制霸':'CONQUEST','地圖':'MAP','省份':'GOVERNORATES','回憶':'MEMORIES','搜尋省份':'Search governorates','搜尋省份（中文／阿拉伯文／英文／地區）':'Search governorates (中文 / العربية / English / region)','清除':'Clear','查看制霸戰報':'View conquest report','編輯鎖定':'Edit lock','回首頁':'Back to home','成就':'Achievements',
 '· 造訪':' · ','星':'stars','評為':'Rated','顆星':'stars','已清除評分':'Rating cleared',
 '已記錄：':'Logged: ','等級提升！':'Level up! ','成就解鎖！':'Achievement unlocked! ','成就達成數更新：':'Achievements now: ','已加入願望清單：':'Added to wishlist: ','已從願望清單移除：':'Removed from wishlist: ','已將 ':'Rated ',' 評為 ':' with ',' 顆星':' stars','已上傳照片':'Photo uploaded','已刪除照片':'Photo deleted',
 '已建立地圖：':'Map created: ','已開啟地圖：':'Map opened: ','找不到這組識別碼，請確認是否輸入正確。':'Code not found — please double-check.','密碼錯誤，無法解鎖。':'Wrong password.','已鎖定編輯。':'Editing locked.','已解鎖編輯。':'Editing unlocked.','已複製戰報！':'Report copied!','已匯出戰報圖片。':'Report image exported.','已匯出資料檔：':'Data file exported: ','已匯入資料檔：':'Data file imported: ','資料檔格式錯誤，無法匯入。':'Invalid data file.','已刪除地圖：':'Map deleted: ','已清除「':'Cleared ','」的所有旅程紀錄與評分。':' — all trips and ratings removed.','此名稱已存在，已開啟既有地圖。':'A map with this name already exists — opened it instead.','密碼不一致，請重新輸入。':'Passwords do not match.','請輸入地圖名稱。':'Please enter a map name.','請選擇造訪層級。':'Please choose a visit tier.','日期格式不正確。':'Invalid date.','最多 5 張照片。':'Up to 5 photos.','已自動儲存。':'Autosaved.','尚未建立任何地圖 — 點擊「建立我的地圖」開始！':'No maps yet — tap "Create My Map" to begin!',
 '埃及制霸戰報':'EGYPT CONQUEST REPORT','總分':'Total score','造訪':'Visited','住宿':'Stays','平均評分':'Avg rating','次':'x','全省走透透':'All over Egypt','旅程數':'Trips','完成度':'Progress','我的足跡：':'My footprints: ','（未造訪）':' (not visited)','／':' / ','今日':'today','制霸率':'Conquest rate','點擊展開戰報…':'Tap to open the report…','全制霸':'ALL CONQUERED',
 '若你喜歡 ':'If you liked ','，可以試試 ':'，try ','！':'!','與':'and','都很棒，下一站 ':'are great — next stop: ','如何？':'?','來自成就：':'From achievement: ','第 ':'Your ',' 個省份，邁向全制霸！':'th governorate — on to full conquest!','同地區還有 ':'Same region, still unvisited: ',' 未造訪！':'!','目標：':'Goal: ',' 地區制霸！':' region conquest!','這是你第一次記錄旅程，挑個最想去的省份開始吧！':'First trip logged — pick a governorate you want most and start!','下一站：':'Next: ','（空）':' (empty)',
 '好友':'Friend','你':'You','共 ':'Total ',' 位好友':' friends','尚未匯入好友資料。':'No friend data imported yet.','全省':'governorates','省份數':'Governorates','行程數':'Trips','最高層級':'Best tier',
 '途經':'Passing','遊玩':'Sightseeing','住宿':'Stay','長居':'Long-term',
 '埃及':'EGYPT','制霸':'CONQUEST','地圖':'MAP','成就點數':'Achievement points','已達成':'Achieved','手動標記':'Mark manually','尚未造訪':'Not visited','尚未造訪：':'Not yet visited: ','識別碼':'Code','下一級':'Next level','純靜態版沒有雲端：':'No cloud here: ','請妥善備份識別碼與資料檔。':'back up your code and data file.','尚未評分':'Not rated yet','已複製識別碼：':'Code copied: '};
