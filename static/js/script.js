// 搜索功能
document.querySelector('.search-box button').addEventListener('click', function() {
    const searchTerm = document.querySelector('.search-box input').value;
    if (searchTerm.trim() !== '') {
        alert('搜索: ' + searchTerm);
        // 实际应用中这里应该是AJAX请求或页面跳转
    }
});

// 订阅表单提交
document.querySelector('.subscribe-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const email = this.querySelector('input').value;
    if (email.trim() !== '') {
        alert('感谢订阅! 我们将发送邮件到: ' + email);
        this.querySelector('input').value = '';
    }
});

// 暗色模式切换
const darkModeToggle = document.createElement('button');
darkModeToggle.innerHTML = '<i class="fas fa-moon"></i>';
darkModeToggle.classList.add('dark-mode-toggle');
darkModeToggle.style.position = 'fixed';
darkModeToggle.style.bottom = '20px';
darkModeToggle.style.right = '20px';
darkModeToggle.style.padding = '10px';
darkModeToggle.style.background = 'var(--dark-color)';
darkModeToggle.style.color = 'white';
darkModeToggle.style.border = 'none';
darkModeToggle.style.borderRadius = '50%';
darkModeToggle.style.cursor = 'pointer';
darkModeToggle.style.zIndex = '100';

document.body.appendChild(darkModeToggle);

darkModeToggle.addEventListener('click', function() {
    document.body.classList.toggle('dark-mode');
    if (document.body.classList.contains('dark-mode')) {
        localStorage.setItem('darkMode', 'enabled');
        this.innerHTML = '<i class="fas fa-sun"></i>';
    } else {
        localStorage.setItem('darkMode', 'disabled');
        this.innerHTML = '<i class="fas fa-moon"></i>';
    }
});

// 检查本地存储中的暗色模式设置
if (localStorage.getItem('darkMode') === 'enabled') {
    document.body.classList.add('dark-mode');
    darkModeToggle.innerHTML = '<i class="fas fa-sun"></i>';
}

// 暗色模式样式
const style = document.createElement('style');
style.textContent = `
    .dark-mode {
        --text-color: #f0f0f0;
        --light-color: #34495e;
        background-color: #2c3e50;
        color: var(--text-color);
    }
    
    .dark-mode .header,
    .dark-mode .article-card,
    .dark-mode .widget {
        background-color: #34495e;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.3);
    }
    
    .dark-mode .nav ul li a,
    .dark-mode .article-content h2 a {
        color: #f0f0f0;
    }
    
    .dark-mode .footer {
        background-color: #1a252f;
    }
`;
document.head.appendChild(style);