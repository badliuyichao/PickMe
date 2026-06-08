// 中奖名单 tab
import { apiGet, apiDel } from '../api.js';
import { connectSSE } from '../sse.js';

const state = { results: [], prizes: [] };
const pane = document.querySelector('.tab-pane[data-tab="results"]');

pane.innerHTML = `
  <div class="card">
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <h3 style="border:none; padding:0; margin:0;">中奖名单 <span id="r-summary" class="muted"></span></h3>
      <div style="display:flex; gap:10px;">
        <button id="r-export" class="btn-save">导出为 .txt</button>
        <button id="r-clear" class="btn-del">清空</button>
      </div>
    </div>
    <div id="r-body" style="margin-top:14px;"></div>
  </div>
`;

function escapeHtml(s) {
  return String(s).replace(/[<>&"]/g, c => ({'<':'&lt;','>':'&gt;','&':'&amp;','"':'&quot;'}[c]));
}

function renderList() {
  const body = pane.querySelector('#r-body');
  pane.querySelector('#r-summary').textContent = `(共 ${state.results.length} 条)`;
  if (state.results.length === 0) {
    body.innerHTML = '<p class="muted" style="text-align:center; padding:30px;">尚无中奖记录</p>';
    return;
  }

  // 按奖项分组
  const groups = new Map();
  for (const r of state.results) {
    if (!groups.has(r.prize_id)) groups.set(r.prize_id, []);
    groups.get(r.prize_id).push(r);
  }

  body.innerHTML = [...groups.entries()].map(([pid, rs]) => {
    const prize = state.prizes.find(p => p.id === pid);
    const color = prize?.color || '#FFD700';
    const name = prize?.name || rs[0].prize_name;
    return `
      <div class="results-prize-group" style="--prize-color:${color}">
        <div class="results-prize-header">
          <span>${escapeHtml(name)}</span>
          <span class="muted">${rs.length} 人</span>
        </div>
        <ul class="results-winner-list">
          ${rs.map(r => `<li>${escapeHtml(r.winner_name)}<time>${r.timestamp}</time></li>`).join('')}
        </ul>
      </div>
    `;
  }).join('');
}

pane.querySelector('#r-export').addEventListener('click', () => {
  if (state.results.length === 0) { alert('暂无数据'); return; }
  const lines = state.results.map(r => `${r.prize_name}: ${r.winner_name} (${r.timestamp})`);
  const blob = new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'results.txt'; a.click();
  URL.revokeObjectURL(url);
});

pane.querySelector('#r-clear').addEventListener('click', async () => {
  if (!confirm('确认清空所有中奖记录？此操作不可恢复')) return;
  try { await apiDel('/api/results'); await refresh(); }
  catch (e) { alert('清空失败: ' + e.message); }
});

let es = null;
function setupSSE() {
  if (es) return;
  es = connectSSE({
    draw_completed: () => refresh(),
    reset: () => refresh(),
  });
}

export async function refresh() {
  try {
    const [results, prizes] = await Promise.all([
      apiGet('/api/results'),
      apiGet('/api/prizes'),
    ]);
    state.results = results;
    state.prizes = prizes;
    renderList();
    setupSSE();
  } catch (e) {
    console.error('[results] refresh failed:', e);
  }
}
