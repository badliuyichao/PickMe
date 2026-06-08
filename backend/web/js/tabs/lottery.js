// 抽奖 tab (完整版: 选奖项 -> 滚动抽奖 -> 烟花 + 锁帧)
import { apiGet, apiPost } from '../api.js';
import { connectSSE } from '../sse.js';

const state = {
  prizes: [],
  results: [],
  participants: [],     // 用于滚动
  currentPrizeId: null,
  rolling: false,
};

let roller = null;  // window.PickMeFX.NameRoller 实例

const pane = document.querySelector('.tab-pane[data-tab="lottery"]');

pane.innerHTML = `
  <div class="lottery-layout">
    <div class="card prize-selector">
      <h3>选择奖项</h3>
      <div id="lottery-prize-list" class="lottery-prize-list"></div>
    </div>

    <div class="card lottery-stage">
      <h3>抽奖</h3>
      <div class="lottery-stage-wrap">
        <canvas id="lottery-roller" class="lottery-roller"></canvas>
        <div id="lottery-overlay" class="lottery-overlay">
          <div class="lottery-placeholder">请先选择奖项</div>
        </div>
      </div>
      <div class="lottery-actions">
        <button id="lottery-draw" class="btn-primary btn-large" disabled>开始抽奖</button>
      </div>
    </div>

    <div class="card">
      <h3>本场中奖 <span id="lottery-count" class="muted"></span></h3>
      <ul id="lottery-results" class="lottery-results"></ul>
    </div>
  </div>
`;

function escapeHtml(s) {
  return String(s).replace(/[<>&"]/g, c => ({'<':'&lt;','>':'&gt;','&':'&amp;','"':'&quot;'}[c]));
}

function renderPrizeList() {
  const list = pane.querySelector('#lottery-prize-list');
  if (state.prizes.length === 0) {
    list.innerHTML = '<p class="muted">请先在「奖项设置」中添加奖项</p>';
    return;
  }
  list.innerHTML = state.prizes.map(p => {
    const done = p.drawn >= p.count;
    const active = state.currentPrizeId === p.id;
    return `
      <div class="lottery-prize-item ${active ? 'active' : ''} ${done ? 'done' : ''}"
           data-id="${p.id}" style="--prize-color:${p.color}">
        <span class="lottery-prize-dot"></span>
        <span class="lottery-prize-name">${escapeHtml(p.name)}</span>
        <span class="lottery-prize-progress">${p.drawn}/${p.count}</span>
      </div>
    `;
  }).join('');
  list.querySelectorAll('.lottery-prize-item').forEach(el => {
    el.addEventListener('click', () => {
      if (el.classList.contains('done')) return;
      state.currentPrizeId = Number(el.dataset.id);
      renderPrizeList();
      renderStage();
    });
  });
}

function renderStage() {
  const overlay = pane.querySelector('#lottery-overlay');
  const drawBtn = pane.querySelector('#lottery-draw');
  if (!state.currentPrizeId) {
    overlay.innerHTML = '<div class="lottery-placeholder">请先选择奖项</div>';
    overlay.style.opacity = '1';
    drawBtn.disabled = true;
    return;
  }
  const prize = state.prizes.find(p => p.id === state.currentPrizeId);
  if (!prize) return;
  const done = prize.drawn >= prize.count;
  drawBtn.disabled = done || state.rolling;
  drawBtn.textContent = done ? '该奖项已抽完' : `抽取 ${prize.name}`;
  overlay.innerHTML = `
    <div class="lottery-overlay-inner" style="color:${prize.color}">
      <div class="lottery-prize-title">${escapeHtml(prize.name)}</div>
      <div class="lottery-prize-sub">剩余 ${prize.count - prize.drawn} / ${prize.count}</div>
    </div>
  `;
}

function renderResults() {
  pane.querySelector('#lottery-count').textContent = `(本场 ${state.results.length} 条)`;
  const ul = pane.querySelector('#lottery-results');
  if (state.results.length === 0) {
    ul.innerHTML = '<li class="muted">尚无中奖记录</li>';
    return;
  }
  ul.innerHTML = state.results.slice(0, 50).map(r => `
    <li>
      <span class="lottery-result-prize">${escapeHtml(r.prize_name)}</span>
      <span class="lottery-result-name">${escapeHtml(r.winner_name)}</span>
      <span class="muted">${r.timestamp}</span>
    </li>
  `).join('');
}

async function startRoller() {
  if (!roller) {
    roller = new window.PickMeFX.NameRoller(pane.querySelector('#lottery-roller'));
  }
  roller.setNames(state.participants.map(p => p.name));
  roller.start();
}

pane.querySelector('#lottery-draw').addEventListener('click', async () => {
  if (state.rolling || !state.currentPrizeId) return;
  state.rolling = true;
  pane.querySelector('#lottery-draw').disabled = true;
  pane.querySelector('#lottery-overlay').style.opacity = '0.1';
  await startRoller();

  try {
    const out = await apiPost('/api/draw', { prize_id: state.currentPrizeId });
    // 滚动一段时间后锁帧
    await sleep(1200);
    roller.lock(out.result.winner_name);
    // 烟花
    const color = out.prize.color;
    for (let i = 0; i < 5; i++) {
      setTimeout(() => {
        const x = window.innerWidth  * (0.2 + Math.random() * 0.6);
        const y = window.innerHeight * (0.2 + Math.random() * 0.4);
        window.PickMeFX.spawnFirework?.(x, y, color);
      }, i * 200);
    }
    onDrawCompleted(out);
  } catch (e) {
    alert('抽奖失败: ' + e.message);
    pane.querySelector('#lottery-overlay').style.opacity = '1';
  } finally {
    state.rolling = false;
    pane.querySelector('#lottery-draw').disabled = false;
  }
});

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function onDrawCompleted(out) {
  const p = state.prizes.find(x => x.id === out.prize.id);
  if (p) p.drawn = out.prize.drawn;
  state.results.unshift(out.result);
  if (state.results.length > 50) state.results.length = 50;
  renderPrizeList();
  renderStage();
  renderResults();
}

let es = null;
function setupSSE() {
  if (es) return;
  es = connectSSE({
    draw_completed: (data) => {
      const p = state.prizes.find(x => x.id === data.prize.id);
      if (p) p.drawn = data.prize.drawn;
      state.results.unshift(data.result);
      if (state.results.length > 50) state.results.length = 50;
      renderPrizeList();
      renderResults();
      // 别人中奖时也给个烟花
      if (data.prize.id !== state.currentPrizeId) {
        const x = window.innerWidth  * 0.5;
        const y = window.innerHeight * 0.3;
        window.PickMeFX.spawnFirework?.(x, y, data.prize.color);
      }
    },
    reset: async () => { state.results = []; await refresh(); },
  });
}

export async function refresh() {
  try {
    const [prizes, results, participants] = await Promise.all([
      apiGet('/api/prizes'),
      apiGet('/api/results'),
      apiGet('/api/participants'),
    ]);
    state.prizes = prizes;
    state.results = results.slice(0, 50);
    state.participants = participants;
    if (state.currentPrizeId && !prizes.find(p => p.id === state.currentPrizeId)) {
      state.currentPrizeId = null;
    }
    renderPrizeList();
    renderStage();
    renderResults();
    if (state.participants.length > 0) await startRoller();
    setupSSE();
  } catch (e) {
    console.error('[lottery] refresh failed:', e);
  }
}
