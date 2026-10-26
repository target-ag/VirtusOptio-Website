# Virtus Optio

The Virtus Optio website for Mark Deniel: ethical selling, practical sales systems, and stronger client relationships. Built with MkDocs Material, with a custom homepage, Business blog, and light and dark themes.

## Local preview

Use Python 3.11, matching `.python-version` and the production build.

```sh
git clone https://github.com/target-ag/VirtusOptio-Website.git
cd VirtusOptio-Website
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./serve.sh
```

Open [the local preview](http://127.0.0.1:8000/). The preview includes draft blog posts; production builds exclude them.

## Production build

```sh
.venv/bin/python -m mkdocs build --strict
```

The generated website is written to `site/`, which is excluded from Git. Cloudflare Pages runs the production build and hosts the result whenever `main` changes.

The canonical production URL is [virtusoptio.com](https://virtusoptio.com/), configured in `mkdocs.yml`. The Cloudflare Pages fallback is [virtusoptio-website.pages.dev](https://virtusoptio-website.pages.dev/).

## Deploy with Cloudflare Pages

1. Create or sign in to a [Cloudflare account](https://dash.cloudflare.com/sign-up).
2. In **Workers & Pages**, create a **Pages** project and connect GitHub. Grant access to `target-ag/VirtusOptio-Website` and select it.
3. Configure the project:

   | Setting | Value |
   | --- | --- |
   | Production branch | `main` |
   | Framework preset | `None` |
   | Build command | `pip install -r requirements.txt && mkdocs build --strict` |
   | Build output directory | `site` |
   | Root directory | Repository root; leave blank |
   | Environment variable | `PYTHON_VERSION=3.11` |

4. Save and deploy. Cloudflare provides an HTTPS address ending in `.pages.dev` and rebuilds the site when `main` changes.
5. Connect `virtusoptio.com` and `www.virtusoptio.com` under **Custom domains**. Keep `site_url: https://virtusoptio.com/` in `mkdocs.yml` so canonical links and the sitemap use the main domain.

To use your own domain, add it under the Pages project's **Custom domains** tab and follow Cloudflare's DNS instructions. See [Git integration](https://developers.cloudflare.com/pages/get-started/git-integration/) and [custom domains](https://developers.cloudflare.com/pages/configuration/custom-domains/).

## Editing the website

- `overrides/home.html`: homepage content and layout.
- `overrides/partials/`: shared header, logo, and theme controls.
- `docs/stylesheets/` and `docs/javascripts/`: styles and behavior.
- `docs/blog/posts/`: Markdown articles; new posts inherit the shared article styling.
- `docs/assets/`: images and branding.
- `mkdocs.yml`: site metadata and build configuration.

See [SETUP.md](SETUP.md) for blog front matter, draft publishing, theme details, and image notes. Contact buttons point to [Mark Deniel on LinkedIn](https://www.linkedin.com/in/mark-d-819a57224/).

## Credits

Adapted from the [Datalumina MkDocs website template](https://github.com/datalumina/mkdocs-website-template), using [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/). Original template attribution and notices are retained; third-party dependencies remain subject to their respective licenses.
