/* The Death of Seneca / 2026. Brightness, accessible image viewer, ambient player. */
(function(){
"use strict";
var body=document.body;
if(!body.classList.contains("seneca"))return;

/* Public visitors see the curated brightness for each painting, but NO controls.
   Editor view is opened only from the authenticated admin: seneca.html?edit=1.
   The server always verifies X-Admin before allowing changes. */
var defaultLight=1.2,levels={};
var frames=Array.prototype.slice.call(document.querySelectorAll(".seneca-plate"));
var editorEnabled=false;
var editUiById={};
var modalStrip=null;
function idOf(fig){return fig && fig.getAttribute("data-no");}
function levelOf(id){
 var raw=Number(levels[id]);
 return Number.isFinite(raw)&&raw>=.8&&raw<=1.85?raw:defaultLight;
}
function applyLight(id){
 var amount=levelOf(id);
 frames.forEach(function(f){
  if(idOf(f)!==id)return;
  var pic=f.querySelector("img");
  if(pic)pic.style.setProperty("--seneca-light",String(amount));
 });
 if(id==="04"){
  var cover=document.querySelector(".seneca-cover-picture img");
  if(cover)cover.style.setProperty("--seneca-light",String(amount));
 }
 if(typeof current!=="undefined"&&current>=0&&figures[current]&&idOf(figures[current])===id&&img){
  img.style.setProperty("--seneca-light",String(amount));
 }
 (editUiById[id]||[]).forEach(function(strip){
  var range=strip.querySelector("input");
  var output=strip.querySelector("output");
  if(range&&document.activeElement!==range)range.value=String(amount);
  if(output)output.textContent=Math.round(amount*100)+"%";
 });
}
function applyAll(){
 frames.forEach(function(f){applyLight(idOf(f));});
}
function acceptLevels(data){
 if(!data||!data.levels||typeof data.levels!=="object")return;
 frames.forEach(function(f){
  var id=idOf(f),v=Number(data.levels[id]);
  if(Number.isFinite(v)&&v>=.8&&v<=1.85)levels[id]=v;
 });
 applyAll();
}
function editorToken(){try{return localStorage.getItem("dl-admin")||"";}catch(_){return"";}}
function editorRequest(method,payload){
 return fetch("/api/admin/seneca/brightness",{
  method:method,
  headers:{"X-Admin":editorToken(),"Content-Type":"application/json"},
  body:payload?JSON.stringify(payload):undefined,
  cache:"no-store"
 }).then(function(r){if(!r.ok)throw Error("Authorization or save failed ("+r.status+")");return r.json();});
}
function createStrip(id,isViewer){
 var strip=document.createElement("div");
 strip.className="seneca-edit-strip";
 var label=document.createElement("label");
 label.textContent="BRIGHTNESS / "+id;
 var slider=document.createElement("input");
 slider.type="range";slider.dataset.frame=id;slider.min=".8";slider.max="1.85";slider.step=".05";slider.value=String(levelOf(id));
 slider.setAttribute("aria-label","Brightness for painting "+id);
 var out=document.createElement("output");out.textContent=Math.round(levelOf(id)*100)+"%";
 var reset=document.createElement("button");reset.type="button";reset.textContent="100%";
 reset.title="Restore neutral brightness for this image";
 var status=document.createElement("span");status.className="seneca-edit-status";status.setAttribute("role","status");status.textContent="EDITOR ONLY · AUTO-SAVE";
 strip.append(label,slider,out,reset,status);
 label.appendChild(document.createTextNode(" "));
 label.htmlFor="seneca-slider-"+id+(isViewer?"-viewer":"-work");
 slider.id=label.htmlFor;
 (editUiById[id]||(editUiById[id]=[])).push(strip);
 var pending=false;
 function preview(v){
  levels[id]=Math.round(Math.min(1.85,Math.max(.8,v))*20)/20;
  out.textContent=Math.round(levelOf(id)*100)+"%";
  applyLight(id);
  status.textContent="UNSAVED";
 }
 function save(){
  if(pending)return;
  pending=true;status.textContent="SAVING…";slider.disabled=true;reset.disabled=true;
  var v=levelOf(id);
  editorRequest("PUT",{id:id,brightness:v}).then(function(data){
   acceptLevels(data);status.textContent="SAVED";
  }).catch(function(){
   status.textContent="SAVE FAILED · RETRY";
  }).finally(function(){pending=false;slider.disabled=false;reset.disabled=false;});
 }
 slider.addEventListener("input",function(){preview(Number(slider.value));});
 slider.addEventListener("change",save);
 reset.addEventListener("click",function(){preview(1);slider.value="1";save();});
 return strip;
}
function editorBanner(text,authenticated){
 var top=document.createElement("div");top.className="seneca-editor-banner";
 var t=document.createElement("span");t.textContent=text;top.appendChild(t);
 var a=document.createElement("a");
 a.href=authenticated?"seneca.html":"admin.html";
 a.textContent=authenticated?"EXIT EDITOR →":"SIGN IN TO EDIT →";
 top.appendChild(a);document.body.prepend(top);
}
function setupEditor(){
 editorEnabled=true;
 document.body.classList.add("seneca-editor-mode");
 editorBanner("EDITOR MODE · EACH PAINTING HAS ITS OWN BRIGHTNESS · SAVED TO SITE",true);
 frames.forEach(function(f){
  f.appendChild(createStrip(idOf(f)));
 });
}
fetch("/api/seneca/brightness",{cache:"no-store"}).then(function(r){
 if(!r.ok)throw Error("Brightness unavailable");
 return r.json();
}).then(acceptLevels).catch(function(){/* Default 120% fallback remains usable. */});
if(new URLSearchParams(location.search).get("edit")==="1"){
 if(!editorToken()){
  editorBanner("EDITOR MODE REQUIRES ADMIN SIGN-IN",false);
 }else{
  editorRequest("GET").then(function(data){acceptLevels(data);setupEditor();}).catch(function(){
   editorBanner("EDITOR MODE REQUIRES VALID ADMIN AUTHORIZATION",false);
  });
 }
}

/* Reuse the gallery's expected interactions: fit-to-screen, caption, next/previous, Esc. */
var figures=Array.prototype.slice.call(document.querySelectorAll(".seneca-plate"));
var dialog=document.getElementById("seneca-viewer");
var img=dialog&&dialog.querySelector(".seneca-view-image");
var num=dialog&&dialog.querySelector(".seneca-view-number");
var title=dialog&&dialog.querySelector(".seneca-view-title");
var description=dialog&&dialog.querySelector(".seneca-view-description");
var previousFocus=null,current=-1;
var descriptions={
 "01":"The villa at dusk. Seneca's final residence is imagined as monumental architecture. No surviving source establishes this building's appearance.",
 "02":"The arrival of soldiers. The official order reaches the philosopher, seen here from the soldiers' perspective.",
 "03":"The order. A document becomes an object of dread. Its lettering is invented for this painting, not a transcription of Tacitus or an ancient inscription.",
 "04":"The last hours. Seneca surrounded by those closest to him. The witnesses, basin and statuary are arranged as a painterly interpretation.",
 "05":"The hand. After the public space comes the vulnerable body. The historical account describes the opening of the veins.",
 "06":"Paulina. Seneca's wife wanted to share his death. Tacitus records the attempt and her survival, although the figures and arrangement here are imagined.",
 "07":"Seneca. An imagined portrait of the philosopher. No reliable likeness from his final hours is known.",
 "08":"The bath. Tacitus describes heated water and steam at the end of Seneca's protracted death. The gesture and lighting are pictorial inventions.",
 "09":"The empty room. The space remains after the people are gone. This final image is an artistic epilogue, not a fact stated in the ancient account."
};
function renderFrame(i){
 if(!figures.length||!dialog||!img)return;
 current=(i+figures.length)%figures.length;
 var f=figures[current],source=f.querySelector("img"),id=f.getAttribute("data-no")||String(current+1).padStart(2,"0");
 var imageHref=f.querySelector("a").getAttribute("href");
 img.src=imageHref;img.alt=source.alt||"Artwork";
 if(num)num.textContent=id+" / "+String(figures.length).padStart(2,"0");
 if(title)title.textContent=f.querySelector("figcaption span:nth-child(2)")?.textContent||"Untitled";
 if(description)description.textContent=descriptions[id]||source.alt||"";
 img.style.setProperty("--seneca-light",String(levelOf(id)));
 if(modalStrip){var idBefore=modalStrip.querySelector("input")?.getAttribute("data-frame");if(idBefore&&editUiById[idBefore])editUiById[idBefore]=editUiById[idBefore].filter(function(el){return el!==modalStrip;});modalStrip.remove();modalStrip=null;}
 if(editorEnabled){
   modalStrip=createStrip(id,true);
   dialog.querySelector(".seneca-view-footer").appendChild(modalStrip);
 }
}
function openAt(i){
 if(!dialog||!dialog.showModal)return;
 previousFocus=document.activeElement;
 renderFrame(i);dialog.showModal();
 dialog.querySelector(".seneca-view-close")?.focus();
}
function close(){if(dialog?.open)dialog.close();}
figures.forEach(function(f,i){var a=f.querySelector("a");if(!a)return;a.addEventListener("click",function(e){
 if(e.ctrlKey||e.metaKey||e.shiftKey||e.altKey||e.button!==0)return;
 if(typeof dialog.showModal!=="function")return; e.preventDefault();openAt(i);
});});
if(dialog){
 dialog.querySelectorAll("[data-view-step]").forEach(function(b){b.addEventListener("click",function(){renderFrame(current+Number(b.getAttribute("data-view-step")));});});
 dialog.querySelector(".seneca-view-close")?.addEventListener("click",close);
 dialog.addEventListener("click",function(e){if(e.target===dialog)close();});
 dialog.addEventListener("close",function(){if(img)img.removeAttribute("src");if(modalStrip){var idBefore=modalStrip.querySelector("input")?.getAttribute("data-frame");if(idBefore&&editUiById[idBefore])editUiById[idBefore]=editUiById[idBefore].filter(function(el){return el!==modalStrip;});modalStrip.remove();modalStrip=null;}if(previousFocus&&typeof previousFocus.focus==="function")previousFocus.focus();});
 var tx=null;dialog.addEventListener("touchstart",function(e){tx=e.changedTouches[0]?.clientX??null;},{passive:true});
 dialog.addEventListener("touchend",function(e){if(tx===null)return;var delta=e.changedTouches[0].clientX-tx;if(Math.abs(delta)>65)renderFrame(current+(delta<0?1:-1));tx=null;},{passive:true});
}
function isTyping(el){return !!el?.closest?.('input,textarea,select,[contenteditable="true"]');}
document.addEventListener("keydown",function(e){
 if(e.altKey||e.ctrlKey||e.metaKey||isTyping(e.target))return;
 if(dialog?.open){
  if(e.key==="ArrowLeft"){e.preventDefault();renderFrame(current-1);return;}
  if(e.key==="ArrowRight"){e.preventDefault();renderFrame(current+1);return;}
 }

});

/* SOUND DESIGN STUDY: two synchronized audio mixes, no autoplay.
   Spoken dialogue is a sourced dramatic RECONSTRUCTION and is not a
   documented verbatim exchange. All cue provenance is in public transcript. */
var audio=document.getElementById("seneca-track");
var play=document.getElementById("seneca-play");
var progress=document.getElementById("seneca-progress");
var volume=document.getElementById("seneca-volume");
var time=document.getElementById("seneca-time");
var cueSpeaker=document.getElementById("seneca-cue-speaker");
var cueText=document.getElementById("seneca-cue-text");
var cueTranslation=document.getElementById("seneca-cue-translation");
var cuePane=document.getElementById("seneca-captions");
var ccButton=document.getElementById("seneca-cc");
var transcript=document.getElementById("seneca-transcript-lines");
var modeButtons=Array.prototype.slice.call(document.querySelectorAll("[data-mode]"));
var playIcon=play?.querySelector(".seneca-play-icon");
var playWord=play?.querySelector(".seneca-play-word");
var sources={
 dialogue:"assets/seneca/seneca-dialogue-study.mp3",
 score:"assets/seneca/seneca-score-study.mp3"
};
var audioMode="dialogue",ccOn=true,cues=[],durationFallback=185.76;
var savedSilenceTime=0;
var transMap={
 "01":"You cannot know where death awaits you. Therefore await it everywhere.",
 "11":"I showed you the consolations of life. You prefer the honour of death.",
 "16":"I accept the condition. I do not fear the judgment."
};
function mmss(n){if(!isFinite(n))n=0;n=Math.floor(n);return String(Math.floor(n/60)).padStart(2,"0")+":"+String(n%60).padStart(2,"0");}
function descriptionOfCue(cue){
 if(cue.language==="latin"){
  if(cue.source.includes("Epistulae"))return "SENECA · EARLIER LETTER / EXACT LATIN";
  return "SENECA · AS REPORTED BY TACITUS / LATIN";
 }
 if(cue.source.toLowerCase().includes("english rendering"))return "SENECA · TACITUS / ENGLISH RENDERING";
 return cue.speaker+" · RECONSTRUCTED DIALOGUE";
}
function fillCaptions(){
 if(!cuePane||!cueSpeaker||!cueText)return;
 cuePane.hidden=audioMode!=="dialogue"||!ccOn;
 if(cuePane.hidden)return;
 var sec=audio&&isFinite(audio.currentTime)?audio.currentTime:0;
 var cue=cues.find(function(c){return sec>=c.start&&sec<=c.end;});
 if(cue){
  cueSpeaker.textContent=descriptionOfCue(cue);
  cueText.textContent=cue.text;
  if(cueTranslation){cueTranslation.textContent=transMap[cue.id]||"";cueTranslation.hidden=!transMap[cue.id];}
 }else{
  cueSpeaker.textContent="THE DEATH OF SENECA / 2026";
  cueText.textContent=sec>173?"AFTER THE WORDS, THE ROOM.":"A DRAMATIZED CONVERSATION · SENECA & PAULINA";
  if(cueTranslation){cueTranslation.textContent="";cueTranslation.hidden=true;}
 }
}
function updatePlayButton(){
 if(!play)return;
 var playing=audioMode!=="silence"&&audio&&!audio.paused;
 if(playIcon)playIcon.textContent=playing?"Ⅱ":"▶";
 if(playWord)playWord.textContent=audioMode==="silence"?"SILENT":playing?"PAUSE":"PLAY";
 play.disabled=audioMode==="silence";
 play.setAttribute("aria-label",playing?"Pause soundtrack":"Play soundtrack");
}
function refreshTime(){
 if(!audio)return;
 var t=audioMode==="silence"?savedSilenceTime:(isFinite(audio.currentTime)?audio.currentTime:0);
 var len=isFinite(audio.duration)&&audio.duration>0?audio.duration:durationFallback;
 if(progress)progress.value=String(Math.min(1000,Math.round(t/len*1000)));
 if(time)time.textContent=mmss(t)+" / "+mmss(len);
 fillCaptions();
}
function setMode(next,requestedPlay){
 if(!["dialogue","score","silence"].includes(next)||!audio)return;
 var wasPlaying=requestedPlay===true||(!audio.paused&&audioMode!=="silence");
 var prevTime=audioMode==="silence"?savedSilenceTime:audio.currentTime;
 if(!isFinite(prevTime)||prevTime<0)prevTime=0;
 audio.pause();audioMode=next;
 document.querySelector(".seneca-music-player")?.setAttribute("data-audio-mode",next);
 modeButtons.forEach(function(btn){btn.setAttribute("aria-pressed",btn.getAttribute("data-mode")===next?"true":"false");});
 if(next==="silence"){
  savedSilenceTime=prevTime;updatePlayButton();fillCaptions();refreshTime();return;
 }
 var path=sources[next],isNew=!audio.currentSrc||!audio.currentSrc.endsWith(path);
 if(isNew){audio.src=path;audio.load();}
 function restore(){try{audio.currentTime=Math.min(prevTime,(audio.duration||durationFallback)-.1);}catch(_){}refreshTime();}
 if(isNew)audio.addEventListener("loadedmetadata",restore,{once:true});
 else restore();
 if(wasPlaying){
  var playPromise=audio.play();
  if(playPromise&&playPromise.catch)playPromise.catch(function(){updatePlayButton();});
 }
 updatePlayButton();refreshTime();
}
if(audio&&play){
 audio.volume=.62;
 play.addEventListener("click",function(){
  if(audioMode==="silence")return;
  if(audio.paused){var p=audio.play();if(p&&p.catch)p.catch(updatePlayButton);}
  else audio.pause();
 });
 modeButtons.forEach(function(button){button.addEventListener("click",function(){setMode(button.getAttribute("data-mode"));});});
 audio.addEventListener("play",updatePlayButton);
 audio.addEventListener("pause",updatePlayButton);
 audio.addEventListener("loadedmetadata",refreshTime);
 audio.addEventListener("timeupdate",refreshTime);
 audio.addEventListener("ended",updatePlayButton);
 audio.addEventListener("error",function(){if(playWord)playWord.textContent="UNAVAILABLE";play.disabled=true;});
 if(progress)progress.addEventListener("input",function(){
  var len=isFinite(audio.duration)&&audio.duration>0?audio.duration:durationFallback;
  var point=Number(progress.value)/1000*len;
  if(audioMode==="silence")savedSilenceTime=point;
  else if(audio.readyState>=1)audio.currentTime=point;
  refreshTime();
 });
 if(volume)volume.addEventListener("input",function(){audio.volume=Number(volume.value);});
 if(ccButton)ccButton.addEventListener("click",function(){
  ccOn=!ccOn;ccButton.textContent=ccOn?"CC ON":"CC OFF";
  ccButton.setAttribute("aria-pressed",ccOn?"true":"false");fillCaptions();
 });
 updatePlayButton();
 refreshTime();
}
function insertTranscript(list){
 if(!transcript)return;
 transcript.textContent="";
 if(!list.length){var li=document.createElement("li");li.textContent="Transcript unavailable.";transcript.appendChild(li);return;}
 list.forEach(function(c){
  var li=document.createElement("li");
  var button=document.createElement("button");
  button.type="button";button.className="seneca-transcript-jump";
  button.textContent=mmss(c.start);button.setAttribute("aria-label","Jump to "+mmss(c.start));
  button.addEventListener("click",function(){
   setMode("dialogue",false);
   function jump(){try{audio.currentTime=c.start;}catch(_){}refreshTime();if(audio.paused){var p=audio.play();if(p&&p.catch)p.catch(updatePlayButton);}}
   if(audio.readyState>=1)jump();else audio.addEventListener("loadedmetadata",jump,{once:true});
  });
  var speech=document.createElement("div");
  var who=document.createElement("strong");who.textContent=c.speaker+" · "+(c.language==="latin"?"LATIN":"ENGLISH");
  var p=document.createElement("p");p.textContent=c.text;
  var small=document.createElement("small");small.textContent=c.source;
  speech.append(who,p,small);li.append(button,speech);transcript.appendChild(li);
 });
}
fetch("assets/seneca/seneca-dialogue.json",{cache:"force-cache"}).then(function(r){
 if(!r.ok)throw Error("transcript not found");
 return r.json();
}).then(function(data){
 cues=Array.isArray(data.cues)?data.cues:[];
 if(Number.isFinite(data.duration))durationFallback=data.duration;
 insertTranscript(cues);fillCaptions();refreshTime();
}).catch(function(){insertTranscript([]);});
})();