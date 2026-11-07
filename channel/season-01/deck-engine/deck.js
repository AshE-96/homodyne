/* Homodyne recording deck v6 · shared engine. Inlined by scripts/build-decks.py.
   Keys: → / Space / PageDown next · ← / PageUp previous · Home / End · F fullscreen · H hide chrome · N presenter notes.
   ?frame=N (or #N) opens frame N (0 = cover). window.HMD exposes show() and frames for tests. */
(function () {
  'use strict';
  var root = document.documentElement;
  var fa = root.lang === 'fa';
  var stage = document.querySelector('.stage');
  var frames = Array.prototype.slice.call(document.querySelectorAll('.frame'));
  var counter = document.getElementById('counter');
  var timeEl = document.getElementById('time');
  var progress = document.querySelector('.progress');
  var current = 0;

  function digits(s) { return fa ? String(s).replace(/\d/g, function (d) { return '۰۱۲۳۴۵۶۷۸۹'[d]; }) : String(s); }
  function pad(n) { return n < 10 ? '0' + n : String(n); }
  function clock(sec) { sec = +sec || 0; return pad(Math.floor(sec / 60)) + ':' + pad(sec % 60); }

  // beat counters inside each frame ("02 / 14"); the cover has none
  var beats = frames.filter(function (f) { return f.id !== 'cover'; });
  beats.forEach(function (f, i) {
    var c = f.querySelector('.chrome .count');
    if (c) c.textContent = digits(pad(i + 1) + ' / ' + pad(beats.length));
  });

  function scale() {
    var navH = document.body.classList.contains('hide-chrome') ? 0 : 43;
    var w = window.innerWidth, h = window.innerHeight - navH;
    var s = Math.min(w / 1920, h / 1080);
    stage.style.transform = 'translate(' + (w - 1920 * s) / 2 + 'px,' + Math.max(0, (h - 1080 * s) / 2) + 'px) scale(' + s + ')';
  }

  // shrink a frame's content (CSS zoom) only if it would not fit; report it so the source can be tightened
  function fit(frame) {
    var main = frame.querySelector('main'), box = frame.querySelector('.fit');
    if (!main || !box) return;
    box.style.zoom = '';
    var z = Math.min(1, main.clientHeight / box.scrollHeight, main.clientWidth / box.scrollWidth);
    if (z < 0.999) {
      box.style.zoom = String(Math.floor(z * 1000) / 1000);
      frame.dataset.zoom = box.style.zoom;
      if (window.console) console.warn('frame ' + (frame.id || '?') + ' content shrunk to ' + box.style.zoom);
    }
  }

  function show(n) {
    current = Math.max(0, Math.min(frames.length - 1, n));
    frames.forEach(function (f, i) { f.classList.toggle('active', i === current); });
    var f = frames[current];
    fit(f);
    counter.textContent = digits((current + 1) + ' / ' + frames.length);
    timeEl.textContent = f.id === 'cover' ? (fa ? 'کاور' : 'cover') : digits(clock(f.dataset.start));
    progress.style.width = ((current + 1) / frames.length * 100) + '%';
    try { history.replaceState(null, '', '#' + current); } catch (e) { /* file:// in some browsers */ }
  }

  // cover wave: noise that resolves into one clean signal, the idea behind the name
  function wave() {
    var svg = document.querySelector('.cover .wave');
    if (!svg) return;
    var W = 1664, H = 150, mid = H / 2, seed = 7;
    function rnd() { seed = (seed * 16807) % 2147483647; return seed / 2147483647; }
    var noisy = [], clean = [];
    for (var x = 0; x <= W; x += 4) {
      var t = x / W, mix = Math.min(1, Math.max(0, (t - 0.28) / 0.22)); // 0 = all noise, 1 = all signal
      var sig = Math.sin(x / 46) * 46;
      var noise = (Math.sin(x / 7.3) * 18 + Math.sin(x / 3.1) * 12 + (rnd() - 0.5) * 70) * (1 - mix);
      var y = mid - (sig * mix + noise);
      (t < 0.5 ? noisy : clean).push(x + ',' + y.toFixed(1));
      if (t >= 0.5 && clean.length === 1) noisy.push(x + ',' + y.toFixed(1));
    }
    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    svg.innerHTML =
      '<polyline points="' + noisy.join(' ') + '" fill="none" stroke="#A9A69D" stroke-opacity=".75" stroke-width="3" stroke-linejoin="round"/>' +
      '<polyline points="' + clean.join(' ') + '" fill="none" stroke="#E8A33D" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>';
  }

  document.getElementById('next').onclick = function () { show(current + 1); };
  document.getElementById('prev').onclick = function () { show(current - 1); };
  document.addEventListener('keydown', function (e) {
    var k = e.key;
    if (k === 'ArrowRight' || k === 'PageDown' || k === ' ') { e.preventDefault(); show(current + 1); }
    else if (k === 'ArrowLeft' || k === 'PageUp') { e.preventDefault(); show(current - 1); }
    else if (k === 'Home') show(0);
    else if (k === 'End') show(frames.length - 1);
    else if (k.toLowerCase() === 'n') document.body.classList.toggle('show-notes');
    else if (k.toLowerCase() === 'h') { document.body.classList.toggle('hide-chrome'); scale(); }
    else if (k.toLowerCase() === 'f') {
      if (document.fullscreenElement) document.exitFullscreen(); else root.requestFullscreen();
    }
  });
  window.addEventListener('resize', scale);

  wave();
  scale();
  var q = /[?&]frame=(\d+)/.exec(location.search) || /^#(\d+)$/.exec(location.hash);
  show(q ? +q[1] : 0);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { fit(frames[current]); });
  window.HMD = { show: show, frames: frames, fit: fit, get current() { return current; } };
})();
