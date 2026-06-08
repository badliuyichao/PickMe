// FX 主控: 启动 Three.js 场景, 提供 spawnFirework() API 给 lottery tab
(function () {
  const THREE = window.THREE;
  if (!THREE) {
    console.error('[FX] THREE not loaded');
    return;
  }

  function start() {
    const canvas = document.getElementById('fx-canvas');
    if (!canvas) return;

    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(0x000000, 0);

    const bg = new window.PickMeFX.BackgroundScene(canvas);
    bg.setRenderer(renderer);
    bg.resize(window.innerWidth, window.innerHeight);

    const fw = new window.PickMeFX.FireworkSystem(bg.scene);

    function loop() {
      requestAnimationFrame(loop);
      fw.update();
      renderer.render(bg.scene, bg.camera);
    }
    loop();

    window.addEventListener('resize', () => {
      renderer.setSize(window.innerWidth, window.innerHeight);
      bg.resize(window.innerWidth, window.innerHeight);
    });

    // 暴露给业务
    window.PickMeFX.spawnFirework = (x, y, color) => {
      // 在画布坐标 -> NDC -> 场景坐标
      const w = window.innerWidth, h = window.innerHeight;
      const sx = (x / w) * w - w/2;   // = x - w/2
      const sy = h/2 - (y / h) * h;   // = h/2 - y
      fw.spawn(sx, sy, new THREE.Color(color).getHex());
    };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
