/* The Death of Seneca / 2026. Brightness, accessible image viewer, ambient player. */
(function(){
"use strict";
var body=document.body;
if(!body.classList.contains("seneca"))return;

/* Brightness is a non-destructive display preference, not an edit to the paintings. */
var panel=document.getElementById("seneca-light-controls");
var slider=document.getElementById("seneca-brightness");
var output=document.getElementById("seneca-brightness-value");
var toggle=document.getElementById("seneca-light-toggle");
var reset=document.getElementById("seneca-light-reset");
var defaultLight=1.2,brightness=defaultLight,key="dlorian-seneca-brightness-v1";
try {var saved=parseFloat(localStorage.getItem(key));if(isFinite(saved))brightness=saved;} catch (_) {}
function clamp(n){return Math.min(1.85,Math.max(.80,Math.round(n*20)/20));}
function applyBrightness(n){
 brightness=clamp(n); body.style.setProperty("--seneca-light",String(brightness));
 if(slider)slider.value=String(brightness);
 if(output)output.textContent=Math.round(brightness*100)+"%";
 try{localStorage.setItem(key,String(brightness));}catch(_){}
}
applyBrightness(brightness);
if(slider)slider.addEventListener("input",function(){applyBrightness(parseFloat(slider.value));});
if(reset)reset.addEventListener("click",function(){applyBrightness(1);});
if(toggle&&panel)toggle.addEventListener("click",function(){
 panel.hidden=!panel.hidden;toggle.setAttribute("aria-expanded",String(!panel.hidden));
 if(!panel.hidden)slider.focus();
});

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
 dialog.addEventListener("close",function(){if(img)img.removeAttribute("src");if(previousFocus&&typeof previousFocus.focus==="function")previousFocus.focus();});
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
 if(e.key.toLowerCase()==="b"){if(toggle){e.preventDefault();toggle.click();}return;}
 if(e.key==="]"||e.key==="+"||e.key==="="){e.preventDefault();applyBrightness(brightness+.05);}
 else if(e.key==="["||e.key==="-"){e.preventDefault();applyBrightness(brightness-.05);}
 else if(e.key==="0"){e.preventDefault();applyBrightness(1);}
});

/* User-initiated playback only. This is an original temporary sound study,
   not a Suno track. A finished score can replace the asset without changing JS. */
var audio=document.getElementById("seneca-track");
var play=document.getElementById("seneca-play");
var progress=document.getElementById("seneca-progress");
var volume=document.getElementById("seneca-volume");
var time=document.getElementById("seneca-time");
function mmss(n){if(!isFinite(n))n=0;n=Math.floor(n);return String(Math.floor(n/60)).padStart(2,"0")+":"+String(n%60).padStart(2,"0");}
function refreshTime(){
 if(!audio)return;
 var dur=isFinite(audio.duration)?audio.duration:0;
 if(progress&&!progress.matches(":active"))progress.value=dur?String(Math.round(audio.currentTime/dur*1000)):"0";
 if(time)time.textContent=mmss(audio.currentTime)+" / "+mmss(dur);
}
if(audio&&play){
 audio.volume=.62;
 play.addEventListener("click",function(){
  if(audio.paused){var promise=audio.play();if(promise&&promise.catch)promise.catch(function(){play.textContent="PLAY";});}
  else audio.pause();
 });
 audio.addEventListener("play",function(){play.textContent="PAUSE";play.setAttribute("aria-label","Pause soundtrack");});
 audio.addEventListener("pause",function(){play.textContent="PLAY";play.setAttribute("aria-label","Play soundtrack");});
 audio.addEventListener("loadedmetadata",refreshTime);
 audio.addEventListener("timeupdate",refreshTime);
 audio.addEventListener("error",function(){play.disabled=true;play.textContent="UNAVAILABLE";});
 if(progress)progress.addEventListener("input",function(){if(isFinite(audio.duration))audio.currentTime=Number(progress.value)/1000*audio.duration;refreshTime();});
 if(volume)volume.addEventListener("input",function(){audio.volume=Number(volume.value);});
 refreshTime();
}
})();