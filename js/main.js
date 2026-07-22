// ==================== 输入处理 ====================
window.addEventListener('keydown', e => {
    keys[e.key.toLowerCase()] = true;
    if (['arrowup','arrowdown','arrowleft','arrowright',' '].includes(e.key.toLowerCase())) {
        e.preventDefault();
    }
    if (e.key.toLowerCase() === 'p' && gameState === 'playing') {
        paused = !paused;
    }
});
window.addEventListener('keyup', e => {
    keys[e.key.toLowerCase()] = false;
});

// ==================== 初始化 ====================
window.onload = () => {
    canvas = document.getElementById('gameCanvas');
    ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = false;
    loadImages().then(() => {
        console.log('Images loaded');
    });
};
