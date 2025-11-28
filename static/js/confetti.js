/**
 * World-Class Confetti Animation
 */

window.createConfetti = function(x, y) {
    const colors = [
        '#667eea', '#764ba2', '#f093fb', '#2af598',
        '#009efd', '#fa709a', '#fee140', '#30cfd0'
    ];

    const confettiCount = 50;
    const container = document.createElement('div');
    container.style.position = 'fixed';
    container.style.top = '0';
    container.style.left = '0';
    container.style.width = '100%';
    container.style.height = '100%';
    container.style.pointerEvents = 'none';
    container.style.zIndex = '10000';
    document.body.appendChild(container);

    for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        const color = colors[Math.floor(Math.random() * colors.length)];
        const size = Math.random() * 10 + 5;

        confetti.style.position = 'absolute';
        confetti.style.left = x + 'px';
        confetti.style.top = y + 'px';
        confetti.style.width = size + 'px';
        confetti.style.height = size + 'px';
        confetti.style.backgroundColor = color;
        confetti.style.borderRadius = Math.random() > 0.5 ? '50%' : '0';
        confetti.style.opacity = '1';
        confetti.style.transform = 'scale(0)';

        container.appendChild(confetti);

        const angle = (Math.random() * Math.PI * 2);
        const velocity = Math.random() * 200 + 100;
        const rotation = Math.random() * 720 - 360;

        const tx = Math.cos(angle) * velocity;
        const ty = Math.sin(angle) * velocity + Math.random() * 100;

        confetti.animate([
            {
                transform: 'translate(0, 0) scale(0) rotate(0deg)',
                opacity: 1
            },
            {
                transform: `translate(${tx}px, ${ty}px) scale(1) rotate(${rotation}deg)`,
                opacity: 1,
                offset: 0.7
            },
            {
                transform: `translate(${tx}px, ${ty + 200}px) scale(0) rotate(${rotation * 2}deg)`,
                opacity: 0
            }
        ], {
            duration: 1500 + Math.random() * 500,
            easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
        }).onfinish = () => {
            confetti.remove();
        };
    }

    setTimeout(() => {
        container.remove();
    }, 3000);
};

// Add sparkle effect
window.createSparkles = function(element) {
    const rect = element.getBoundingClientRect();
    const x = rect.left + rect.width / 2;
    const y = rect.top + rect.height / 2;

    for (let i = 0; i < 20; i++) {
        const sparkle = document.createElement('div');
        sparkle.style.position = 'fixed';
        sparkle.style.left = x + 'px';
        sparkle.style.top = y + 'px';
        sparkle.style.width = '4px';
        sparkle.style.height = '4px';
        sparkle.style.backgroundColor = '#fff';
        sparkle.style.borderRadius = '50%';
        sparkle.style.pointerEvents = 'none';
        sparkle.style.zIndex = '9999';
        sparkle.style.boxShadow = '0 0 10px rgba(255, 255, 255, 0.8)';

        document.body.appendChild(sparkle);

        const angle = (Math.PI * 2 / 20) * i;
        const distance = 50 + Math.random() * 30;
        const tx = Math.cos(angle) * distance;
        const ty = Math.sin(angle) * distance;

        sparkle.animate([
            {
                transform: 'translate(0, 0) scale(0)',
                opacity: 1
            },
            {
                transform: `translate(${tx}px, ${ty}px) scale(1)`,
                opacity: 1,
                offset: 0.5
            },
            {
                transform: `translate(${tx * 1.5}px, ${ty * 1.5}px) scale(0)`,
                opacity: 0
            }
        ], {
            duration: 800,
            easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
        }).onfinish = () => {
            sparkle.remove();
        };
    }
};
