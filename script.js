// ── Aura Web Studio — script.js ──────────────────────────────
// Extracted from inline script. All functionality preserved.

// ── WhatsApp number ───────────────────────────────────────────
const WA = '971551343144';
const WA_URL = `https://wa.me/${WA}`;
document.getElementById('wa-fab').href = WA_URL;
document.getElementById('footer-wa').href = WA_URL;

// ── Copyright year ────────────────────────────────────────────
document.getElementById('year').textContent = new Date().getFullYear();

// ── Splash ────────────────────────────────────────────────────
const splash = document.getElementById('splash');
const splashBar = document.getElementById('splash-bar');
const DUR = 5000;
let done = false;

function dismissSplash() {
  if (done) return; done = true;
  sessionStorage.setItem('splashSeen', '1');
  splash.style.opacity = '0';
  setTimeout(() => { splash.style.display = 'none'; }, 700);
}

if (sessionStorage.getItem('splashSeen')) {
  splash.style.display = 'none'; done = true;
} else {
  splashBar.style.transition = `width ${DUR}ms linear`;
  requestAnimationFrame(() => { splashBar.style.width = '100%'; });
  setTimeout(dismissSplash, DUR);
  document.getElementById('splash-enter').addEventListener('click', dismissSplash);
}

// ── Header scroll ─────────────────────────────────────────────
window.addEventListener('scroll', () => {
  document.getElementById('header').classList.toggle('scrolled', window.scrollY > 60);
});

// ── Burger + mobile nav auto-close ───────────────────────────
const headerEl = document.getElementById('header');
document.getElementById('burger').addEventListener('click', () => {
  headerEl.classList.toggle('nav-open');
});
document.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', () => headerEl.classList.remove('nav-open'));
});

// ── Reveal on scroll ──────────────────────────────────────────
const observer = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('revealed'); observer.unobserve(e.target); }
  });
}, { threshold: 0.12 });
document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

// ── Use case modal data ───────────────────────────────────────
const projects = {
  fashion: {
    img: 'images/portfolio_fashion_main.png',
    tag: 'Fashion House · Next.js · Framer Motion · Vercel',
    title: 'Fashion House',
    desc: 'Full brand presence for an independent Parisian fashion house. Full-screen editorial lookbook, collection drop pages with countdown and waitlist, cinematic scroll transitions, and an inquiry funnel wired directly to agent handoff. Delivered in 42 hours.',
    stack: ['Next.js', 'Framer Motion', 'Vercel', 'WhatsApp Business'],
    result: '↑ 280% online inquiries · Delivered in 42h'
  },
  architecture: {
    img: 'images/portfolio_architecture.png',
    tag: 'Architecture Studio · Custom Code · GSAP',
    title: 'Architecture Studio',
    desc: 'Cinematic portfolio for a boutique firm spanning Dubai and Luxembourg. Immersive full-screen project case studies, parallax photography, animated spec sidebars, and a bespoke inquiry system with agent handoff on WhatsApp. Delivered in 38 hours.',
    stack: ['HTML', 'CSS', 'GSAP', 'Intersection Observer', 'Netlify'],
    result: 'Delivered in 38h · Featured in 3 publications'
  },
  restaurant: {
    img: 'images/portfolio_restaurant.png',
    tag: 'Fine Dining · Custom Code · Reservation System',
    title: 'Gastronomic Restaurant',
    desc: "Complete brand experience for a Monaco gastronomic table. Chef's narrative, seasonal menu, philosophy section, and a direct reservation system cutting OTA dependency entirely. Every cover sold out within the first week.",
    stack: ['HTML', 'CSS', 'JavaScript', 'Stripe', 'Resend'],
    result: 'Fully booked · Week one · OTA dependency cut by 60%'
  },
  fragrance: {
    img: 'images/portfolio_ecommerce.png',
    tag: 'Product Launch · GSAP · Stripe',
    title: 'Luxury Fragrance Launch',
    desc: 'Limited-edition launch page for a Paris perfume house. Animated editorial hero, countdown to release, exclusive early-access form, and Stripe pre-order integration. Built to convert at premium price point with zero discount incentive.',
    stack: ['JavaScript', 'GSAP', 'Stripe', 'Vercel'],
    result: '€120K in pre-orders · 72h after launch'
  },
  director: {
    img: 'images/portfolio_fashion_2.png',
    tag: 'Personal Brand · Framer · Custom CMS',
    title: 'Creative Director',
    desc: 'Stark, confident personal presence for a Monaco-based creative director. Every project presented as a full-page immersive case study. Direct inquiry form with agent handoff — no intermediary, no friction. Delivered in 29 hours.',
    stack: ['Framer', 'Custom CMS', 'WhatsApp Business', 'Cloudflare'],
    result: '100% inquiry-to-consultation rate'
  },
  photographer: {
    img: 'images/portfolio_photographer.png',
    tag: 'Photography · Custom Code · Booking System',
    title: 'Fashion Photographer',
    desc: 'Full-bleed editorial portfolio and integrated booking system for a Paris-based fashion photographer. Full-screen gallery, editorial biography, press archive, and a seamless booking form. Fully booked within 72 hours of going live.',
    stack: ['HTML', 'CSS', 'JavaScript', 'Resend', 'Netlify'],
    result: 'Fully booked within 72h of launch'
  }
};

// ── Modal ─────────────────────────────────────────────────────
const backdrop = document.getElementById('modal-backdrop');
const modal = document.getElementById('modal');
const modalClose = document.getElementById('modal-close');

function openModal(p) {
  document.getElementById('modal-img').src = p.img;
  document.getElementById('modal-img').alt = p.title;
  document.getElementById('modal-tag').textContent = p.tag;
  document.getElementById('modal-title').textContent = p.title;
  document.getElementById('modal-desc').textContent = p.desc;
  document.getElementById('modal-stack').innerHTML = p.stack.map(s => `<span class="stack-pill">${s}</span>`).join('');
  document.getElementById('modal-result').textContent = p.result;
  backdrop.classList.add('open');
  document.body.style.overflow = 'hidden';
  // Focus trap: move focus into modal
  modalClose.focus();
}

function closeModal() {
  backdrop.classList.remove('open');
  document.body.style.overflow = '';
}

document.querySelectorAll('.p-card').forEach(card => {
  card.addEventListener('click', () => {
    const p = projects[card.dataset.project];
    if (p) openModal(p);
  });
});

modalClose.addEventListener('click', closeModal);
backdrop.addEventListener('click', e => { if (e.target === backdrop) closeModal(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

// Keyboard trap inside modal
modal.addEventListener('keydown', e => {
  if (e.key !== 'Tab') return;
  const focusable = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
  const first = focusable[0], last = focusable[focusable.length - 1];
  if (e.shiftKey) { if (document.activeElement === first) { last.focus(); e.preventDefault(); } }
  else { if (document.activeElement === last) { first.focus(); e.preventDefault(); } }
});

// ── FAQ ───────────────────────────────────────────────────────
document.querySelectorAll('.faq-q').forEach(btn => {
  btn.addEventListener('click', () => {
    const isOpen = btn.getAttribute('aria-expanded') === 'true';
    document.querySelectorAll('.faq-q').forEach(b => b.setAttribute('aria-expanded', 'false'));
    btn.setAttribute('aria-expanded', isOpen ? 'false' : 'true');
  });
});

// ── Lead Form → WhatsApp ──────────────────────────────────────
document.getElementById('lead-form').addEventListener('submit', function(e) {
  e.preventDefault();
  const fields = [
    { id: 'f-name',  errId: 'err-name',  msg: 'Please enter your name.' },
    { id: 'f-email', errId: 'err-email', msg: 'Please enter a valid email.' },
    { id: 'f-phone', errId: 'err-phone', msg: 'Please enter your phone number.' },
    { id: 'f-pkg',   errId: 'err-pkg',   msg: 'Please select a package.' },
    { id: 'f-brief', errId: 'err-brief', msg: 'Please describe your vision.' },
  ];
  let valid = true;
  fields.forEach(f => {
    const el = document.getElementById(f.id);
    const err = document.getElementById(f.errId);
    const empty = !el.value.trim();
    el.classList.toggle('invalid', empty);
    err.textContent = empty ? f.msg : '';
    if (empty) valid = false;
  });
  if (!valid) {
    this.classList.add('shake');
    setTimeout(() => this.classList.remove('shake'), 500);
    return;
  }
  const name  = document.getElementById('f-name').value.trim();
  const email = document.getElementById('f-email').value.trim();
  const phone = document.getElementById('f-phone').value.trim();
  const pkg   = document.getElementById('f-pkg').value;
  const brief = document.getElementById('f-brief').value.trim();
  const msg = encodeURIComponent(
    `Hi Aura Studio! Here's my project brief:\n\n` +
    `👤 Name: ${name}\n📧 Email: ${email}\n📦 Package: ${pkg}\n\n💡 Vision:\n${brief}`
  );
  const label = document.getElementById('submit-label');
  const btn = document.getElementById('form-submit');
  label.textContent = 'Sending...';
  btn.disabled = true;
  setTimeout(() => {
    window.open(`${WA_URL}?text=${msg}`, '_blank');
    // Success state
    label.textContent = 'Brief Sent! ✓';
    btn.style.background = 'var(--accent-warm)';
    this.reset();
    fields.forEach(f => {
      document.getElementById(f.id).classList.remove('invalid');
      document.getElementById(f.errId).textContent = '';
    });
    setTimeout(() => {
      label.textContent = 'Send My Brief →';
      btn.style.background = '';
      btn.disabled = false;
    }, 3000);
  }, 400);
});
