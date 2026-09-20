// 轻量交互：根据滚动位置高亮当前栏目
(function () {
  const links = Array.from(document.querySelectorAll('.nav__links a'));
  const map = new Map();
  links.forEach((a) => {
    const id = a.getAttribute('href').slice(1);
    const el = document.getElementById(id);
    if (el) map.set(el, a);
  });

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          links.forEach((l) => l.style.color = '');
          const a = map.get(entry.target);
          if (a) a.style.color = 'var(--ink)';
        }
      });
    },
    { rootMargin: '-45% 0px -50% 0px' }
  );

  map.forEach((_, el) => observer.observe(el));
})();
