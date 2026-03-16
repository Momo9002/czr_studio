---
description: Add a new portfolio case study to Aura Web Studio
---

# Add New Case Study

## When to Use

When you have a real client, or want to add a new fictional use case to the portfolio.

## Steps

1. **Create the case study page** — copy closest existing one as template:
```
cp cases/architecture-studio.html cases/new-name.html
```

2. **Generate a portfolio thumbnail** — use `generate_image` tool:
   - Size: ~800×500px
   - Style: match existing portfolio images (dark, cinematic, premium)
   - Save to: `images/portfolio_newname.png`

3. **Add to portfolio grid in `index.html`** — find the `portfolio-grid` section and add a new `.p-card`:
```html
<a class="p-card" href="cases/new-name.html" data-project="newname">
  <div class="p-img-wrap">
    <img src="images/portfolio_newname.png" alt="Project Name" loading="lazy" width="800" height="500">
    <div class="p-hover"><span>View Case ↗</span></div>
  </div>
  <div class="p-meta">
    <span class="p-tag">Industry · Tech · Stack</span>
    <h3>Project Name</h3>
    <p>Short description. Delivered in Xh.</p>
  </div>
</a>
```

4. **Add modal data** — in the `projects` JS object in `index.html`:
```js
newname: {
  img: 'images/portfolio_newname.png',
  tag: 'Industry · Tech · Stack',
  title: 'Project Name',
  desc: 'Full description for modal.',
  stack: ['Tech1', 'Tech2'],
  result: 'Key outcome metric'
},
```

5. **Update portfolio count** — if the grid now has 7+ cards, consider removing one or adjusting the CSS grid layout in `style.css` (`.portfolio-grid`).

## Real Client Case Studies

For real clients, replace the fictional names with initials only (e.g. "S.L. — Architecture") and get written permission before using.
