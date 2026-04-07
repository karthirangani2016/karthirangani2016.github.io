// ─── Navbar scroll effect ──────────────────────────────
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 40);
  updateActiveLink();
});

// ─── Hamburger menu ────────────────────────────────────
const hamburger = document.getElementById('hamburger');
const navLinks = document.getElementById('navLinks');

hamburger.addEventListener('click', () => {
  navLinks.classList.toggle('open');
});

navLinks.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', () => navLinks.classList.remove('open'));
});

// ─── Active nav link on scroll ─────────────────────────
function updateActiveLink() {
  const sections = document.querySelectorAll('section[id]');
  const links = document.querySelectorAll('.nav-link');
  let current = '';

  sections.forEach(section => {
    if (window.scrollY >= section.offsetTop - 120) {
      current = section.getAttribute('id');
    }
  });

  links.forEach(link => {
    link.classList.remove('active');
    if (link.getAttribute('href') === `#${current}`) {
      link.classList.add('active');
    }
  });
}

// ─── Animated counters ─────────────────────────────────
function animateCounters() {
  document.querySelectorAll('.stat-number').forEach(el => {
    const target = parseInt(el.dataset.target);
    const duration = 1800;
    const step = target / (duration / 16);
    let current = 0;

    const timer = setInterval(() => {
      current += step;
      if (current >= target) {
        el.textContent = target;
        clearInterval(timer);
      } else {
        el.textContent = Math.floor(current);
      }
    }, 16);
  });
}

// ─── Intersection Observer (fade-in + counters) ────────
const observerOptions = { threshold: 0.15 };

const fadeObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      fadeObserver.unobserve(entry.target);
    }
  });
}, observerOptions);

const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      animateCounters();
      counterObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.5 });

document.addEventListener('DOMContentLoaded', () => {
  // Fade-in elements
  const animatables = [
    '.service-card',
    '.portfolio-card',
    '.testimonial-card',
    '.about-content',
    '.about-visual',
    '.section-header',
    '.contact-info',
    '.contact-form',
  ];

  animatables.forEach(selector => {
    document.querySelectorAll(selector).forEach((el, i) => {
      el.classList.add('fade-in');
      el.style.transitionDelay = `${i * 80}ms`;
      fadeObserver.observe(el);
    });
  });

  // Counter animation trigger
  const statsEl = document.querySelector('.hero-stats');
  if (statsEl) counterObserver.observe(statsEl);
});

// ─── Contact form ──────────────────────────────────────
const contactForm = document.getElementById('contactForm');
const formSuccess = document.getElementById('formSuccess');

contactForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const btn = contactForm.querySelector('button[type="submit"]');
  btn.disabled = true;
  btn.innerHTML = '<span>Sending...</span><i class="fa-solid fa-spinner fa-spin"></i>';

  setTimeout(() => {
    formSuccess.classList.add('show');
    contactForm.reset();
    btn.disabled = false;
    btn.innerHTML = '<span>Send Message</span><i class="fa-solid fa-paper-plane"></i>';
    setTimeout(() => formSuccess.classList.remove('show'), 5000);
  }, 1200);
});

// ─── Smooth scroll for anchor links ────────────────────
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', (e) => {
    const target = document.querySelector(anchor.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// ─── MIT License toggle ────────────────────────────────
const mitToggle = document.getElementById('mitToggle');
const mitSection = document.getElementById('mit');
const mitChevron = document.getElementById('mitChevron');

if (mitToggle) {
  mitToggle.addEventListener('click', () => {
    const isOpen = mitSection.classList.toggle('open');
    mitChevron.classList.toggle('open', isOpen);
  });
}
