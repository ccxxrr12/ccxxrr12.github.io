// 主JavaScript文件
document.addEventListener('DOMContentLoaded', () => {
    // 页面加载动画效果
    const cards = document.querySelectorAll('.post-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.15}s`;
    });
    
    // 导航项点击效果
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            navItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // 创建新动态
    const newPostButton = document.querySelector('.new-post-button');
    newPostButton.addEventListener('click', () => {
        // 这里可以添加创建新动态的模态框逻辑
        alert('创建新动态功能需要后端支持，这里是前端UI演示');
    });
});

// 添加到全局样式的媒体查看器样式
const style = document.createElement('style');
style.textContent = `
.media-viewer {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.media-viewer-content {
    position: relative;
    max-width: 90%;
    max-height: 90%;
}

.media-viewer-content img {
    max-height: 90vh;
    max-width: 90vw;
    border-radius: 8px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
}

.close-viewer {
    position: absolute;
    top: 20px;
    right: 20px;
    width: 40px;
    height: 40px;
    background: rgba(255,255,255,0.15);
    border: none;
    border-radius: 50%;
    color: white;
    font-size: 24px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.close-viewer:hover {
    background: rgba(255,255,255,0.3);
    transform: rotate(90deg);
}
`;
document.head.appendChild(style);