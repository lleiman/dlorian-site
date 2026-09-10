/* Портфолио Dlorian. Ванильный JS, без сборки и зависимостей. */
(function () {
  "use strict";

  var THUMB = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 21h3V9H2v12zm19.7-10.6c.2-.3.3-.7.3-1.1V8c0-1.1-.9-2-2-2h-5.2l.8-3.8v-.3c0-.4-.2-.8-.4-1.1L14.2 0 7.6 6.6c-.4.4-.6.9-.6 1.4v10c0 1.1.9 2 2 2h9c.8 0 1.5-.5 1.8-1.2l3-7c.1-.1.1-.3.1-.4z"/></svg>';
  var PEN = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 2H4a2 2 0 0 0-2 2v18l4-4h14a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2z"/></svg>';

  var stack = document.querySelector(".stack");
  var dataEl = document.getElementById("works");
  var works = dataEl ? JSON.parse(dataEl.textContent) : [];

  /* ---------- проявление по загрузке ----------
     Кадр не спрятан до скролла: он появляется, как только пришёл сам файл.
     Если картинка уже в кеше — показываем сразу, без мигания. */
  function reveal(el) { el.classList.add("on"); }

  document.querySelectorAll(".work img, .work video").forEach(function (el) {
    if (el.tagName === "IMG") {
      if (el.complete) reveal(el);
      else el.addEventListener("load", function () { reveal(el); }, { once: true });
      el.addEventListener("error", function () { reveal(el); }, { once: true });
    } else {
      reveal(el); /* у видео есть постер, ждать нечего */
    }
  });

  /* ---------- видео играет только когда видно ----------
     45 роликов в лентах плюс обложки серий и монтаж на первом экране;
     одновременный автоплей убил бы и трафик, и батарею. */
  var calm = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var vids = calm ? [] : document.querySelectorAll("video[data-auto]");
  if (vids.length && "IntersectionObserver" in window) {
    var vio = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var v = e.target;
        if (e.isIntersecting) {
          if (v.preload === "none") v.preload = "auto";
          var p = v.play();
          if (p && p.catch) p.catch(function () {});
        } else {
          v.pause();
        }
      });
    }, { rootMargin: "150px 0px", threshold: 0.15 });
    vids.forEach(function (v) { vio.observe(v); });
  }

  /* ---------- подписка на новые работы ---------- */
  var subForm = document.querySelector(".sub");
  if (subForm) {
    subForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var inp = subForm.querySelector('input[name="email"]');
      var msg = subForm.querySelector(".submsg");
      var val = (inp.value || "").trim();
      if (!val) { msg.textContent = "enter an address"; return; }
      var btn = subForm.querySelector('button[type="submit"]');
      btn.disabled = true;
      msg.textContent = "sending…";
      fetch("/api/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: val })
      }).then(function (r) {
        return r.json().then(function (j) {
          if (!r.ok) throw new Error(j && j.error ? j.error : "did not work");
          return j;
        });
      }).then(function () {
        subForm.dataset.done = "1";
        msg.textContent = "done — I will write when there is something new";
        inp.value = "";
      }).catch(function (err) {
        msg.textContent = err.message || "did not send";
      }).then(function () { btn.disabled = false; });
    });
  }

  /* ---------- список серий ---------- */
  var menuBtn = document.querySelector(".bar .menu");
  var menuList = document.getElementById("menulist");
  if (menuBtn && menuList) {
    var setMenu = function (open) {
      menuList.hidden = !open;
      menuBtn.setAttribute("aria-expanded", String(open));
      document.body.style.overflow = open ? "hidden" : "";
    };
    menuBtn.addEventListener("click", function () {
      setMenu(menuList.hidden);
    });
    menuList.addEventListener("click", function (e) {
      if (e.target === menuList) setMenu(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !menuList.hidden) setMenu(false);
    });
  }

  /* ---------- наверх ----------
     Страница серии — до 44 экранов прокрутки; без этого со дна не выбраться. */
  var upBtn = document.createElement("button");
  upBtn.className = "totop";
  upBtn.type = "button";
  upBtn.textContent = "top";
  upBtn.addEventListener("click", function () {
    window.scrollTo({ top: 0, behavior: calm ? "auto" : "smooth" });
  });
  document.body.appendChild(upBtn);

  var ticking = false;
  window.addEventListener("scroll", function () {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      if (window.scrollY > window.innerHeight * 1.5) upBtn.setAttribute("data-on", "");
      else upBtn.removeAttribute("data-on");
      ticking = false;
    });
  }, { passive: true });

  /* ---------- карточка для соцсетей ----------
     Собирается прямо в браузере: кадр во всю ширину, затемнение снизу,
     подпись — как на превью ссылок, чтобы всё выглядело одной серией.
     Альбомная 1200×630. */

  /* витрина лежит в корне, ленты серий — в /s/, поэтому путь к кадру
     и адрес страницы вычисляются, а не зашиты */
  var PARTS = location.pathname.replace(/^\/+|\/+$/g, "").split("/").filter(Boolean);
  var UP = PARTS.length > 1 ? "../" : "";      /* /s/… и /w/… лежат на уровень ниже */
  var HERE = PARTS.join("/") || "index.html";  /* адрес этой страницы для подписи */
  var SLUGNOW = (location.pathname.split("/").pop() || "").replace(".html", "");

  function tracked(ctx, text, x, y, space) {
    if ("letterSpacing" in ctx) {          /* современные браузеры умеют сами */
      ctx.letterSpacing = space + "px";
      ctx.fillText(text, x, y);
      ctx.letterSpacing = "0px";
      return;
    }
    /* Запасной путь: рисуем посимвольно. Здесь textAlign не работает сам —
       ширину со шпациями считаем и центрируем руками. */
    var w = 0, i;
    for (i = 0; i < text.length; i++) w += ctx.measureText(text[i]).width + space;
    w -= space;
    var cx = ctx.textAlign === "center" ? x - w / 2 : x;
    var was = ctx.textAlign;
    ctx.textAlign = "left";
    for (i = 0; i < text.length; i++) {
      ctx.fillText(text[i], cx, y);
      cx += ctx.measureText(text[i]).width + space;
    }
    ctx.textAlign = was;
  }

  /* Карточка для соцсетей.

     Два размера: сторис 1080×1920 и лента 1080×1350. Если отдать в сторис
     карточку не 9:16, инстаграм сам дорисует поля размытием — получается
     коряво, поэтому размер выбирается заранее.

     Полосы сверху и снизу не фиксированы: кадр вписывается в доступную
     высоту, а всё оставшееся делится между полосами поровну, и подпись
     centrируется внутри своей. Так между кадром и текстом не остаётся
     ничейного зазора, как было при жёстком окне. */
  var CARD = {
    story: { w: 1080, h: 1920, top: 300, bot: 330 },
    feed:  { w: 1080, h: 1350, top: 230, bot: 260 }
  };
  var cardFmt = "story";

  function makeCard(n, seriesName, fmt) {
    var C = CARD[fmt || cardFmt] || CARD.story;
    return new Promise(function (resolve, reject) {
      var W = C.w, H = C.h;
      var cv = document.createElement("canvas");
      cv.width = W; cv.height = H;
      var ctx = cv.getContext("2d");
      var img = new Image();

      img.onload = function () {
        /* фон: та же работа, растянутая на весь холст и размытая */
        ctx.fillStyle = "#000";
        ctx.fillRect(0, 0, W, H);
        var canBlur = false;
        try {
          ctx.filter = "blur(64px)";
          canBlur = ctx.filter !== "none";
        } catch (e) {}
        if (canBlur) {
          var br = Math.max(W / img.width, H / img.height) * 1.35;
          var bw = img.width * br, bh = img.height * br;
          ctx.drawImage(img, (W - bw) / 2, (H - bh) / 2, bw, bh);
          ctx.filter = "none";
        }
        ctx.fillStyle = "rgba(0,0,0,.66)";
        ctx.fillRect(0, 0, W, H);

        /* кадр целиком, без обрезки, в оставшуюся высоту */
        var maxW = W - 96;
        var maxH = H - C.top - C.bot;
        var r = Math.min(maxW / img.width, maxH / img.height);
        var w = img.width * r, h = img.height * r;
        var x = (W - w) / 2;
        /* лишнюю высоту делим между полосами поровну */
        var slack = (maxH - h) / 2;
        var y = C.top + slack;
        ctx.save();
        ctx.shadowColor = "rgba(0,0,0,.75)";
        ctx.shadowBlur = 48;
        ctx.shadowOffsetY = 10;
        ctx.drawImage(img, x, y, w, h);
        ctx.restore();

        ctx.textAlign = "center";
        ctx.textBaseline = "alphabetic";

        /* подпись centrируется в своей полосе, а не липнет к краю */
        var topMid = y / 2;
        ctx.fillStyle = "#f2f2f2";
        ctx.font = '500 56px "IBM Plex Mono", monospace';
        tracked(ctx, "DLORIAN", W / 2, topMid + 4, 12);
        ctx.fillStyle = "#8a8a8a";
        ctx.font = '400 23px "IBM Plex Mono", monospace';
        tracked(ctx, seriesName || "", W / 2, topMid + 52, 5);

        var botTop = y + h, botMid = botTop + (H - botTop) / 2;
        var d = deckOf(n);
        var title = (d && d.name) ? "'" + d.name + "'" : (seriesName || "") + " · " + pad(n);
        ctx.fillStyle = "#f2f2f2";
        ctx.font = '500 40px "IBM Plex Mono", monospace';
        tracked(ctx, title.toUpperCase(), W / 2, botMid - 6, 6);

        if (d && d.note) {
          ctx.fillStyle = "#9a9a9a";
          ctx.font = '400 25px "IBM Plex Sans", sans-serif';
          ctx.fillText(cut(ctx, d.note, W - 140), W / 2, botMid + 44);
        }

        ctx.fillStyle = "#6e6e6e";
        ctx.font = '400 21px "IBM Plex Mono", monospace';
        tracked(ctx, location.host, W / 2, H - 64, 3);

        cv.toBlob(function (b) {
          b ? resolve(b) : reject(new Error("could not build"));
        }, "image/jpeg", 0.92);
      };

      img.onerror = function () { reject(new Error("frame did not load")); };
      /* тот же origin, поэтому canvas не «пачкается» и toBlob работает */
      img.src = UP + "assets/img/" + pad(n) + ".jpg";
    });
  }

  /* подпись из витрины, если работа туда попала и получила имя */
  function deckOf(n) {
    try {
      var el = document.getElementById("deckShare");
      if (!el) return null;
      var list = JSON.parse(el.textContent);
      for (var i = 0; i < list.length; i++) if (list[i].n === n) return list[i];
    } catch (e) {}
    return null;
  }

  function cut(ctx, text, max) {
    if (ctx.measureText(text).width <= max) return text;
    var t = text;
    while (t.length > 4 && ctx.measureText(t + "…").width > max) t = t.slice(0, -1);
    return t + "…";
  }

  /* Показываем готовую карточку и даём сохранить её.

     Прямой отправки в инстаграм из браузера не существует: он не
     регистрируется приёмником файлов в системном «Поделиться» и принимает
     только картинки из галереи. Схема instagram-stories:// доступна лишь
     зарегистрированным приложениям Facebook. Поэтому честный путь —
     сохранить в галерею и выложить из самого приложения. */
  var cardBox = null;

  function showCard(blob, file, caption, n, remake) {
    if (cardBox) cardBox.remove();
    var url = URL.createObjectURL(blob);

    cardBox = document.createElement("div");
    cardBox.className = "card";
    var im = document.createElement("img");
    im.src = url;
    im.alt = "card for instagram";
    cardBox.appendChild(im);

    var row = document.createElement("div");
    row.className = "crow2";
    cardBox.appendChild(row);

    function btn(text, fn) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "cbtn";
      b.textContent = text;
      b.onclick = fn;
      row.appendChild(b);
      return b;
    }

    /* Формат выбирается заранее: карточку не 9:16 инстаграм в сторис
       обводит своим размытием, и выглядит это криво. */
    var fmts = document.createElement("div");
    fmts.className = "crow2 cfmt";
    cardBox.insertBefore(fmts, row);
    [["story", "9:16 story"], ["feed", "4:5 feed"]].forEach(function (f) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "cbtn";
      b.textContent = f[1];
      if (cardFmt === f[0]) b.setAttribute("data-on", "");
      b.onclick = function () {
        if (cardFmt === f[0] || !remake) return;
        cardFmt = f[0];
        remake();
      };
      fmts.appendChild(b);
    });

    /* Системное «Поделиться»: оттуда удобно «Сохранить в Фото», телеграм,
       почта. Инстаграм в списке бывает не всегда — тогда сохраняем. */
    if (navigator.canShare && navigator.canShare({ files: [file] })) {
      btn("[share]", function () {
        navigator.share({ files: [file], text: caption }).catch(function () {});
      });
    }

    btn("[save]", function () {
      var a = document.createElement("a");
      a.href = url;
      a.download = file.name;
      a.click();
    });

    btn("[link]", function (e) {
      if (!navigator.clipboard) return;
      navigator.clipboard.writeText(caption).then(function () {
        e.target.textContent = "[copied]";
        setTimeout(function () { e.target.textContent = "[link]"; }, 1800);
      }).catch(function () {});
    });

    btn("[close]", closeCard);

    var hint = document.createElement("p");
    hint.className = "chint";
    hint.textContent = "Instagram may not appear in the system list — then save the image to your gallery and post it from the app. "
      + "Put the link in your profile bio: Instagram strips links from captions.";
    cardBox.appendChild(hint);

    document.body.appendChild(cardBox);
    document.body.style.overflow = "hidden";
    cardBox.addEventListener("click", function (e) {
      if (e.target === cardBox) closeCard();
    });
  }

  function closeCard() {
    if (!cardBox) return;
    var im = cardBox.querySelector("img");
    if (im) URL.revokeObjectURL(im.src);
    cardBox.remove();
    cardBox = null;
    document.body.style.overflow = "";
  }

  function share(n, seriesName, give) {
    var was = give.textContent;
    give.textContent = "[building…]";
    give.disabled = true;

    var link = location.origin + "/" + HERE;
    var caption = "DLORIAN — " + (seriesName || "") + " · " + pad(n) + "\n" + link;

    /* шрифт мог ещё не догрузиться — иначе подпись уедет в системный моно */
    var ready = document.fonts && document.fonts.load
      ? document.fonts.load('500 64px "IBM Plex Mono"').catch(function () {})
      : Promise.resolve();

    function build() {
      return makeCard(n, seriesName).then(function (blob) {
        var file = new File([blob], "dlorian-" + pad(n) + "-" + cardFmt + ".jpg",
                            { type: "image/jpeg" });
        showCard(blob, file, caption, n, build);
      });
    }

    ready.then(build).then(function () {
      give.textContent = was;
    }).catch(function (e) {
      give.textContent = (e && e.name === "AbortError") ? was : "[failed]";
      setTimeout(function () { give.textContent = was; }, 2600);
    }).then(function () { give.disabled = false; });
  }

  /* ================= админка (Ctrl+Shift+E) =================
     Правит те же json, из которых собирается сайт, и просит сервер
     пересобрать страницы. Данные лежат на томе, поэтому правки переживают
     деплой. Токен хранится в браузере и никуда больше не уходит. */

  var AKEY = "dl-admin";
  var apanel = null;

  function atoken() {
    try { return localStorage.getItem(AKEY) || ""; } catch (e) { return ""; }
  }

  function aapi(url, opts) {
    opts = opts || {};
    opts.headers = opts.headers || {};
    opts.headers["X-Admin"] = atoken();
    return fetch(url, opts).then(function (r) {
      if (r.status === 404) throw new Error("неверный токен");
      return r.json().then(function (j) {
        if (!r.ok) throw new Error(j && j.error ? j.error : "did not work");
        return j;
      });
    });
  }

  function ael(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  function afield(label, value, rows) {
    var w = ael("label", "afield");
    w.appendChild(ael("span", null, label));
    var t = ael("textarea");
    t.value = value || "";
    t.rows = rows || 3;
    w.appendChild(t);
    return { box: w, input: t };
  }

  /* какая страница открыта — от этого зависит, что правим */
  function actx() {
    if (document.querySelector(".deck")) return "deck";
    if (document.querySelector(".stack")) return "series";
    if (document.querySelector(".bands")) return "index";
    return null;
  }

  function seriesName() {
    var h = document.querySelector(".head h1");
    return h ? h.textContent.trim() : null;
  }

  function closeAdmin() {
    if (apanel) { apanel.remove(); apanel = null; }
    document.body.style.overflow = "";
  }

  function openAdmin() {
    if (apanel) { closeAdmin(); return; }
    if (!atoken()) {
      var t = window.prompt("Токен админки");
      if (!t) return;
      try { localStorage.setItem(AKEY, t.trim()); } catch (e) {}
    }
    var ctx = actx();
    if (!ctx) return;

    apanel = ael("div", "admin");
    document.body.appendChild(apanel);
    document.body.style.overflow = "hidden";

    var head = ael("div", "ahead");
    head.appendChild(ael("b", null, "админка"));
    head.appendChild(ael("span", "actx",
      ctx === "series" ? "серия " + seriesName() :
      ctx === "deck" ? "витрина" : "главная"));
    var full = document.createElement("a");
    full.className = "abtn";
    full.href = "/admin.html";
    full.textContent = "вся админка";
    full.style.textDecoration = "none";
    head.appendChild(full);

    var forget = ael("button", "abtn", "забыть токен");
    forget.onclick = function () {
      try { localStorage.removeItem(AKEY); } catch (e) {}
      closeAdmin();
    };
    var shut = ael("button", "abtn", "закрыть");
    shut.onclick = closeAdmin;
    head.appendChild(forget);
    head.appendChild(shut);
    apanel.appendChild(head);

    var body = ael("div", "abody");
    apanel.appendChild(body);
    var foot = ael("div", "afoot");
    var msg = ael("span", "amsg", "загружаю…");
    var save = ael("button", "abtn asave", "сохранить и пересобрать");
    foot.appendChild(msg);
    foot.appendChild(save);
    apanel.appendChild(foot);

    if (ctx === "index") buildIndexAdmin(body, msg, save);
    else if (ctx === "series") buildSeriesAdmin(body, msg, save);
    else buildDeckAdmin(body, msg, save);
  }

  function saver(msg, save, fn) {
    save.onclick = function () {
      save.disabled = true;
      msg.textContent = "сохраняю и пересобираю…";
      fn().then(function () {
        msg.textContent = "готово, обновляю страницу";
        setTimeout(function () { location.reload(); }, 700);
      }).catch(function (e) {
        msg.textContent = e.message || "не сохранилось";
        save.disabled = false;
      });
    };
  }

  /* ---------- главная: манифест и показы ----------
     Показы правятся именно отсюда: страница показов не существует, пока
     не заведена первая дата, и открыть админку там было бы негде. */
  function buildIndexAdmin(body, msg, save) {
    Promise.all([
      aapi("/api/admin/content?file=notes.json"),
      aapi("/api/admin/content?file=shows.json")
    ]).then(function (r) {
      var notes = r[0].data, shows = (r[1].data || []).slice();
      body.innerHTML = "";
      var f = afield("Манифест на главной", notes._manifest || "", 5);
      body.appendChild(f.box);

      body.appendChild(ael("span", "alab", "Показы — дата, город, площадка"));
      var wrap = ael("div", "aworks");
      body.appendChild(wrap);
      function draw() {
        wrap.innerHTML = "";
        shows.forEach(function (x, i) {
          var row = ael("div", "ashow");
          [["date", "2026-11-14"], ["city", "город"],
           ["venue", "площадка"], ["note", "примечание"]].forEach(function (k) {
            var inp = document.createElement("input");
            inp.type = "text";
            inp.placeholder = k[1];
            inp.value = x[k[0]] || "";
            inp.oninput = function () { x[k[0]] = inp.value; };
            if (k[0] === "date") inp.className = "adate";
            row.appendChild(inp);
          });
          var rm = ael("button", "abtn", "✕");
          rm.onclick = function () { shows.splice(i, 1); draw(); };
          row.appendChild(rm);
          wrap.appendChild(row);
        });
      }
      draw();
      var add = ael("button", "abtn", "+ показ");
      add.onclick = function () {
        shows.push({ date: "", city: "", venue: "", note: "" });
        draw();
      };
      body.appendChild(add);
      msg.textContent = "";

      saver(msg, save, function () {
        notes._manifest = f.input.value.trim();
        return aapi("/api/admin/content?file=notes.json", {
          method: "PUT", headers: { "Content-Type": "application/json" },
          body: JSON.stringify(notes)
        }).then(function () {
          return aapi("/api/admin/content?file=shows.json", {
            method: "PUT", headers: { "Content-Type": "application/json" },
            body: JSON.stringify(shows.filter(function (x) {
              return (x.date || "").trim() || (x.city || "").trim();
            }))
          });
        });
      });
    }).catch(function (e) { msg.textContent = e.message; });
  }

  /* ---------- серия: текст, порядок, удаление, добавление ---------- */
  function buildSeriesAdmin(body, msg, save) {
    var nm = seriesName();
    Promise.all([
      aapi("/api/admin/content?file=notes.json"),
      aapi("/api/admin/content?file=series.json"),
      aapi("/api/admin/catalog"),
      aapi("/api/admin/content?file=prices.json")
    ]).then(function (r) {
      var notes = r[0].data, series = r[1].data, cat = r[2].works;
      var prices = r[3].data || {};
      var list = (series[nm] || []).slice();
      var nd = notes[nm] || (notes[nm] = { lead: "", notes: [] });
      body.innerHTML = "";

      var lead = afield("Заявление серии", typeof nd.lead === "string" ? nd.lead : "", 4);
      body.appendChild(lead.box);

      var notesWrap = ael("div", "alist");
      body.appendChild(ael("span", "alab", "Тексты между работами"));
      body.appendChild(notesWrap);
      var noteInputs = [];
      function addNote(v) {
        var row = ael("div", "arow");
        var f = afield("", v || "", 2);
        var del = ael("button", "abtn", "✕");
        del.onclick = function () { row.remove(); f.input.dataset.gone = "1"; };
        row.appendChild(f.box);
        row.appendChild(del);
        notesWrap.appendChild(row);
        noteInputs.push(f.input);
      }
      (nd.notes || []).forEach(function (x) {
        addNote(typeof x === "string" ? x : (x && x.text) || "");
      });
      var addN = ael("button", "abtn", "+ текст");
      addN.onclick = function () { addNote(""); };
      body.appendChild(addN);

      body.appendChild(ael("span", "alab", "Работы серии — порядок, удаление"));
      var works = ael("div", "aworks");
      body.appendChild(works);
      function drawWorks() {
        works.innerHTML = "";
        list.forEach(function (n, i) {
          var row = ael("div", "awork");
          var im = document.createElement("img");
          im.src = (actx() === "series" ? "../" : "") + "assets/thumb/" + pad3(n) + ".jpg";
          im.loading = "lazy";
          row.appendChild(im);
          row.appendChild(ael("span", null, pad3(n)));

          /* цена. Пустая строка = записи нет и на сайте ничего не появится */
          var pr = prices[String(n)] || {};
          if (typeof pr === "string") pr = { price: pr, status: "available" };
          var pin = document.createElement("input");
          pin.type = "text";
          pin.className = "aprice";
          pin.placeholder = "цена";
          pin.value = pr.price || "";
          var sel = document.createElement("select");
          [["available", "в продаже"], ["request", "по запросу"],
           ["reserved", "бронь"], ["sold", "продано"]].forEach(function (o) {
            var op = document.createElement("option");
            op.value = o[0]; op.textContent = o[1];
            sel.appendChild(op);
          });
          sel.value = pr.status || "available";
          function keep() {
            var v = pin.value.trim(), st = sel.value;
            if (!v && st === "available") delete prices[String(n)];
            else prices[String(n)] = { price: v, status: st };
          }
          pin.oninput = keep;
          sel.onchange = keep;
          row.appendChild(pin);
          row.appendChild(sel);

          var up = ael("button", "abtn", "↑");
          up.onclick = function () {
            if (i > 0) { list.splice(i - 1, 0, list.splice(i, 1)[0]); drawWorks(); }
          };
          var dn = ael("button", "abtn", "↓");
          dn.onclick = function () {
            if (i < list.length - 1) { list.splice(i + 1, 0, list.splice(i, 1)[0]); drawWorks(); }
          };
          var rm = ael("button", "abtn", "✕");
          rm.onclick = function () { list.splice(i, 1); drawWorks(); };
          row.appendChild(up); row.appendChild(dn); row.appendChild(rm);
          works.appendChild(row);
        });
      }
      drawWorks();

      var addRow = ael("div", "arow");
      var inp = document.createElement("input");
      inp.type = "text";
      inp.placeholder = "номер работы, например 207";
      var addW = ael("button", "abtn", "добавить");
      addW.onclick = function () {
        var n = parseInt(inp.value, 10);
        if (!n) return;
        var known = cat.some(function (w) { return w.n === n; });
        if (!known) { msg.textContent = "работы " + n + " не существует"; return; }
        if (list.indexOf(n) >= 0) { msg.textContent = "уже в серии"; return; }
        list.push(n); inp.value = ""; msg.textContent = ""; drawWorks();
      };
      addRow.appendChild(inp); addRow.appendChild(addW);
      body.appendChild(addRow);
      msg.textContent = "";

      saver(msg, save, function () {
        nd.lead = lead.input.value.trim();
        nd.notes = noteInputs.filter(function (t) { return !t.dataset.gone; })
          .map(function (t) { return t.value.trim(); })
          .filter(Boolean);
        series[nm] = list;
        return aapi("/api/admin/content?file=notes.json", {
          method: "PUT", headers: { "Content-Type": "application/json" },
          body: JSON.stringify(notes)
        }).then(function () {
          return aapi("/api/admin/content?file=series.json", {
            method: "PUT", headers: { "Content-Type": "application/json" },
            body: JSON.stringify(series)
          });
        }).then(function () {
          return aapi("/api/admin/content?file=prices.json", {
            method: "PUT", headers: { "Content-Type": "application/json" },
            body: JSON.stringify(prices)
          });
        });
      });
    }).catch(function (e) { msg.textContent = e.message; });
  }

  /* ---------- витрина: имена, подписи, порядок, состав ---------- */
  function buildDeckAdmin(body, msg, save) {
    Promise.all([
      aapi("/api/admin/content?file=deck.json"),
      aapi("/api/admin/catalog")
    ]).then(function (r) {
      var deck = r[0].data.slice(), cat = r[1].works;
      body.innerHTML = "";
      var wrap = ael("div", "adeck");
      body.appendChild(wrap);

      function draw() {
        wrap.innerHTML = "";
        deck.forEach(function (d, i) {
          var row = ael("div", "adrow");
          var im = document.createElement("img");
          im.src = "assets/thumb/" + pad3(d.n) + ".jpg";
          im.loading = "lazy";
          row.appendChild(im);
          var col = ael("div", "adcol");
          col.appendChild(ael("span", "adnum", pad3(d.n) + " · " + d.series));
          var nameI = document.createElement("input");
          nameI.type = "text"; nameI.placeholder = "имя работы";
          nameI.value = d.name || "";
          nameI.oninput = function () { d.name = nameI.value; };
          var noteI = document.createElement("input");
          noteI.type = "text"; noteI.placeholder = "подпись — что это";
          noteI.value = d.note || "";
          noteI.oninput = function () { d.note = noteI.value; };
          col.appendChild(nameI); col.appendChild(noteI);
          row.appendChild(col);
          var up = ael("button", "abtn", "↑");
          up.onclick = function () {
            if (i > 0) { deck.splice(i - 1, 0, deck.splice(i, 1)[0]); draw(); }
          };
          var dn = ael("button", "abtn", "↓");
          dn.onclick = function () {
            if (i < deck.length - 1) { deck.splice(i + 1, 0, deck.splice(i, 1)[0]); draw(); }
          };
          var rm = ael("button", "abtn", "✕");
          rm.onclick = function () { deck.splice(i, 1); draw(); };
          row.appendChild(up); row.appendChild(dn); row.appendChild(rm);
          wrap.appendChild(row);
        });
      }
      draw();

      var addRow = ael("div", "arow");
      var inp = document.createElement("input");
      inp.type = "text";
      inp.placeholder = "номер работы, например 207";
      var add = ael("button", "abtn", "добавить в витрину");
      add.onclick = function () {
        var n = parseInt(inp.value, 10);
        var w = cat.filter(function (x) { return x.n === n; })[0];
        if (!w) { msg.textContent = "работы " + n + " не существует"; return; }
        if (!w.series) { msg.textContent = "работа не входит ни в одну серию"; return; }
        if (deck.some(function (d) { return d.n === n; })) {
          msg.textContent = "уже в витрине"; return;
        }
        deck.push({ n: n, series: w.series, name: "", note: "" });
        inp.value = ""; msg.textContent = ""; draw();
      };
      addRow.appendChild(inp); addRow.appendChild(add);
      body.appendChild(addRow);
      msg.textContent = "";

      saver(msg, save, function () {
        return aapi("/api/admin/content?file=deck.json", {
          method: "PUT", headers: { "Content-Type": "application/json" },
          body: JSON.stringify(deck)
        });
      });
    }).catch(function (e) { msg.textContent = e.message; });
  }

  document.addEventListener("keydown", function (e) {
    if (e.ctrlKey && e.shiftKey && (e.code === "KeyE" || e.key === "E" || e.key === "e")) {
      e.preventDefault();
      openAdmin();
    }
    if (e.key === "Escape" && apanel) closeAdmin();
    if (e.key === "Escape" && cardBox) closeCard();
  });

  /* ---------- витрина ----------
     Одна работа на экран, перелистывание стрелками, клавишами и свайпом.
     Соседние кадры подгружаются заранее, остальные не грузятся вовсе:
     иначе на входе прилетело бы шестнадцать картинок разом. */
  var deckEl = document.querySelector(".deck");
  var deckData = document.getElementById("deckData");
  if (deckEl && deckData) {
    var dk = JSON.parse(deckData.textContent);
    var frames = [].slice.call(deckEl.querySelectorAll(".fr"));
    var capH2 = deckEl.querySelector(".cap h2");
    var capMat = deckEl.querySelector(".cap .mat");
    var capSrc = deckEl.querySelector(".cap .src");
    var tick = deckEl.querySelector(".tick");
    var cur = 0;

    var wake = function (i) {
      var f = frames[(i + frames.length) % frames.length];
      var im = f && f.querySelector("img");
      if (im && !im.getAttribute("src") && im.dataset.src) {
        im.src = im.dataset.src;
        im.removeAttribute("data-src");
      }
    };

    var goto = function (i) {
      i = (i % dk.length + dk.length) % dk.length;
      frames[cur].classList.remove("on");
      cur = i;
      frames[cur].classList.add("on");
      var d = dk[i];
      capH2.textContent = "'" + (d.name || d.series + " · " + pad3(d.n)) + "'";
      capMat.textContent = d.note || "";
      capSrc.textContent = "view series " + d.series + " →";
      capSrc.href = "s/" + d.slug + ".html";
      if (tick) tick.textContent = pad2(i + 1) + " / " + pad2(dk.length);
      wake(i); wake(i + 1); wake(i - 1);
    };

    /* Кнопка «поделиться» рядом со ссылкой на серию. Витрина — парадная
       страница, показывать работу логичнее всего именно отсюда, а раньше
       кнопка жила только в лентах серий. */
    var dgive = document.createElement("button");
    dgive.type = "button";
    dgive.className = "give dgive";
    dgive.textContent = "[share]";
    var capBox = deckEl.querySelector(".cap");
    if (capBox) capBox.appendChild(dgive);

    deckEl.addEventListener("click", function (e) {
      if (e.target.closest(".dgive")) {
        share(dk[cur].n, dk[cur].series, dgive);
        return;
      }
      var a = e.target.closest(".arw");
      if (a) goto(cur + (+a.dataset.d));
    });

    document.addEventListener("keydown", function (e) {
      if (menuList && !menuList.hidden) return;
      if (e.key === "ArrowLeft") goto(cur - 1);
      else if (e.key === "ArrowRight") goto(cur + 1);
    });

    var tx = null;
    deckEl.addEventListener("touchstart", function (e) {
      tx = e.changedTouches[0].clientX;
    }, { passive: true });
    deckEl.addEventListener("touchend", function (e) {
      if (tx === null) return;
      var dx = e.changedTouches[0].clientX - tx;
      if (Math.abs(dx) > 45) goto(cur + (dx < 0 ? 1 : -1));
      tx = null;
    }, { passive: true });

    wake(1);
    goto(0);
  }

  function pad2(n) { return String(n).padStart(2, "0"); }

  /* ---------- слайдшоу на первом экране ----------
     Порядок — по лайкам. Первый слайд уже отрисован сервером, поэтому
     страница видна сразу; скрипт только достраивает остальные и,
     если голоса есть, переставляет их вперёд. */
  function pad3(n) { return String(n).padStart(3, "0"); }

  var slidesBox = document.querySelector(".hero .slides");
  var heroEl = document.getElementById("heroData");
  if (slidesBox && heroEl) {
    var hd = JSON.parse(heroEl.textContent);

    var startShow = function (list) {
      list = list.filter(function (n) { return hd.slug[n]; }).slice(0, 10);
      if (!list.length) return;
      var orig = slidesBox.querySelector(".slide");
      var made = list.map(function (n) {
        var a = document.createElement("a");
        a.className = "slide";
        a.href = "s/" + hd.slug[n] + ".html";
        var img = document.createElement("img");
        img.src = "assets/img/" + pad3(n) + ".jpg";
        img.alt = "";
        img.width = 1600;
        img.height = 900;
        a.appendChild(img);
        slidesBox.appendChild(a);
        return a;
      });

      var swap = function () {
        if (orig) {
          orig.classList.remove("on");
          setTimeout(function () { orig.remove(); }, 1300);
        }
        made[0].classList.add("on");
        if (calm || made.length < 2) return;   /* без движения — один кадр */
        var i = 0;
        setInterval(function () {
          made[i].classList.remove("on");
          i = (i + 1) % made.length;
          made[i].classList.add("on");
          var nx = made[(i + 1) % made.length].querySelector("img");
          if (nx && !nx.complete) nx.loading = "eager";
        }, 5200);
      };

      /* ждём первый кадр, иначе на его месте мигнёт чёрное */
      var first = made[0].querySelector("img");
      if (first.complete) swap();
      else {
        first.addEventListener("load", swap, { once: true });
        first.addEventListener("error", swap, { once: true });
      }
    };

    fetch("/api/summary").then(function (r) { return r.json(); }).then(function (sum) {
      var liked = Object.keys(sum || {}).map(function (k) {
        return { n: +k, s: (sum[k].up || 0) - (sum[k].down || 0) };
      }).filter(function (x) { return x.s > 0; })
        .sort(function (a, b) { return b.s - a.s; })
        .map(function (x) { return x.n; });
      /* пока лайков мало — добираем запасным порядком из covers.py */
      hd.best.forEach(function (n) {
        if (liked.length < 8 && liked.indexOf(n) < 0) liked.push(n);
      });
      startShow(liked);
    }).catch(function () { startShow(hd.best.slice(0, 8)); });
  }

  var headEl = document.querySelector(".head");
  var SERIES_NAME = (headEl && headEl.dataset.series)
    || (document.querySelector(".head h1") || {}).textContent || "";

  if (!stack || !works.length) return;

  /* ================= реакции и комментарии ================= */

  var counts = {};   /* work -> {up, down, comments} */
  var mine = {};     /* work -> 1 | -1 */
  var apiOK = true;

  /* Метка голосующего живёт в браузере. Это не защита от накрутки, а
     защита от случайного двойного клика и способ поднять кнопки нажатыми. */
  function token() {
    var t = null;
    try { t = localStorage.getItem("dl-voter"); } catch (e) {}
    if (!t) {
      t = (Date.now().toString(36) + Math.random().toString(36).slice(2, 12))
        .replace(/[^a-z0-9]/g, "").slice(0, 32);
      try { localStorage.setItem("dl-voter", t); } catch (e) {}
    }
    return t;
  }

  function api(url, opts) {
    opts = opts || {};
    opts.headers = opts.headers || {};
    opts.headers["X-Voter"] = token();
    return fetch(url, opts).then(function (r) {
      return r.json().then(function (j) {
        if (!r.ok) throw new Error(j && j.error ? j.error : "did not work");
        return j;
      });
    });
  }

  /* Ноль не показываем: строка «078 0 0 0» — шум, а не информация.
     Пустой <b> прячется правилом b:empty в CSS. */
  function num(n) { return n > 0 ? String(n) : ""; }

  function paint(work) {
    var c = counts[work] || { up: 0, down: 0, comments: 0 };
    document.querySelectorAll('.acts[data-n="' + work + '"]').forEach(function (row) {
      var up = row.querySelector('[data-v="1"] b');
      var dn = row.querySelector('[data-v="-1"] b');
      var cm = row.querySelector(".c b");
      if (up) up.textContent = num(c.up);
      if (dn) dn.textContent = num(c.down);
      if (cm) cm.textContent = num(c.comments);
      row.querySelectorAll("[data-v]").forEach(function (b) {
        b.setAttribute("aria-pressed", String(+b.dataset.v === mine[work]));
      });
    });
    if (at >= 0 && works[at] && works[at].n === work) paintPanel(work);
  }

  function paintPanel(work) {
    if (!view) return;
    var c = counts[work] || { up: 0, down: 0, comments: 0 };
    view.querySelector('.vote [data-v="1"] b').textContent = num(c.up);
    view.querySelector('.vote [data-v="-1"] b').textContent = num(c.down);
    view.querySelectorAll(".vote [data-v]").forEach(function (b) {
      b.setAttribute("aria-pressed", String(+b.dataset.v === mine[work]));
    });
  }

  function vote(work, dir) {
    if (!apiOK) return;
    var next = mine[work] === dir ? 0 : dir;   /* повторный клик снимает голос */
    api("/api/vote", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ work: work, dir: next })
    }).then(function (j) {
      counts[work] = { up: j.up, down: j.down, comments: (counts[work] || {}).comments || j.comments };
      if (next === 0) delete mine[work]; else mine[work] = next;
      paint(work);
    }).catch(function () {});
  }

  /* разметка кнопок под каждым кадром */
  document.querySelectorAll(".work").forEach(function (fig) {
    var n = +fig.dataset.n;
    var bot = fig.querySelector(".bot");
    if (!bot) return;
    var acts = document.createElement("span");
    acts.className = "acts";
    acts.dataset.n = n;
    acts.innerHTML =
      '<button type="button" data-v="1" aria-pressed="false" aria-label="Like">' + THUMB + "<b></b></button>" +
      '<button type="button" data-v="-1" aria-pressed="false" aria-label="Dislike">' + THUMB + "<b></b></button>" +
      '<button type="button" class="c" aria-label="Comments">' + PEN + "<b></b></button>";
    bot.appendChild(acts);
  });

  stack.addEventListener("click", function (e) {
    var b = e.target.closest(".acts button");
    if (!b) return;
    e.preventDefault();
    e.stopPropagation();
    var n = +b.closest(".acts").dataset.n;
    if (b.dataset.v) vote(n, +b.dataset.v);
    else openAt(n, true);
  });

  /* ---------- просмотр во весь экран ---------- */

  var view = document.createElement("div");
  view.className = "view";
  view.innerHTML =
    '<div class="stage">' +
      '<button class="shut" type="button" aria-label="Close">[ESC]</button>' +
      '<button class="talk" type="button" aria-label="Comments">[comments]</button>' +
      '<button class="step" data-d="-1" type="button" aria-label="Previous">←</button>' +
      '<button class="step" data-d="1" type="button" aria-label="Next">→</button>' +
      '<div class="slot"></div><div class="cap"></div>' +
    "</div>" +
    '<aside class="side">' +
      '<div class="vote">' +
        '<button type="button" data-v="1" aria-pressed="false" aria-label="Like">' + THUMB + "<b></b></button>" +
        '<button type="button" data-v="-1" aria-pressed="false" aria-label="Dislike">' + THUMB + "<b></b></button>" +
        '<button type="button" class="give">[share]</button>' +
        '<button type="button" class="more">[comments]</button>' +
        '<button type="button" class="close-side">[hide]</button>' +
      "</div>" +
      '<ul class="clist"></ul>' +
      '<form class="cform">' +
        '<input type="text" name="name" placeholder="name (optional)" maxlength="60" autocomplete="name">' +
        '<textarea name="body" placeholder="say something" maxlength="2000"></textarea>' +
        '<div class="cprev" hidden></div>' +
        '<div class="crow">' +
          '<label class="pick">photo<input type="file" accept="image/*" hidden></label>' +
          '<button type="submit">send</button>' +
        "</div>" +
        '<div class="cnote"></div>' +
      "</form>" +
    "</aside>";
  document.body.appendChild(view);

  var slot = view.querySelector(".slot");
  var cap = view.querySelector(".cap");
  var clist = view.querySelector(".clist");
  var cform = view.querySelector(".cform");
  var cnote = view.querySelector(".cnote");
  var cprev = view.querySelector(".cprev");
  var cfile = cform.querySelector('input[type="file"]');
  var at = -1;
  var lastFocus = null;

  function pad(n) { return String(n).padStart(3, "0"); }

  function show(i) {
    if (i < 0) i = works.length - 1;
    if (i >= works.length) i = 0;
    at = i;
    var w = works[i];
    slot.innerHTML = "";
    var el;
    if (w.k === "video") {
      el = document.createElement("video");
      el.src = "../assets/vid/" + pad(w.n) + ".mp4";
      el.poster = "../assets/poster/" + pad(w.n) + ".jpg";
      el.muted = true; el.loop = true; el.playsInline = true; el.autoplay = true;
      el.setAttribute("controls", "");
    } else {
      el = document.createElement("img");
      el.src = "../assets/img/" + pad(w.n) + ".jpg";
      el.alt = "Work " + pad(w.n);
    }
    slot.appendChild(el);
    cap.textContent = pad(w.n) + " / " + pad(works.length);
    paintPanel(w.n);
    if (view.getAttribute("data-side") === "full") loadComments(w.n);
    clearDraft();
  }

  /* На телефоне развёрнутая панель занимала 37% экрана, а сама работа —
     24%: пустая форма комментария была крупнее картины. Поэтому на узком
     экране панель открывается сжатой — видны только пальцы, комментарии
     разворачиваются по «[отзывы]». На широком всё сразу, как и просили. */
  /* 760, а не 900: 900 px — это обычное неразвёрнутое окно на ноутбуке,
     и на нём панель молча схлопывалась до пальцев без поля комментария.
     Порог должен совпадать с брейкпоинтом боковой раскладки в CSS. */
  function narrow() { return window.innerWidth < 760; }

  function openAt(n, withSide) {
    var i = works.findIndex(function (w) { return w.n === n; });
    if (i < 0) return;
    lastFocus = document.activeElement;
    view.setAttribute("data-open", "");
    if (withSide && apiOK) view.setAttribute("data-side", narrow() ? "compact" : "full");
    document.body.style.overflow = "hidden";
    show(i);
    view.querySelector(".shut").focus();
  }

  function shut() {
    view.removeAttribute("data-open");
    view.removeAttribute("data-side");
    document.body.style.overflow = "";
    slot.innerHTML = "";
    at = -1;
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  stack.addEventListener("click", function (e) {
    if (e.target.closest(".acts")) return;
    var fig = e.target.closest(".work");
    if (!fig) return;
    e.preventDefault();
    /* панель открыта сразу: лайки — главное, ради чего кадр разворачивают,
       и прятать их за отдельным нажатием неправильно */
    openAt(+fig.dataset.n, true);
  });

  view.addEventListener("click", function (e) {
    var step = e.target.closest(".step");
    if (step) { show(at + (+step.dataset.d)); return; }
    if (e.target.closest(".give")) {
      if (at >= 0) share(works[at].n, SERIES_NAME, view.querySelector(".give"));
      return;
    }
    if (e.target.closest(".close-side")) {
      /* на телефоне «скрыть» возвращает к пальцам, а не убирает панель целиком */
      if (narrow()) view.setAttribute("data-side", "compact");
      else view.removeAttribute("data-side");
      return;
    }
    if (e.target.closest(".more") || e.target.closest(".talk")) {
      if (!apiOK) return;
      view.setAttribute("data-side", "full");
      if (at >= 0) loadComments(works[at].n);
      return;
    }
    var vb = e.target.closest(".vote [data-v]");
    if (vb) { if (at >= 0) vote(works[at].n, +vb.dataset.v); return; }
    if (e.target.classList.contains("cpic")) {
      window.open(e.target.src, "_blank", "noopener");
      return;
    }
    if (e.target.closest(".shut") || e.target === view ||
        e.target === slot || e.target.classList.contains("stage")) shut();
  });

  document.addEventListener("keydown", function (e) {
    if (!view.hasAttribute("data-open")) return;
    if (e.target.matches("input, textarea")) {
      if (e.key === "Escape") e.target.blur();
      return;
    }
    if (e.key === "Escape") shut();
    else if (e.key === "ArrowLeft") show(at - 1);
    else if (e.key === "ArrowRight") show(at + 1);
  });

  /* ---------- комментарии ---------- */

  function when(iso) {
    try {
      return new Date(iso).toLocaleDateString("ru-RU",
        { day: "2-digit", month: "2-digit", year: "2-digit" });
    } catch (e) { return ""; }
  }

  function render(list) {
    clist.innerHTML = "";
    list.forEach(function (c) {
      var li = document.createElement("li");
      var head = document.createElement("div");
      head.className = "chead";
      var b = document.createElement("b");
      b.textContent = c.name;
      var t = document.createElement("span");
      t.textContent = when(c.at);
      head.appendChild(b);
      head.appendChild(t);
      var p = document.createElement("p");
      p.className = "cbody";
      p.textContent = c.body;          /* только textContent: тексты чужие */
      li.appendChild(head);
      li.appendChild(p);
      if (c.photo) {
        var im = document.createElement("img");
        im.className = "cpic";
        im.src = c.photo;
        im.alt = "photo in comment";
        im.loading = "lazy";
        li.appendChild(im);
      } else if (c.photoPending) {
        var w = document.createElement("span");
        w.className = "cwait";
        w.textContent = "photo awaiting review";
        li.appendChild(w);
      }
      clist.appendChild(li);
    });
  }

  function loadComments(work) {
    clist.innerHTML = "";
    api("/api/comments?work=" + work).then(function (j) {
      if (at >= 0 && works[at].n === work) render(j.comments || []);
    }).catch(function () {});
  }

  function clearDraft() {
    cform.querySelector('[name="body"]').value = "";
    cfile.value = "";
    cprev.hidden = true;
    cprev.innerHTML = "";
    cnote.textContent = "";
    cnote.removeAttribute("data-bad");
  }

  cfile.addEventListener("change", function () {
    cprev.innerHTML = "";
    var f = cfile.files && cfile.files[0];
    if (!f) { cprev.hidden = true; return; }
    if (f.size > 8 * 1024 * 1024) {
      cnote.textContent = "file over 8 MB";
      cnote.setAttribute("data-bad", "");
      cfile.value = "";
      cprev.hidden = true;
      return;
    }
    var im = document.createElement("img");
    im.src = URL.createObjectURL(f);
    im.onload = function () { URL.revokeObjectURL(im.src); };
    var drop = document.createElement("button");
    drop.type = "button";
    drop.textContent = "remove";
    drop.onclick = function () { cfile.value = ""; cprev.hidden = true; cprev.innerHTML = ""; };
    cprev.appendChild(im);
    cprev.appendChild(drop);
    cprev.hidden = false;
  });

  cform.addEventListener("submit", function (e) {
    e.preventDefault();
    if (at < 0) return;
    var work = works[at].n;
    var body = cform.querySelector('[name="body"]').value.trim();
    if (!body) {
      cnote.textContent = "write something";
      cnote.setAttribute("data-bad", "");
      return;
    }
    var fd = new FormData();
    fd.append("work", work);
    fd.append("body", body);
    fd.append("name", cform.querySelector('[name="name"]').value.trim());
    if (cfile.files && cfile.files[0]) fd.append("photo", cfile.files[0]);

    var btn = cform.querySelector('button[type="submit"]');
    btn.disabled = true;
    cnote.removeAttribute("data-bad");
    cnote.textContent = "sending…";

    api("/api/comments", { method: "POST", body: fd }).then(function (j) {
      clearDraft();
      counts[work] = j.tally;
      paint(work);
      loadComments(work);
      cnote.textContent = j.comment && j.comment.photoPending
        ? "sent — photo awaiting review" : "sent";
    }).catch(function (err) {
      cnote.textContent = err.message || "did not send";
      cnote.setAttribute("data-bad", "");
    }).then(function () { btn.disabled = false; });
  });

  /* ---------- стартовая загрузка счётчиков ---------- */

  Promise.all([
    api("/api/summary").catch(function () { apiOK = false; return {}; }),
    api("/api/mine").catch(function () { return {}; })
  ]).then(function (r) {
    counts = r[0] || {};
    var m = r[1] || {};
    Object.keys(m).forEach(function (k) { mine[+k] = m[k]; });
    if (!apiOK) {
      document.querySelectorAll(".acts").forEach(function (a) { a.remove(); });
      return;
    }
    works.forEach(function (w) { paint(w.n); });
  });
})();
