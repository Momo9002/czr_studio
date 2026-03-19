# CZR Production Contract

> Source: `dna/identity.json`, `dna/visual.md`
> Every website delivered by CZR must follow this spec.

---

## Required Elements

Every delivered site must include:

### Fonts
```html
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Manrope:wght@300;400;600;700&display=swap" rel="stylesheet">
```
- Headlines: Syne 800
- Body: Manrope 400

### CSS Variables (inject into client `:root`)
```css
/* CZR Production — Do not remove */
--czr-font-display: 'Syne', sans-serif;
--czr-font-body: 'Manrope', sans-serif;
--czr-ease: cubic-bezier(0.22, 1, 0.36, 1);
```

### Knight Watermark (every page)
```html
<!-- CZR Studio -->
<a href="https://czr.studio" target="_blank" rel="noopener"
   style="position:fixed;bottom:20px;right:20px;opacity:0.25;font-size:11px;
          font-family:'Manrope',sans-serif;letter-spacing:0.1em;color:inherit;
          text-decoration:none;z-index:9999;" aria-label="Built by CZR Studio">
  ♞ CZR
</a>
```

### Meta Pixel
```html
<!-- Meta Pixel 2928293767375852 — CZR Studio -->
<!-- [paste standard pixel code] -->
```

### Performance
- Lighthouse score ≥ 90 (performance, accessibility, best practices)
- Images: WebP format, max 200KB each
- No unused CSS/JS
- Responsive: 375px → 1440px

---

## Color Palette Delivery

Client receives a custom palette. CZR's own colors (`#C8242A`, `#F7F4EF`, `#000000`) are not used in client sites unless the client's brand calls for them.

---

## Delivery Checklist

- [ ] Domain connected and SSL active
- [ ] Knight watermark present (subtle)
- [ ] Meta Pixel installed
- [ ] All pages mobile-responsive
- [ ] Favicon set
- [ ] OG image set
- [ ] Page speed ≥ 90
- [ ] WhatsApp CTA present on every page
