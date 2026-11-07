#!/usr/bin/env node
/**
 * drive-decks.js — runtime test for the episode screen layers.
 *
 * check-decks.py verifies structure. This one actually runs each deck in a
 * DOM and presses the keys, because the failures that matter on recording day
 * are runtime ones: chrome that never injects, a table whose config points at
 * nothing, a right-arrow walk that dead-ends halfway through the episode.
 *
 * Needs jsdom, which is deliberately not vendored into this repo:
 *
 *     npm install jsdom          # once, anywhere on the path
 *     node scripts/drive-decks.js
 *
 * Exit code is non-zero if any deck fails.
 */

const fs = require('fs'), path = require('path'), { JSDOM } = require('jsdom');

const ROOT = path.resolve(__dirname, '..');
const decks = fs.readdirSync(path.join(ROOT, 'parts', '02-benchmarking', '_archive', 'v1-m2lab'))
  .filter(d => /^\d$/.test(d)).sort()
  .map(d => path.join(ROOT, 'parts', '02-benchmarking', '_archive', 'v1-m2lab', d))
  .flatMap(dir => fs.readdirSync(dir).filter(f => f.endsWith('Design_Mockup.html')).map(f => path.join(dir, f)));

let failed = 0;

for (const file of decks) {
  const rel = path.relative(ROOT, file);
  const errors = [];
  const dom = new JSDOM(fs.readFileSync(file, 'utf8'), {
    runScripts: 'dangerously', pretendToBeVisual: true, url: 'file://' + file,
    virtualConsole: new (require('jsdom').VirtualConsole)().on('jsdomError', e => errors.push(e.message)),
  });
  const { window } = dom;
  const doc = window.document;

  const press = k => doc.dispatchEvent(new window.KeyboardEvent('keydown', { key: k, bubbles: true }));

  const slides = [...doc.querySelectorAll('.slide')];
  const dots   = doc.querySelectorAll('.chrome__dots .dot').length;
  const ep     = (doc.querySelector('.chrome__bar b') || {}).textContent;

  if (!doc.getElementById('chrome')) errors.push('chrome was never injected');
  if (dots !== slides.length) errors.push(`${dots} dots for ${slides.length} slides`);

  // every table/entity/list the config declared must have produced rows
  for (const t of doc.querySelectorAll('table.mtable')) {
    if (!t.querySelectorAll('tbody tr').length) errors.push(`table #${t.id} rendered no rows`);
  }
  for (const g of doc.querySelectorAll('.entity-grid')) {
    if (!g.children.length) errors.push(`entity grid #${g.id} rendered no cards`);
  }

  // walk the whole deck with right-arrow only, exactly as on the day
  press('Home');
  const beats = [];
  let guard = 0, lastNum = '';
  while (guard++ < 400) {
    const num = doc.getElementById('c-num').textContent;
    const step = doc.getElementById('c-step').textContent;
    if (num !== lastNum) { beats.push(step || '—'); lastNum = num; }
    const before = num + '|' + step;
    press('ArrowRight');
    if (before === doc.getElementById('c-num').textContent + '|' + doc.getElementById('c-step').textContent) break;
  }
  const endNum = doc.getElementById('c-num').textContent;
  const expected = String(slides.length).padStart(2, '0');
  if (!endNum.startsWith(expected)) errors.push(`right-arrow walk stopped at ${endNum}, not ${expected}`);

  // going back must land on a completed slide, never an empty one
  press('Home'); press('ArrowDown'); press('ArrowDown');
  press('ArrowLeft');
  let back = doc.getElementById('c-step').textContent;
  if (back && !/beat (\d+)\/\1$/.test(back)) errors.push(`stepping back landed on "${back}", not a finished slide`);

  // the other record-day keys must not throw
  for (const k of ['h', 'b', 's', 't', '?', 'Escape', 'r', 'End', 'Home']) press(k);

  console.log(`${errors.length ? 'FAIL' : 'ok  '}  ${rel.padEnd(52)} ${ep}  ${slides.length} slides  ${guard} presses`);
  errors.forEach(e => console.log('        ' + e));
  if (errors.length) failed++;
  window.close();
}
console.log(`\n${decks.length} deck(s) driven, ${failed} failed`);
process.exit(failed ? 1 : 0);
