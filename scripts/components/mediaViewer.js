// 媒体查看器功能
document.addEventListener('DOMContentLoaded', () => {
    const mediaItems = document.querySelectorAll('.media-item');
    
    mediaItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.stopPropagation();
            
            const mediaUrl = this.style.backgroundImage
                .replace('url("', '')
                .replace('")', '');
            
            // 创建媒体查看器
            const viewer = document.createElement('div');
            viewer.classList.add('media-viewer');
            
            viewer.innerHTML = `
                <div class="media-viewer-content">
                    <img src="${mediaUrl}" alt="Full size media">
                    <button class="close-viewer">&times;</button>
                </div>
            `;
            
            document.body.appendChild(viewer);
            document.body.style.overflow = 'hidden';
            
            // 关闭查看器
            viewer.querySelector('.close-viewer').addEventListener('click', () => {
                viewer.remove();
                document.body.style.overflow = '';
            });
            
            // 点击背景关闭
            viewer.addEventListener('click', (e) => {
                if (e.target === viewer) {
                    viewer.remove();
                    document.body.style.overflow = '';
                }
            });
        });
    });
});