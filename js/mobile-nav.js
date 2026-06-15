// 移动端导航菜单切换
(function() {
  function initMobileNav() {
    var nav = document.getElementById('nav-links');
    if (!nav) return;

    var btn = document.getElementById('mobile-menu-btn');
    if (!btn) {
      // 如果按钮不存在，创建并插入
      btn = document.createElement('button');
      btn.id = 'mobile-menu-btn';
      btn.className = 'mobile-menu-btn';
      btn.innerHTML = '☰';
      btn.setAttribute('aria-label', '菜单');
      // 插入到 nav-links 之前
      nav.parentNode.insertBefore(btn, nav);
    }

    // 绑定点击事件（先移除可能存在的旧事件，避免重复）
    btn.replaceWith(btn.cloneNode(true));
    btn = document.getElementById('mobile-menu-btn');

    btn.addEventListener('click', function() {
      nav.classList.toggle('open');
      btn.innerHTML = nav.classList.contains('open') ? '✕' : '☰';
    });

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
