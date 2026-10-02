# Unpublished improvements — October 1, 2026

Backup: backup/pre-seo-reviews-2026-10-01 at b314ebadf93fdcc2bcae8329bb4ba6dece8501e3.
Production main is unchanged. Review this branch before merging.

## Included
- Homepage carousel with eight customer quotes transcribed from provided screenshots. Peggy's repeated feedback appears once. Google Bob has no surname in the screenshot, so no initial was invented or cross-platform identity assumed. Five stars are shown for Bob and Arlene only. Facebook comments and recommendations keep their source labels.
- Pause/play, previous/next, keyboard-accessible controls, pauses on focus/hover, respects reduced motion, all quotes readable without JS.
- Home/office lead copy and Tech Help visit walkthrough; more natural Contact headline.
- Service-specific inquiry links; reply preference, validation, pending/success/error messages, no personal data in analytics.
- Responsive optimized images, correct intrinsic sizes, separate small logo/favicon, locally hosted sharing images.
- Local search titles, descriptions, canonical URLs, business identity/hours and breadcrumbs; robots/sitemap; 404 root-relative links.
- Backups, templates, scripts and internal docs excluded from GitHub Pages publication. Backup branch retains the old site.
- Existing kits, kit prices, purchase links, artwork and catalog layout preserved. No service landing pages, project examples or blog added.

## Must finish before deploying the direct form
1. Create/choose a Formspree form belonging to Josh and verify joshthetechtamer@gmail.com as its destination. No account was created, email sent or paid plan selected during this task.
2. Put the real https://formspree.io/f/FORM_ID endpoint in data/site-config.json, then run python scripts/build_pages.py.
3. Enable provider spam protection/domain restriction, review provider data handling and publish an accurate privacy notice as appropriate to the selected setup.
4. Perform one authorized end-to-end submission, confirm inbox delivery and confirm provider failure/retry behavior. Offline preview submissions are simulations and explicitly say so.
5. Run python scripts/validate_site.py --production. It intentionally fails until a real endpoint is configured. This verifies configuration, not delivery.

## Account-side follow-up (not completed without account access)
- Google Business Profile: confirm service-area business, categories, actual hours and services; add latest photos; obtain its exact public listing/review URL. Do not publish a private home address or invent an office.
- Search Console: verify ownership, submit https://joshthetechtamer.com/sitemap.xml and inspect seven main pages. No verification token was invented.
- Analytics: confirm events arrive, designate successful inquiries as key events; use Gumroad orders to measure purchases (kit_click is not a purchase).

## Business decisions still needed
Minimum billable time, travel fees, accepted payment methods and unresolved-problem policy were not supplied in the current approval. Draft FAQ asks customers to confirm these before a visit; it does not invent prices, guarantees or policies. Wednesday remains appointment-setting only. Structured hours omit Wednesday rather than claim on-site service that day.

## Future work intentionally deferred
Blog articles with supporting kit links, individual kit sales improvements, bundles, samples and project examples.

## Build
Templates preserve the current approved layout and page content. scripts/build_pages.py applies shared enhancements from data. Run scripts/optimize_assets.py only when source images change, then build_pages.py. build_preview.py creates the offline review artifact outside the published site.
