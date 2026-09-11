
/* ============================================================
   埃及制霸地圖 — 應用邏輯
   ============================================================ */
const $ = id => document.getElementById(id);
let map=null, geoLayer=null, labelLayer=null, selectedPref=null, editRecIdx=null;
let psSel=-1;

function snack(msg){ try{ mdui.snackbar({message: t(msg)}); }catch(e){ alert(t(msg)); } }
function openDlg(id){ const d=$(id); if(d) d.open = true; }
function closeDlg(id){ const d=$(id); if(d) d.open = false; }
function today(){ const d=new Date(); return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0'); }
function confirmDlg(title,desc,fn){
  $('confirmTitle').textContent=t(title);
  $('confirmDesc').textContent=t(desc);
  $('btnConfirmOk').onclick=()=>{ closeDlg('dlgConfirm'); fn&&fn(); };
  openDlg('dlgConfirm');
}

/* ============ 地圖 ============ */
function centroid(f){
  let xs=0,ys=0,n=0;
  const coords=f.geometry.type==='Polygon'?f.geometry.coordinates:f.geometry.coordinates[0];
  for(const ring of coords){ for(const [x,y] of ring){ xs+=x; ys+=y; n++; } }
  return [ys/n, xs/n];
}
function fillFor(best){
  return best===0?'#F0E7DF':best===1?'#F3CDBF':best===2?'#E89376':best===3?'#D2603F':'#B02A1A';
}
function setupMap(){
  if(map) return;
  map = L.map('map',{zoomControl:false,minZoom:5,maxZoom:9}).setView([26.8,30.8],6);
  const BOUNDS=[[21.9,24.5],[31.9,37.1]];
  map.fitBounds(BOUNDS);
  map.options.minZoom=5;
  const gj = window.EGYPT_GEOJSON;
  geoLayer = L.geoJSON(gj,{
    style: f=>{ const d=curData(); const best=d?prefInfo(d)[f.properties.id].best:0; return {fillColor:fillFor(best),color:'#fff',weight:1.1,fillOpacity:1}; },
    onEachFeature:(f,layer)=>{
      layer.on('click',()=>selectPref(f.properties.id));
      layer.on('mouseover',()=>{
        const d=curData(); const info=d?prefInfo(d)[f.properties.id]:null;
        const tier = info && info.best>0 ? t(TYPE_NAME[info.best]) : t('未造訪');
        layer.bindTooltip(t(PROVINCES[f.properties.id].ar)+' · '+tier,{direction:'top',className:'pref-hover-tip',sticky:true}).openTooltip();
      });
      layer.on('mouseout',()=>{ layer.unbindTooltip(); });
    }
  }).addTo(map);
  labelLayer = L.layerGroup().addTo(map);
  for(const f of gj.features){
    const p=PROVINCES[f.properties.id];
    const c=centroid(f);
    L.marker(c,{interactive:false,icon:L.divIcon({className:'pref-label',html:p.ar,iconSize:[0,0]})}).addTo(labelLayer);
  }
  map.on('zoomend',()=>{ labelLayer.eachLayer(l=>{ l.setOpacity(map.getZoom()>=5.5?1:0); }); });
  map.on('click',(e)=>{ if(!e.originalEvent.target.closest('.leaflet-interactive')){ selectedPref=null; renderPanel(); } });
}
function selectPref(id,fly){
  selectedPref=id;
  if(geoLayer){
    geoLayer.eachLayer(l=>{
      const f=l.feature;
      l.setStyle({stroke:'#fff',strokeWidth:1.1});
      if(f.properties.id===id){ l.setStyle({stroke:'#C29A2B',strokeWidth:2.6}); if(fly){ map.flyTo(centroid(f),Math.max(map.getZoom(),6.4),{duration:.8}); } }
    });
  }
  renderPanel();
}
function refreshMapFill(){
  if(!geoLayer) return;
  const d=curData();
  geoLayer.eachLayer(l=>{
    const best=d?prefInfo(d)[l.feature.properties.id].best:0;
    l.setStyle({fillColor:fillFor(best),color:'#fff',strokeWidth:(selectedPref===l.feature.properties.id?2.6:1.1)});
  });
}
function flashPref(id){
  if(!geoLayer) return;
  geoLayer.eachLayer(l=>{
    if(l.feature.properties.id===id){
      const el=l.getElement(); if(el){ el.classList.remove('just-logged'); void el.offsetWidth; el.classList.add('just-logged'); }
      setTimeout(()=>{ el && el.classList.remove('just-logged'); },1500);
    }
  });
}

/* ============ 面板 ============ */
function chipEl(x){
  const c=document.createElement('mdui-chip'); c.variant='assist'; c.textContent=t(x); return c;
}
function renderPanel(){
  const d=curData();
  const empty=$('panelEmpty'), content=$('panelContent');
  if(!d || !selectedPref){
    empty.classList.remove('hidden'); content.classList.add('hidden');
    $('panelWrap').scrollTop=0;
    return;
  }
  empty.classList.add('hidden'); content.classList.remove('hidden');
  const p=PROVINCES[selectedPref], pd=d.prefs[selectedPref], info=prefInfo(d)[selectedPref];
  const head=$('panelHead');
  $('pRegion').textContent=t(REGIONS[p.region].name);
  $('pNameJa').textContent=p.ar;
  $('pNameZh').textContent=prefName(p);
  $('pTagline').textContent=t(p.tagline);
  $('pBest').textContent = info.best>0 ? t(TYPE_NAME[info.best]) : t('未造訪');
  $('pPts').textContent = info.best>0 ? TYPE_PTS[info.best] : 0;
  $('pCount').textContent = info.count;
  const pimg = PREF_IMG[selectedPref];
  head.classList.toggle('has-photo', pd.photos.length>0 || !!pimg);
  head.style.backgroundImage = pd.photos.length>0 ? `url("${pd.photos[0]}")` : (pimg ? `url("${pimg}")` : 'none');
  const reg=document.createElement('span');
  const fbox=$('pFood'); fbox.innerHTML=''; p.food.forEach(x=>fbox.appendChild(chipEl(x)));
  const sbox=$('pSpots'); sbox.innerHTML=''; p.spots.forEach(x=>sbox.appendChild(chipEl(x)));
  const mbox=$('pMatsuri'); mbox.innerHTML=''; p.matsuri.forEach(x=>mbox.appendChild(chipEl(x)));
  const wt=$('btnWishToggle');
  wt.textContent=pd.wish?t('★ 已想去'):t('☆ 想去');
  wt.style.setProperty('--mdui-button-container-color', pd.wish?'rgba(194,154,43,.16)':'');
  renderStars(pd.rate);
  renderPhotos(pd);
  renderRecords(pd,info);
  $('pLockHint').classList.toggle('hidden', isUnlocked());
  $('btnAddRecord').disabled = !isUnlocked();
  $('btnClearPref').disabled = !isUnlocked();
  $('panelWrap').scrollTop=0;
}
function renderStars(rate){
  const box=$('rateStars'); box.innerHTML='';
  const locked=!isUnlocked();
  for(let i=1;i<=5;i++){
    const b=document.createElement('button');
    b.type='button'; b.className='rate-star'+(i<=rate?' on':'')+(locked?' locked':'');
    b.textContent='★';
    if(!locked) b.onclick=()=>{
      const d=curData();
      if(d.prefs[selectedPref].rate===i){ d.prefs[selectedPref].rate=0; snack(t('已清除評分')); }
      else{ d.prefs[selectedPref].rate=i; snack(t('已將 ')+prefName(PROVINCES[selectedPref])+t(' 評為 ')+'★'.repeat(i)); }
      d.updated=Date.now(); saveCur(); renderStars(d.prefs[selectedPref].rate); refreshApp();
    };
    box.appendChild(b);
  }
  $('rateNote').textContent = rate>0 ? '★'.repeat(rate)+' · '+t('評為')+rate+t('顆星') : t('尚未評分');
}
function renderPhotos(pd){
  const box=$('pfPhotos'); box.innerHTML='';
  pd.photos.forEach((src,i)=>{
    const w=document.createElement('div'); w.className='pf-photo';
    const img=document.createElement('img'); img.src=src; img.alt='';
    img.onclick=()=>{ $('photoBigWrap').innerHTML=`<img src="${src}" alt=""><div class="pb-cap">${pd.records.length} · ${prefName(PROVINCES[selectedPref])}</div>`; openDlg('dlgPhoto'); };
    const del=document.createElement('button'); del.className='pf-del'; del.textContent='✕';
    del.onclick=e=>{ e.stopPropagation(); pd.photos.splice(i,1); curData().updated=Date.now(); saveCur(); renderPanel(); refreshApp(); snack(t('已刪除照片')); };
    w.appendChild(img); w.appendChild(del); box.appendChild(w);
  });
  if(pd.photos.length<5){
    const add=document.createElement('button'); add.className='pf-add'; add.type='button';
    add.innerHTML='<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>'+t('上傳');
    add.onclick=()=>{ $('photoInput').click(); };
    box.appendChild(add);
  }
}
function recordRow(rec,i){
  const d=document.createElement('div'); d.className='record-row';
  d.onclick=()=>{ if(!isUnlocked()) return; editRecIdx=i; openRecordDlg(); };
  const top=document.createElement('div'); top.className='rr-top';
  const type=document.createElement('span'); type.className='rr-type'; type.style.background=TYPE_COLOR[rec.type]; type.textContent=t(TYPE_NAME[rec.type]);
  const date=document.createElement('span'); date.className='rr-date'; date.textContent=rec.date||'—';
  const stars=document.createElement('span'); stars.className='rr-stars'; stars.textContent=rec.rating?'★'.repeat(rec.rating):'';
  top.appendChild(type); top.appendChild(date); top.appendChild(stars);
  d.appendChild(top);
  if(rec.note){ const n=document.createElement('div'); n.className='rr-note'; n.textContent=rec.note; d.appendChild(n); }
  const hint=document.createElement('div'); hint.className='rr-edit-hint'; hint.textContent='✎';
  d.appendChild(hint);
  return d;
}
function renderRecords(pd,info){
  const box=$('pRecords'); box.innerHTML='';
  if(!pd.records.length){
    const e=document.createElement('div'); e.className='record-empty';
    e.textContent=t('還沒有任何旅程紀錄 —')+' '+t('點選省份，按下「新增旅程」開始記錄足跡。');
    box.appendChild(e); return;
  }
  pd.records.forEach((r,i)=>box.appendChild(recordRow(r,i)));
}
function isUnlocked(){
  const r=registry(); const m=r.created.find(x=>x.id===r.active);
  return !m || !m.pass || m.unlocked===true;
}

/* ============ 新增／編輯旅程 ============ */
function openRecordDlg(){
  if(!isUnlocked()){ snack(t('已鎖定編輯 — 點擊頂欄鎖頭解鎖後才能記錄旅程')); return; }
  const d=curData(); const p=PROVINCES[selectedPref];
  $('recTitle').textContent = p.ar+' · '+prefName(p);
  const oldRec = editRecIdx!=null ? d.prefs[selectedPref].records[editRecIdx] : null;
  $('recDate').value = oldRec ? (oldRec.date||today()) : today();
  $('recNote').value = oldRec ? (oldRec.note||'') : '';
  $('recRating').value = oldRec ? (oldRec.rating||4) : 4;
  updateRatingVal();
  $('recType').value = oldRec ? String(oldRec.type||2) : '2';
  renderRecAch(d, oldRec ? (oldRec.ach||[]) : []);
  openDlg('dlgRecord');
}
function updateRatingVal(){
  const v=Number($('recRating').value)||0;
  $('recRatingVal').textContent = v>0 ? '★'.repeat(v)+'☆'.repeat(5-v) : '—';
}
function renderRecAch(d,checked){
  const info=prefInfo(d);
  const list=[];
  for(const a of ACH){
    const relevant = a.kind==='manual' || (a.kind==='group' && a.groups.some(g=>g.includes(selectedPref)));
    if(relevant) list.push(a);
  }
  const box=$('recAch');
  $('recAchField').classList.toggle('hidden', list.length===0);
  box.innerHTML='';
  list.forEach(a=>{
    const auto = a.kind!=='manual' && achGot(a,info,[]);
    const label=document.createElement('label'); label.className='ach-check';
    const cb=document.createElement('mdui-checkbox'); cb.value=a.id; cb.checked=auto||checked.includes(a.id);
    cb.disabled=auto;
    label.innerHTML=`<span class="ac-ic">${a.icon}</span><span class="ac-t"><b>${t(a.name)}</b><span>${t(a.cond)}</span></span><span class="ac-p">+${a.pts}</span>`;
    label.insertBefore(cb,label.firstChild);
    cb.addEventListener('change',()=>{});
    box.appendChild(label);
  });
}
function saveRecord(){
  const d=curData(); const p=PROVINCES[selectedPref];
  if(!isUnlocked()){ snack(t('已鎖定編輯 — 點擊頂欄鎖頭解鎖後才能記錄旅程')); return; }
  const type=Number($('recType').value)||2;
  if(!type){ snack(t('請選擇造訪層級。')); return; }
  const date=$('recDate').value||'';
  const rating=Number($('recRating').value)||0;
  const note=$('recNote').value.trim();
  const ach=[]; $('recAch').querySelectorAll('mdui-checkbox').forEach(c=>{ if(c.checked) ach.push(c.value); });
  const manualAch = ach.includes(MANUAL_ACH.id);
  const rec={type,date,rating,note,ach};
  const before = computeScore(d);
  if(editRecIdx!=null){
    d.prefs[selectedPref].records[editRecIdx]=rec;
  }else{
    d.prefs[selectedPref].records.push(rec);
  }
  if(manualAch && !d.ach.manual.includes(MANUAL_ACH.id)) d.ach.manual.push(MANUAL_ACH.id);
  if(!manualAch && d.ach.manual.includes(MANUAL_ACH.id)) d.ach.manual=d.ach.manual.filter(x=>x!==MANUAL_ACH.id);
  d.updated=Date.now(); saveCur();
  const after=computeScore(d);
  editRecIdx=null; closeDlg('dlgRecord');
  renderPanel(); refreshApp();
  flashPref(selectedPref);
  snack(t('已記錄：')+p.ar+' '+t(TYPE_NAME[type])+' +'+TYPE_PTS[type]+' '+t('分'));
  const newAch=after.achList.filter(x=>x.got && !before.achList.find(y=>y.a.id===x.a.id));
  newAch.forEach(x=>{ setTimeout(()=>snack(t('成就解鎖！')+t(x.a.name)+' +'+x.a.pts+' '+t('分')),600); });
  const lvBefore=levelOf(before.total), lvAfter=levelOf(after.total);
  if(lvAfter.idx>lvBefore.idx){ setTimeout(()=>snack(t('等級提升！')+t(lvAfter.lv.name)+' '+lvAfter.lv.icon),1200); }
  if(newAch.length){ setTimeout(()=>snack(t('成就達成數更新：')+after.achList.filter(x=>x.got).length),1800); }
}

/* ============ 願望清單／時間線 ============ */
let wishTab='wish';
function openWish(){ if(!curData()){ snack(t('尚未建立任何地圖 — 點擊「建立我的地圖」開始！')); return; } wishTab='wish'; renderWishDialog(); openDlg('dlgWish'); }
function renderWishDialog(){
  const d=curData();
  const wishIds=Object.keys(d.prefs).filter(id=>d.prefs[id].wish);
  $('wtWishN').textContent=wishIds.length;
  $('wtWish').classList.toggle('active',wishTab==='wish');
  $('wtTl').classList.toggle('active',wishTab==='tl');
  const body=$('wishBody'); body.innerHTML='';
  if(wishTab==='wish'){
    const wishIds=Object.keys(d.prefs).filter(id=>d.prefs[id].wish).map(Number);
    if(!wishIds.length){
      body.innerHTML=`<div class="wish-empty">${t('還沒有想去的地方 —')}<br>${t('在省份面板按下「☆ 想去」收藏，或在地圖上找靈感。')}</div>`;
      return;
    }
    const grid=document.createElement('div'); grid.className='wish-grid';
    wishIds.forEach(id=>{
      const p=PROVINCES[id];
      const c=document.createElement('div'); c.className='wish-card';
      c.innerHTML=`<h4>${p.ar}<span class="wz">${prefName(p)}</span></h4><div class="w-region">${t(REGIONS[p.region].name)}</div><div class="w-tag">${t(p.tagline)}</div>`;
      const acts=document.createElement('div'); acts.className='w-acts';
      const go=document.createElement('mdui-button'); go.variant='tonal'; go.textContent=t('定位'); go.style.flex='1';
      go.onclick=()=>{ closeDlg('dlgWish'); selectPref(id,true); };
      const rm=document.createElement('mdui-button'); rm.variant='text'; rm.textContent=t('取消想去');
      rm.onclick=()=>{ d.prefs[id].wish=false; d.updated=Date.now(); saveCur(); renderWishDialog(); refreshApp(); snack(t('已從願望清單移除：')+p.ar); };
      acts.appendChild(go); acts.appendChild(rm); c.appendChild(acts);
      grid.appendChild(c);
    });
    body.appendChild(grid);
  }else{
    const items=[];
    for(const id of Object.keys(d.prefs)){
      d.prefs[id].records.forEach((r,i)=>{
        items.push({id:Number(id),rec:r,idx:i,date:r.date||'9999'});
      });
    }
    items.sort((a,b)=>a.date<b.date?-1:a.date>b.date?1:0);
    if(!items.length){
      body.innerHTML=`<div class="wish-empty">${t('還沒有任何旅程紀錄 —')}<br>${t('點選省份，按下「新增旅程」開始記錄足跡。')}</div>`;
      return;
    }
    const list=document.createElement('div'); list.className='tl-list';
    items.forEach(it=>{
      const p=PROVINCES[it.id];
      const row=document.createElement('div'); row.className='tl-item';
      row.innerHTML=`<div class="tl-date">${it.rec.date||'—'}</div>
        <div class="tl-main"><div class="tl-top"><span class="tl-name">${p.ar}<span class="wz">${prefName(p)}</span></span><span class="tl-type t${it.rec.type}">${t(TYPE_NAME[it.rec.type])}</span>${it.rec.rating?`<span class="tl-rt">${'★'.repeat(it.rec.rating)}</span>`:''}</div>
        ${it.rec.note?`<div class="tl-note">${it.rec.note}</div>`:''}</div>`;
      row.onclick=()=>{ closeDlg('dlgWish'); selectPref(it.id,true); };
      list.appendChild(row);
    });
    body.appendChild(list);
  }
}

/* ============ 成就 ============ */
let achCat='全部';
function openAch(){ if(!curData()){ snack(t('尚未建立任何地圖 — 點擊「建立我的地圖」開始！')); return; } achCat='全部'; renderAchDialog(); openDlg('dlgAch'); }
function renderAchDialog(){
  const d=curData(); const sc=computeScore(d);
  const got=sc.achList.filter(x=>x.got).length;
  $('achSummary').innerHTML=`${t('達成')} <b>${got}</b> / ${ACH.length} · ${t('成就點數')} <b>${sc.achPts}</b> ${t('分')}`;
  const cats=$('achCats'); cats.innerHTML='';
  ACH_CATS.forEach(c=>{
    const b=document.createElement('button'); b.className='ach-cat'+(achCat===c?' on':''); b.textContent=t(c);
    b.onclick=()=>{ achCat=c; renderAchDialog(); };
    cats.appendChild(b);
  });
  const grid=$('achGrid'); grid.innerHTML='';
  const list=sc.achList.filter(x=>achCat==='全部'||x.a.cat===achCat);
  if(!list.length){ grid.innerHTML='<div class="sug-empty">—</div>'; }
  list.forEach(({a,got})=>{
    const c=document.createElement('div'); c.className='ach-item'+(got?' got':'');
    const info=prefInfo(d);
    let progressTxt='';
    if(a.kind==='group'){
      const g=a.groups[0];
      const done=g.filter(id=>info[id] && info[id].best>=a.level).length;
      progressTxt=`<div class="ai-cond">${done}/${g.length} · ${g.map(id=>PROVINCES[id].ar).join(' · ')}</div>`;
    }else if(a.kind==='count'){
      const n=a.prefs.filter(id=>info[id] && info[id].best>=a.level).length;
      progressTxt=`<div class="ai-cond">${n}/${a.n}</div>`;
    }else{
      progressTxt=`<div class="ai-cond">${t(a.cond)}</div>`;
    }
    c.innerHTML=`<div class="ai-top"><span class="ai-ic">${a.icon}</span><span class="ai-name">${t(a.name)}</span><span class="ai-pts">+${a.pts}</span><span class="ai-state"></span></div>${progressTxt}`;
    if(a.kind==='manual'){
      const btn=document.createElement('mdui-button'); btn.variant='tonal'; btn.size='small'; btn.className='ai-manual';
      btn.textContent=got?t('已達成'):t('手動標記');
      btn.onclick=()=>{ if(!isUnlocked()){ snack(t('已鎖定編輯 — 點擊頂欄鎖頭解鎖後才能記錄旅程')); return; } confirmDlg('確定？',t(a.name)+' '+t(a.cond),()=>{
        if(d.ach.manual.includes(a.id)){ d.ach.manual=d.ach.manual.filter(x=>x!==a.id); } else { d.ach.manual.push(a.id); }
        d.updated=Date.now(); saveCur(); renderAchDialog(); refreshApp(); snack(t('已自動儲存。'));
      }); };
      c.appendChild(btn);
    }
    c.onclick=()=>{ snack(a.icon+' '+t(a.name)+' · +'+a.pts+' '+t('分')+' — '+t(a.cond)); };
    grid.appendChild(c);
  });
}

/* ============ 戰報 ============ */
function openReport(){ if(!curData()){ snack(t('尚未建立任何地圖 — 點擊「建立我的地圖」開始！')); return; } renderReport(); openDlg('dlgReport'); }
function reportStats(d){
  const sc=computeScore(d); const info=sc.info;
  const visited=Object.keys(info).filter(id=>info[id].best>0).length;
  const stay=Object.keys(info).filter(id=>info[id].best>=3).length;
  const trips=Object.keys(info).reduce((s,id)=>s+info[id].count,0);
  let sum=0,cnt=0;
  for(const id in info){ for(const r of info[id].records){ if(r.rating){ sum+=r.rating; cnt++; } } }
  const avg=cnt? (sum/cnt).toFixed(1):'0.0';
  const lv=levelOf(sc.total);
  return {sc,info,visited,stay,trips,avg,lv,completion:Math.round(visited/27*100)};
}
function renderReport(){
  const d=curData(); const s=reportStats(d); const r=registry(); const m=r.created.find(x=>x.id===r.active);
  const levelName=t(s.lv.lv.name)+' '+s.lv.lv.icon;
  let text = `${t('埃及制霸戰報')}\n${t('等級')}：${levelName}\n${t('總分')}：${s.sc.total} ${t('分')}\n${t('造訪')}：${s.visited} / 27 ${t('省份')}（${s.completion}%）\n${t('住宿')}：${s.stay} ${t('省份')} · ${t('旅程數')}：${s.trips}\n${t('平均評分')}：${s.avg}\n${t('制霸率')}：${s.completion}%\n`;
  const visitedIds=Object.keys(s.info).filter(id=>s.info[id].best>0).map(Number);
  const unvis=Object.keys(s.info).filter(id=>s.info[id].best===0).map(Number);
  text += `\n${t('我的足跡：')}${visitedIds.map(id=>PROVINCES[id].ar).join(LANG==='ar'?'، ':LANG==='en'?', ':'、')||t('（空）')}\n`;
  text += `${t('尚未造訪：')}${unvis.map(id=>PROVINCES[id].ar).join(LANG==='ar'?'، ':LANG==='en'?', ':'、')||'—'}\n`;
  text += `\n${t('識別碼')}：${d.code}`;
  $('reportBody').innerHTML=`
    <div class="report-hero">
      <div class="rh-level">${t('等級')} ${s.lv.idx+1} / ${LEVELS.length}</div>
      <div class="rh-big">${levelName}</div>
      <div class="rh-score">${t('總分')} <b>${s.sc.total}</b> ${t('分')}</div>
    </div>
    <div class="report-stats">
      <div class="report-stat"><div class="rs-num">${s.visited}<small>/27</small></div><div class="rs-lbl">${t('造訪')}</div></div>
      <div class="report-stat"><div class="rs-num">${s.stay}</div><div class="rs-lbl">${t('住宿')}</div></div>
      <div class="report-stat"><div class="rs-num">${s.trips}</div><div class="rs-lbl">${t('旅程數')}</div></div>
      <div class="report-stat"><div class="rs-num">${s.avg}</div><div class="rs-lbl">${t('平均評分')}</div></div>
      <div class="report-stat"><div class="rs-num">${s.completion}%</div><div class="rs-lbl">${t('完成度')}</div></div>
    </div>
    <div class="report-text">${text}</div>
    <div class="report-note">⚠️ ${t('純靜態版沒有雲端：')}${t('請妥善備份識別碼與資料檔。')}</div>
    <div class="report-danger" style="margin-top:14px;display:flex;justify-content:center"><mdui-button id="rpDelete2" variant="tonal" style="color:var(--mdui-color-error)">${t('刪除這張地圖')}</mdui-button></div>`;
  $('rpDelete2').onclick=$('rpDelete').onclick=()=>confirmDlg('確定？',t('刪除這張地圖')+'：'+(m?m.name:''),deleteMap);
}
function exportReportImage(){
  const d=curData(); const s=reportStats(d);
  const W=1240,H=860;
  const cv=document.createElement('canvas'); cv.width=W; cv.height=H;
  const ctx=cv.getContext('2d');
  const g=ctx.createLinearGradient(0,0,0,H);
  g.addColorStop(0,'#FDF6E8'); g.addColorStop(1,'#F3E7CE');
  ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
  // 頂飾
  ctx.fillStyle='#AE2A1C'; ctx.fillRect(0,0,W,10);
  ctx.fillStyle='#111'; ctx.fillRect(0,H-10,W,10);
  // 標題
  ctx.textAlign='center'; ctx.fillStyle='#292117';
  ctx.font='900 58px "Noto Serif SC",serif';
  ctx.fillText(t('埃及制霸戰報'),W/2,86);
  ctx.font='700 22px "Noto Sans SC",sans-serif'; ctx.fillStyle='#8F7D68';
  ctx.fillText('EGYPT CONQUEST REPORT',W/2,122);
  ctx.fillStyle='#C29A2B'; ctx.fillRect(W/2-52,140,104,4);
  // 等級＋分數
  ctx.fillStyle='#292117'; ctx.font='900 34px "Noto Sans SC",sans-serif';
  ctx.fillText(s.lv.lv.icon+' '+t(s.lv.lv.name),W/2,196);
  ctx.fillStyle='#AE2A1C'; ctx.font='900 30px "Noto Sans SC",sans-serif';
  ctx.fillText(t('總分')+' '+s.sc.total+' '+t('分'),W/2,238);
  // 迷你地圖
  const mx=80,my=280,mw=W-160,mh=360;
  ctx.strokeStyle='rgba(41,33,23,.25)'; ctx.lineWidth=1;
  const LON0=24.5,LON1=37.1,LAT0=21.9,LAT1=31.9;
  const px=x=>mx+(x-LON0)/(LON1-LON0)*mw;
  const py=y=>my+(LAT1-y)/(LAT1-LAT0)*mh;
  const info=s.info;
  for(const f of window.EGYPT_GEOJSON.features){
    const best=info[f.properties.id]?info[f.properties.id].best:0;
    ctx.beginPath();
    const polys=f.geometry.type==='Polygon'?[f.geometry.coordinates]:f.geometry.coordinates;
    for(const poly of polys){
      for(let i=0;i<poly.length;i++){
        const [x,y]=poly[i];
        i===0?ctx.moveTo(px(x),py(y)):ctx.lineTo(px(x),py(y));
      }
    }
    ctx.fillStyle=fillFor(best); ctx.fill();
    ctx.strokeStyle='#fff'; ctx.lineWidth=1.6; ctx.stroke();
  }
  // 統計列
  ctx.textAlign='center'; ctx.fillStyle='#292117'; ctx.font='700 26px "Noto Sans SC",sans-serif';
  const stats=[
    [t('造訪'),s.visited+'/27'],
    [t('住宿'),String(s.stay)],
    [t('旅程數'),String(s.trips)],
    [t('平均評分'),s.avg],
    [t('完成度'),s.completion+'%'],
  ];
  ctx.fillStyle='#8F7D68'; ctx.font='700 20px "Noto Sans SC",sans-serif';
  stats.forEach((st,i)=>{
    const x=W/2+(i-(stats.length-1)/2)*180;
    ctx.fillStyle='#8F7D68'; ctx.fillText(st[0],x,700);
    ctx.fillStyle='#AE2A1C'; ctx.font='900 34px "Noto Serif SC",serif';
    ctx.fillText(st[1],x,740);
    ctx.font='700 20px "Noto Sans SC",sans-serif';
  });
  ctx.textAlign='right'; ctx.fillStyle='#8F7D68'; ctx.font='600 18px "Noto Sans SC",sans-serif';
  ctx.fillText(d.code+' · '+t('今日'),W-30,H-36);
  const a=document.createElement('a');
  a.download=('egypt-report-'+d.code+'.png').replace(/[^a-zA-Z0-9._-]/g,'_');
  a.href=cv.toDataURL('image/png');
  a.click();
  snack(t('已匯出戰報圖片。'));
}
function exportData(){
  const d=curData();
  const out={app:'egypt-conquest',version:1,name:d.name,code:d.code,created:d.created,updated:Date.now(),prefs:{},ach:d.ach};
  for(const id in d.prefs){
    out.prefs[id]={records:d.prefs[id].records,wish:d.prefs[id].wish,rate:d.prefs[id].rate};
  }
  const blob=new Blob([JSON.stringify(out)],{type:'application/json'});
  const a=document.createElement('a');
  a.download=(d.name||'egypt-map')+'.json';
  a.href=URL.createObjectURL(blob);
  a.click();
  setTimeout(()=>URL.revokeObjectURL(a.href),2000);
  snack(t('已匯出資料檔：')+a.download);
}
function deleteMap(){
  const r=registry();
  const id=r.active;
  r.created=r.created.filter(x=>x.id!==id);
  LS.del('data_'+id);
  r.active=null; saveRegistry(r);
  closeDlg('dlgReport');
  showHome();
  snack(t('已刪除地圖：')+(id||''));
}
function copyReportText(){
  const d=curData(); const s=reportStats(d);
  let text=`【${t('埃及制霸戰報')}】${d.name}\n`;
  text+=`${t('等級')} ${s.lv.idx+1}：${t(s.lv.lv.name)} ${s.lv.lv.icon}\n`;
  text+=`${t('總分')} ${s.sc.total} ${t('分')} ｜ ${t('造訪')} ${s.visited}/27 ｜ ${t('住宿')} ${s.stay} ｜ ${t('旅程數')} ${s.trips}\n`;
  text+=`${t('制霸率')} ${s.completion}%\n`;
  const visitedIds=Object.keys(s.info).filter(id=>s.info[id].best>0).map(Number);
  text+=`${t('我的足跡：')}${visitedIds.map(id=>PROVINCES[id].ar).join(LANG==='ar'?'، ':LANG==='en'?', ':'、')||t('（空）')}\n`;
  text+=`${t('識別碼')} ${d.code}`;
  copyText(text);
  snack(t('已複製戰報！'));
}
function copyText(text){
  if(navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(text).catch(()=>fallbackCopy(text));
  }else fallbackCopy(text);
}
function fallbackCopy(text){
  const ta=document.createElement('textarea');
  ta.value=text; ta.style.position='fixed'; ta.style.opacity='0';
  document.body.appendChild(ta); ta.select();
  try{ document.execCommand('copy'); }catch(e){}
  document.body.removeChild(ta);
}
function copyCode(){
  const d=curData(); copyText(d.code); snack(t('已複製識別碼：')+d.code);
}

/* ============ 旅遊建議 ============ */
function openSuggest(){ if(!curData()){ snack(t('尚未建立任何地圖 — 點擊「建立我的地圖」開始！')); return; } renderSuggest(); openDlg('dlgSuggest'); }
function renderSuggest(){
  const d=curData(); const sc=computeScore(d); const info=sc.info;
  const hot=[2,22,23,1,4,24,27,16];
  const body=$('sugList'); body.innerHTML='';
  const unvisited=Object.keys(info).filter(id=>info[id].best===0).map(Number);
  const unfinished=sc.achList.filter(x=>!x.got).map(x=>x.a);
  if(!unvisited.length){
    body.innerHTML=`<div class="sug-empty">🏆 ${t('全制霸')}</div>`;
    return;
  }
  const scoreMap={};
  unvisited.forEach(id=>{ scoreMap[id]=scoreMap[id]||0; });
  hot.forEach((id,i)=>{ if(unvisited.includes(id)) scoreMap[id]+=3+Math.max(0,2-i); });
  unfinished.forEach(a=>{
    if(a.kind==='group') a.groups[0].forEach(id=>{ if(unvisited.includes(id)) scoreMap[id]+=2; });
    if(a.kind==='count') a.prefs.forEach(id=>{ if(unvisited.includes(id)) scoreMap[id]+=1; });
  });
  for(const rk in REGIONS){
    const ids=REGIONS[rk].ids;
    if(ids.some(id=>info[id] && info[id].best>0)){
      ids.forEach(id=>{ if(unvisited.includes(id)) scoreMap[id]+=1; });
    }
  }
  const ranked=Object.keys(scoreMap).map(Number).sort((a,b)=>scoreMap[b]-scoreMap[a]).slice(0,8);
  const used=new Set();
  ranked.forEach((id,i)=>{
    const p=PROVINCES[id];
    let reason='';
    if(i===0 && scoreMap[id]>=3) reason=t('這是你第一次記錄旅程，挑個最想去的省份開始吧！');
    else{
      const ach=unfinished.find(a=>a.kind==='group' && a.groups[0].includes(id));
      if(ach) reason=t('來自成就：')+t(ach.name);
      else{
        for(const rk in REGIONS){
          if(REGIONS[rk].ids.includes(id) && REGIONS[rk].ids.some(x=>info[x] && info[x].best>0)){
            const rest=REGIONS[rk].ids.filter(x=>unvisited.includes(x)&&x!==id).length;
            if(rest>0) reason=t('同地區還有 ')+rest+t(' 未造訪！');
            break;
          }
        }
        if(!reason && hot.includes(id)) reason=t('第 ')+(Object.keys(info).filter(x=>info[x].best>0).length+1)+t(' 個省份，邁向全制霸！');
        if(!reason) reason=t('下一站：')+t(p.tagline);
      }
    }
    const c=document.createElement('div'); c.className='sug-card';
    c.innerHTML=`<div class="sug-ja">${p.ar}</div><div class="sug-body"><div class="sug-name">${prefName(p)}<span class="sug-region">${t(REGIONS[p.region].name)}</span></div><div class="sug-reason">${reason}</div></div><div class="sug-go">→</div>`;
    c.onclick=()=>{ closeDlg('dlgSuggest'); selectPref(id,true); };
    body.appendChild(c);
  });
}

/* ============ 好友排行 ============ */
const FRIENDS_KEY='friends';
let frSort='pts';
function friendsList(){ return LS.get(FRIENDS_KEY)||[]; }
function saveFriends(l){ LS.set(FRIENDS_KEY,l); }
function openFriends(){ if(!curData()){ snack(t('尚未建立任何地圖 — 點擊「建立我的地圖」開始！')); return; } renderFriends(); openDlg('dlgFriends'); }
function renderFriends(){
  const d=curData(); const sc=computeScore(d); const me={name:d.name+' ('+t('你')+')',code:d.code,pts:sc.total,lv:levelOf(sc.total).idx+1,visited:Object.keys(sc.info).filter(id=>sc.info[id].best>0).length,me:true};
  const list=friendsList().map(f=>{
    const s=computeScore(f); const info=s.info;
    return {name:f.name,code:f.code,pts:s.total,lv:levelOf(s.total).idx+1,visited:Object.keys(info).filter(id=>info[id].best>0).length,me:false};
  });
  list.push(me);
  list.sort((a,b)=>frSort==='pts'?b.pts-a.pts:frSort==='visited'?b.visited-a.visited:b.lv-a.lv);
  const scroll=$('frScroll');
  if(list.length<=1){
    scroll.innerHTML=`<div class="sug-empty">${t('尚未匯入好友資料。')}</div>`;
    return;
  }
  let html=`<table class="fr-table"><thead><tr><th>#</th><th data-sort="name">${t('好友')}</th><th data-sort="pts" class="${frSort==='pts'?'fr-sort-on':''}">${t('分')}</th><th data-sort="lv" class="${frSort==='lv'?'fr-sort-on':''}">${t('等級')}</th><th data-sort="visited" class="${frSort==='visited'?'fr-sort-on':''}">${t('造訪')}</th><th></th></tr></thead><tbody>`;
  list.forEach((f,i)=>{
    const cls=f.me?' class="me"':'';
    html+=`<tr${cls}><td class="fr-rank">${i+1}</td><td class="fr-name">${f.name}${f.me?'<span class="fr-me-tag">'+t('你')+'</span>':''}<div class="fr-code">${f.code}</div></td><td class="fr-pts">${f.pts}</td><td class="fr-lv">${f.lv} · ${t(LEVELS[f.lv-1].name)}</td><td>${f.visited}/27</td><td>${f.me?'':`<mdui-button-icon class="fr-del" data-code="${f.code}"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6L6 18"/><path d="M6 6l12 12"/></svg></mdui-button-icon>`}</td></tr>`;
  });
  html+='</tbody></table>';
  scroll.innerHTML=html;
  scroll.querySelectorAll('th[data-sort]').forEach(th=>{
    th.onclick=()=>{ frSort=th.dataset.sort; renderFriends(); };
  });
  scroll.querySelectorAll('.fr-del').forEach(b=>{
    b.onclick=()=>{
      const code=b.dataset.code;
      saveFriends(friendsList().filter(f=>f.code!==code));
      renderFriends();
    };
  });
}

/* ============ 建立／載入／解鎖 ============ */
function openCreate(){
  $('cfName').value=''; $('cfPass').value=''; $('cfPass2').value='';
  openDlg('dlgCreate');
}
function createMap(){
  const name=$('cfName').value.trim();
  if(!name){ snack(t('請輸入地圖名稱。')); return; }
  const p1=$('cfPass').value, p2=$('cfPass2').value;
  if(p1!==p2){ snack(t('密碼不一致，請重新輸入。')); return; }
  const r=registry();
  const exist=r.created.find(x=>x.name===name);
  if(exist){ r.active=exist.id; saveRegistry(r); closeDlg('dlgCreate'); enterMap(); snack(t('此名稱已存在，已開啟既有地圖。')+' '+exist.code); return; }
  const code=genCode();
  const id=Date.now().toString(36)+Math.random().toString(36).slice(2,6);
  r.created.push({id,name,pass:p1||'',code,created:Date.now(),updated:Date.now()});
  LS.set('data_'+id,newMapData(name,code));
  r.active=id; saveRegistry(r);
  closeDlg('dlgCreate');
  enterMap();
  snack(t('已建立地圖：')+name+'（'+code+'）');
}
function openLoad(){ $('lfCode').value=''; renderLocalMaps(); openDlg('dlgLoad'); }
function renderLocalMaps(){
  const r=registry(); const box=$('localMaps'); box.innerHTML='';
  if(!r.created.length){
    box.innerHTML=`<div class="sug-empty">${t('尚未建立任何地圖 — 點擊「建立我的地圖」開始！')}</div>`;
    return;
  }
  r.created.forEach(m=>{
    const d=LS.get('data_'+m.id); const sc=d?computeScore(d):null;
    const b=document.createElement('button'); b.className='local-map'+(r.active===m.id?' active':'');
    b.innerHTML=`<span class="lm-name">${m.name}</span><span class="lm-code">${m.code}</span><span class="lm-meta">${sc?sc.total+' '+t('分')+' · '+Object.keys(sc.info).filter(id=>sc.info[id].best>0).length+'/27':''}</span>`;
    b.onclick=()=>{ r.active=m.id; saveRegistry(r); closeDlg('dlgLoad'); enterMap(); snack(t('已開啟地圖：')+m.name); };
    box.appendChild(b);
  });
}
function loadByCode(){
  const code=$('lfCode').value.trim().toUpperCase();
  if(!code) return;
  const id=codeToId(code);
  if(!id){ snack(t('找不到這組識別碼，請確認是否輸入正確。')); return; }
  const r=registry(); r.active=id; saveRegistry(r);
  closeDlg('dlgLoad'); enterMap();
  const m=r.created.find(x=>x.id===id);
  snack(t('已開啟地圖：')+m.name);
}
function openUnlock(){ $('ufPass').value=''; openDlg('dlgUnlock'); }
function unlock(){
  const r=registry(); const m=r.created.find(x=>x.id===r.active);
  if(!m){ closeDlg('dlgUnlock'); return; }
  if($('ufPass').value===m.pass){ m.unlocked=true; saveRegistry(r); closeDlg('dlgUnlock'); refreshApp(); renderPanel(); snack(t('已解鎖編輯。')); }
  else{ snack(t('密碼錯誤，無法解鎖。')); }
}
function lockEdit(){
  const r=registry(); const m=r.created.find(x=>x.id===r.active);
  if(!m) return;
  if(m.pass){ m.unlocked=false; saveRegistry(r); refreshApp(); renderPanel(); snack(t('已鎖定編輯。')); }
  else{ snack(t('已鎖定編輯。')); }
}

/* ============ 搜尋 ============ */
function buildSearchIndex(){
  const idx=[];
  for(const id in PROVINCES){
    const p=PROVINCES[id];
    idx.push({id:Number(id),tokens:[p.zh,p.ar,p.en.toLowerCase(),REGIONS[p.region].name]});
  }
  return idx;
}
const SEARCH_IDX=buildSearchIndex();
function renderPrefSearch(q){
  const drop=$('prefSearchDrop'); drop.innerHTML=''; drop.classList.remove('hidden');
  if(!q){ $('psClear').style.display='none'; drop.innerHTML=`<div class="ps-empty">—</div>`; return; }
  const low=q.toLowerCase();
  const hits=SEARCH_IDX.filter(x=>x.tokens.some(tk=>tk.toLowerCase().includes(low))).slice(0,12);
  $('psClear').style.display='inline-flex';
  if(!hits.length){ drop.innerHTML=`<div class="ps-empty">—</div>`; return; }
  hits.forEach((h,i)=>{
    const p=PROVINCES[h.id];
    const b=document.createElement('button'); b.type='button'; b.className='ps-item'+(psSel===i?' on':'');
    b.innerHTML=`<span class="ps-ja">${p.ar}</span><span class="ps-zh">${prefName(p)}</span><span class="ps-reg">${t(REGIONS[p.region].name)}</span>`;
    b.onclick=()=>{ selectPref(h.id,true); closeSearch(); };
    drop.appendChild(b);
  });
}
function closeSearch(){
  $('prefSearch').value=''; psSel=-1;
  $('prefSearchDrop').classList.add('hidden');
  $('prefSearchWrap').classList.remove('open');
  $('psClear').style.display='none';
}

/* ============ 頂欄／等級條 ============ */
function refreshApp(){
  const d=curData();
  const top=$('appbar');
  if(!d){ $('appScore').textContent='0'; $('appLevel').textContent='—'; top.classList.add('hidden'); return; }
  top.classList.remove('hidden');
  const sc=computeScore(d); const lv=levelOf(sc.total);
  $('appScore').textContent=sc.total;
  $('appLevel').textContent=(lv.idx+1)+' '+t(lv.lv.name);
  const strip=$('levelStrip');
  strip.classList.remove('hidden');
  $('lsLevel').textContent=lv.lv.icon+' '+t(lv.lv.name)+' · '+sc.total+' '+t('分');
  if(lv.next){
    const span=lv.next.pts-lv.lv.pts||1;
    $('levelProgress').value=Math.min(1,Math.max(0,(sc.total-lv.lv.pts)/span));
    $('lsNext').textContent=t('下一級')+'：'+t(lv.next.name)+'（'+(lv.next.pts-sc.total)+'）';
  }else{
    $('levelProgress').value=1;
    $('lsNext').textContent='MAX';
  }
  refreshMapFill();
  renderContinueCard();
  if(!$('view-map').classList.contains('hidden') && $('dlgWish').open) renderWishDialog();
  if($('dlgAch').open) renderAchDialog();
  if($('dlgReport').open) renderReport();
  if($('dlgSuggest').open) renderSuggest();
  if($('dlgFriends').open) renderFriends();
}
function renderContinueCard(){
  const r=registry(); const d=curData();
  const card=$('continueCard');
  if(!d){ card.classList.add('hidden'); return; }
  const m=r.created.find(x=>x.id===r.active);
  if(!m) return;
  card.classList.remove('hidden');
  $('ccName').textContent=m.name;
  $('ccMeta').textContent=m.code+' · '+t('今日')+' '+new Date().toLocaleDateString();
}

/* ============ 視圖切換 ============ */
function enterMap(){
  $('view-home').classList.add('hidden');
  $('view-map').classList.remove('hidden');
  setupMap();
  setTimeout(()=>{ if(map) map.invalidateSize(); },50);
  refreshApp();
  if(!selectedPref) renderPanel();
}
function showHome(){
  $('view-map').classList.add('hidden');
  $('view-home').classList.remove('hidden');
  selectedPref=null;
  renderContinueCard();
}

/* ============ 事件綁定 ============ */
function bind(){
  $('btnCreate').addEventListener('click',openCreate);
  $('cfCancel').addEventListener('click',()=>closeDlg('dlgCreate'));
  $('cfSubmit').addEventListener('click',createMap);
  $('cfName').addEventListener('keydown',e=>{ if(e.key==='Enter') createMap(); });
  $('btnLoad').addEventListener('click',openLoad);
  $('lfCancel').addEventListener('click',()=>closeDlg('dlgLoad'));
  $('lfSubmit').addEventListener('click',loadByCode);
  $('lfCode').addEventListener('keydown',e=>{ if(e.key==='Enter') loadByCode(); });
  $('lfImport').addEventListener('click',()=>$('importFile').click());
  $('importFile').addEventListener('change',e=>{
    const f=e.target.files[0]; if(!f) return;
    const fr=new FileReader();
    fr.onload=()=>{
      try{
        const j=JSON.parse(fr.result);
        if(!j || !j.prefs || !j.name){ throw 0; }
        const r=registry();
        const code=j.code&&/^EGY-/.test(j.code)?j.code:genCode();
        let m=r.created.find(x=>x.code===code);
        if(!m){
          m={id:Date.now().toString(36)+Math.random().toString(36).slice(2,6),name:j.name,pass:'',code,created:Date.now(),updated:Date.now()};
          r.created.push(m);
        }
        const data=newMapData(m.name,m.code);
        for(const id in j.prefs){
          if(data.prefs[id]){
            data.prefs[id].records=(j.prefs[id].records||[]).map(x=>({type:x.type||2,date:x.date||'',rating:x.rating||0,note:x.note||'',ach:x.ach||[]}));
            data.prefs[id].wish=!!j.prefs[id].wish;
            data.prefs[id].rate=j.prefs[id].rate||0;
          }
        }
        if(j.ach && Array.isArray(j.ach.manual)) data.ach.manual=j.ach.manual.filter(x=>x===MANUAL_ACH.id);
        LS.set('data_'+m.id,data);
        r.active=m.id; saveRegistry(r);
        closeDlg('dlgLoad'); enterMap();
        snack(t('已匯入資料檔：')+m.name);
      }catch(err){ snack(t('資料檔格式錯誤，無法匯入。')); }
    };
    fr.readAsText(f);
    e.target.value='';
  });
  $('btnLock').addEventListener('click',()=>{ if(curData()){ const m=registry().created.find(x=>x.id===registry().active); if(m&&m.pass){ if(m.unlocked) lockEdit(); else openUnlock(); } else { snack(t('已鎖定編輯。')); } } });
  $('ufCancel').addEventListener('click',()=>closeDlg('dlgUnlock'));
  $('ufSubmit').addEventListener('click',unlock);
  $('ufPass').addEventListener('keydown',e=>{ if(e.key==='Enter') unlock(); });
  $('btnHome').addEventListener('click',showHome);
  $('btnAch').addEventListener('click',openAch);
  $('btnAchTeaser').addEventListener('click',openAch);
  $('achClose').addEventListener('click',()=>closeDlg('dlgAch'));
  $('btnWish').addEventListener('click',openWish);
  $('wtWish').addEventListener('click',()=>{ wishTab='wish'; renderWishDialog(); });
  $('wtTl').addEventListener('click',()=>{ wishTab='tl'; renderWishDialog(); });
  $('wishClose').addEventListener('click',()=>closeDlg('dlgWish'));
  $('btnReport').addEventListener('click',openReport);
  $('rpClose').addEventListener('click',()=>closeDlg('dlgReport'));
  $('rpCopy').addEventListener('click',copyReportText);
  $('rpImg').addEventListener('click',exportReportImage);
  $('rpExport').addEventListener('click',exportData);
  $('rpCode').addEventListener('click',copyCode);
  $('rpDelete').addEventListener('click',()=>confirmDlg('確定？',t('刪除這張地圖'),deleteMap));
  $('btnSuggestTeaser').addEventListener('click',openSuggest);
  $('sugClose').addEventListener('click',()=>closeDlg('dlgSuggest'));
  $('btnFriendsTeaser').addEventListener('click',openFriends);
  $('frClose').addEventListener('click',()=>closeDlg('dlgFriends'));
  $('frImport').addEventListener('click',()=>$('friendImport').click());
  $('friendImport').addEventListener('change',e=>{
    const f=e.target.files[0]; if(!f) return;
    const fr=new FileReader();
    fr.onload=()=>{
      try{
        const j=JSON.parse(fr.result);
        if(!j || !j.prefs || !j.name) throw 0;
        saveFriends(friendsList().filter(x=>x.code!==j.code).concat([j]));
        renderFriends();
        snack(t('已匯入資料檔：')+j.name);
      }catch(err){ snack(t('資料檔格式錯誤，無法匯入。')); }
    };
    fr.readAsText(f);
    e.target.value='';
  });
  $('photoClose').addEventListener('click',()=>closeDlg('dlgPhoto'));
  $('photoInput').addEventListener('change',e=>{
    const f=e.target.files[0]; if(!f) return;
    const d=curData(); const pd=d.prefs[selectedPref];
    if(pd.photos.length>=5){ snack(t('最多 5 張照片。')); e.target.value=''; return; }
    const fr=new FileReader();
    fr.onload=()=>{
      const img=new Image();
      img.onload=()=>{
        const maxW=1280;
        const scale=Math.min(1,maxW/img.width);
        const cv=document.createElement('canvas');
        cv.width=Math.round(img.width*scale); cv.height=Math.round(img.height*scale);
        cv.getContext('2d').drawImage(img,0,0,cv.width,cv.height);
        pd.photos.push(cv.toDataURL('image/jpeg',.82));
        d.updated=Date.now(); saveCur();
        renderPanel(); refreshApp();
        snack(t('已上傳照片'));
      };
      img.src=fr.result;
    };
    fr.readAsDataURL(f);
    e.target.value='';
  });
  $('btnAddRecord').addEventListener('click',()=>{ editRecIdx=null; openRecordDlg(); });
  $('recCancel').addEventListener('click',()=>{ editRecIdx=null; closeDlg('dlgRecord'); });
  $('recSubmit').addEventListener('click',saveRecord);
  $('recRating').addEventListener('change',updateRatingVal);
  $('recRating').addEventListener('input',updateRatingVal);
  $('btnWishToggle').addEventListener('click',()=>{
    if(!isUnlocked()){ snack(t('已鎖定編輯 — 點擊頂欄鎖頭解鎖後才能記錄旅程')); return; }
    const d=curData(); const p=PROVINCES[selectedPref];
    d.prefs[selectedPref].wish=!d.prefs[selectedPref].wish;
    d.updated=Date.now(); saveCur();
    renderPanel(); refreshApp();
    snack(d.prefs[selectedPref].wish?(t('已加入願望清單：')+p.ar):(t('已從願望清單移除：')+p.ar));
  });
  $('btnClearPref').addEventListener('click',()=>{
    const p=PROVINCES[selectedPref];
    confirmDlg('確定？',t('已清除「')+p.ar+t('」的所有旅程紀錄與評分。'),()=>{
      const d=curData();
      d.prefs[selectedPref]=newPrefData();
      d.updated=Date.now(); saveCur();
      renderPanel(); refreshApp();
      snack(t('已清除「')+p.ar+t('」的所有旅程紀錄與評分。'));
    });
  });
  $('btnRandom').addEventListener('click',()=>{
    const d=curData(); const info=d?prefInfo(d):null;
    const ids=Object.keys(PROVINCES).map(Number);
    const un=info?ids.filter(id=>info[id].best===0):ids;
    const pool=un.length?un:ids;
    selectPref(pool[Math.floor(Math.random()*pool.length)],true);
  });
  $('psToggle').addEventListener('click',()=>{
    const w=$('prefSearchWrap');
    w.classList.toggle('open');
    if(w.classList.contains('open')){ $('prefSearch').focus(); renderPrefSearch($('prefSearch').value); }
  });
  $('psClear').addEventListener('click',()=>{ $('prefSearch').value=''; psSel=-1; renderPrefSearch(''); $('prefSearch').focus(); });
  $('prefSearch').addEventListener('input',e=>{ psSel=-1; renderPrefSearch(e.target.value); });
  $('prefSearch').addEventListener('keydown',e=>{
    const drop=$('prefSearchDrop');
    const items=drop.querySelectorAll('.ps-item');
    if(e.key==='ArrowDown'&&items.length){ e.preventDefault(); psSel=(psSel+1)%items.length; items.forEach((b,i)=>b.classList.toggle('on',i===psSel)); }
    if(e.key==='ArrowUp'&&items.length){ e.preventDefault(); psSel=(psSel-1+items.length)%items.length; items.forEach((b,i)=>b.classList.toggle('on',i===psSel)); }
    if(e.key==='Enter'){ const on=drop.querySelector('.ps-item.on'); if(on) on.click(); }
  });
  $('levelStrip').addEventListener('click',openReport);
  $('btnContinue').addEventListener('click',enterMap);
  $('btnSwitch').addEventListener('click',openLoad);
  document.querySelectorAll('#langSwitch button').forEach(b=>{
    b.addEventListener('click',()=>{ LANG=b.dataset.lang; applyLang(); });
  });
  document.querySelectorAll('.rm-btn').forEach(b=>{
    b.addEventListener('click',()=>{ if(curData()) enterMap(); else snack(t('尚未建立任何地圖 — 點擊「建立我的地圖」開始！')); });
  });
  $('btnConfirmNo').addEventListener('click',()=>closeDlg('dlgConfirm'));
}

/* ============ 啟動 ============ */
function init(){
  bind();
  applyLang();
  const d=curData();
  if(d){ enterMap(); } else { showHome(); }
}
document.addEventListener('DOMContentLoaded',init);
</script>
</body>
</html>
