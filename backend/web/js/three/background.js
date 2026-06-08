// 背景粒子系统: 800 个缓慢漂浮的霓虹色粒子
// 暴露全局 window.PickMeFX.BackgroundScene
(function () {
  const THREE = window.THREE;
  if (!THREE) { console.error('[BackgroundScene] THREE not loaded'); return; }

  class BackgroundScene {
    constructor(canvas) {
      this.canvas = canvas;
      this.scene = new THREE.Scene();
      this.count = 800;
      this.colors = [0x00fff5, 0xff00ff, 0xffd700, 0xff0055];
      this._build();
      this._animate = this._animate.bind(this);
      requestAnimationFrame(this._animate);
    }

    _build() {
      const w = this.canvas.clientWidth || window.innerWidth;
      const h = this.canvas.clientHeight || window.innerHeight;
      this.camera = new THREE.OrthographicCamera(-w/2, w/2, h/2, -h/2, 0.1, 100);
      this.camera.position.z = 10;

      const geom = new THREE.BufferGeometry();
      const positions = new Float32Array(this.count * 3);
      const velocities = new Float32Array(this.count * 3);
      const colorArr = new Float32Array(this.count * 3);

      const w2 = w/2, h2 = h/2;
      for (let i = 0; i < this.count; i++) {
        positions[i*3+0] = (Math.random() - 0.5) * w;
        positions[i*3+1] = (Math.random() - 0.5) * h;
        positions[i*3+2] = 0;
        velocities[i*3+0] = (Math.random() - 0.5) * 0.3;
        velocities[i*3+1] = (Math.random() - 0.5) * 0.3;
        const c = new THREE.Color(this.colors[Math.floor(Math.random() * this.colors.length)]);
        colorArr[i*3+0] = c.r; colorArr[i*3+1] = c.g; colorArr[i*3+2] = c.b;
      }
      geom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      geom.setAttribute('color', new THREE.BufferAttribute(colorArr, 3));

      const mat = new THREE.PointsMaterial({
        size: 2.5,
        vertexColors: true,
        transparent: true,
        opacity: 0.7,
        sizeAttenuation: false,
        blending: THREE.AdditiveBlending,
        depthWrite: false,
      });
      this.points = new THREE.Points(geom, mat);
      this.scene.add(this.points);
      this._velocities = velocities;
      this._w = w; this._h = h;
    }

    resize(w, h) {
      this._w = w; this._h = h;
      this.camera.left = -w/2; this.camera.right = w/2;
      this.camera.top = h/2; this.camera.bottom = -h/2;
      this.camera.updateProjectionMatrix();
    }

    _animate() {
      requestAnimationFrame(this._animate);
      const pos = this.points.geometry.attributes.position.array;
      const vel = this._velocities;
      const w2 = this._w/2, h2 = this._h/2;
      for (let i = 0; i < this.count; i++) {
        pos[i*3+0] += vel[i*3+0];
        pos[i*3+1] += vel[i*3+1];
        if (pos[i*3+0] >  w2) pos[i*3+0] = -w2;
        if (pos[i*3+0] < -w2) pos[i*3+0] =  w2;
        if (pos[i*3+1] >  h2) pos[i*3+1] = -h2;
        if (pos[i*3+1] < -h2) pos[i*3+1] =  h2;
      }
      this.points.geometry.attributes.position.needsUpdate = true;
      this.renderer.render(this.scene, this.camera);
    }

    setRenderer(renderer) {
      this.renderer = renderer;
    }

    dispose() {
      this.points.geometry.dispose();
      this.points.material.dispose();
    }
  }

  window.PickMeFX = window.PickMeFX || {};
  window.PickMeFX.BackgroundScene = BackgroundScene;
})();
