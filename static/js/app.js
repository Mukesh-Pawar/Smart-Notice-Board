document.addEventListener('DOMContentLoaded', () => {
  const sidebar = document.getElementById('sidebar');
  const toggle = document.getElementById('menuToggle');
  const backdrop = document.getElementById('sidebarBackdrop');
  const closeMenu = () => { if (sidebar) sidebar.classList.remove('open'); if (backdrop) backdrop.classList.remove('show'); };
  if (toggle && sidebar) toggle.addEventListener('click', () => { sidebar.classList.toggle('open'); if (backdrop) backdrop.classList.toggle('show'); });
  if (backdrop) backdrop.addEventListener('click', closeMenu);
  document.querySelectorAll('.sidebar .nav-link').forEach((el) => el.addEventListener('click', closeMenu));
  document.querySelectorAll('[data-confirm]').forEach((el) => el.addEventListener('click', (event) => { if (!window.confirm(el.dataset.confirm)) event.preventDefault(); }));
});
