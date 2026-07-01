// =============================================
//  21ST ACADEMY — CAREER MAPPING WORKSHOP
//  main.js — Navbar, Scroll, Video, Reveals
// =============================================

document.addEventListener('DOMContentLoaded', () => {

  // ---- NAVBAR SCROLL ----
  const navbar = document.getElementById('navbar');
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 60);
  });

  // ---- HAMBURGER MENU ----
  const hamburger = document.getElementById('hamburger');
  const navLinks = document.querySelector('.nav-links');
  hamburger?.addEventListener('click', () => {
    navLinks.classList.toggle('open');
  });

  // Close menu on link click
  document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', () => navLinks.classList.remove('open'));
  });

  // ---- VIDEO SECTION ----
  const videoPlaceholder = document.getElementById('videoPlaceholder');
  const videoEmbed = document.getElementById('videoEmbed');
  const playBtn = document.getElementById('playBtn');

  if (videoPlaceholder) {
    videoPlaceholder.addEventListener('click', () => {
      videoPlaceholder.classList.add('hidden');
      videoEmbed.classList.remove('hidden');
    });
  }

  // ---- SCROLL REVEAL ----
  const revealEls = document.querySelectorAll(
    '.gain-card, .benefit-item, .stat, .poster-card, .form-card, .register-left, .video-wrapper'
  );

  revealEls.forEach(el => el.classList.add('reveal'));

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  revealEls.forEach(el => observer.observe(el));

  // ---- POSTER DOWNLOAD ----
  window.downloadPoster = function(num) {
    // Creates a simple download trigger — in production, link to actual image files
    const canvas = document.createElement('canvas');
    canvas.width = 800;
    canvas.height = 1100;
    const ctx = canvas.getContext('2d');

    const configs = {
      1: {
        bg1: '#111111', bg2: '#2d0f0f', bg3: '#9B1C1C',
        title: 'CAREER\nMAPPING\nWORKSHOP',
        sub: 'The Right Move Changes The Game.'
      },
      2: {
        bg1: '#9B1C1C', bg2: '#3d0808', bg3: '#111111',
        title: 'YOUR CAREER.\nYOUR MOVE.',
        sub: '27 June 2026 · 9:30 AM · Poonamalle, Chennai'
      },
      3: {
        bg1: '#1a1a1a', bg2: '#7A1515', bg3: '#C0392B',
        title: 'FREE\nWORKSHOP',
        sub: 'Career Mapping · Assessment · Mentorship'
      }
    };

    const c = configs[num];
    const grad = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    grad.addColorStop(0, c.bg1);
    grad.addColorStop(0.5, c.bg2);
    grad.addColorStop(1, c.bg3);
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Chess pattern
    ctx.fillStyle = 'rgba(255,255,255,0.025)';
    for (let x = 0; x < canvas.width; x += 80) {
      for (let y = 0; y < canvas.height; y += 80) {
        if ((Math.floor(x / 80) + Math.floor(y / 80)) % 2 === 0) {
          ctx.fillRect(x, y, 80, 80);
        }
      }
    }

    // Logo
    ctx.fillStyle = '#C0392B';
    ctx.font = 'bold 48px Arial';
    ctx.fillText('21st ACADEMY', 60, 90);

    // Title
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 96px Arial';
    const lines = c.title.split('\n');
    lines.forEach((line, i) => {
      ctx.fillText(line, 60, 280 + (i * 110));
    });

    // Subtitle
    ctx.fillStyle = 'rgba(255,255,255,0.7)';
    ctx.font = '28px Arial';
    ctx.fillText(c.sub, 60, 280 + (lines.length * 110) + 60);

    // Date bar
    ctx.fillStyle = 'rgba(155,28,28,0.6)';
    ctx.fillRect(0, canvas.height - 160, canvas.width, 160);
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 36px Arial';
    ctx.fillText('27th June 2026  ·  Poonamalle, Chennai', 60, canvas.height - 90);
    ctx.font = '24px Arial';
    ctx.fillStyle = 'rgba(255,255,255,0.6)';
    ctx.fillText('admin@21stacademy.in  ·  +91 99 44 74 7090', 60, canvas.height - 45);

    canvas.toBlob(blob => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `21stAcademy-CareerWorkshop-Poster-${num}.png`;
      a.click();
      URL.revokeObjectURL(url);
    });
  };

  // ---- SMOOTH SCROLL OFFSET FOR FIXED NAV ----
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        e.preventDefault();
        const offset = 80;
        const top = target.getBoundingClientRect().top + window.scrollY - offset;
        window.scrollTo({ top, behavior: 'smooth' });
      }
    });
  });

});
