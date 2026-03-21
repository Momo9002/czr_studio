# CZR Studio — Color Palette

> All colors extracted from the live design system (`style.css`).

---

## Core Palette

### Backgrounds

| Name | Hex | RGB | CSS Token |
|---|---|---|---|
| Background | `#000000` | `0, 0, 0` | `--bg` |
| Surface | `#080808` | `8, 8, 8` | `--surface` |
| Surface 2 | `#0F0F0F` | `15, 15, 15` | `--surface-2` |
| Surface 3 | `#181818` | `24, 24, 24` | `--surface-3` |

### Accent

| Name | Hex | RGB | CSS Token |
|---|---|---|---|
| Accent (White) | `#FFFFFF` | `255, 255, 255` | `--accent` |
| Accent Soft | `rgba(255,255,255,0.07)` | — | `--accent-soft` |

### Mondrian Primaries

| Name | Hex | RGB | CSS Token | Usage |
|---|---|---|---|---|
| Red | `#C8242A` | `200, 36, 42` | `--m-red` | Primary accent, underlines, progress |
| Yellow | `#F0C029` | `240, 192, 41` | `--m-yellow` | Secondary accent, highlights |
| Blue | `#1A4BA8` | `26, 75, 168` | `--m-blue` | Tertiary accent, tiles |
| Line | `#1F1F1F` | `31, 31, 31` | `--m-line` | Grid dividers |

### Text

| Name | Hex | CSS Token | Usage |
|---|---|---|---|
| Primary | `#FFFFFF` | `--text` | Headlines, strong |
| Muted | `#999999` | `--text-muted` | Body copy |
| Dim | `#555555` | `--text-dim` | Labels, captions |

### Borders

| Name | Value | CSS Token |
|---|---|---|
| Rule | `rgba(255,255,255,0.05)` | `--rule` |
| Rule Hard | `rgba(255,255,255,0.10)` | `--rule-hard` |
| Rule Bright | `rgba(255,255,255,0.18)` | `--rule-bright` |

---

## Color Rays (Hero Animation)

The hero canvas draws animated rays using these exact specs:

```js
{ color: [200, 36, 42],   opacity: 0.18 }  // Red
{ color: [240, 192, 41],  opacity: 0.14 }  // Yellow
{ color: [26,  75,  168], opacity: 0.16 }  // Blue
```

Rays are drawn with radial gradients fading from origin to transparent, creating the signature CZR "light burst" effect.
