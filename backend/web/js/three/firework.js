// 烟花粒子系统: 50 槽位对象池, 每次 spawn() 复用, 60 帧生命周期
(function () {
  const THREE = window.THREE;
  if (!THREE) return;

  class FireworkSystem {
    constructor(scene, count = 50, particlesPerBurst = 60) {
      this.scene = scene;
      this.slots = [];  // {alive, particles[], frame, x, y, color, vx, vy}
      for (let i = 0; i < count; i++) {
        this.slots.push(this._buildSlot(particlesPerBurst));
        this.scene.add(this.slots[i].points);
      }
      this.PARTICLES_PER_BURST = particlesPerBurst;
      this.LIFETIME = 80;  // 帧
    }

    _buildSlot(n) {
      const geom = new THREE.BufferGeometry();
      const positions = new Float32Array(n * 3);
      const velocities = new Float32Array(n * 3);
      const colors = new Float32Array(n * 3);
      geom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      geom.setAttribute('color', new THREE.BufferAttribute(colors, 3));
      const mat = new THREE.PointsMaterial({
        size: 4,
        vertexColors: true,
        transparent: true,
        opacity: 1.0,
        sizeAttenuation: false,
        blending: THREE.AdditiveBlending,
        depthWrite: false,
      });
      const points = new THREE.Points(geom, mat);
      points.visible = false;
      return { points, positions, velocities, colors, n, alive: false, frame: 0, cx: 0, cy: 0 };
    }

    spawn(x, y, color) {
      // 找一个空闲槽位; 都没有就重置最早一个
      let slot = this.slots.find(s => !s.alive);
      if (!slot) {
        slot = this.slots[0];
        this.slots.push(this.slots.shift());  // 移到末尾, 优先用前面的
      }
      slot.alive = true;
      slot.frame = 0;
      slot.cx = x; slot.cy = y;
      const baseColor = new THREE.Color(color);
      for (let i = 0; i < slot.n; i++) {
        const angle = Math.random() * Math.PI * 2;
        const speed = 2 + Math.random() * 6;
        slot.positions[i*3+0] = x;
        slot.positions[i*3+1] = y;
        slot.positions[i*3+2] = 0;
        slot.velocities[i*3+0] = Math.cos(angle) * speed;
        slot.velocities[i*3+1] = Math.sin(angle) * speed;
        slot.velocities[i*3+2] = 0;
        // 颜色随机抖动
        const c = baseColor.clone().offsetHSL((Math.random()-0.5)*0.1, 0, (Math.random()-0.5)*0.2);
        slot.colors[i*3+0] = c.r; slot.colors[i*3+1] = c.g; slot.colors[i*3+2] = c.b;
      }
      slot.points.geometry.attributes.position.needsUpdate = true;
      slot.points.geometry.attributes.color.needsUpdate = true;
      slot.points.material.opacity = 1.0;
      slot.points.visible = true;
    }

    update() {
      for (const slot of this.slots) {
        if (!slot.alive) continue;
        slot.frame++;
        const t = slot.frame / this.LIFETIME;
        for (let i = 0; i < slot.n; i++) {
          slot.positions[i*3+0] += slot.velocities[i*3+0];
          slot.positions[i*3+1] += slot.velocities[i*3+1];
          slot.velocities[i*3+0] *= 0.96;  // 阻力
          slot.velocities[i*3+1] *= 0.96;
          slot.velocities[i*3+1] -= 0.08;  // 重力
        }
        slot.points.geometry.attributes.position.needsUpdate = true;
        slot.points.material.opacity = Math.max(0, 1 - t);
        if (slot.frame >= this.LIFETIME) {
          slot.alive = false;
          slot.points.visible = false;
        }
      }
    }
  }

  window.PickMeFX = window.PickMeFX || {};
  window.PickMeFX.FireworkSystem = FireworkSystem;
})();
