// 姓名滚动: Canvas 2D 高速切换 + 减速 + 锁帧
// 暴露 window.PickMeFX.NameRoller
(function () {
  const NEON_COLORS = ['#00fff5', '#ff00ff', '#FFD700', '#ff0055', '#ffffff'];

  class NameRoller {
    constructor(canvas) {
      this.canvas = canvas;
      this.ctx = canvas.getContext('2d');
      this.names = [];        // 全部参与者姓名 (从外部灌入)
      this.display = [];      // 50 个槽位, 每帧显示的名字
      this.currentIndex = 0;
      this.lastSwitch = 0;
      this.interval = 50;     // ms, 原桌面版 roll_speed
      this.running = false;
      this.locked = false;    // 锁帧 (开奖时)
      this.lockName = '';
      this._resize();
      window.addEventListener('resize', () => this._resize());
    }

    setNames(names) {
      this.names = names.slice();
      // 初始化 50 个槽位
      this.display = [];
      for (let i = 0; i < 50; i++) {
        this.display.push(this._pickName());
      }
    }

    _pickName() {
      if (this.names.length === 0) return '—';
      return this.names[Math.floor(Math.random() * this.names.length)];
    }

    _resize() {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const rect = this.canvas.getBoundingClientRect();
      this.canvas.width  = rect.width  * dpr;
      this.canvas.height = rect.height * dpr;
      this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    start() {
      this.running = true;
      this.locked = false;
      this._loop = this._loop.bind(this);
      requestAnimationFrame(this._loop);
    }

    stop() { this.running = false; }

    lock(winnerName) {
      this.locked = true;
      this.lockName = winnerName;
      // 把 winnerName 放到所有槽位中央
      const mid = Math.floor(this.display.length / 2);
      this.display[mid] = winnerName;
    }

    _loop(ts) {
      if (!this.running) return;
      requestAnimationFrame(this._loop);
      this._render(ts);
    }

    _render(ts) {
      const ctx = this.ctx;
      const w = this.canvas.clientWidth;
      const h = this.canvas.clientHeight;
      ctx.clearRect(0, 0, w, h);

      const center = Math.floor(this.display.length / 2);

      if (!this.locked) {
        // 高速切换
        if (ts - this.lastSwitch >= this.interval) {
          this.display[center] = this._pickName();
          this.lastSwitch = ts;
        }
      }

      // 渲染所有名字 (中间最大, 两侧渐小)
      const baseSize = Math.min(w, h) * 0.10;
      for (let i = 0; i < this.display.length; i++) {
        const offset = i - center;
        if (offset === 0) continue;  // 中间另外画
        const dist = Math.abs(offset);
        const size = baseSize * Math.max(0.2, 1 - dist * 0.06);
        const alpha = Math.max(0, 1 - dist * 0.10);
        const y = h/2 + offset * baseSize * 0.7;
        ctx.font = `bold ${size}px "Microsoft YaHei", sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = NEON_COLORS[(i + this.currentIndex) % NEON_COLORS.length];
        ctx.globalAlpha = alpha * 0.5;
        ctx.fillText(this.display[i], w/2, y);
      }
      ctx.globalAlpha = 1;

      // 渲染中间 (锁帧时高亮)
      const name = this.locked ? this.lockName : this.display[center];
      const color = this.locked
        ? '#FFD700'
        : NEON_COLORS[this.currentIndex % NEON_COLORS.length];
      const scale = this.locked ? 1.4 + Math.sin(ts / 100) * 0.05 : 1.0;
      ctx.font = `bold ${baseSize * scale}px "Microsoft YaHei", sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      // 发光效果
      ctx.shadowColor = color;
      ctx.shadowBlur = this.locked ? 40 : 20;
      ctx.fillStyle = color;
      ctx.fillText(name, w/2, h/2);
      ctx.shadowBlur = 0;

      this.currentIndex++;
    }
  }

  window.PickMeFX = window.PickMeFX || {};
  window.PickMeFX.NameRoller = NameRoller;
})();
