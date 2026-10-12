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
