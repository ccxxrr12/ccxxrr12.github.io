// 点赞功能实现
document.addEventListener('DOMContentLoaded', () => {
    const likeButtons = document.querySelectorAll('.like-btn');
    
    likeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const isLiked = this.classList.contains('liked');
            const countSpan = this.querySelector('span');
            let count = parseInt(countSpan.textContent);
            
            if (isLiked) {
                this.classList.remove('liked');
                countSpan.textContent = count - 1;
            } else {
                this.classList.add('liked');
                this.classList.add('like-animation');
                countSpan.textContent = count + 1;
                
                // 移除动画类以允许重复触发
                setTimeout(() => {
                    this.classList.remove('like-animation');
                }, 600);
            }
        });
    });
});