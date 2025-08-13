// 主JavaScript文件
import './modules/intersection.js';
import './modules/theme.js';

// 全局功能
document.addEventListener('DOMContentLoaded', function() {
  // 过滤功能
  const filterButtons = document.querySelectorAll('.filter-button');
  if (filterButtons.length > 0) {
    filterButtons.forEach(button => {
      button.addEventListener('click', function() {
        filterButtons.forEach(btn => btn.classList.remove('active'));
        this.classList.add('active');
        // 这里可以添加实际的过滤逻辑
      });
    });
  }
  
  // 移动端菜单（如果需要）
  const menuToggle = document.createElement('button');
  menuToggle.innerHTML = '☰';
  menuToggle.classList.add('menu-toggle');
  
  const nav = document.querySelector('.nav-links');
  if (nav) {
    document.querySelector('.navbar').appendChild(menuToggle);
    
    menuToggle.addEventListener('click', function() {
      nav.classList.toggle('active');
    });
  }
});