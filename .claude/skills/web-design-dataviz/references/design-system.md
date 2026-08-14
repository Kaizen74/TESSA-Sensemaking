# Design System Reference — 2026

## Banned defaults (the "AI look")

These three looks are what generic AI design produces regardless of subject. Never use them unless the brief explicitly asks:
1. Warm cream background + high-contrast serif display + terracotta/clay accent
2. Near-black background + single acid-green or vermilion accent
3. Broadsheet layout: hairline rules, zero border-radius, dense newspaper columns

Also banned unless earned by content: numbered section markers (01/02/03) where order carries no meaning; gradient-accented big-number heroes as a reflex; purple-to-blue gradients on tech pages; emoji as design elements in professional work.

## 2026 trend catalog — pick deliberately, one direction per project

| Trend | What it is | Best for | Avoid when |
|---|---|---|---|
| Warm minimalism | Clean layouts + soft natural palettes (clay, soil, wood tones), readable serifs, subtle grain, generous whitespace | Advisory, professional services, premium B2B | Youth brands wanting energy |
| Bento grids | Modular box-based layout mixing content types in one view | Dashboards, product features, e-commerce homepages | Long-form narrative pages |
| Scrollytelling | Scroll-triggered narrative reveals guiding a story | Complex offerings, case studies, launches | Frequently revisited utility pages (friction) |
| Expressive typography | Oversized custom headlines as the design's centerpiece | Brand-led B2C, portfolio, campaign pages | Data-dense interfaces |
| Dopamine color | Bright saturated palettes, high-contrast pairings | Youth/lifestyle B2C, Gen Z & Gen Alpha products | Trust-critical B2B, finance |
| Y2K / dial-up nostalgia | Pixel fonts, sticker layers, playful chaos, early-web energy | Gen Z consumer brands (relevant to charm-style products) | Any professional/enterprise context |
| Human scribble | Hand-drawn overlays, doodles, handwriting accents pushing back on AI polish | Indie/craft/maker brands, personal warmth | Corporate credibility contexts |
| Glassmorphism | Translucent layered panels adding depth | Focusing attention on forms/CTAs, fintech cards | Text-heavy content (readability) |
| Dark aesthetic | Dark background, light text, imagery pops | Premium/luxury e-commerce, media | Long reading sessions, older audiences |
| Tasteful maximalism | Rich layers, bold fonts, dense composition — with grid discipline underneath | Standing out in crowded consumer categories | Anything needing calm evaluation |

2026's meta-shift: discipline over spectacle. Trends serve outcomes (clarity, trust, conversion), never "because it's trendy."

## Tokens

**Color:** 4–6 named values: background, surface, primary text, secondary text, one accent, optional second accent. Accent appears in ≤10% of the canvas. Derive the palette from the subject's world (materials, environment, product colors) — not from a default library.

**Type:** 2–3 faces by role. Display face carries personality and is used sparingly (hero, section heads). Body face optimizes reading (16px+ base, 1.5–1.7 line height). Utility face (often a mono or condensed sans) for data, captions, labels. Set a modular scale and stick to it — 4 to 5 sizes total.

**Spacing:** one base unit (4 or 8px), all spacing as multiples. Whitespace is a feature: sections breathe; density is a choice, never an accident.

**Motion:** an orchestrated moment beats scattered effects. Budget: one page-load sequence OR one scroll signature, plus quiet micro-interactions (hover states, button feedback). Every animation ≤ 400ms for UI feedback; respect `prefers-reduced-motion`. Excess motion is the #1 tell of AI-generated design.

## Copy rules

- Words are design material: every label reduces effort or it goes
- Name things by what people control ("Save changes", not "Submit")
- Specific beats clever; active voice; sentence case
- Errors say what happened and how to fix it — no apology, no vagueness
- Empty states invite action

## Layout heuristics

- The hero is a thesis: open with the most characteristic thing in the subject's world
- Big headline + short message above the fold; depth below for those who scroll
- Grid-based sections for scan-and-compare content; sticky nav on pages > 3 screens tall
- Structure encodes meaning: dividers, eyebrows, and labels only where they say something true about the content
