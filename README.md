# rorymason.xyz

Rory Mason's design portfolio. It's a small static site: `build.mjs` reads the
`content/` folder and writes the finished site to `dist/`. There's no npm install
and no framework, just Node.

## Edit the site

| To change... | Edit |
|---|---|
| Email, LinkedIn, CV link, homepage intro, tags, colours | `site.config.mjs` |
| The About page | `content/about.html` |
| A project | `content/projects/<project>/project.json` and `page.html` |
| Styles | `static/css/site.css` |

Anything left empty in `site.config.mjs` (for example `cv: ''`) is hidden on the site.
To add a CV, put the PDF in `static/files/` and set `cv: '/files/your-cv.pdf'`.

## Add a project

1. Copy `content/projects/_template` and rename the folder. The folder name
   becomes the web address (`/work/folder-name/`). Folders starting with `_` are ignored.
2. Put images in its `images/` folder (JPG or PNG, ideally under 2000px wide).
3. Fill in `project.json`:
   - `order`: position on the homepage (1 is first)
   - `section`: `"featured"` for the main list, `"other"` for the smaller Other work row
   - `tags`: any of `ux`, `research`, `brand`, `strategy`, `motion` (set in `site.config.mjs`)
   - `color`: `rose`, `sky`, `butter`, `lavender`, `peach`, `mint` or `grey`
   - `card.style`: how it looks on the homepage
     - `"phones"` with `images` (one to three phone screens)
     - `"photo"` with `image` (a photo filling the right half)
     - `"framed"` with `image` (an image with a shadow, like a brand book page)
     - `"band"` for no image, just a slim text row (add `"quote"` to show a quote on the right)
   - `hero`: optional, the big image at the top of the project page. It defaults to the
     card visual. Set it to `null` for none.
   - `cta`: optional, replaces the "View project" link text on the card
   - `"page": false` shows the card with no link
   - `"hidden": true` leaves the project off the site completely
4. Write the page in `page.html` using the blocks in the template.
5. Run `node build.mjs` and open the site locally, or just push and let Cloudflare build it.

Never edit `dist/`. It's rebuilt from scratch every time.

## Preview locally

```sh
node build.mjs
cd dist && python3 -m http.server 8787
# open http://localhost:8787
```

## Hosting (Cloudflare Pages)

Cloudflare builds the site from GitHub on every push. Build settings:

- Build command: `node build.mjs`
- Build output directory: `dist`
- Root directory: leave empty

The fonts (Geist, SIL Open Font License) are self-hosted in `static/fonts/`, so the site
makes no requests to Google Fonts.
