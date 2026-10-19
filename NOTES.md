# Portfolio handover notes

Last updated 19 October 2026.

## How the site works
- Repo: github.com/rorymason/photo-website. `main` is live on rorymason.xyz (Cloudflare Pages runs `node build.mjs` and serves `dist/`). The `portfolio` branch has a preview at portfolio.photo-website-2yj.pages.dev. Both are currently identical.
- Each project is a folder in `content/projects/<slug>/` with `project.json`, `page.html`, `images/` and `files/`. `_template/` shows every block you can use.
- Site settings (intro, email, CV, tags, colours) are in `site.config.mjs`. The CV PDF is `static/files/rory-mason-cv.pdf`.
- Homepage order: Phonidex (rose), The Jury's Out (sky), Rhapsody (peach), Experiencing Agency (lavender), Slow Looking (butter), Meaningful listening (mint), then Protect Your Ears and Photography (grey) under Other work. Keep warm and cool pastels alternating.

## Copy rules
British English, natural and friendly. No em dashes, en dashes or double hyphens, and nothing that reads as AI-written.

## Related files
- Rhapsody brand guidelines canvas: https://claude.ai/artifact/RymKUcSXeDH8HqrGby6QVW (PDF is in `content/projects/rhapsody/files/`)
- CV doc: https://claude.ai/code/artifact/ccca31f6-6fa0-4ba5-be1a-0424bbfe3760. The site PDF was rebuilt from it as one A4 page, so it has to be re-exported whenever the doc changes.
- Source material on Rory's Mac: Documents/portfolio (Phonidex screens, CV) and Documents/new portfolio (original Notion export).

## Open points
1. Rhapsody: confirm or drop the v2 additions (Violet Light #B77BFF, Surface Grey #F2F2F2, shortened value names, tone of voice page, imagery page using his 35mm photos, rebuilt app screens with made-up events) and the reflection points on the case study page.
2. Phonidex: add the demo video when it exists (a commented-out slot is at the top of `page.html`).
3. The Jury's Out: write the full case study once the brand directions are done (currently "Case study incoming").
4. Experiencing Agency: better mockups (could be redrawn in Figma) and the participant photo as a JPG (the HEIC wouldn't convert).
5. Meaningful listening (thesis): one sentence per finding and a stronger image.
6. Photography: add more photos.
7. About page: check the draft lines.
8. Protect Your Ears: set the Google Drive video to "Anyone with the link".
9. Site extras: Impressum check, favicon and social share (OG) image.
