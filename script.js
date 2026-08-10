(() => {
  const root = document.documentElement;
  const body = document.body;
  const header = document.querySelector('.site-header');
  const themeButton = document.querySelector('.theme-toggle');
  const themeMeta = document.querySelector('meta[name="theme-color"]');
  const navToggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const savedTheme = localStorage.getItem('xihang-theme');
  const preferredTheme = window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  const initialTheme = savedTheme || preferredTheme;
  root.dataset.theme = initialTheme;
  themeMeta.setAttribute('content', initialTheme === 'light' ? '#f5f8f6' : '#07111a');

  themeButton.addEventListener('click', () => {
    const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    localStorage.setItem('xihang-theme', next);
    themeMeta.setAttribute('content', next === 'light' ? '#f5f8f6' : '#07111a');
  });

  const closeNav = () => {
    navToggle.setAttribute('aria-expanded', 'false');
    navToggle.setAttribute('aria-label', 'Open navigation');
    navLinks.classList.remove('open');
    body.classList.remove('nav-open');
  };

  navToggle.addEventListener('click', () => {
    const open = navToggle.getAttribute('aria-expanded') !== 'true';
    navToggle.setAttribute('aria-expanded', String(open));
    navToggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    navLinks.classList.toggle('open', open);
    body.classList.toggle('nav-open', open);
  });
  navLinks.querySelectorAll('a').forEach(link => link.addEventListener('click', closeNav));

  window.addEventListener('scroll', () => header.classList.toggle('scrolled', window.scrollY > 16), { passive: true });
  document.getElementById('year').textContent = new Date().getFullYear();

  if (!reducedMotion) {
    window.addEventListener('pointermove', event => {
      root.style.setProperty('--pointer-x', `${event.clientX}px`);
      root.style.setProperty('--pointer-y', `${event.clientY}px`);
    }, { passive: true });
  }

  const revealItems = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !reducedMotion) {
    const revealObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.11, rootMargin: '0px 0px -40px' });
    revealItems.forEach((item, index) => {
      item.style.transitionDelay = `${Math.min((index % 4) * 55, 165)}ms`;
      revealObserver.observe(item);
    });
  } else {
    revealItems.forEach(item => item.classList.add('visible'));
  }

  const filters = document.querySelectorAll('.filter');
  const publications = document.querySelectorAll('.pub-card');
  filters.forEach(filter => {
    filter.addEventListener('click', () => {
      filters.forEach(button => button.classList.remove('active'));
      filter.classList.add('active');
      const topic = filter.dataset.filter;
      publications.forEach(card => {
        const show = topic === 'all' || card.dataset.topic === topic;
        card.classList.toggle('hidden', !show);
      });
    });
  });

  if (!reducedMotion && matchMedia('(pointer: fine)').matches) {
    document.querySelectorAll('.pub-card').forEach(card => {
      card.addEventListener('pointermove', event => {
        const rect = card.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width - .5;
        const y = (event.clientY - rect.top) / rect.height - .5;
        card.style.transform = `perspective(900px) rotateX(${-y * 2.5}deg) rotateY(${x * 2.5}deg) translateY(-2px)`;
      });
      card.addEventListener('pointerleave', () => { card.style.transform = ''; });
    });
  }

  const sections = [...document.querySelectorAll('main section[id]')];
  const navAnchors = [...document.querySelectorAll('.nav-links a')];
  const sectionObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        navAnchors.forEach(anchor => anchor.classList.toggle('active', anchor.getAttribute('href') === `#${entry.target.id}`));
      }
    });
  }, { rootMargin: '-35% 0px -58%', threshold: 0 });
  sections.forEach(section => sectionObserver.observe(section));

  const canvas = document.getElementById('network-canvas');
  const ctx = canvas.getContext('2d');
  let particles = [];
  let frame;
  let pointer = { x: -9999, y: -9999 };

  function resizeCanvas() {
    const rect = canvas.getBoundingClientRect();
    const ratio = Math.min(devicePixelRatio, 2);
    canvas.width = rect.width * ratio;
    canvas.height = rect.height * ratio;
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    const count = Math.min(72, Math.max(34, Math.floor(rect.width / 19)));
    particles = Array.from({ length: count }, () => ({
      x: Math.random() * rect.width,
      y: Math.random() * rect.height * .86,
      vx: (Math.random() - .5) * .16,
      vy: (Math.random() - .5) * .16,
      r: Math.random() * 1.15 + .45
    }));
  }

  function drawNetwork() {
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    ctx.clearRect(0, 0, width, height);
    const light = root.dataset.theme === 'light';
    particles.forEach((particle, index) => {
      particle.x += particle.vx;
      particle.y += particle.vy;
      if (particle.x < 0 || particle.x > width) particle.vx *= -1;
      if (particle.y < 0 || particle.y > height * .9) particle.vy *= -1;
      const dxPointer = pointer.x - particle.x;
      const dyPointer = pointer.y - particle.y;
      const pointerDistance = Math.hypot(dxPointer, dyPointer);
      if (pointerDistance < 140) {
        particle.x -= dxPointer * .0007;
        particle.y -= dyPointer * .0007;
      }
      ctx.beginPath();
      ctx.arc(particle.x, particle.y, particle.r, 0, Math.PI * 2);
      ctx.fillStyle = light ? 'rgba(8,127,109,.38)' : 'rgba(105,231,204,.42)';
      ctx.fill();

      for (let j = index + 1; j < particles.length; j++) {
        const other = particles[j];
        const distance = Math.hypot(particle.x - other.x, particle.y - other.y);
        if (distance < 118) {
          ctx.beginPath();
          ctx.moveTo(particle.x, particle.y);
          ctx.lineTo(other.x, other.y);
          ctx.strokeStyle = light
            ? `rgba(8,127,109,${(1 - distance / 118) * .13})`
            : `rgba(105,231,204,${(1 - distance / 118) * .15})`;
          ctx.lineWidth = .6;
          ctx.stroke();
        }
      }
    });
    frame = requestAnimationFrame(drawNetwork);
  }

  canvas.addEventListener('pointermove', event => {
    const rect = canvas.getBoundingClientRect();
    pointer = { x: event.clientX - rect.left, y: event.clientY - rect.top };
  });
  canvas.addEventListener('pointerleave', () => { pointer = { x: -9999, y: -9999 }; });
  resizeCanvas();
  if (!reducedMotion) drawNetwork(); else drawNetwork(), cancelAnimationFrame(frame);
  window.addEventListener('resize', resizeCanvas, { passive: true });
})();
