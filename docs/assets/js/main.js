// main.js - 红色末日生存游戏官网交互

class RedStarSurvival {
    constructor() {
        this.init();
    }

    init() {
        this.createStarfield();
        this.createMeteorShower();
        this.setupEventListeners();
        this.startPulseAnimation();
        this.setupScrollEffects();
    }

    // 创建星空背景
    createStarfield() {
        const starfield = document.querySelector('.starfield');
        const starCount = 150;

        for (let i = 0; i < starCount; i++) {
            const star = document.createElement('div');
            star.className = 'star';
            
            // 随机星体属性
            const size = Math.random() * 3 + 1;
            const posX = Math.random() * 100;
            const posY = Math.random() * 100;
            const duration = Math.random() * 5 + 2;
            const delay = Math.random() * 5;
            
            // 随机星体类型（红色、橙色、白色）
            const starTypes = ['red', 'orange', ''];
            const starType = starTypes[Math.floor(Math.random() * starTypes.length)];
            if (starType) star.classList.add(starType);
            
            star.style.cssText = `
                width: ${size}px;
                height: ${size}px;
                left: ${posX}%;
                top: ${posY}%;
                animation-duration: ${duration}s;
                animation-delay: ${delay}s;
            `;
            
            starfield.appendChild(star);
        }
    }

    // 创建陨石雨效果
    createMeteorShower() {
        setInterval(() => {
            this.createMeteor();
        }, 500);
    }

    createMeteor() {
        const meteor = document.createElement('div');
        meteor.className = 'meteor';
        
        const startX = Math.random() * 100;
        const duration = Math.random() * 3 + 2;
        const size = Math.random() * 3 + 1;
        
        meteor.style.cssText = `
            left: ${startX}%;
            width: ${size}px;
            height: ${size * 20}px;
            animation-duration: ${duration}s;
            opacity: ${Math.random() * 0.5 + 0.5};
        `;
        
        document.body.appendChild(meteor);
        
        // 动画结束后移除元素
        setTimeout(() => {
            meteor.remove();
        }, duration * 1000);
    }

    // 脉冲动画效果
    startPulseAnimation() {
        const elements = document.querySelectorAll('.pulse-glow');
        
        setInterval(() => {
            elements.forEach(element => {
                element.style.setProperty('--pulse-glow', 
                    `hsl(${Math.random() * 20 + 0}, 100%, 50%)`);
            });
        }, 2000);
    }

    // 设置事件监听器
    setupEventListeners() {
        // 下载按钮点击效果
        const downloadButtons = document.querySelectorAll('.download-btn');
        downloadButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                this.animateButtonClick(e.target);
                this.showDownloadToast();
            });
        });

        // 鼠标移动视差效果
        document.addEventListener('mousemove', (e) => {
            this.handleParallax(e);
        });

        // 滚动动画
        window.addEventListener('scroll', () => {
            this.handleScrollAnimation();
        });
    }

    // 按钮点击动画
    animateButtonClick(button) {
        button.style.transform = 'scale(0.95)';
        setTimeout(() => {
            button.style.transform = 'scale(1)';
        }, 150);
    }

    // 显示下载提示
    showDownloadToast() {
        const toast = document.createElement('div');
        toast.textContent = '🚀 开始生存挑战！';
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(45deg, var(--star-red), var(--star-orange));
            color: white;
            padding: 15px 25px;
            border-radius: 25px;
            font-family: 'Orbitron', sans-serif;
            font-weight: bold;
            z-index: 1000;
            animation: slideInRight 0.5s ease;
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.5s ease';
            setTimeout(() => toast.remove(), 500);
        }, 3000);
    }

    // 鼠标视差效果
    handleParallax(e) {
        const moveX = (e.clientX - window.innerWidth / 2) * 0.01;
        const moveY = (e.clientY - window.innerHeight / 2) * 0.01;
        
        document.querySelector('.hero').style.transform = 
            `translate(${moveX}px, ${moveY}px)`;
    }

    // 滚动动画
    handleScrollAnimation() {
        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.5;
        
        document.querySelector('.starfield').style.transform = 
            `translateY(${rate}px)`;
    }

    // 设置滚动效果
    setupScrollEffects() {
        // 使用 Intersection Observer 实现滚动动画
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animation = 
                        `fadeInUp 0.6s ease forwards`;
                }
            });
        }, { threshold: 0.1 });

        // 观察所有需要动画的元素
        document.querySelectorAll('.feature-card, .timeline-item').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            observer.observe(el);
        });
    }
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    @keyframes fadeInUp {
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(style);

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new RedStarSurvival();
});

// 添加性能监控
window.addEventListener('load', () => {
    console.log('🚀 红色末日生存游戏官网已加载完成');
    
    // 预加载重要资源
    this.preloadResources();
});

// 资源预加载
function preloadResources() {
    const images = [
        '/assets/images/screenshots/gameplay1.jpg',
        '/assets/images/screenshots/gameplay2.jpg',
        '/assets/images/backgrounds/red-star.jpg'
    ];
    
    images.forEach(src => {
        const img = new Image();
        img.src = src;
    });
}

// 添加键盘快捷键
document.addEventListener('keydown', (e) => {
    // Ctrl + D 快速下载
    if (e.ctrlKey && e.key === 'd') {
        e.preventDefault();
        document.querySelector('.download-btn').click();
    }
    
    // ESC 键显示紧急信息
    if (e.key === 'Escape') {
        showEmergencyAlert();
    }
});

function showEmergencyAlert() {
    const alert = document.createElement('div');
    alert.innerHTML = `
        <div style="
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(255, 42, 42, 0.95);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            z-index: 10000;
            border: 3px solid var(--star-orange);
            backdrop-filter: blur(10px);
        ">
            <h3>🚨 紧急警报</h3>
            <p>红色陨石雨接近中！立即进入避难所！</p>
            <button onclick="this.parentElement.remove()" style="
                background: white;
                color: var(--star-red);
                border: none;
                padding: 10px 20px;
                border-radius: 20px;
                margin-top: 15px;
                cursor: pointer;
                font-weight: bold;
            ">确认</button>
        </div>
    `;
    document.body.appendChild(alert);
}