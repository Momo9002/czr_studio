---
description: Start local dev server for Aura Web Studio
---

# Dev Server

Aura is a static site — no build step needed.

## Start Server

// turbo
1. Run the local server:
```
python3 -m http.server 8765 --directory /Volumes/Amaur/Documents/antigravity_mac/aura_web
```

2. Open in browser:
```
open http://localhost:8765
```

## Hard Refresh (if CSS not updating)

In browser: `Cmd + Shift + R`

Or bump the version in `index.html`:
```html
<link rel="stylesheet" href="style.css?v=3">
```

## Stop Server

`Ctrl + C` in the terminal running the server.
