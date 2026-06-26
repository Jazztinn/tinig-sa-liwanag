---
name: "Sugidanon"
description: "A public research exhibit for a Hiligaynon code-switch ASR benchmark."
colors:
  festival-paper: "#fff7ed"
  festival-wash: "#ffedd5"
  lantern-glow: "#fde68a55"
  glass-surface: "#ffffff8c"
  solid-surface: "#ffffff"
  ink: "#1a1a1a"
  warm-ink: "#2a2320"
  woven-muted: "#6b5e54"
  clay-line: "#7c5c3c2e"
  flame: "#f97316"
  flame-strong: "#ea580c"
  banana-switch: "#f59e0b"
  ok-green: "#16a34a"
  ok-wash: "#f0fdf4"
  error-red: "#dc2626"
  error-wash: "#fef2f2"
typography:
  display:
    fontFamily: "Borel, cursive"
    fontSize: "clamp(2.4rem, 6vw, 3.6rem)"
    fontWeight: 400
    lineHeight: 1.1
  body:
    fontFamily: "system-ui, Segoe UI, Roboto, Arial, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.55
  title:
    fontFamily: "system-ui, Segoe UI, Roboto, Arial, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 700
    lineHeight: 1.35
  label:
    fontFamily: "system-ui, Segoe UI, Roboto, Arial, sans-serif"
    fontSize: "0.72rem"
    fontWeight: 700
    letterSpacing: "0.03em"
rounded:
  sm: "8px"
  md: "12px"
  lg: "16px"
  pill: "999px"
spacing:
  s1: "4px"
  s2: "8px"
  s3: "12px"
  s4: "16px"
  s5: "20px"
  s6: "24px"
  s7: "32px"
  s8: "48px"
components:
  glass-container:
    backgroundColor: "{colors.glass-surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "20px 24px"
  filter-pill:
    backgroundColor: "{colors.solid-surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "5px 14px"
  token-error:
    backgroundColor: "{colors.error-wash}"
    textColor: "{colors.error-red}"
    rounded: "{rounded.sm}"
    padding: "3px 8px"
  token-correct:
    backgroundColor: "{colors.ok-wash}"
    textColor: "{colors.ok-green}"
    rounded: "{rounded.sm}"
    padding: "3px 8px"
---

# Design System: Sugidanon

## 1. Overview

**Creative North Star: "Festival Research Table"**

Sugidanon should feel like evidence laid out under warm public light: approachable, human, and inspectable. The current system combines a soft festival-orange surface, glass panels, tactile filter controls, and plain research copy to keep the benchmark legible for judges while preserving technical credibility.

This is a brand-facing research surface, not a generic app shell. The visual system must keep the ASR benchmark first, make the negative switch penalty easy to inspect, and prevent translation-demo styling from becoming the identity.

**Key Characteristics:**
- Warm, public, and community-rooted rather than cold lab software.
- Dense enough for metrics, clips, and filters, but still readable in a judged demo setting.
- Evidence-led: every decorative decision should support audio, token diffs, cohort boundaries, or reproduction paths.
- Glass is a material accent, not a license to lower contrast.

## 2. Colors

The palette is a committed warm research palette: festival paper surfaces, flame-orange emphasis, and strict semantic colors for correctness and error states.

### Primary
- **Flame** (`#f97316`): primary accent for selected controls, data fills, badges, and action emphasis.
- **Flame Strong** (`#ea580c`): stronger emphasis for the Sugidanon wordmark, key gap values, and durable accent text.

### Secondary
- **Banana Switch** (`#f59e0b`): switch-region cue and language-pair bar energy. Use only for switch proximity or related data.

### Tertiary
- **OK Green** (`#16a34a`): correct tokens and lower WER values.
- **Error Red** (`#dc2626`): ASR errors and high WER values.

### Neutral
- **Festival Paper** (`#fff7ed`): page background.
- **Festival Wash** (`#ffedd5`): radial wash behind the surface field.
- **Glass Surface** (`#ffffff8c`): translucent panel material; must degrade to solid white when backdrop filters are unsupported.
- **Ink** (`#1a1a1a`) and **Warm Ink** (`#2a2320`): primary readable text.
- **Woven Muted** (`#6b5e54`): secondary explanatory copy and labels.

### Named Rules

**The Semantic Color Rule.** Green, red, and amber are data-state colors first. Never use them as decoration where they could be mistaken for correctness, error, or switch state.

**The Benchmark First Rule.** Orange emphasis belongs on the finding, filters, reproduction paths, and model tags. Do not spend it on generic marketing flourish.

## 3. Typography

**Display Font:** Borel with cursive fallback.
**Body Font:** system-ui with Segoe UI, Roboto, Arial, sans-serif fallbacks.
**Label/Mono Font:** none.

**Character:** The Borel display face gives the benchmark a local, oral-story signature, while the system sans keeps metrics and protocol text fast to read. This pairing works only when Borel is reserved for the wordmark and not sprayed across UI labels.

### Hierarchy
- **Display** (400, `clamp(2.4rem, 6vw, 3.6rem)`, 1.1): Sugidanon wordmark and no more.
- **Headline** (800, `clamp(2.6rem, 8vw, 3.6rem)`, 1): major WER numbers where comparison is the content.
- **Title** (700, `0.95rem`, 1.35): card and section titles inside compact panels.
- **Body** (400, `15px`, 1.55): explanatory prose, clipped to about 68-72ch where the story is being read.
- **Label** (700, `0.72rem`, `0.03em`, uppercase allowed): compact tags, row labels, table headers, and filter labels.

### Named Rules

**The One Script Rule.** Borel appears only in the Sugidanon brand mark. All benchmark reading, filtering, and data comparison uses system sans.

## 4. Elevation

Depth is mostly material and tonal: translucent glass panels, inset controls, and row state changes. Shadows are minimal and stateful; at rest, cards should not stack heavy borders and broad shadows.

### Shadow Vocabulary
- **Low Ambient** (`0 1px 3px rgba(0, 0, 0, 0.12)`): small controls only.
- **Raised Clip** (`0 4px 20px rgba(0, 0, 0, 0.1), 0 1px 4px rgba(0, 0, 0, 0.06)`): open clip row or active lifted state only.
- **Inset Pill** (`inset 0 2px 5px rgba(0, 0, 0, 0.13), inset 0 -1px 0 rgba(255, 255, 255, 0.6)`): segmented control trough.

### Named Rules

**The Open Row Rule.** Elevation appears when the user opens or activates evidence. Static sections stay flat glass.

## 5. Components

### Buttons
- **Shape:** pill for segmented filters and action buttons (`999px`); small controls use compact padding.
- **Primary:** flame fill (`#f97316`) with white text for active filter state.
- **Hover / Focus:** hover increases surface opacity; focus must add a visible outline or equivalent ring if the component is revised.
- **Secondary / Ghost:** glass button surface with semibold ink text.

### Chips
- **Style:** pill chips with low-chroma semantic tint; switch chips use amber, domain chips use warm neutral.
- **State:** chips identify metadata, not actions. Keep click targets separate from passive labels.

### Cards / Containers
- **Corner Style:** softly rounded panels (`16px`), compact nested content (`8px` or `12px`).
- **Background:** translucent glass at rest; solid white fallback for unsupported backdrop filters.
- **Shadow Strategy:** no decorative shadow at rest. Use raised clip shadow only for opened evidence.
- **Border:** white translucent border for glass, hairline dividers for row separation.
- **Internal Padding:** panel padding ranges from `20px` to `32px`; clip rows use tighter `13px 20px`.

### Inputs / Fields
- **Style:** the main Next surface has no text inputs; prediction blocks use recessed neutral wells.
- **Focus:** any future fields should use the flame accent for focus, but with a high-contrast ring.
- **Error / Disabled:** error copy should use red with text labels, not red alone.

### Navigation
- **Style:** no persistent nav in the current benchmark explorer. Reproduction links act as navigation cards and should stay plainly labeled with destination and purpose.

### Token Diff

Token pills are the signature component. Correct tokens are green, ASR errors are red with a line-through, and switch-region tokens receive an amber inset outline. Tooltip text explains status, switch region, and language tag.

## 6. Do's and Don'ts

### Do:
- **Do** lead with the benchmark, not the translation scaffold.
- **Do** keep headline, development, and robustness cohorts visually separate.
- **Do** pair every large metric with enough plain-language context to prevent misreading WER.
- **Do** preserve strong contrast for muted prose, filter labels, token text, and chart values.
- **Do** use audio clips and token diffs as the primary proof pattern.

### Don't:
- **Don't** present Sugidanon as a finished translation app, consumer voice product, or generic AI demo.
- **Don't** blend extension cohorts into the headline result.
- **Don't** overclaim Hiligaynon language authority where labels remain `seed_unverified`.
- **Don't** use generic SaaS hero cliches, decorative metric cards that bury methodology, or generic "AI for good" framing.
- **Don't** use glass effects that make body text, labels, or token states harder to read.
