# November 2026 audit implementation

Source: NOMAXX audit dated 11 November 2026, supplied by Markos. Changes prepared 12 November 2026.

## Implemented

- Open Graph and Twitter metadata, with page-specific 1200 × 627 social images and a default fallback.
- More descriptive blog metadata and a shorter article search title.
- Empty categories and archive pages marked noindex and excluded from both sitemaps; empty sales category hidden from navigation until a published article exists.
- Date-free article URLs with permanent redirects from the existing published article URL. Existing category redirects retained.
- About page, three service pages and a service overview; copy derived from the site's existing service positioning, without invented credentials, fees, case studies or results.
- Homepage service links and a clearer business-owner audience statement.
- Email as the primary contact action and LinkedIn as the alternative, per Markos's explicit preference. No calendar or booking integration. WhatsApp remains available.
- One email setting in `mkdocs.yml` (`extra.contact_email`), used by templates, Markdown email links, structured data, the copy-email control and security.txt.
- Removal of the automatic cookie banner and its old acknowledgement storage, while preserving theme controls. Privacy/cookie descriptions updated to match.
- Person and ProfessionalService structured data, LinkedIn sameAs and author relationships. No unverified business address or region added.
- Original and unused logo variants excluded from deployment, while preserving source originals in Git. Standalone font CSS and font source notes excluded from deployed output; font licensing retained.
- Removal of published blog excerpt markers and unused portrait-placeholder CSS.
- Public `/.well-known/security.txt` with a November 2027 expiry; renew before expiry.
- Cloudflare header directive to remove unnecessary wildcard CORS. Verify the final response after deployment because account-level transforms may also affect it.
- Three broken Obsidian-relative links repaired to their intended MkDocs destinations.

## User choices and outstanding inputs

- Keep the site in English for this update.
- No booking link: enquiries should go to email or LinkedIn.
- Markos is setting up domain email. Do not install SPF `-all` or null MX while that setup is in progress. Use the chosen provider's actual MX, SPF and DKIM records and validate alignment before enforcing DMARC.
- The currently published Gmail address remains the temporary contact. Replace `extra.contact_email` when Markos supplies the new address and update the provider description in the privacy policy if applicable.
- VAT ID **NL005130408B50**, supplied by Markos on 12 November 2026, is included in the footer, terms and structured business data. The business address still needs to be supplied for public display. The audit author's Rotterdam address and VAT ID are NOMAXX's details, not Virtus Optio's.
- Real client reviews, logos and results require supplied content and permission. None were invented.

## Account-level follow-up (not completed by source changes)

- Disable Cloudflare Web Analytics injection to preserve the no-analytics setup. Keep the strict CSP; do not allow the blocked tracker just to hide its error.
- Add a Cloudflare domain redirect from www to the apex domain, preserving path and query string. Pages `_redirects` does not support domain-level redirects: https://developers.cloudflare.com/pages/configuration/redirects/
- Coordinate DNSSEC between Cloudflare and the registrar; verify the DS record after enabling it.
- Configure domain email authentication for the actual new provider, then validate incoming/outgoing mail before changing enforcement.
- Verify Google Search Console and Bing ownership using their account-issued records, then submit the sitemap.
- Validate previews with LinkedIn Post Inspector after deployment.
- Consider CAA only after checking the current certificate issuers and renewal requirements.
- No hosting migration, subscription, third-party access grant or recurring content automation was made. The audit's hosting proposal is not an implementation requirement.

## Validation

- `mkdocs build --strict`.
- `python scripts/check_security.py site`: exact CSP compatibility for all generated HTML pages.
- `python scripts/check_site.py`: local link targets, social image targets, one H1 per page, metadata, canonical URLs, noindex/sitemap consistency, removed build artifacts and security.txt.
- JavaScript syntax checks.
- Browser checks at desktop and mobile widths: navigation, email dialog, light/dark theme, preference reset, and unobstructed contact controls.

## Deployment

The source repository is `target-ag/VirtusOptio-Website`; its documented production host is Cloudflare Pages and production branch is `main`. Changes are prepared in the local checkout; see the conversation for the final deployment status. Account-level items above require separate verification and are not fixed merely by publishing this build.
