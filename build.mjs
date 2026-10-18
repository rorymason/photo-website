// ─────────────────────────────────────────────────────────────
//  build.mjs: turns content/ + static/ into the finished site in dist/
//  Run:  node build.mjs        (no npm install needed)
// ─────────────────────────────────────────────────────────────

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import site from './site.config.mjs';

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(ROOT, 'dist');
const PROJECTS_DIR = path.join(ROOT, 'content', 'projects');

// ── small helpers ────────────────────────────────────────────

const esc = (s = '') =>
  String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

// Allows <em>/<strong> in JSON copy but escapes everything else.
const rich = (s = '') =>
  esc(s).replace(/&lt;(\/?)(em|strong)&gt;/g, '<$1$2>');

function rmrf(p) { fs.rmSync(p, { recursive: true, force: true }); }
function mkdirp(p) { fs.mkdirSync(p, { recursive: true }); }
function copyDir(src, dest) {
  if (!fs.existsSync(src)) return;
  mkdirp(dest);
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, entry.name);
    const d = path.join(dest, entry.name);
    if (entry.isDirectory()) copyDir(s, d);
    else if (!entry.name.startsWith('.')) fs.copyFileSync(s, d);
  }
}
function write(rel, html) {
  const file = path.join(OUT, rel);
  mkdirp(path.dirname(file));
  fs.writeFileSync(file, html);
}

// Reads pixel size from a JPEG or PNG so <img> tags get width/height (no layout jumps).
function imageSize(file) {
  try {
    const buf = fs.readFileSync(file);
    if (buf.readUInt32BE(0) === 0x89504e47) return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) };
    if (buf[0] === 0xff && buf[1] === 0xd8) {
      let i = 2;
      while (i < buf.length) {
        if (buf[i] !== 0xff) { i++; continue; }
        const marker = buf[i + 1];
        const len = buf.readUInt16BE(i + 2);
        if (marker >= 0xc0 && marker <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(marker)) {
          return { h: buf.readUInt16BE(i + 5), w: buf.readUInt16BE(i + 7) };
        }
        i += 2 + len;
      }
    }
  } catch { /* missing file: handled by caller */ }
  return null;
}

const warnings = [];

// Adds width/height/lazy-loading to every <img> whose src points into the project folder.
function processImages(html, projectDir, slug) {
  return html.replace(/<img\b([^>]*?)\/?>/g, (tag, attrs) => {
    const srcMatch = attrs.match(/\ssrc="([^"]+)"/);
    if (!srcMatch) return tag;
    const src = srcMatch[1];
    if (/^(https?:)?\/\//.test(src) || src.startsWith('/')) return tag;
    const file = path.join(projectDir, src);
    if (!fs.existsSync(file)) warnings.push(`${slug}: missing image ${src}`);
    let extra = '';
    if (!/\swidth=/.test(attrs)) {
      const size = imageSize(file);
      if (size) extra += ` width="${size.w}" height="${size.h}"`;
    }
    if (!/\sloading=/.test(attrs)) extra += ' loading="lazy"';
    if (!/\sdecoding=/.test(attrs)) extra += ' decoding="async"';
    if (!/\salt=/.test(attrs)) warnings.push(`${slug}: image ${src} has no alt text`);
    return `<img${attrs}${extra}>`;
  });
}

// ── icons (simple stroke icons, 24px grid) ───────────────────

const ICONS = {
  phone: '<rect x="6" y="2.5" width="12" height="19" rx="3"/><path d="M11 18h2"/>',
  search: '<circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.2-4.2"/>',
  sparkle: '<path d="M12 3l2.1 6.9L21 12l-6.9 2.1L12 21l-2.1-6.9L3 12l6.9-2.1z"/>',
  compass: '<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/>',
  camera: '<path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/>',
  arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  back: '<path d="M19 12H5M11 6l-6 6 6 6"/>',
};
const icon = (name, size = 14) =>
  `<svg class="icon" aria-hidden="true" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${ICONS[name] || ''}</svg>`;

function tagPill(key) {
  const t = site.tags[key];
  if (!t) { warnings.push(`unknown tag "${key}"`); return ''; }
  return `<span class="tag">${icon(t.icon)}${esc(t.label)}</span>`;
}
const tagRow = (p) =>
  `<div class="tag-row">${p.tags.map(tagPill).join('')}${p.format ? `<span class="format">${esc(p.format)}</span>` : ''}</div>`;

// ── load projects ────────────────────────────────────────────

function loadProjects() {
  const list = [];
  for (const slug of fs.readdirSync(PROJECTS_DIR)) {
    if (slug.startsWith('_') || slug.startsWith('.')) continue; // _template etc.
    const dir = path.join(PROJECTS_DIR, slug);
    if (!fs.statSync(dir).isDirectory()) continue;
    const metaFile = path.join(dir, 'project.json');
    if (!fs.existsSync(metaFile)) { warnings.push(`${slug}: no project.json, skipped`); continue; }
    let meta;
    try { meta = JSON.parse(fs.readFileSync(metaFile, 'utf8')); }
    catch (e) { throw new Error(`content/projects/${slug}/project.json is not valid JSON: ${e.message}`); }
    if (meta.hidden) continue;
    const pageFile = path.join(dir, 'page.html');
    const body = fs.existsSync(pageFile) ? fs.readFileSync(pageFile, 'utf8') : '';
    list.push({
      slug,
      dir,
      section: 'featured',
      tags: [],
      color: 'grey',
      card: { style: 'band' },
      facts: {},
      ...meta,
      hasPage: meta.page !== false && body.trim().length > 0,
      body,
    });
  }
  return list.sort((a, b) => (a.order ?? 99) - (b.order ?? 99));
}

const colorOf = (p) => site.colors[p.color] || p.color || site.colors.grey;
const linkOf = (p) => `/work/${p.slug}/`;
const imgSrc = (p, src, absolute = true) => (absolute ? `/work/${p.slug}/${src}` : src);

// ── visuals shared by cards and heroes ───────────────────────

function phones(p, images, cls, absolute) {
  return `<div class="${cls}">${images
    .map((im, i) => {
      const file = typeof im === 'string' ? im : im.src;
      const alt = typeof im === 'string' ? '' : im.alt || '';
      const size = imageSize(path.join(p.dir, file));
      const dims = size ? ` width="${size.w}" height="${size.h}"` : '';
      return `<img class="phone phone--${i + 1}" src="${esc(imgSrc(p, file, absolute))}" alt="${esc(alt)}"${dims} decoding="async">`;
    })
    .join('')}</div>`;
}
function single(p, im, cls, absolute) {
  const size = imageSize(path.join(p.dir, im.src));
  const dims = size ? ` width="${size.w}" height="${size.h}"` : '';
  return `<div class="${cls}"><img src="${esc(imgSrc(p, im.src, absolute))}" alt="${esc(im.alt || '')}"${dims} decoding="async"></div>`;
}
function visual(p, v, context) {
  if (!v) return '';
  if (v.style === 'phones') return phones(p, v.images || [], `${context}-visual visual--phones`, true);
  if (v.style === 'photo') return single(p, v.image, `${context}-visual visual--photo`, true);
  if (v.style === 'framed') return single(p, v.image, `${context}-visual visual--framed`, true);
  return '';
}

// ── homepage cards ───────────────────────────────────────────

function featuredCard(p) {
  const tagsAttr = p.tags.join(' ');
  const open = p.hasPage ? `<a class="card" href="${linkOf(p)}"` : `<div class="card card--static"`;
  const close = p.hasPage ? '</a>' : '</div>';
  const cta = p.hasPage
    ? `<span class="cta">${esc(p.cta || 'View project')}</span>`
    : `<span class="cta cta--muted">${esc(p.cta || 'Case study coming soon')}</span>`;
  const style = `--card:${colorOf(p)}`;

  if (!p.card || p.card.style === 'band') {
    const right = p.card?.quote
      ? `<p class="card-quote">"${esc(p.card.quote)}"</p>`
      : `<p class="card-summary">${rich(p.summary)}</p>`;
    return `${open} data-tags="${tagsAttr}" style="${style}" data-band>
  <div class="card-band-left">${tagRow(p)}<h2 class="card-title">${esc(p.title)}</h2></div>
  <div class="card-band-right">${right}${cta}</div>
${close}`;
  }
  return `${open} data-tags="${tagsAttr}" style="${style}">
  <div class="card-text">
    ${tagRow(p)}
    <div>
      <h2 class="card-title">${esc(p.title)}</h2>
      <p class="card-summary">${rich(p.summary)}</p>
      ${cta}
    </div>
  </div>
  ${visual(p, p.card, 'card')}
${close}`;
}

function otherCard(p) {
  const img = p.card?.image || p.card?.images?.[0];
  const im = typeof img === 'string' ? { src: img, alt: '' } : img;
  const size = im ? imageSize(path.join(p.dir, im.src)) : null;
  const dims = size ? ` width="${size.w}" height="${size.h}"` : '';
  const open = p.hasPage ? `<a class="mini" href="${linkOf(p)}"` : `<div class="mini"`;
  const close = p.hasPage ? '</a>' : '</div>';
  return `${open} data-tags="${p.tags.join(' ')}">
  ${im ? `<img src="${esc(imgSrc(p, im.src))}" alt="${esc(im.alt || '')}"${dims} loading="lazy" decoding="async">` : ''}
  <div class="mini-text">${tagRow(p)}<h3 class="mini-title">${esc(p.title)}</h3></div>
${close}`;
}

// ── page shell ───────────────────────────────────────────────

function head({ title, description, path: pagePath, image }) {
  const fullTitle = title ? `${title} | ${site.name}` : `${site.name} | ${site.role}`;
  const url = site.url + pagePath;
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(fullTitle)}</title>
<meta name="description" content="${esc(description || site.description)}">
<link rel="canonical" href="${esc(url)}">
<meta property="og:type" content="website">
<meta property="og:title" content="${esc(fullTitle)}">
<meta property="og:description" content="${esc(description || site.description)}">
<meta property="og:url" content="${esc(url)}">
${image ? `<meta property="og:image" content="${esc(site.url + image)}">` : ''}
<meta name="theme-color" content="#FFFFFF">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/fonts/Geist-Variable.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/css/site.css">
<script src="/js/site.js" defer></script>
</head>`;
}

function header(active) {
  const item = (href, label, key) =>
    `<a href="${href}" class="nav-link"${active === key ? ' aria-current="page"' : ''}>${label}</a>`;
  return `<header class="site-header wrap">
  <a class="brand" href="/"><span class="brand-name">${esc(site.name)}</span><span class="brand-role">${esc(site.role)}</span></a>
  <nav class="nav" aria-label="Main">
    ${item('/', 'Work', 'work')}
    ${item('/about/', 'About', 'about')}
    ${site.cv ? `<a href="${esc(site.cv)}" class="nav-link">CV</a>` : ''}
    <a href="#contact" class="nav-link nav-link--solid">Get in touch</a>
  </nav>
</header>`;
}

function footer() {
  const items = [];
  if (site.email) {
    items.push(`<div class="contact-item">
      <span class="contact-label">Email</span>
      <div class="contact-row">
        <a class="contact-value" href="mailto:${esc(site.email)}">${esc(site.email)}</a>
        <button type="button" class="copy" data-copy="${esc(site.email)}">Copy</button>
      </div>
    </div>`);
  }
  if (site.linkedin) {
    items.push(`<div class="contact-item"><span class="contact-label">LinkedIn</span><a class="contact-value" href="${esc(site.linkedin)}" rel="noopener">View my profile</a></div>`);
  }
  if (site.cv) {
    items.push(`<div class="contact-item"><span class="contact-label">CV</span><a class="contact-value" href="${esc(site.cv)}">Download PDF</a></div>`);
  }
  return `<footer class="wrap">
  <section class="contact" id="contact" aria-labelledby="contact-title">
    <h2 id="contact-title">Get in contact with me here:</h2>
    <div class="contact-grid">${items.join('\n')}</div>
  </section>
  <p class="copyright">© ${new Date().getFullYear()} ${esc(site.name)}</p>
</footer>`;
}

const page = (opts, main) => `${head(opts)}
<body>
<a class="skip" href="#main">Skip to content</a>
${header(opts.active)}
<main id="main">
${main}
</main>
${footer()}
</body>
</html>
`;

// ── pages ────────────────────────────────────────────────────

function homePage(projects) {
  const featured = projects.filter((p) => p.section !== 'other');
  const other = projects.filter((p) => p.section === 'other');
  const counts = {};
  for (const p of projects) for (const t of p.tags) counts[t] = (counts[t] || 0) + 1;
  const filterButtons = [
    `<button type="button" class="filter" data-filter="all" aria-pressed="true">All work <span class="count">${projects.length}</span></button>`,
    ...Object.entries(site.tags)
      .filter(([key]) => counts[key])
      .map(([key, t]) =>
        `<button type="button" class="filter" data-filter="${key}" aria-pressed="false">${icon(t.icon, 15)}${esc(t.label)} <span class="count">${counts[key]}</span></button>`),
  ].join('\n');

  const firstImage = featured.find((p) => p.card?.images?.length);
  const ogImage = firstImage ? imgSrc(firstImage, typeof firstImage.card.images[0] === 'string' ? firstImage.card.images[0] : firstImage.card.images[0].src) : undefined;

  return page({ active: 'work', path: '/', image: ogImage }, `
<section class="intro wrap">
  <h1>${esc(site.intro)} <span class="muted">${esc(site.introMuted)}</span></h1>
</section>

<div class="wrap">
  <div class="filters" role="group" aria-label="Filter projects by discipline">
    <span class="filters-label">Show</span>
    ${filterButtons}
  </div>
  <p class="filter-status" aria-live="polite"></p>

  <section class="work" aria-label="Selected work">
    ${featured.map(featuredCard).join('\n')}
  </section>

  ${other.length ? `<section class="other" aria-labelledby="other-title">
    <h2 id="other-title" class="section-label">Other work</h2>
    <div class="other-grid">${other.map(otherCard).join('\n')}</div>
  </section>` : ''}
</div>`);
}

function aboutPage() {
  const file = path.join(ROOT, 'content', 'about.html');
  const body = fs.existsSync(file) ? fs.readFileSync(file, 'utf8') : '';
  return page({ active: 'about', title: 'About', path: '/about/' }, `<div class="wrap about">${body}</div>`);
}

function projectPage(p, next) {
  const facts = Object.entries(p.facts || {}).filter(([, v]) => v);
  const hero = p.hero === null ? '' : visual(p, p.hero || p.card, 'hero');
  const body = processImages(p.body, p.dir, p.slug);
  const firstImg = (p.hero || p.card)?.images?.[0] || (p.hero || p.card)?.image;
  const ogImage = firstImg ? imgSrc(p, typeof firstImg === 'string' ? firstImg : firstImg.src) : undefined;

  return page({ active: 'work', title: p.title, description: p.summary?.replace(/<[^>]+>/g, ''), path: linkOf(p), image: ogImage }, `
<article class="wrap case" style="--project:${colorOf(p)}">
  <a class="back" href="/">${icon('back', 16)}All work</a>
  <header class="case-header">
    ${tagRow(p)}
    <h1>${esc(p.title)}</h1>
    <p class="case-intro">${rich(p.intro || p.summary)}</p>
  </header>
  ${facts.length ? `<dl class="facts">${facts.map(([k, v]) => `<div><dt>${esc(k)}</dt><dd>${rich(v)}</dd></div>`).join('')}</dl>` : ''}
  ${hero}
  <div class="case-body">
${body}
  </div>
  ${next ? `<a class="next" href="${linkOf(next)}" style="--card:${colorOf(next)}">
    <span><span class="next-label">Next project</span><span class="next-title">${esc(next.title)}</span></span>
    <span class="next-arrow">${icon('arrow', 22)}</span>
  </a>` : ''}
</article>`);
}

function notFoundPage() {
  return page({ title: 'Page not found', path: '/404' }, `
<section class="intro wrap">
  <h1>Sorry, that page doesn't exist. <span class="muted"><a href="/">Back to my work</a></span></h1>
</section>`);
}

// ── build ────────────────────────────────────────────────────

function build() {
  const t0 = Date.now();
  rmrf(OUT);
  mkdirp(OUT);
  copyDir(path.join(ROOT, 'static'), OUT);

  const projects = loadProjects();
  const withPages = projects.filter((p) => p.hasPage);

  for (const p of projects) {
    for (const t of p.tags) if (!site.tags[t]) warnings.push(`${p.slug}: unknown tag "${t}"`);
    copyDir(path.join(p.dir, 'images'), path.join(OUT, 'work', p.slug, 'images'));
    copyDir(path.join(p.dir, 'files'), path.join(OUT, 'work', p.slug, 'files'));
  }
  withPages.forEach((p, i) => {
    const next = withPages.length > 1 ? withPages[(i + 1) % withPages.length] : null;
    write(`work/${p.slug}/index.html`, projectPage(p, next));
  });

  write('index.html', homePage(projects));
  write('about/index.html', aboutPage());
  write('404.html', notFoundPage());

  const urls = ['/', '/about/', ...withPages.map(linkOf)];
  write('sitemap.xml', `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.map((u) => `  <url><loc>${site.url}${u}</loc></url>`).join('\n')}
</urlset>
`);
  write('robots.txt', `User-agent: *\nAllow: /\nSitemap: ${site.url}/sitemap.xml\n`);

  for (const w of warnings) console.warn('⚠ ' + w);
  console.log(`Built ${projects.length} projects (${withPages.length} with pages) into dist/ in ${Date.now() - t0}ms`);
}

build();
