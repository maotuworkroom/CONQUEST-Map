# -*- coding: utf-8 -*-
import re, json

# ---------- 动态 key 提取 ----------
html = open('index.html', encoding='utf-8').read()
ach_src = open('ach_js.txt', encoding='utf-8').read()
cnt_src = open('countries_js.txt', encoding='utf-8').read()

levels = re.findall(r"\{name:'([^']+)',icon:'[^']+',pts:(\d+)", html)
level_names = [n for n,_ in levels]

ach_names = re.findall(r"name:'([^']+)',pts:", ach_src)
ach_conds = re.findall(r"cond:'([^']+)',kind:", ach_src)

regions = re.findall(r"'[^']+':\{name:'([^']+)', ids:", cnt_src)
taglines = re.findall(r"tagline:'([^']+)',food:", cnt_src)

# ---------- 英文翻译 ----------
EN = {
 # ---- 界面（清洗 key 全量）----
 ' / 5 星':' / 5 stars',' — 請妥善備份':' — keep it safe',' 分':' pts',' 分 · ':' pts · ',
 ' 分）':' pts)',' 國':' more',' 國已評分':' rated',' 國已評，平均 ':' rated, avg ',
 ' 已存在於本機，匯入將覆蓋原有資料。確定繼續？':' already exists on this device. Importing will overwrite it. Continue?',
 ' 張照片':' photos',' 星':' stars',' 的資料（純靜態版無法跨裝置讀取）':' not found (no cloud, device-local only)',
 ' 筆紀錄將被移除，無法復原。':' record(s) will be removed. This cannot be undone.',
 ' 評為 ':' rated ',' 項：':': ','（+':' (+','+20 分':'+20 pts','+25 分':'+25 pts',
 '+30 分':'+30 pts','+45 分':'+45 pts','Natural Earth（簡化）':'Natural Earth (simplified)',
 '★ 已想去':'★ In wishlist','☆ 想去':'☆ Want to go','」 識別碼 ':' (code ',
 '」全部記錄？':'" completely?','」地區制霸：還差 ':'" region sweep: need ',
 '」將從排行中移除。':'" will be removed from the leaderboard.','」成就：還差 ':'" achievement: need ',
 '」的第 ':' #','」的記錄':' records of "','」還差 ':'" need ','【歐洲制霸戰報】':'【EUROPE CONQUEST REPORT】',
 '上傳':'Add','上傳照片':'Photo Albums','亮眼成就':'Top Achievements','亮眼成就：':'Top achievements: ',
 '住宿':'Stay','住宿 +10':'Stay +10','你的歐洲制霸進度總覽，可複製文字、匯出圖片或匯出資料檔。':'Your conquest progress at a glance — copy text, export an image or the data file.',
 '你的評價 ':'Your rating: ','例：我的歐洲公路之旅、巴黎聖誕市集':'e.g. My European road trip, Paris Christmas market',
 '依你的足跡推薦下一趟旅程':'Next-destination ideas from your travels','依你的足跡與未完成的成就，推薦下一站。':'Next-destination ideas based on your travels and unfinished achievements.',
 '僅存本機 · 不隨資料檔匯出':'Local only · not included in exports','儲存旅程':'Save Trip','先點選一個國家':'Pick a country first',
 '兩次輸入的密碼不一致':'Passwords don\'t match','再+2':'+2 more','分':'pts','分享制霸戰報':'Share your conquest report',
 '切換':'Switch','刪除':'Remove','刪除好友？':'Remove friend?','刪除照片':'Remove photo','刪除這張地圖':'Delete this map',
 '刪除這張地圖？':'Delete this map?','刪除這筆旅程？':'Delete this trip?','制霸':'CONQUEST','制霸戰報':'Conquest Report',
 '制霸足跡':'Conquest Footprint','前往國家 →':'Go to country →','勾選即認領此成就（仍需達成國家條件）':'Tick to claim (country conditions still apply)',
 '匯入失敗：不是有效的制霸資料檔':'Import failed: not a valid data file','匯入好友資料檔':'Import friend data',
 '匯入好友資料檔，本機比拚制霸進度':'Import friends\' data files and compare progress','匯出圖片':'Export image',
 '匯出圖片失敗':'Image export failed','匯出資料檔':'Export data','取消':'Cancel','取消想去':'Remove',
 '同一國家多次造訪':'Multiple visits to the same country','名所景點':'Sights','名稱':'Name','回憶':'Memories','回首頁':'Back to home',
 '國':'countries','國家':'Countries','國家評分':'Ratings','國家評分：':'Ratings: ',
 '在國家面板按下「☆ 想去」收藏，或在地圖上點選找靈感。':'tap "☆ Want to go" in a country panel or explore the map.',
 '在地圖上點選歐洲國家，右側面板會顯示在地美食、景點與祭典介紹。':'Click a country on the map to see local food, sights and festivals in the side panel.',
 '在地美食':'Local Food','在這一國達成的成就':'Achievements earned here','地區':'Region','地區制霸':'Region Sweep',
 '地區制霸 / 7':'Regions / 7','地區制霸：':'Regions: ','地區足跡':'Regions covered','地區足跡：':'Regions: ',
 '地圖':'MAP','填寫地圖名稱與編輯密碼（可留空），系統會產生一組專屬識別碼。純靜態版沒有雲端：識別碼與密碼都只存在這台裝置的瀏覽器裡，無法重設，建議截圖備份。':'Name your map and set an edit password (optional). You\'ll get a unique code. This is a fully static build — no cloud: your code and password live only in this browser and can\'t be reset. Screenshot them for backup.',
 '太厲害了 — 47 國全部造訪過，等下一段旅程啟程吧。':'Amazing — all 47 countries visited. Time to plan the next journey!',
 '好友排行':'Friend Leaderboard','完成「':'Complete "','完整功能':'Features','定位':'Locate','密碼不正確':'Incorrect password',
 '將刪除這座國家的全部旅程紀錄、國家評分與旅途照片，無法復原。':'All trips, rating and photos for this country will be deleted. This cannot be undone.',
 '尚未建立任何地圖 — 從首頁「建立我的地圖」開始。':'No maps yet — start from "Create My Map" on the home page.',
 '已上傳照片（僅存本機）':'Photo added (local only)','已刪除地圖':'Map deleted','已刪除好友':'Friend removed',
 '已刪除照片':'Photo removed','已刪除紀錄':'Record deleted','已匯入地圖「':'Map imported: "','已匯出戰報圖片':'Report image exported',
 '已匯出資料檔，請妥善保存':'Data file exported — keep it safe','已建立地圖「':'Map created: "','已清除「':'Cleared "',
 '已獲得 ':'Unlocked ','已移出願望清單':'Removed from wishlist','已移除評價':'Rating removed','已複製識別碼 ':'Code copied: ',
 '已解鎖，可以編輯了':'Unlocked — editing enabled','已記錄：':'Logged: ','已造訪':'Visited','已達最高等級':'Max level reached',
 '已鎖定編輯':'Editing locked','已鎖定編輯 — 點擊頂欄鎖頭解鎖後才能記錄旅程':'Editing locked — unlock via the padlock in the top bar to log trips',
 '已鎖定編輯，無法修改願望清單':'Editing locked — wishlist unchanged','平均 ':'avg ','建立你的制霸地圖':'Create your map',
 '建立地圖':'Create Map','建立地圖後開始收集':'Start collecting after creating a map','建立我的制霸地圖':'Create Your Conquest Map',
 '建立我的地圖':'Create My Map','建立或開啟一張地圖後，才能依足跡推薦行程':'Create or open a map for suggestions',
 '建立或開啟一張地圖後，才能依足跡推薦行程。':'Create or open a map to get suggestions.',
 '建立或開啟一張地圖後，才能收集成就':'Create or open a map to collect achievements','從資料檔匯入':'Import from file',
 '心得':'Notes','想去':'Wishlist','成就':'Ach.','成就 / ':'Achievements / ','成就加成':'Bonus','成就：':'Achievements: ',
 '我':'Me','戰報':'Report','戰報已複製':'Report copied','手動勾選認領':'Tick to claim','打開排行':'Open leaderboard',
 '找不到「':'No results for "','找不到這張地圖的資料':'Map data not found','把想去的國家收進清單，或回顧你的旅程足跡。':'Save countries you want to visit, or revisit your journey timeline.',
 '把旅途照片掛到地圖上（僅存本機）':'Pin trip photos to the map (local only)',
 '排行榜只在本機計算與顯示，不經由任何雲端。更新好友：請對方重新匯出資料檔，再匯入覆蓋同名好友即可。':'Rankings are computed and shown only on this device — no cloud. To refresh: ask your friend to re-export, then import to overwrite.',
 '搜尋國家':'Search countries','搜尋國家（中文／英文／地區）':'Search (Chinese / English / region)','操作說明':'How It Works',
 '新增旅程':'Add Trip','新增旅程 · ':'Add trip · ','旅程時間線':'Timeline','旅程紀錄':'Trips logged','旅途照片':'Trip photos',
 '旅遊建議':'Trip Suggestions','日期':'Date','最佳層級':'Best tier','未填日期':'No date','未造訪':'Not visited',
 '本機已建立的地圖（點選即開啟）：':'Maps on this device (tap to open):','本機找不到 ':'Not found on this device: ',
 '本站得分':'Country score','查看全部成就':'View all achievements','查看制霸戰報':'View conquest report',
 '查看在地美食、景點與祭典，並記錄你的旅程。':'and explore local food, sights and festivals while logging your trips.',
 '查看已有地圖':'Open Existing Map','查看建議':'View suggestions','歐洲':'Europe','歐洲制霸地圖 · 純靜態版 — 所有資料僅存於本機瀏覽器（localStorage），不提供雲端儲存服務。':'Europe Conquest Map · Static build — all data stays in this browser (localStorage); no cloud storage.',
 '歐洲制霸戰報':'Europe Conquest Report','歐洲國家邊界 © Natural Earth（簡化）（GeoJSON）· 地圖渲染 Leaflet · 介面 MDUI 2':'Country boundaries © Natural Earth (simplified) (GeoJSON) · Map by Leaflet · UI by MDUI 2',
 '正在繪製戰報圖片…':'Rendering report image…','每個國家只要有一筆旅程就會計分，造訪層級越高、加分越多。該地區全部國家皆造訪可獲「地區制霸」加成，全數「住宿」以上再加成；特殊成就另行加分。同一國家計分以最高造訪層級為準。':'Any logged trip scores points; higher tiers score more. Visiting every country in a region earns a Region Sweep bonus, all-Stay-or-better adds another; special achievements add more. Each country counts at its best tier.',
 '每國最多 ':'Max per country: ','沒有可匯出的戰報':'Nothing to export','清除':'Clear','清除「':'Clear all for "',
 '清除此國':'Clear country','為地圖命名並設定編輯密碼（可留空），系統會產生一組專屬識別碼。':'Name your map and set an edit password (optional); you\'ll get a unique code.',
 '為每個國家加上你的主觀評價':'Rate each country your way','為每次造訪選擇「途經／遊玩／住宿／長居」，可填寫日期、評分與心得，並勾選在該國達成的特殊成就。':'For each visit pick a tier — Pass Through / Sightseeing / Stay / Long Stay — add date, rating and notes, and tick achievements earned there.',
 '照片 ':'Photo ','特殊成就':'Achievements','當前制霸等級':'Current level','確定':'OK','確定？':'Are you sure?',
 '祭典行事':'Festivals','筆':' trips','等級':'Level','等級：':'Level: ','紀錄':'Records',
 '純靜態版沒有雲端伺服器：識別碼只在本機生效。要跨裝置繼續記錄，請用「匯出資料檔」把資料帶走，再在另一台裝置「從資料檔匯入」。':'No cloud server: codes work only on this device. To continue elsewhere, export your data file and import it on another device.',
 '純靜態版沒有雲端伺服器：識別碼無法跨裝置讀取資料，只在本機生效。':'No cloud server: codes only work on this device.',
 '純靜態版沒有雲端：請好友「匯出資料檔」傳給你，再匯入比拚 — 排行只在你自己的瀏覽器裡計算。':'No cloud: ask friends to export their data file and import it — rankings are computed only in your browser.',
 '累積分數、升級等級':'Earn points, level up','累計總分':'Total Score','經典首選 — 從這裡展開你的歐洲制霸':'Classic pick — start your conquest here',
 '編輯旅程 · ':'Edit trip · ','編輯鎖定':'Editing locked','總分':'Score','總分 ':'Score ','總分：':'Score: ',
 '補齊「':'Complete "','複製失敗，請手動選取戰報文字':'Copy failed — select the report text manually','複製戰報':'Copy report',
 '複製識別碼':'Copy code','覆蓋既有地圖？':'Overwrite existing map?','觀光、一日遊':'Sightseeing / day trip','解鎖':'Unlock',
 '解鎖成就':'Unlock achievement','解鎖成就 ':'Achievement unlocked: ','解鎖編輯':'Unlock Editing','計分說明':'Scoring',
 '記錄你走過的每一寸歐洲，看看你制霸了幾個國？':'Record every inch of Europe you\'ve traveled — how many countries have you conquered?',
 '記錄旅程':'Log a Trip','記錄每一趟旅程':'Log every trip','評分':'Rating','請先選擇國家':'Select a country first',
 '請填寫地圖名稱':'Please enter a map name','請輸入識別碼':'Please enter a code','請選擇圖片檔案':'Choose an image file',
 '識別碼 ':'Code ','讀取圖片失敗':'Could not read the image','距「':'Need "','輸入識別碼開啟這台裝置上已建立的地圖。':'Open a map already created on this device by its code.',
 '輸入這張地圖的編輯密碼以解鎖編輯功能。':'Enter the edit password to unlock editing.','途經':'Pass','途經 +2':'Pass +2',
 '途經、轉乘':'Transit / transfer','造訪國家':'Visited','造訪國家 / 44':'Countries / 44','造訪國家：':'Visited: ',
 '造訪層級':'Visit Tier','造訪層級越高，得分越多；同國重複造訪、地區全制霸與特殊成就，都能帶來額外加分。':'Higher tiers earn more points; revisits, region sweeps and special achievements add bonuses.',
 '進入地圖':'Enter Map','進入地圖上傳':'Upload on map','進入地圖評分':'Rate on map','遊玩':'Sightsee','遊玩 +5':'Sightsee +5',
 '過夜住宿':'Overnight stay','達成條件後自動解鎖；標記「手動」的成就需自行勾選。點擊成就卡片可查看條件。':'Auto-unlock when conditions are met; "manual" achievements are self-ticked. Tap a card for details.',
 '還沒有任何旅程紀錄 —':'No trips logged yet —','還沒有任何資料 — 建立你的地圖，或匯入好友的制霸資料檔開始比拚。':'No data yet — create your map or import a friend\'s file to compete.',
 '還沒有想去的地方 —':'No wishlist yet —','還沒記錄這座國家 — 按下方的「新增旅程」開始吧。':'No trips here yet — hit "Add Trip" below to begin.',
 '重複造訪':'Revisit','長居':'Long Stay','長居 +20':'Long Stay +20','長期居住':'Extended residence','開啟地圖':'Open Map',
 '關閉':'Close','隨機探索':'Random Pick','願望清單':'Wishlist','點擊頂欄的戰報按鈕，產生制霸戰報文字、匯出戰報圖片；也能匯出資料檔，帶到另一台裝置繼續記錄。':'Hit the report button to generate text and image reports, or export a data file to continue on another device.',
 '點星星給這座國家打分':'Tap stars to rate this country','點選國家查看介紹 · 滾輪縮放 / 拖曳移動':'Click a country to explore · scroll to zoom / drag to pan',
 '點選國家，按下「新增旅程」開始記錄足跡。':'click a country and hit "Add Trip".','點選國家，認識歐洲':'Tap countries, explore Europe',
 '點選地圖上的歐洲國家，':'Click a country on the map,','（僅存於本機，請備份）':' (local only — back it up)',
 '）的全部旅程紀錄與成就將從本機刪除，無法復原。建議先匯出備份。':'" — all trips and achievements will be deleted permanently. Export a backup first.',
 '「':'"','」':'"',' 分）':' pts)','』 識別碼 ':' (code ',
 # ---- 对话框/提示补充 ----
 '地圖名稱':'Map name','編輯密碼（可留空）':'Edit password (optional)','再次輸入密碼':'Re-enter password',
 '識別碼　例：EUR-A3K9':'Code e.g. EUR-A3K9','編輯密碼':'Edit password','（可留空）':' (optional)',
 '張照片（最多 ':' photos (max ',')':')','第 ':'#','個國家':' countries','座國家':' country',
 '資料已匯入，請重新載入頁面':'Data imported — please reload the page','不隨資料檔匯出':'not included in exports',
 '還沒記錄任何國家，先從地圖上點選一座國家開始吧。':'No visits yet — pick a country on the map to begin.',
 '推薦給你的下一站':'Suggested next stops','已造訪過，不妨再去一次':'Visited before — worth a return',
 '未完成成就的候選地':'Achievement candidate','已造訪':'Visited','總得分':'Total score','造訪地區':'Regions covered',
 '成就':'Ach.','總分 ':'Score ','成就加成':'Bonus','已加入好友「':'Friend added: "',
 ' 國':' more','（僅存於本機，請備份）':' (local only — keep it backed up)','已刪除好友':'Friend removed',
 '點星星給這座國家打分':'Tap stars to rate this country','已移除評價':'Rating removed',
 '該國家已達成的成就':'Achievements unlocked here','清除此國':'Clear country',
 '旅程時間線':'Timeline','還沒記錄任何國家，先從地圖上點選一座國家開始吧。':'No visits yet — pick a country on the map to begin.',
 '已加入願望清單':'Added to wishlist','已移出願望清單':'Removed from wishlist','太厲害了 — 47 國全部造訪過，等下一段旅程啟程吧。':'Amazing — all 47 countries visited. Time to plan the next journey!',
 # ---- ACH_CATS / 通用 ----
 '絕景':'Scenery','祭典':'Festivals','溫泉':'Onsen','美食':'Food','文化':'Culture','自然':'Nature','城堡':'Castles',
 '運動':'Sports','影劇':'Film & TV','全部':'All','達成':'Unlocked','未達成':'Locked','成就條件':'Requirement',
 '以上':'or above','皆「遊玩」以上':'all "Sightseeing" or above','皆「住宿」以上':'all "Stay" or above',
 '皆「途經」以上':'all "Pass" or above','「遊玩」以上':'"Sightseeing" or above','「住宿」以上':'"Stay" or above',
 '「途經」以上':'"Pass" or above','全國':'all countries','個國':'countries','的國家':' countries','造訪':'visited',
}

# ---- 等级名 ----
LVL = {
 '未啟程旅人':'Untrodden Traveler','新大陸訪客':'New World Visitor','城市漫遊者':'City Roamer','歐洲探索者':'Europe Explorer',
 '文化旅行家':'Culture Traveler','歐洲達人':'Europe Expert','歐陸通':'Continental Connoisseur','國家獵人':'Country Hunter',
 '歐洲制霸者':'Europe Conqueror','傳說的旅人':'Legendary Traveler',
}
# ---- 地区名 ----
REG = {
 '北歐地方':'Nordic Europe','西歐地方':'Western Europe','中歐地方':'Central Europe','南歐地方':'Southern Europe',
 '巴爾幹地方':'The Balkans','東歐地方':'Eastern Europe','歐亞地方':'Eurasia',
}
# ---- 国家简介 ----
TAG = {
 '冰島':'Iceland — the land of fire and ice, where auroras, glaciers and the Blue Lagoon meet the North Atlantic.',
 '挪威':'Norway — land of fjords, Viking grandeur, mountains and the midnight sun.',
 '瑞典':'Sweden — home of Stockholm\'s Nordic design, the Nobel Prize and Swedish meatballs.',
 '芬蘭':'Finland — the land of a thousand lakes, saunas, Santa Claus and tranquil Lapland.',
 '丹麥':'Denmark — Hans Christian Andersen\'s fairy-tale kingdom, cycling and New Nordic cuisine in Copenhagen.',
 '英國':'United Kingdom — from London\'s red phone boxes to the Scottish Highlands, a land of royalty and rock.',
 '愛爾蘭':'Ireland — the Emerald Isle: Dublin\'s pubs, the Cliffs of Moher and Celtic legends.',
 '法國':'France — the land of romance and gastronomy, from the Eiffel Tower to Provence lavender fields.',
 '荷蘭':'Netherlands — tulips, windmills, Amsterdam\'s canals and Van Gogh.',
 '比利時':'Belgium — chocolate, beer and medieval squares; Brussels, the heart of the EU.',
 '盧森堡':'Luxembourg — a pocket grand duchy of gorges, castles and European finance.',
 '瑞士':'Switzerland — the heart of the Alps: the Matterhorn, Jungfrau and precision timepieces.',
 '德國':'Germany — beer festivals and fairy-tale castles, from the Berlin Wall to Bavarian Alps.',
 '奧地利':'Austria — Vienna the music capital, Habsburg splendor and Alpine lakes.',
 '波蘭':'Poland — the heart of Central Europe: Kraków\'s old town and Warsaw\'s rebirth.',
 '捷克':'Czechia — Prague, the golden city of a hundred spires, where beer is cheaper than water.',
 '斯洛伐克':'Slovakia — the Tatra Mountains, castles and Bratislava\'s Danube banks.',
 '匈牙利':'Hungary — Budapest, the Pearl of the Danube: thermal baths and goulash.',
 '葡萄牙':'Portugal — the seafaring nation of Lisbon\'s trams and Porto\'s wine cellars.',
 '西班牙':'Spain — flamenco and paella: Gaudí\'s Barcelona and the Alhambra.',
 '義大利':'Italy — cradle of the Renaissance: the eternal cities of Rome, Florence and Venice.',
 '希臘':'Greece — birthplace of Western civilization: the Acropolis and Aegean blue-and-white isles.',
 '馬耳他':'Malta — heart of the Mediterranean: the Knights\' fortresses and blue lagoons.',
 '塞浦路斯':'Cyprus — island birthplace of Aphrodite: Mediterranean sun and ancient ruins.',
 '克羅埃西亞':'Croatia — pearl of the Adriatic: Dubrovnik\'s old town and the Plitvice Lakes.',
 '斯洛維尼亞':'Slovenia — Lake Bled\'s fairy-tale island where the Alps meet the Mediterranean.',
 '塞爾維亞':'Serbia — Belgrade where the Danube meets the Sava; the passion of the Balkans.',
 '波士尼亞與赫塞哥維納':'Bosnia & Herzegovina — Mostar\'s old bridge and Sarajevo, where East meets West.',
 '蒙特內哥羅':'Montenegro — the Bay of Kotor, a fairy-tale Adriatic fjord under black mountains.',
 '北馬其頓':'North Macedonia — Lake Ohrid\'s old town, homeland of Alexander the Great.',
 '阿爾巴尼亞':'Albania — the land of eagles: Adriatic coast and Ottoman old towns.',
 '保加利亞':'Bulgaria — land of roses: the Rila Monastery and Black Sea resorts.',
 '羅馬尼亞':'Romania — Dracula\'s castle and the Carpathians; Bucharest, the Little Paris.',
 '愛沙尼亞':'Estonia — Tallinn\'s medieval towers, a digital nation on the Baltic.',
 '拉脫維亞':'Latvia — Riga\'s Art Nouveau capital, amber and pine forests.',
 '立陶宛':'Lithuania — Vilnius\'s baroque old town and the amber coast of the Baltic.',
 '烏克蘭':'Ukraine — Kyiv\'s golden domes, rye fields and Cossack history.',
 '摩爾多瓦':'Moldova — land of wine: some of Europe\'s oldest cellars and rolling countryside.',
 '白俄羅斯':'Belarus — Minsk\'s Soviet grandeur, primeval forests and castles.',
 '俄羅斯':'Russia — the double-headed eagle spanning Eurasia: Moscow\'s Red Square and the Hermitage.',
 '土耳其':'Türkiye — where East meets West: Byzantine and Ottoman Istanbul, Cappadocia and Ephesus.',
 '喬治亞':'Georgia — cradle of wine in the Caucasus: Tbilisi\'s old town and snow peaks.',
 '亞美尼亞':'Armenia — land of Noah\'s Ark: an ancient Christian nation beneath Mount Ararat.',
 '亞塞拜然':'Azerbaijan — the Land of Fire: Baku\'s modern skyline on the Caspian.',
}
# ---- 成就名 ----
ACHN = {
 '北歐極光':'Nordic Aurora','阿爾卑斯山脈':'The Alps','地中海海岸':'Mediterranean Coast','多瑙河之旅':'Danube Journey',
 '極北之地':'Far North','波羅的海三國':'Baltic Trio','冰與火之島':'Land of Fire and Ice','愛琴海藍白':'Aegean Blue & White',
 '峽灣之王':'Fjord King','三大夜景':'Three Great Night Views','世界遺產巡禮':'World Heritage Tour','歐盟之心':'Heart of the EU',
 '申根漫步':'Schengen Stroll','文藝復興之路':'Renaissance Trail','音樂之都':'Cities of Music','巴爾幹之路':'Balkan Road',
 '北歐神話':'Norse Mythology','咖啡之國':'Coffee Nations','啤酒之旅':'Beer Journey','葡萄酒之路':'Wine Route',
 '起司巡禮':'Cheese Pilgrimage','巧克力之旅':'Chocolate Trail','海鮮饗宴':'Seafood Feast','甜點之國':'Land of Desserts',
 '歐洲溫泉巡禮':'European Spa Tour','羅馬浴場':'Roman Baths','極光獵人':'Aurora Hunter','國家公園之旅':'National Parks',
 '火山之旅':'Volcano Trail','高加索雪山':'Caucasus Peaks','童話城堡':'Fairy-Tale Castles','騎士團要塞':'Knight Fortresses',
 '多瑙河城堡':'Danube Castles','東歐古堡':'Eastern Castles','環法之路':'Tour de France','足球聖殿':'Football Temples',
 'F1 巡禮':'F1 Grand Prix','滑雪勝地':'Ski Resorts','權力遊戲拍攝地':'Game of Thrones Locations','哈利波特之旅':'Harry Potter Journey',
 '真善美之旅':'Sound of Music Trail','007 龐德之旅':'007 Bond Journey','音樂節巡禮':'Festival Circuit','歌劇院巡禮':'Opera Houses',
 '古典音樂':'Classical Music','歐洲嘉年華':'European Carnivals','聖誕市集':'Christmas Markets','跨年煙火':'New Year Fireworks',
 '仲夏節':'Midsummer',
}
# ---- 成就条件 ----
ACHC = {
 '冰島・挪威・芬蘭皆「遊玩」以上':'Iceland, Norway & Finland all "Sightseeing" or above',
 '瑞士・奧地利・法國皆「遊玩」以上':'Switzerland, Austria & France all "Sightseeing" or above',
 '西班牙・義大利・希臘皆「遊玩」以上':'Spain, Italy & Greece all "Sightseeing" or above',
 '德國・奧地利・匈牙利・羅馬尼亞皆「遊玩」以上':'Germany, Austria, Hungary & Romania all "Sightseeing" or above',
 '挪威・瑞典・芬蘭皆「途經」以上':'Norway, Sweden & Finland all "Pass" or above',
 '愛沙尼亞・拉脫維亞・立陶宛皆「遊玩」以上':'Estonia, Latvia & Lithuania all "Sightseeing" or above',
 '冰島「住宿」以上':'Stay in Iceland or above',
 '希臘「住宿」以上':'Stay in Greece or above',
 '挪威「住宿」以上':'Stay in Norway or above',
 '巴黎・倫敦・伊斯坦堡皆「遊玩」以上':'Paris, London & Istanbul all "Sightseeing" or above',
 '10 國以上「有世界遺產」且「遊玩」以上':'10+ World Heritage countries "Sightseeing" or above',
 '法國・德國・比利時・盧森堡・荷蘭皆「遊玩」以上':'France, Germany, Belgium, Luxembourg & Netherlands all "Sightseeing" or above',
 '25 國以上「途經」以上':'25+ countries "Pass" or above',
 '義大利・法國・德國皆「遊玩」以上':'Italy, France & Germany all "Sightseeing" or above',
 '奧地利・德國・捷克皆「遊玩」以上':'Austria, Germany & Czechia all "Sightseeing" or above',
 '塞爾維亞・波黑・黑山・北馬其頓・阿爾巴尼亞・保加利亞皆「遊玩」以上':'Serbia, Bosnia, Montenegro, N. Macedonia, Albania & Bulgaria all "Sightseeing" or above',
 '冰島・挪威・丹麥皆「遊玩」以上':'Iceland, Norway & Denmark all "Sightseeing" or above',
 '義大利・法國・奧地利皆「遊玩」以上':'Italy, France & Austria all "Sightseeing" or above',
 '德國・捷克・比利時皆「遊玩」以上':'Germany, Czechia & Belgium all "Sightseeing" or above',
 '法國・西班牙・葡萄牙・義大利皆「遊玩」以上':'France, Spain, Portugal & Italy all "Sightseeing" or above',
 '瑞士・法國・荷蘭皆「遊玩」以上':'Switzerland, France & Netherlands all "Sightseeing" or above',
 '比利時・瑞士皆「遊玩」以上':'Belgium & Switzerland all "Sightseeing" or above',
 '葡萄牙・西班牙・希臘皆「遊玩」以上':'Portugal, Spain & Greece all "Sightseeing" or above',
 '法國・義大利・奧地利皆「遊玩」以上':'France, Italy & Austria all "Sightseeing" or above',
 '匈牙利・捷克・冰島皆「遊玩」以上':'Hungary, Czechia & Iceland all "Sightseeing" or above',
 '英國・匈牙利・土耳其皆「遊玩」以上':'UK, Hungary & Türkiye all "Sightseeing" or above',
 '北歐四國任一「住宿」以上':'Stay in any Nordic country or above',
 '克羅埃西亞・斯洛維尼亞・黑山皆「遊玩」以上':'Croatia, Slovenia & Montenegro all "Sightseeing" or above',
 '冰島・義大利・希臘皆「遊玩」以上':'Iceland, Italy & Greece all "Sightseeing" or above',
 '喬治亞・亞美尼亞・亞塞拜然皆「遊玩」以上':'Georgia, Armenia & Azerbaijan all "Sightseeing" or above',
 '德國・法國・捷克皆「遊玩」以上':'Germany, France & Czechia all "Sightseeing" or above',
 '馬耳他・希臘・塞浦路斯皆「遊玩」以上':'Malta, Greece & Cyprus all "Sightseeing" or above',
 '匈牙利・斯洛伐克・羅馬尼亞皆「遊玩」以上':'Hungary, Slovakia & Romania all "Sightseeing" or above',
 '波蘭・愛沙尼亞・拉脫維亞・立陶宛皆「遊玩」以上':'Poland, Estonia, Latvia & Lithuania all "Sightseeing" or above',
 '法國・義大利・西班牙皆「遊玩」以上':'France, Italy & Spain all "Sightseeing" or above',
 '英國・法國・德國・義大利皆「遊玩」以上':'UK, France, Germany & Italy all "Sightseeing" or above',
 '英國・義大利・比利時皆「遊玩」以上':'UK, Italy & Belgium all "Sightseeing" or above',
 '瑞士・奧地利・法國皆「遊玩」以上':'Switzerland, Austria & France all "Sightseeing" or above',
 '克羅埃西亞・西班牙・冰島皆「遊玩」以上':'Croatia, Spain & Iceland all "Sightseeing" or above',
 '英國「遊玩」以上':'UK "Sightseeing" or above','奧地利「遊玩」以上':'Austria "Sightseeing" or above',
 '英國・瑞士・奧地利皆「遊玩」以上':'UK, Switzerland & Austria all "Sightseeing" or above',
 '塞爾維亞・克羅埃西亞・英國皆「遊玩」以上':'Serbia, Croatia & UK all "Sightseeing" or above',
 '義大利・法國・奧地利皆「遊玩」以上':'Italy, France & Austria all "Sightseeing" or above',
 '奧地利・德國・捷克皆「遊玩」以上':'Austria, Germany & Czechia all "Sightseeing" or above',
 '義大利・西班牙・葡萄牙・荷蘭皆「遊玩」以上':'Italy, Spain, Portugal & Netherlands all "Sightseeing" or above',
 '德國・奧地利・法國皆「遊玩」以上':'Germany, Austria & France all "Sightseeing" or above',
 '英國・法國・德國皆「遊玩」以上':'UK, France & Germany all "Sightseeing" or above',
 '瑞典・芬蘭・丹麥皆「遊玩」以上':'Sweden, Finland & Denmark all "Sightseeing" or above',
}

# ---------- 组装 ----------
d = dict(EN)
for k,v in LVL.items(): d[k]=v
for k,v in REG.items(): d[k]=v
for k,v in TAG.items(): d[k]=v
for k,v in ACHN.items(): d[k]=v
for k,v in ACHC.items(): d[k]=v

# JSON 序列化（保持可读）
body = json.dumps(d, ensure_ascii=False, indent=1)
i18n_block = "const I18N = {\n  'en': " + body.replace('\n', '\n  ') + "\n};"
open('i18n_js.txt','w',encoding='utf-8').write(i18n_block)
print('en keys:', len(d))
print('i18n block chars:', len(i18n_block))
