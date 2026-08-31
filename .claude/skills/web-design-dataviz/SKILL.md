---
name: web-design-dataviz
description: Design state-of-the-art websites, landing pages, and data visualizations to 2026 best-practice standards, with distinct B2B and B2C playbooks. Use this skill whenever the user asks to design or build a website, landing page, microsite, product page, marketing site, dashboard, chart, infographic, or interactive data visual — for IOMA Advisory, SATS, the charm venture, or any other purpose. Trigger on "design a site/page/dashboard", "make this look professional/modern", "visualize this data", "build a landing page", or when reviewing/critiquing an existing design. Complements (does not replace) domain-specific skills like capability-diagnostic-dashboard and branded-deck.
---

# Web Design & Data Visualization

Design like a studio lead with a point of view, not a template engine. Every output makes deliberate, subject-specific choices and passes the quality floor before delivery. If the public `frontend-design` skill is available, read it too — this skill extends it with 2026 practice and B2B/B2C playbooks.

## Step 1: Frame the brief

Pin down before designing (infer from context where possible; ask ONE consolidated question only if genuinely blocked):
- **Subject & audience** — what is this, who is it for, what is the page's single job
- **Mode** — B2B or B2C (see playbooks below); dashboards and data visuals additionally read `references/dataviz.md`
- **Brand constraints** — existing palette/logo/voice, or freedom to propose

## Step 2: Design plan before code

Write a compact token plan first: 4–6 named hex colors, 2–3 typefaces by role (characterful display used with restraint + readable body + utility for data), a one-line layout concept, and ONE signature element the design will be remembered by. Then self-check: "would I produce this same plan for any similar brief?" If yes, revise before building. Read `references/design-system.md` for the 2026 trend catalog, banned defaults, and token guidance.

## Step 3: B2B or B2C playbook

**B2B (advisory, corporate, SaaS)** — the site is a self-serve evaluation layer for a buying committee, not a brochure:
- Instant clarity above the fold: what it is, who it's for, why different — in the visitor's language, zero jargon
- Outcome-focused messaging ("here is what you will achieve"), not feature lists
- Design for multiple readers: the decision-maker wants ROI, the operator wants how-it-works — layer content so each finds their path without clutter
- Trust made visible: real client evidence, specific case results, credentials — never stock-photo filler; buyers detect it and trust drops
- Progressive scroll narrative: positioning statement → proof → depth; sticky nav on long pages
- Calm, purposeful motion only (hover reveals, scroll-triggered emphasis); most elements static
- Low-pressure conversion: layered CTAs matched to readiness (read more → download → talk), short forms, no aggressive popups

**B2C (consumer, youth/lifestyle, e-commerce)** — emotion and speed to delight:
- The hero sells a feeling in under 3 seconds; personality is the differentiator
- 2026 consumer aesthetics are bolder: dopamine color, expressive oversized type, bento grids, tasteful maximalism, Y2K/nostalgia notes for Gen Z audiences — pick ONE direction and commit (see trend catalog)
- Product imagery is the content: large, honest, interactive where it earns its keep (spin/zoom)
- Mobile-first is literal: design the phone screen first, scale up
- Frictionless path to purchase/action; speed is a feature — every decoration must justify its load cost

## Step 4: Build to the quality floor (non-negotiable, never announced)

- Responsive down to 380px; touch targets ≥ 44px
- WCAG AA contrast (4.5:1 body text); visible keyboard focus; reduced-motion respected
- One clear H1, logical heading hierarchy, descriptive alt text — humans and AI crawlers both read structure now
- Real copy written from the user's side of the screen: plain verbs, active voice, buttons say exactly what happens
- Performance discipline: no decorative weight that slows first paint

## Step 5: Critique pass

Before delivering, review as a critic: remove one element (there is always one), verify the signature element is the single boldest thing and everything else is quiet, and confirm the design could not be mistaken for a generic template. State one deliberate risk taken and why it serves this brief.

## Data visualization

Any chart, dashboard, or data-driven visual: follow `references/dataviz.md` for chart selection, hierarchy, color encoding, and integrity rules. Headline rule: one question per view, the answer where the eye lands first, and never distort (no truncated axes, no 3D, no pie charts beyond 5 slices).

## Output

Default to a single self-contained HTML file (inline CSS/JS) unless asked otherwise. For multi-unit diagnostic dashboards, defer to the capability-diagnostic-dashboard skill's conventions; for SATS-branded work, respect SATS brand rules; never mix SATS and IOMA identities.
