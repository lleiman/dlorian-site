/* Public page shows approved images only; the first artwork is already in HTML. */
(function(){
"use strict";
var mount=document.getElementById("seneca-gallery");
var info=document.getElementById("seneca-forthcoming");
if(!mount)return;
fetch("assets/seneca/gallery.json",{cache:"no-cache"}).then(function(r){if(!r.ok)throw Error("manifest unavailable");return r.json();}).then(function(data){
 var frames=Array.isArray(data.frames)?data.frames:[];
 var unpublished=frames.filter(function(item){return item.status!=="published";}).length;
 frames.filter(function(item){return item.status==="published" && item.id!=="01";}).forEach(function(item){
  if(!/^assets\/seneca\/[a-zA-Z0-9._-]+\.(webp|jpg|jpeg|png)$/.test(item.src||""))return;
  var fig=document.createElement("figure");
  var a=document.createElement("a");a.href=item.src;a.target="_blank";a.rel="noopener";a.setAttribute("aria-label","Open artwork "+item.id+" full size");
  var img=document.createElement("img");img.src=item.src;img.loading="lazy";img.decoding="async";img.alt=item.alt||("Artwork "+item.id);
  var cap=document.createElement("figcaption");
  var name=document.createElement("span");name.textContent=item.id+" / "+(item.title||"Untitled");
  var kind=document.createElement("span");kind.textContent="ARTWORK · 2026";
  cap.append(name,kind);a.appendChild(img);fig.append(a,cap);mount.appendChild(fig);
 });
 if(info){if(unpublished===0){info.hidden=true;}else{
  var p=info.querySelector("p");if(p)p.textContent=unpublished===1?"One further image is in preparation.":unpublished+" further images are in preparation. New frames will appear here as they are completed.";
 }}
}).catch(function(){/* Master image and forthcoming notice stay usable without JS. */});
})();
