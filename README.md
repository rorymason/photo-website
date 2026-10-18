# rorymason.xyz

Rory Mason’s design portfolio. A small static site: `build.mjs` reads the
`content/` folder and writes the finished site to `dist/`. No npm install, no
frameworks — just Node.

## Edit the site

| To change… | Edit |
|---|---|
| Email, LinkedIn, CV link, homepage intro, tags, colours | `site.config.mjs` |
| The About page | `content/about.html` |
| A project | `content/projects/<project>/project.json` and `page.html` |
| Styles | `static/css/site.css` |

Anything left empty in `site.config.mjs` (e.g. `linkedin: ''`) is hidden on the site.
To add a CV, put the PDF in `static/files/` and set `cv: '/files/your-cv.pdf'`.

## Add a project

1. Copy `content/projects/_template` and rename the folder — the folder name
   becomes the web address (`/work/folder-name/`). Folders starting with `_` are ignored.
2. Put images in its `images/` folder (JPG or PNG, ideally under 2000px wide).
3. Fill in `project.json`:
   - `order` — position on the homepage (1 = first)
   - `section` — `"featured"` for the main list, `"other"` for the smaller Other work row
   - `tags` — any of `ux`, `research`, `brand`, `strategy`, `motion` (set in `site.config.mjs`)
   - `color` — `rose`, `sky`, `butter`, `lavender`, `peach`, `mint` or `grey`
   - `card.style` — how it looks on the homepage:
     - `"phones"` with `images` (1–3 phone screens)
     - `"photo"` with `image` (a photo filling the right half)
     - `"framed"` with `image` (an image with a shadow, e.g. a brand book page)
     - `"band"` — no image, a slim text row (add `"quote"` to show a quote on the right)
   - `hero` — optional; the big image at the top of the project page. Defaults to the
     card visual. Set to `null` for none.
   - `"page": false` — shows the card with “Case study coming soon” and no link
   - `"hidden": true` — leaves the project off the site entirely
4. Write the page in `page.html` using the blocks in the template.
5. Run `node build.mjs` and open `dist/index.html` — or just push and let Cloudflare build it.

Never edit `dist/` — it’s rebuilt from scratch every time.

## Preview locally

```sh
node build.mjs
cd dist && python3 -m http.server 8787
# open http://localhost:8787
```

## Hosting (Cloudflare)

Cloudflare builds the site from GitHub on every push. Build settings:

- **Build command:** `node build.mjs`
- **Build output directory:** `dist`
- **Root directory:** (leave empty)

Fonts (Geist, SIL Open Font License) are self-hosted in `static/fonts/` — no Google Fonts requests.
