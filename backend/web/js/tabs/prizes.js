// 奖项设置 tab
import { apiGet, apiPost, apiPut, apiDel } from '../api.js';

const state = { prizes: [], colors: [] };

const pane = document.querySelector('.tab-pane[data-tab="prizes"]');

pane.innerHTML = `
  <div class="prize-layout">
    <div class="prize-form card">
      <h3>添加奖项</h3>
      <div class="form-row">
        <label>名称 <input id="prize-name" type="text" placeholder="如：特等奖" maxlength="64" /></label>
        <label>人数 <input id="prize-count" type="number" min="1" max="10000" value="1" /></label>
      </div>
      <div class="form-row">
        <label>颜色</label>
        <div id="color-picker" class="color-picker"></div>
      </div>
      <button id="prize-add" class="btn-primary">+ 添加</button>
    </div>

    <div class="prize-list card">
      <h3>奖项列表 <span id="prize-summary" class="muted"></span></h3>
      <table class="data-table">
        <thead>
          <tr><th>名称</th><th>名额</th><th>已抽</th><th>颜色</th><th>操作</th></tr>
        </thead>
        <tbody id="prize-tbody"></tbody>
      </table>
    </div>
  </div>
`;

// 渲染调色板
function renderColors(selected) {
  const picker = pane.querySelector('#color-picker');
  picker.innerHTML = '';
  state.colors.forEach((c) => {
    const sw = document.createElement('div');
    sw.className = 'color-swatch' + (c === selected ? ' selected' : '');
    sw.style.background = c;
    sw.dataset.color = c;
    sw.title = c;
    sw.addEventListener('click', () => {
      pane.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('selected'));
      sw.classList.add('selected');
    });
    picker.appendChild(sw);
  });
  // 默认选中第一项
  if (!pane.querySelector('.color-swatch.selected') && state.colors.length) {
    pane.querySelector('.color-swatch').classList.add('selected');
  }
}

// 渲染列表
function renderList() {
  const tbody = pane.querySelector('#prize-tbody');
  if (state.prizes.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" class="empty">暂无奖项</td></tr>';
    pane.querySelector('#prize-summary').textContent = '';
    return;
  }
  const totalCount = state.prizes.reduce((s, p) => s + p.count, 0);
  const totalDrawn = state.prizes.reduce((s, p) => s + p.drawn, 0);
  pane.querySelector('#prize-summary').textContent = `(共 ${state.prizes.length} 项, 累计 ${totalDrawn}/${totalCount})`;

  tbody.innerHTML = state.prizes.map(p => `
    <tr data-id="${p.id}">
      <td><span class="prize-name" style="color:${p.color}">●</span> ${escapeHtml(p.name)}</td>
      <td>
        <input class="count-edit" type="number" min="1" value="${p.count}" data-orig="${p.count}" />
      </td>
      <td>${p.drawn} / ${p.count}</td>
      <td><span class="color-dot" style="background:${p.color}"></span> <code>${p.color}</code></td>
      <td>
        <button class="btn-save" data-id="${p.id}">保存</button>
        <button class="btn-del" data-id="${p.id}">删除</button>
      </td>
    </tr>
  `).join('');

  tbody.querySelectorAll('.btn-save').forEach(b => {
    b.addEventListener('click', async () => {
      const id = Number(b.dataset.id);
      const tr = b.closest('tr');
      const count = Number(tr.querySelector('.count-edit').value);
      try {
        await apiPut(`/api/prizes/${id}`, { count });
        await refresh();
      } catch (e) { alert('保存失败: ' + e.message); }
    });
  });
  tbody.querySelectorAll('.btn-del').forEach(b => {
    b.addEventListener('click', async () => {
      if (!confirm('确认删除该奖项？')) return;
      try {
        await apiDel(`/api/prizes/${b.dataset.id}`);
        await refresh();
      } catch (e) { alert('删除失败: ' + e.message); }
    });
  });
}

function escapeHtml(s) {
  return String(s).replace(/[<>&"]/g, c => ({'<':'&lt;','>':'&gt;','&':'&amp;','"':'&quot;'}[c]));
}

pane.querySelector('#prize-add').addEventListener('click', async () => {
  const name = pane.querySelector('#prize-name').value.trim();
  const count = Number(pane.querySelector('#prize-count').value);
  const color = pane.querySelector('.color-swatch.selected')?.dataset.color || state.colors[0];
  if (!name) { alert('请输入奖项名称'); return; }
  if (!(count >= 1)) { alert('人数必须 ≥ 1'); return; }
  try {
    await apiPost('/api/prizes', { name, count, color });
    pane.querySelector('#prize-name').value = '';
    pane.querySelector('#prize-count').value = '1';
    await refresh();
  } catch (e) { alert('添加失败: ' + e.message); }
});

export async function refresh() {
  try {
    const [prizes, defaults] = await Promise.all([
      apiGet('/api/prizes'),
      state.colors.length ? Promise.resolve({ colors: state.colors }) : apiGet('/api/prizes/defaults'),
    ]);
    state.prizes = prizes;
    state.colors = defaults.colors;
    renderColors('#FFD700');
    renderList();
  } catch (e) {
    console.error('[prizes] refresh failed:', e);
  }
}
