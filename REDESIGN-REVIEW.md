# Business-card redesign — unpublished review

Built on a local branch from production commit 48c1721. Nothing has been pushed or deployed.

Seven pages: Home, Tech Help, For Business, Digital Kits, Rates & FAQ, About Josh, Contact. Original mascot and portrait retained locally. The color palette and angular/dot details follow the supplied business cards.

Pricing is $50/hour, free initial consultation, estimates for larger projects. Removed the $35 support package. Veteran discount and minimum-time claims omitted pending owner confirmation. No fabricated customer reviews or statistics. Business services now include logo/brand work, advertising setup, startup consulting, and websites/business technology.

Contact form prepares a mailto draft; it does not send messages or book appointments. Gumroad links retain existing product URLs. Analytics loads only on the production domain. Existing home-page hash links route to their replacement pages. No new backend or hosting provider is required.

Edit shared content with scripts/build_pages.py, shared styles in assets/site.css, and interactions in assets/site.js. Run `python3 scripts/build_pages.py` to regenerate the static pages. `python3 scripts/build_preview.py` produces the self-contained offline review file in ../review. It contains all pages, assets, and a desktop/phone toggle.

Validation completed: all internal links and image references resolve; one H1 and unique IDs on each page; schema JSON and both JavaScript files parse; $35 offer absent. Visual browser validation was blocked by the environment. Review desktop/mobile appearance in the offline preview before publication.

Before publication: confirm minimum billing/veteran-discount policy; review the new business-service wording and current hours; obtain owner approval; then merge/deploy using the existing host. Keep old backups out of public navigation. The existing unused booking-handler.php is unchanged.
