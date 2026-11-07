// Build-time data: reads the episode manifests and packages from the repo root,
// writes src/data/episodes.json and copies each deck to public/decks/<slug>/ (fa) and /en/.
import { readFileSync, writeFileSync, mkdirSync, copyFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const site = join(dirname(fileURLToPath(import.meta.url)), '..');
const root = process.env.HOMODYNE_ROOT || join(site, '..');
const meta = JSON.parse(readFileSync(join(site, 'src/data/episodes-meta.json'), 'utf8'));
const manifests = ['channel/season-01/manifest.json', 'channel/global/manifest.json'];

const field = (md, label) => {
  const m = md.match(new RegExp(`\\*\\*${label}:\\*\\*\\s*(.+)`));
  return m ? m[1].replace(/\*\*/g, '').trim() : '';
};

const episodes = [];
for (const file of manifests) {
  for (const ep of JSON.parse(readFileSync(join(root, file), 'utf8'))) {
    const m = meta[ep.hmd];
    if (!m) continue;
    const folder = join(root, ep.path);
    const readme = readFileSync(join(folder, 'README.md'), 'utf8');
    // /decks/<slug>/ is the Persian recording deck (old links keep working), /decks/<slug>/en/ its English twin
    const deck = join(folder, 'deck-fa.html');
    const deckEn = join(folder, 'deck-en.html');
    if (existsSync(deck)) {
      mkdirSync(join(site, 'public/decks', m.slug, 'en'), { recursive: true });
      copyFileSync(deck, join(site, 'public/decks', m.slug, 'index.html'));
      if (existsSync(deckEn)) copyFileSync(deckEn, join(site, 'public/decks', m.slug, 'en', 'index.html'));
    }
    episodes.push({
      hmd: ep.hmd,
      slug: m.slug,
      format: ep.format,
      next: ep.next,
      path: ep.path,
      youtube: m.youtube || null,
      fa: { title: ep.title, summary: field(readme, 'جملهٔ مرکزی'), boundary: field(readme, 'مرز ادعا') },
      en: m.en,
      hasDeck: existsSync(deck),
    });
  }
}
writeFileSync(join(site, 'src/data/episodes.json'), JSON.stringify(episodes, null, 2) + '\n');
console.log(`episodes.json: ${episodes.length} episodes`);
