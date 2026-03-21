/**
 * CZR Studio — DNA Inject
 * Fetches /api/dna at runtime and hydrates the page with brand constants
 * AND applies design flags to control visual behavior.
 *
 * ─── TEXT / DATA ATTRIBUTES ───────────────────────────────────────────────────
 *   data-dna="brand.tagline"              → sets textContent
 *   data-dna-price="packages.sprint.price"→ sets textContent as €999
 *   data-dna-href="brand.whatsapp"        → sets href (WhatsApp/Instagram aware)
 *
 * ─── DESIGN FLAGS (from identity.json → design) ───────────────────────────────
 *   hero_canvas: false        → hides #hero-canvas (removes matrix rays)
 *   hero_video: false         → hides .hero-video + .hero-video-overlay
 *   splash: false             → skips splash screen entirely
 *   ticker: false             → hides the ticker strip
 *   hero_scroll_indicator: false → hides .hero-scroll
 *   animation_intensity       → "none" adds .czr-no-anim to body (CSS can target)
 *                             → "minimal" adds .czr-minimal-anim (default)
 *                             → "full" no class added
 *
 * ─── ADD TO index.html ────────────────────────────────────────────────────────
 *   <script type="module" src="/dna/inject.js"></script>
 */

(async () => {
  // ── Fetch DNA ───────────────────────────────────────────────────────────────
  let dna;
  try {
    const res = await fetch("/api/dna", { cache: "no-store" });
    if (!res.ok) throw new Error(`DNA fetch failed: ${res.status}`);
    dna = await res.json();
  } catch (err) {
    console.warn("[CZR DNA] Could not load DNA — page running with static values.", err);
    return;
  }

  const design = dna.design || {};

  // ── Dot-path resolver ────────────────────────────────────────────────────────
  const get = (obj, path) => {
    if (!path) return undefined;
    return path.split(".").reduce((o, k) => (o != null ? o[k] : undefined), obj);
  };

  // ══════════════════════════════════════════════════════════════════════════════
  //  DESIGN FLAGS — applied before paint where possible
  // ══════════════════════════════════════════════════════════════════════════════

  // 1. Splash — kill immediately so there's no flash of the splash then hide
  if (design.splash === false) {
    const splash = document.getElementById("splash");
    if (splash) {
      splash.style.display = "none";
      // Signal body that splash is done so hero animations fire
      document.body.classList.add("ready");
      // Prevent the inline script from re-showing it
      try { sessionStorage.setItem("czr_splash", "1"); } catch (_) {}
    }
  }

  // 2. Hero canvas (matrix rays)
  if (design.hero_canvas === false) {
    const canvas = document.getElementById("hero-canvas");
    if (canvas) canvas.style.display = "none";
  }

  // 3. Hero video background
  if (design.hero_video === false) {
    document.querySelectorAll(".hero-video, .hero-video-overlay").forEach(el => {
      el.style.display = "none";
    });
  }

  // 4. Ticker strip
  if (design.ticker === false) {
    const ticker = document.querySelector(".ticker");
    if (ticker) ticker.style.display = "none";
  }

  // 5. Scroll indicator
  if (design.hero_scroll_indicator === false) {
    const scroll = document.querySelector(".hero-scroll");
    if (scroll) scroll.style.display = "none";
  }

  // 6. Animation intensity — add class to body for CSS to target
  const intensity = design.animation_intensity || "full";
  if (intensity === "none")    document.body.classList.add("czr-no-anim");
  if (intensity === "minimal") document.body.classList.add("czr-minimal-anim");

  // ══════════════════════════════════════════════════════════════════════════════
  //  DATA INJECTION
  // ══════════════════════════════════════════════════════════════════════════════

  // 7. Inject text content
  document.querySelectorAll("[data-dna]").forEach((el) => {
    const val = get(dna, el.dataset.dna);
    if (val !== undefined && val !== null) {
      el.textContent = String(val);
    }
  });

  // 8. Inject formatted prices (€999, €2 499 etc.)
  document.querySelectorAll("[data-dna-price]").forEach((el) => {
    const val = get(dna, el.dataset.dnaPrice);
    if (val !== undefined && val !== null) {
      const num = Number(val);
      el.textContent = isNaN(num)
        ? String(val)
        : "€" + num.toLocaleString("fr-FR");
    }
  });

  // 9. Inject hrefs
  document.querySelectorAll("[data-dna-href]").forEach((el) => {
    const path = el.dataset.dnaHref;
    const val = get(dna, path);
    if (!val) return;
    if (path === "brand.whatsapp") {
      const cleaned = String(val).replace(/\D/g, "");
      el.href = `https://wa.me/${cleaned}`;
    } else if (path === "brand.instagram") {
      const handle = String(val).replace(/^@/, "");
      el.href = `https://instagram.com/${handle}`;
    } else {
      el.href = String(val);
    }
  });

  // ══════════════════════════════════════════════════════════════════════════════
  //  CSS CUSTOM PROPERTIES — override :root from DNA colors
  // ══════════════════════════════════════════════════════════════════════════════

  if (dna.colors) {
    const root = document.documentElement.style;
    const keyMap = {
      black:     "--black",
      cream:     "--cream",
      white:     "--white",
      red:       "--red",
      hermes:    "--hermes",
      navy:      "--navy",
      gold:      "--gold",
      dark_text: "--dark-text",
      surface:   "--surface",
      surface_2: "--surface-2",
      surface_3: "--surface-3",
    };
    Object.entries(keyMap).forEach(([dnaKey, cssVar]) => {
      const val = dna.colors[dnaKey];
      if (val) root.setProperty(cssVar, val);
    });
  }

  console.log("[CZR DNA] Injected ✓", {
    brand: dna.brand?.name,
    design_flags: Object.keys(design).filter(k => k !== "notes"),
    colors: Object.keys(dna.colors || {}).length,
  });
})();
