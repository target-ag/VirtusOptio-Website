# Personal website setup

This project uses the Datalumina MkDocs template, customized for Virtus Optio with its own branding, homepage portrait, LinkedIn contact links, and Business blog. The original template source remains in Git history.

## Preview

Run `./serve.sh` in this folder and visit http://127.0.0.1:8000.

For a fresh installation, use Python 3.11.18 to match `.python-version` and the production build:

```sh
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./serve.sh
```

Build with `.venv/bin/python -m mkdocs build --strict`, then run `.venv/bin/python scripts/check_security.py site`. Output goes into the ignored `site/` directory.

## Content

- `overrides/home.html`: homepage layout, copy, portrait, and LinkedIn contact links
- `docs/index.md`: homepage metadata
- `docs/assets/`: website images and branding
- `docs/blog/posts/`: add Markdown articles with title and date front matter
- `mkdocs.yml`: site name, navigation, theme, metadata

The homepage portrait uses `docs/assets/mark-deniel-office-cobalt-mug.svg`, a self-contained image that preserves the original photo and applies an ImageGen cobalt edit only inside the mug's exterior silhouette. The original dark opening, person, and background are retained. Embedded WebP layers are lossless; the complete SVG is 1,718,265 bytes. The untouched source remains at `docs/assets/markos-office.webp`. Its frame retains the original 4:5 layout, capped at 408 × 510 CSS pixels. The edit prompt is saved in `mug-color-edit-prompt.txt`.

The header's theme button switches between light and dark on the homepage, blog, and article pages. The choice is saved in the current browser. Theme styles live in `docs/stylesheets/theme.css` and behavior in `docs/javascripts/theme.js`.

The shared header in `overrides/partials/site-header.html` stays visible while scrolling. Its LinkedIn “Let’s talk” action is separate from the navigation links and always remains visible, including on phones. Add future menu links inside `.site-navigation`; they can scroll horizontally without pushing the contact action or theme button out of view. Header layout lives in `docs/stylesheets/navigation.css`, loaded after the page and theme styles.

The accent palette is cobalt: `#2D57C7` for light-mode buttons and highlights, with `#4C7DFF` emphasis rules and `#739BFF` links in dark mode. The light page background matches the supplied swatch exactly: #F9F9F9 (RGB 249, 249, 249), with white and near-white neutral surfaces. Its closing call-to-action panel is neutral charcoal (#202020). Dark page surfaces use neutral charcoal, with a subtle blue tint on the closing call-to-action panel only in dark mode. Page and article titles use Source Sans 3 at weight 700, matching the body font while retaining their larger sizes. The logo tip is solid cobalt #2D57C7 in both themes; only its neutral lettering changes for contrast. The shared brand-logo partial applies the cobalt color through an SVG alpha filter, preserving the original mark shape and keeping the source artwork unchanged. The website loads the lossless WebP logo (122,474 bytes); its original PNG remains available in the brand assets.

## Loading-speed check — 26 October 2026

Three desktop browser runs used a temporary instrumented production build over localhost, with fresh local asset URLs and no network throttling. External font caching was not reset. Median first contentful paint was 92 ms, largest contentful paint 108 ms, and load event 51.6 ms. All three runs reported zero layout shift during the observation window. Raw measurements are saved in `loading-speed-results.json`.

At the time of this test, the homepage's local HTML, CSS, JavaScript, and requested images totaled about 1.40 MB, plus external fonts, using the original 1.26 MB portrait. The later isolated cobalt-mug edit uses a 1.72 MB self-contained SVG, so these earlier transfer figures do not describe the current portrait. These local measurements are not a public mobile performance score; repeat a deployed-site test under a representative mobile network after launch.

Social-card generation is disabled so the site does not require native imaging libraries. Author details are rendered by the custom article template. Case Studies is excluded from the website.

## Publish to Cloudflare Pages

The website's GitHub destination is `target-ag/VirtusOptio-Website`. Cloudflare Pages runs the production build and hosts the result whenever `main` changes.

The canonical production URL is `https://virtusoptio.com/`. The existing Pages deployment remains available at `https://virtusoptio-website.pages.dev/` as a fallback.

1. Create or sign in to a Cloudflare account. In Workers & Pages, create a Pages project and connect GitHub.
2. Grant access to `target-ag/VirtusOptio-Website`, then select that repository and production branch `main`.
3. Choose framework preset `None`, leave the root directory blank, set the build command to `pip install -r requirements.txt && mkdocs build --strict && python scripts/check_security.py site`, and set the output directory to `site`.
4. Set the environment variable `PYTHON_VERSION` to `3.11.18`, matching the project's `.python-version`, and deploy.
5. Cloudflare assigns an HTTPS `.pages.dev` address. Future pushes to `main` trigger new production deployments.
6. Open the Pages project's Custom domains tab to connect `virtusoptio.com` and `www.virtusoptio.com`, following Cloudflare's DNS instructions. Keep `site_url: https://virtusoptio.com/` in `mkdocs.yml` so canonical links and the sitemap use the main domain.

See Cloudflare's [Git integration instructions](https://developers.cloudflare.com/pages/get-started/git-integration/), [build image settings](https://developers.cloudflare.com/pages/configuration/build-image/), and [custom domain guide](https://developers.cloudflare.com/pages/configuration/custom-domains/). An apex domain requires a Cloudflare zone and its nameservers; a subdomain can use the CNAME record specified by Cloudflare.

The homepage uses the supplied portrait and “Find me on LinkedIn” links. Draft articles remain excluded from production, and the public blog can retain its Coming soon state until approved articles are ready. The Cloudflare account and initial Pages deployment are configured; custom-domain availability depends on DNS activation and Cloudflare's domain verification.

## Blog categories and article lists

The blog uses `overrides/blog.html` and `docs/stylesheets/blog.css`. Its categories are **Business Growth** and **Sales & Acquisition**. The shared category links open filtered lists, and an empty category shows an explicit empty state. Source pages under `docs/blog/category/` keep both categories available before they have published posts. The old Business category URL redirects to Business Growth.

To add a post, create a Markdown file in `docs/blog/posts/` with `title`, `date`, `description`, and `categories: [Business Growth]` or `categories: [Sales & Acquisition]` in its front matter. Choose both when the post belongs to both topics. Add `start_here: true` to feature it in the text-only Start here list. The newest post becomes the featured article automatically; the remaining posts appear below it. Descriptions are the summaries shown in the list.

Add a `cover` object with `src`, `alt`, `width`, and `height` to show the article image in the latest and category lists. Optional `sources` entries contain `src` and `width` for responsive image variants. Use the growth article's front matter as an example. Paths are relative to the site root. The list cover does not insert an image into the article body; include that separately when wanted.

## Individual article layout

Articles use `overrides/blog-post.html` and `docs/stylesheets/post.css`. The template includes a narrow reading column, date and reading time, author details, an optional TL;DR, and a Continue reading section.

Every Markdown post added under `docs/blog/posts/` automatically uses this article template through the MkDocs blog plugin. No `template` front-matter field is needed. Keep template overrides out of individual posts so new articles inherit the same typography, cobalt accents, light/dark themes, shared header, and LinkedIn contact action. The mobile header hides on downward scrolling and returns on upward scrolling or keyboard focus; desktop navigation stays visible. Use the shared `partials/arrow-up-right.html` SVG for link arrows so iOS does not render emoji.

Optional front matter:

- `summary`: text for the TL;DR.
- `author_name`, `author_role`, `author_bio`, and `author_avatar`: author details. The current default is Mark Deniel at Virtus Optio; an initial is shown until an author portrait is supplied. Both the byline and More about link open his LinkedIn profile.
- `faq`: a list of `question` and `answer` pairs shown after the article.
- `guide`: an optional link to an older article or guide beneath the author line, with a small ↗ arrow. Supply `title` and `url`; `label` is optional and defaults to Related article. Leave out `guide` to hide the entire line.
- `related`: a list of `title`, `url`, and optional `date` values for related articles. Use site-relative URLs such as `blog/2026/10/26/article-slug/`.
- `draft: true`: shows the article during `./serve.sh`, with a preview notice, but excludes it from the production build and search index.

`better-sales-conversations.md` is sample draft copy for reviewing the layout. Keep it as a draft until its content is approved. Remove `draft: true` only when an article is ready to publish.

To link an article to an earlier post, add this to its front matter, replacing the example title and URL with a real published post:

```yaml
guide:
  label: Related article
  title: The title of your earlier article
  url: blog/2026/10/20/earlier-article-slug/
```

Use the destination's generated URL relative to the site root, without a leading slash or a `.md` extension. This keeps links portable between the local preview and the deployed website. A full `https://` URL also works for an external article. The label can be changed to `Part of the guide` when appropriate. No article is linked automatically.
