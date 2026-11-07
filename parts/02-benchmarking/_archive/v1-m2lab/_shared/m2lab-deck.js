/* ══════════════════════════════════════════════════════════════════════════
   M2Lab — Benchmark Chapter · SHARED DECK ENGINE
   Companion to m2lab-deck.css. Shared by all nine episode decks.

   An episode deck writes its slides as markup, then calls:

     M2Deck.init({
       runtime : 1100,                                  // episode length, seconds
       tables  : { 'tbl-id': { head:[], rows:[[]], term:0, strike:3, chips:'id' } },
       entities: { 'grid-id': [ {name, tone, rows:[[k,v]], limit} ] },
       lists   : { 'ul-id'  : { items:[], countId:'badge-id' } }
     });

   THE BUILD SYSTEM
   One step counter per slide drives three declarative hooks:

     data-build="n"   hidden → revealed at n → focused at n → dimmed after n
     data-track="n"   always visible; .is-now at n, .is-done after n
     data-since="n"   always visible; .is-since from n onward (state changes)

   Design Language §2.2 / §2.5: elements arrive with the spoken line, the one
   being explained turns amber, everything already said drops to muted. The
   presenter drives every beat with →; nothing is on a timer.

   Each slide also carries data-at="<step>" so a deck's bespoke choreography
   can be written as plain CSS instead of more JavaScript.
   ══════════════════════════════════════════════════════════════════════════ */

window.M2Deck = (function(){
  'use strict';

  /* ─── small helpers ──────────────────────────────────────────────────── */
  function el(tag, cls, text){
    var n = document.createElement(tag);
    if(cls) n.className = cls;
    if(text !== undefined) n.textContent = text;
    return n;
  }
  function pad2(n){ return (n < 10 ? '0' : '') + n; }
  function each(list, fn){ Array.prototype.forEach.call(list, fn); }

  /* ─── renderers ──────────────────────────────────────────────────────── */

  /* One table row per spoken beat. `term` marks the entity column, `strike`
     marks a column that should read as crossed out, `chips` renders an
     overview strip so a long table never loses the audience. */
  function buildTable(id, spec){
    var t = document.getElementById(id);
    if(!t) return;

    var thead = el('thead'), htr = el('tr');
    spec.head.forEach(function(h){
      var th = el('th', null, h);
      th.setAttribute('scope','col');
      htr.appendChild(th);
    });
    thead.appendChild(htr);
    t.appendChild(thead);

    var tbody = el('tbody');
    spec.rows.forEach(function(cells, i){
      var tr = el('tr');
      tr.dataset.build = String(i + 1);
      cells.forEach(function(cell, ci){
        var cls = spec.term === ci ? 'term' : (spec.strike === ci ? 'strike' : null);
        tr.appendChild(el('td', cls, cell));
      });
      tbody.appendChild(tr);
    });
    t.appendChild(tbody);

    if(spec.chips){
      var wrap = document.getElementById(spec.chips);
      if(wrap){
        spec.rows.forEach(function(cells, i){
          var c = el('span','chip', cells[0]);
          c.dataset.track = String(i + 1);
          wrap.appendChild(c);
        });
      }
    }
  }

  /* Design Language §2.4 — first column is the entity with a neutral tone dot
     (never amber, so it cannot compete with the signal colour), and the
     "doesn't prove" band is always the last row and the loudest. */
  function buildEntities(id, list){
    var wrap = document.getElementById(id);
    if(!wrap) return;

    list.forEach(function(e, i){
      var card = el('article','entity');
      card.dataset.build = String(i + 1);

      var head = el('div','entity__head');
      var dot  = el('span','entity__dot');
      dot.dataset.tone = e.tone;
      head.appendChild(dot);
      head.appendChild(el('h3','entity__name', e.name));
      card.appendChild(head);

      var body = el('div','entity__body');
      (e.rows || []).forEach(function(pair){
        var row = el('div','entity__row');
        row.appendChild(el('div','entity__k', pair[0]));
        row.appendChild(el('div','entity__v', pair[1]));
        body.appendChild(row);
      });
      card.appendChild(body);

      if(e.limit){
        var limit = el('div','entity__limit');
        limit.appendChild(el('div','entity__k', e.limitLabel || 'Doesn’t prove'));
        limit.appendChild(el('div','entity__v', e.limit));
        card.appendChild(limit);
      }
      wrap.appendChild(card);
    });
  }

  function fillList(id, spec){
    var ul = document.getElementById(id);
    if(!ul) return;
    var items = spec.items || spec;
    items.forEach(function(x){ ul.appendChild(el('li', null, x)); });
    var badge = spec.countId && document.getElementById(spec.countId);
    if(badge) badge.textContent = items.length;
  }

  /* Record-day chrome — Design Language §2.15. Identical on every deck, so it
     is injected rather than copy-pasted into nine files. It is an overlay:
     hiding it with H must not move a single pixel of the frame. */
  var CHROME = ''
    + '<div class="chrome" id="chrome">'
    +   '<div class="scrub" id="scrub" style="width:0"></div>'
    +   '<div class="chrome__bar">'
    +     '<span>M2Lab · Benchmarking Foundations · <b>{EP}</b> — <span id="c-num">01/01</span></span>'
    +     '<span id="c-comp"></span><span id="c-step"></span><span id="c-time"></span>'
    +     '<span class="chrome__clock" id="c-clock">T 00:00</span>'
    +   '</div>'
    +   '<div class="chrome__dots" id="c-dots"></div>'
    +   '<p class="chrome__hint">← → build · ↑ ↓ slide · H hide · ? keys</p>'
    + '</div>'
    + '<div class="blackout" aria-hidden="true"></div>'
    + '<div class="help" role="dialog" aria-label="Keyboard shortcuts"><div class="help__panel">'
    +   '<h2>Record-day keys</h2><dl>'
    +   '<dt>→ / Space</dt><dd>Next build beat, then next slide</dd>'
    +   '<dt>←</dt><dd>Previous beat / slide</dd>'
    +   '<dt>↑ ↓</dt><dd>Jump a whole slide, skipping its build</dd>'
    +   '<dt>Home / End</dt><dd>First / last slide</dd>'
    +   '<dt>R</dt><dd>Reset this slide’s build to the start</dd>'
    +   '<dt>H</dt><dd>Hide the reference bar — do this before recording</dd>'
    +   '<dt>F</dt><dd>Fullscreen</dd>'
    +   '<dt>B</dt><dd>Blank to graphite (hold between takes)</dd>'
    +   '<dt>S</dt><dd>Source strip on / off</dd>'
    +   '<dt>T</dt><dd>Start / reset the runtime clock</dd>'
    +   '<dt>P</dt><dd>Print the downloadable card as A4</dd>'
    +   '<dt>?</dt><dd>This panel</dd>'
    +   '</dl></div></div>';

  /* ─── init ───────────────────────────────────────────────────────────── */
  function init(cfg){
    cfg = cfg || {};
    var RUNTIME = cfg.runtime || 1100;

    if(!document.getElementById('chrome')){
      document.getElementById('deck').insertAdjacentHTML(
        'beforeend', CHROME.replace('{EP}', cfg.episode || 'Ep.01'));
    }

    Object.keys(cfg.tables   || {}).forEach(function(k){ buildTable(k, cfg.tables[k]); });
    Object.keys(cfg.entities || {}).forEach(function(k){ buildEntities(k, cfg.entities[k]); });
    Object.keys(cfg.lists    || {}).forEach(function(k){ fillList(k, cfg.lists[k]); });

    /* Proof / Source strips — Design Language §2.7 */
    each(document.querySelectorAll('.slide[data-source]'), function(s){
      s.appendChild(el('p','source-strip', s.dataset.source));
    });

    /* ── canvas scaler: the deck is always 1920×1080 and is scaled, never
       reflowed, so the design and the screen recording are the same pixels ── */
    var deck = document.getElementById('deck');
    function fit(){
      deck.style.setProperty('--k', Math.min(window.innerWidth / 1920, window.innerHeight / 1080));
    }
    window.addEventListener('resize', fit);
    fit();

    /* ── slide + build engine ── */
    var slides = Array.prototype.slice.call(document.querySelectorAll('.slide'));

    slides.forEach(function(s){
      var max = 0;
      each(s.querySelectorAll('[data-build],[data-track],[data-since]'), function(n){
        ['build','track','since'].forEach(function(key){
          var v = parseInt(n.dataset[key], 10);
          if(!isNaN(v)) max = Math.max(max, v);
        });
      });
      s._maxBuild = max;
      s._maxStep  = max > 0 ? max + 1 : 0;  // the extra beat = summing up: all lit, none dimmed
      s._focus    = s.dataset.focus !== 'off';
    });

    var idx = 0, step = 0;

    function paint(){
      slides.forEach(function(s, i){
        var on = i === idx;
        s.classList.toggle('is-active', on);
        s.setAttribute('aria-hidden', on ? 'false' : 'true');
      });

      var s = slides[idx];
      s.dataset.at = step;                    // lets bespoke choreography be pure CSS
      var focusing = s._focus && step <= s._maxBuild;

      each(s.querySelectorAll('[data-build]'), function(n){
        var b = parseInt(n.dataset.build, 10);
        n.classList.toggle('is-in',    step >= b);
        n.classList.toggle('is-focus', focusing && step === b);
        n.classList.toggle('is-dim',   focusing && step >  b);
      });
      each(s.querySelectorAll('[data-track]'), function(n){
        var b = parseInt(n.dataset.track, 10);
        n.classList.toggle('is-now',  step === b);
        n.classList.toggle('is-done', step >  b);
      });
      each(s.querySelectorAll('[data-since]'), function(n){
        n.classList.toggle('is-since', step >= parseInt(n.dataset.since, 10));
      });

      document.body.classList.toggle('on-graphite', s.dataset.theme === 'graphite');
      paintChrome(s);
    }

    function firstStep(s){ return s._maxBuild > 0 ? 1 : 0; }

    function goTo(i, atEnd){
      idx  = Math.max(0, Math.min(slides.length - 1, i));
      step = atEnd ? slides[idx]._maxStep : firstStep(slides[idx]);
      paint();
    }
    function next(){
      if(step < slides[idx]._maxStep){ step++; paint(); }
      else if(idx < slides.length - 1){ goTo(idx + 1, false); }
    }
    function prev(){
      if(step > firstStep(slides[idx])){ step--; paint(); }
      else if(idx > 0){ goTo(idx - 1, true); }   // land on the finished slide, not an empty one
    }

    /* ── chrome ── */
    var dotsWrap = document.getElementById('c-dots');
    slides.forEach(function(s, i){
      var b = el('button','dot');
      b.type = 'button';
      b.setAttribute('aria-label','Slide ' + (i + 1) + ' — ' + (s.dataset.comp || ''));
      b.addEventListener('click', function(ev){ ev.stopPropagation(); goTo(i, false); });
      dotsWrap.appendChild(b);
    });
    var dots   = Array.prototype.slice.call(dotsWrap.children);
    var cNum   = document.getElementById('c-num');
    var cComp  = document.getElementById('c-comp');
    var cStep  = document.getElementById('c-step');
    var cTime  = document.getElementById('c-time');
    var cClock = document.getElementById('c-clock');
    var scrub  = document.getElementById('scrub');

    function paintChrome(s){
      dots.forEach(function(d, i){ d.classList.toggle('is-on', i === idx); });
      cNum.textContent  = pad2(idx + 1) + '/' + pad2(slides.length);
      cComp.textContent = s.dataset.comp || '';
      cStep.textContent = s._maxStep ? ('beat ' + step + '/' + s._maxStep) : '';
      cTime.textContent = s.dataset.time || '';
      var st = s.dataset.start;
      scrub.style.width = (st === undefined ? 100 : Math.round(Number(st) / RUNTIME * 100)) + '%';
    }

    /* Rehearsal clock: how far this take has drifted from the scripted timing. */
    var t0 = null;
    setInterval(function(){
      if(t0 === null) return;
      var sec = Math.floor((Date.now() - t0) / 1000);
      cClock.textContent = 'T ' + pad2(Math.floor(sec / 60)) + ':' + pad2(sec % 60);
      var target = Number(slides[idx].dataset.start);
      cClock.classList.toggle('is-late', !isNaN(target) && sec - target > 25);
    }, 500);

    /* ── input ── */
    document.addEventListener('keydown', function(e){
      if(e.metaKey || e.ctrlKey || e.altKey) return;
      var k = e.key;
      if(document.body.classList.contains('is-help') && k !== '?' && k !== 'Escape') return;

      switch(k){
        case 'ArrowRight': case ' ': case 'PageDown': e.preventDefault(); next(); return;
        case 'ArrowLeft':  case 'PageUp':             e.preventDefault(); prev(); return;
        case 'ArrowDown':  e.preventDefault(); goTo(idx + 1, false); return;
        case 'ArrowUp':    e.preventDefault(); goTo(idx - 1, false); return;
        case 'Home':       e.preventDefault(); goTo(0, false); return;
        case 'End':        e.preventDefault(); goTo(slides.length - 1, false); return;
        case 'Escape':     document.body.classList.remove('is-help','is-blank'); return;
        case '?':          document.body.classList.toggle('is-help'); return;
      }

      switch(k.toLowerCase()){
        case 'r': step = firstStep(slides[idx]); paint(); break;
        case 'h': document.body.classList.toggle('chrome-hidden'); break;
        case 'b': document.body.classList.toggle('is-blank'); break;
        case 's': document.body.classList.toggle('hide-source'); break;
        case 'p': window.print(); break;
        case 't': t0 = (t0 === null ? Date.now() : null);
                  if(t0 === null){ cClock.textContent = 'T 00:00'; cClock.classList.remove('is-late'); }
                  break;
        case 'f':
          if(!document.fullscreenElement){ document.documentElement.requestFullscreen && document.documentElement.requestFullscreen(); }
          else { document.exitFullscreen && document.exitFullscreen(); }
          break;
      }
    });

    document.getElementById('viewport').addEventListener('click', function(e){
      if(e.target.closest('.chrome') || document.body.classList.contains('is-help')) return;
      if(e.clientX > window.innerWidth / 2){ next(); } else { prev(); }
    });

    /* A visible cursor ruins a clean take. */
    var idleTimer;
    function wake(){
      document.body.classList.remove('is-idle');
      clearTimeout(idleTimer);
      idleTimer = setTimeout(function(){ document.body.classList.add('is-idle'); }, 2000);
    }
    document.addEventListener('mousemove', wake);
    wake();

    goTo(0, false);   // opens on the first beat, never on an empty frame

    return { goTo: goTo, next: next, prev: prev, slides: slides };
  }

  return { init: init, el: el };
})();
