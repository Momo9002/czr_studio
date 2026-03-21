# CZR Studio — Typography Specimen

> Font selections and usage reference.

---

## Display Font: Syne

- **Source:** [Google Fonts — Syne](https://fonts.google.com/specimen/Syne)
- **Category:** Sans-serif, geometric, high-impact
- **Weights used:** 400, 600, 700, **800 (primary)**
- **CSS variable:** `--font-display: 'Syne', sans-serif`

### Usage

| Context | Weight | Size | Tracking |
|---|---|---|---|
| Hero headlines | 800 | `clamp(4rem, 11vw, 10rem)` | `-0.045em` |
| Section headlines | 800 | `clamp(2.4rem, 5.5vw, 5rem)` | `-0.04em` |
| Card titles | 800 | `clamp(1.2rem, 2.2vw, 1.8rem)` | `-0.03em` |
| Wordmark (CZR.) | 800 | `1.4rem` (header) | `-0.05em` |
| Step numbers | 800 | `4rem` | `-0.05em` |
| Metrics | 800 | `2.8rem` | `-0.04em` |

### Character

Syne is bold, geometric, and opinionated. It commands attention without shouting. The tight negative tracking creates visual density that reads as confident and premium.

---

## Body Font: Manrope

- **Source:** [Google Fonts — Manrope](https://fonts.google.com/specimen/Manrope)
- **Category:** Sans-serif, geometric, highly readable
- **Weights used:** 300, 400, 500, 600, **700**
- **CSS variable:** `--font-body: 'Manrope', sans-serif`

### Usage

| Context | Weight | Size | Tracking |
|---|---|---|---|
| Body copy | 400 | `1rem` (16px) | normal |
| Descriptions | 400 | `0.9-1.05rem` | normal |
| Eyebrows / labels | 700 | `0.65rem` | `0.22em` |
| Buttons | 700 | `0.8rem` | `0.08em` |
| Navigation | 600-700 | `0.72-0.75rem` | `0.1em` |
| Card tags | 700 | `0.6rem` | `0.16em` |

### Character

Manrope is clean, modern, and neutral. It provides excellent readability at small sizes and creates a refined, professional feel when spaced wide in uppercase for labels and buttons.

---

## Google Fonts Embed

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Manrope:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

## CSS Variables

```css
:root {
  --font-display: 'Syne', sans-serif;
  --font-body:    'Manrope', sans-serif;
}
```
