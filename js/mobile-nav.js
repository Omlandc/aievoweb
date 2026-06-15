// 移动端导航菜单切换
(function() {
  function initMobileNav() {
    var nav = document.getElementById('nav-links');
    if (!nav) return;

    // 检查是否已有按钮
    if (document.getElementById('mobile-menu-btn')) return;

    var btn = document.createElement('button');
    btn.id = 'mobile-menu-btn';
    btn.className = 'mobile-menu-btn';
    btn.innerHTML = '☰';
    btn.setAttribute('aria-label', '菜单');
    btn.addEventListener('click', function() {
      nav.classList.toggle('open');
      btn.innerHTML = nav.classList.contains('open') ? '✕' : '☰';
    });

    // 插入到 nav-links 之前
    nav.parentNode.insertBefore(btn, nav);

    // 点击菜单项后自动关闭
    nav.querySelectorAll('a').forEach(function(link) {
      link.addEventListener('click', function() {
        nav.classList.remove('open');
        btn.innerHTML = '☰';
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMobileNav);
  } else {
    initMobileNav();
  }
})();
