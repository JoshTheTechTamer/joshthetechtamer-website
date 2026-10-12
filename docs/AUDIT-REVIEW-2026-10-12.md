# Audit fixes — review only, October 12, 2026

Production source backup: branch `backup/pre-audit-2026-10-12`, commit `e3398feb089342c88fb7c1dd4a4ba67782755f69`.

## Changes
- Privacy policy and accessibility help page; links on every page and privacy link beside the contact form.
- Google Analytics loads only after explicit opt-in. Footer cookie settings allow withdrawal. Preference is stored locally. The contact form remains independent of analytics.
- Header pause/play control retains a paused preference across pages. Visibility and intersection events cannot restart an explicitly paused animation; reduced motion still prevents animation.
- Scam checklist prioritizes containment and immediate payment-provider contact. Payment-method and unexpected-code explanations avoid misleading absolutes.
- Website hero identifies care as optional and first-year hosting/domain as included.
- Proposed care terms clarify existing-site repairs, third-party limitations, cancellation by email/text before the next bill, service through the paid period, and hosting transition. Josh should review these proposed business terms before publication.
- Service coverage preserves the explicit existing town list. The inconsistent Iowa City footer reference is removed; no additional service area is promised.
- Local font replaces Google Fonts requests; business schema uses the existing optimized 69 KB logo rather than the 1.27 MB original.
- Sitemap includes the two new pages; dates reflect this update.

## Verification and scope
Existing validation suite passes after updating expectations for the authorized copy changes and new pages. The content-lock baseline is intentionally refreshed for this audit, not removed. JavaScript syntax checks pass. Preview has CSP connect-src/form-action none, no external scripts, disabled form submission, embedded artwork/CSS/JS and desktop/390px/320px views.

The Cloudflare connector currently exposes MVP's account only. No production deployment, account setting, Stripe billing, or live form submission was changed. Account retention settings and delivery remain unverified. This is not a legal compliance certification.

## Reproduce
`python scripts/build_pages.py`
`python scripts/validate_site.py`
`python scripts/build_audit_preview.py`

The standalone preview is emitted outside the repository in `../review/Tech_Tamer_Audit_Preview.html` and is never part of the production build.


## Extended checklist review (preview only)
Added Terms, Cancellations & Refunds, and Cookies pages, metadata, sitemap entries and footer links. Terms/refunds are explicitly proposed, not effective policies. Josh must approve deposit deductions, cancellation treatment and care proration before publication; confirm Gumroad checkout terms match. Consumer rights are preserved rather than imposing blanket no-refund language.

Form disclosure explains request-specific contact, no marketing enrollment and possible text charges. City/time remain optional; one contact method is collected. The handler whitelists and limits fields, validates contact input and checks Turnstile server-side. Account-level mail retention, access controls, deployed bindings and real delivery are not verified. No live form was submitted.

Analytics code loads Google only on opt-in, supports withdrawal and disables advertising personalization/signals. Visible external-resource inventory found Turnstile as the external script; local images/fonts are used and Stripe/Gumroad are outbound links. Actual provider cookies and account configuration still need a live browser inspection.

Alt descriptions reviewed for obvious missing/generic alternatives; removed marketing suffixes. Added global keyboard focus and reduced-motion anchor scrolling. Existing menu Escape handling, labels, native validation and status announcements retained. Browser installation failed in this environment; contrast, screen-reader behavior, real tab sequence, zoom and mobile overflow are not certified.

Reviews: 14 existing source-labeled quotes retained verbatim. No evidence establishes they are fake. Source URLs/screenshots, accuracy, and any material relationships or incentives require owner confirmation. No new reviews or ratings created. Image inventory includes branded illustrations, Josh photographs, a photo with Madonna, kit covers and site screenshots. Repository possession is not proof of copyright or model permission. Keep original files, creation records, stock/tool licenses and participant permissions before marking provenance verified.

Official research reviewed October 12, 2026:
- Iowa Code 715D: https://www.legis.iowa.gov/docs/code/715D.pdf — scope depends on annual consumer counts (100,000, or 25,000 plus over half of gross revenue from personal-data sales). Actual counts/revenue unknown; no exemption conclusion made.
- Iowa consumer fraud: https://www.legis.iowa.gov/docs/code/714.16.pdf — avoid deceptive representations; removed a remaining recovery-outcome promise.
- Iowa cancellation guidance: https://www.iowaattorneygeneral.gov/for-consumers/general-consumer-information/right-to-cancel and federal exceptions: https://consumer.ftc.gov/articles/buyers-remorse-ftcs-cooling-rule-may-help — qualifying at-home sales can require cancellation notices/forms; a website policy does not substitute for transaction paperwork. Applicability depends on how work is sold and arranged.
- FTC reviews rule: https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers — preserve genuine feedback; do not fabricate or misrepresent endorsements. Evidence review still needed.
- DOJ accessibility guidance: https://www.ada.gov/resources/web-guidance/ — businesses must consider accessible services; automated checks alone do not establish accessibility.
- Copyright Office AI report: https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf — AI provenance does not establish exclusive copyright; human contributions and third-party rights require separate review.
- Illinois home-repair guidance (because service area includes Illinois): https://illinoisattorneygeneral.gov/Page-Attachments/HomeRepairConstructionWhatYouShouldKnow.pdf — assess whether any physical installation jobs fall within covered work; ordinary computer support is not automatically classified as home remodeling. Licensing, tax, registration and transaction-specific obligations remain outside this source-only review.

No legal-compliance certification is claimed. Business identity/contact information is taken from the existing site, not independently registry-verified. No live publication authorized or performed.
