// 主题切换功能
document.addEventListener('DOMContentLoaded', function() {
  const themeToggle = document.createElement('button');
  themeToggle.id = 'theme-toggle';
  themeToggle.innerHTML = '🌙';
  themeToggle.style.position = 'fixed';
  themeToggle.style.bottom = '20px';
  themeToggle.style.right = '20px';
  themeToggle.style.zIndex = '1000';
  themeToggle.style.background = 'rgba(255,255,255,0.8)';
  themeToggle.style.backdropFilter = 'blur(10px)';
  themeToggle.style.border = 'none';
  themeToggle.style.borderRadius = '50%';
  themeToggle.style.width = '50px';
  themeToggle.style.height = '50px';
  themeToggle.style.fontSize = '24px';
  themeToggle.style.cursor = 'pointer';
  themeToggle.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
  
  document.body.appendChild(themeToggle);
  
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'dark') {
    document.documentElement.classList.add('dark-mode');
    themeToggle.innerHTML = '☀️';
  }
  
  themeToggle.addEventListener('click', function() {
    document.documentElement.classList.toggle('dark-mode');
    
    if (document.documentElement.classList.contains('dark-mode')) {
      localStorage.setItem('theme', 'dark');
      themeToggle.innerHTML = '☀️';
    } else {
      localStorage.setItem('theme', 'light');
      themeToggle.innerHTML = '🌙';
    }
  });
});