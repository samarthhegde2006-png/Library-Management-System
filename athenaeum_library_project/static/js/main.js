/* THE ATHENAEUM — Built by Tanush Muddapur | Parchment Light / Espresso Dark Mode & Scroll Animations */
(function() {
  const savedTheme = localStorage.getItem('athenaeum_theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
})();

document.addEventListener('DOMContentLoaded', () => {
  const themeBtn = document.getElementById('theme-toggle-btn');
  const syncLabel = () => {
    if (!themeBtn) return;
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    themeBtn.innerHTML = isDark ? '☀ Light' : '☾ Dark';
  };
  syncLabel();

  if (themeBtn) {
    themeBtn.addEventListener('click', () => {
      const curr = document.documentElement.getAttribute('data-theme');
      const next = curr === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('athenaeum_theme', next);
      syncLabel();
    });
  }

  const obs = new IntersectionObserver((entries) => {
    entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add('in-view'); });
  }, { threshold: 0.08 });
  document.querySelectorAll('.slide-up, .slide-down, .fade-scale').forEach((el) => obs.observe(el));

  const navWrap = document.getElementById('liquid-nav-wrapper');
  let lastY = window.scrollY;
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    if (navWrap) {
      if (y > lastY && y > 380) navWrap.classList.add('nav-hidden');
      else navWrap.classList.remove('nav-hidden');
    }
    lastY = y;
  }, { passive: true });

  const burger = document.getElementById('mobile-hamburger');
  const menu = document.getElementById('primary-nav-menu');
  if (burger && menu) burger.addEventListener('click', () => menu.classList.toggle('mobile-open'));

  setTimeout(() => {
    document.querySelectorAll('.aether-toast').forEach((t) => { t.style.opacity = '0'; setTimeout(() => t.remove(), 400); });
  }, 4000);
});

function toggleMoreMenu(e) {
  e.stopPropagation();
  const dd = document.getElementById('nav-more-dropdown');
  if (dd) dd.classList.toggle('open');
}

document.addEventListener('click', (e) => {
  const dd = document.getElementById('nav-more-dropdown');
  if (dd && !dd.contains(e.target)) dd.classList.remove('open');
});

function switchBookEdition(swatchBtn, imgSrc, editionName) {
  const card = swatchBtn.closest('.book-card');
  if (!card) return;
  const img = card.querySelector('.primary-book-img');
  if (img && imgSrc) {
    img.style.opacity = '0.35';
    setTimeout(() => { img.src = imgSrc; img.style.opacity = '1'; }, 140);
  }
  const label = card.querySelector('.active-edition-label');
  if (label) label.textContent = editionName;
  card.querySelectorAll('.swatch-circle').forEach(s => s.classList.remove('active'));
  swatchBtn.classList.add('active');
}

function swapBookGallery(thumbEl, src, caption) {
  const mainImg = document.getElementById('fk-main-image');
  if (mainImg) {
    mainImg.style.opacity = '0.35';
    setTimeout(() => { mainImg.src = src; mainImg.style.opacity = '1'; }, 140);
  }
  const cap = document.getElementById('fk-image-caption');
  if (cap && caption) cap.textContent = caption;
  document.querySelectorAll('.fk-thumb').forEach(t => t.classList.remove('active'));
  thumbEl.classList.add('active');
}

function togglePwd(id, btn) {
  const inp = document.getElementById(id);
  if (!inp) return;
  inp.type = inp.type === 'password' ? 'text' : 'password';
  btn.textContent = inp.type === 'password' ? 'Show' : 'Hide';
}
