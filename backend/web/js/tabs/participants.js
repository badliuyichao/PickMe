// 参与者管理 tab
import { apiGet, apiPost, apiDel } from '../api.js';

const state = { participants: [] };
const pane = document.querySelector('.tab-pane[data-tab="participants"]');

pane.innerHTML = `
  <div class="participant-layout">
    <div class="card">
      <h3>添加单个参与者</h3>
      <div class="form-row">
        <label>姓名 <input id="p-name" type="text" placeholder="如：张三" maxlength="64" /></label>
        <label>部门 <input id="p-dept" type="text" placeholder="可选" maxlength="64" /></label>
      </div>
      <button id="p-add" class="btn-primary">+ 添加</button>
    </div>

    <div class="card">
      <h3>批量导入 <span class="muted">（每行一个姓名）</span></h3>
      <div class="form-row">
        <label style="flex:1">统一部门 <input id="p-batch-dept" type="text" placeholder="可选" maxlength="64" /></label>
      </div>
      <textarea id="p-batch-text" placeholder="张三&#10;李四&#10;王五&#10;..."></textarea>
      <div style="margin-top:10px; display:flex; gap:10px;">
        <button id="p-batch-add" class="btn-primary">批量导入</button>
        <label class="file-btn">
          <input id="p-file" type="file" accept=".txt" style="display:none" />
          <span>从 .txt 文件导入</span>
        </label>
        <button id="p-export" class="btn-save">导出为 .txt</button>
        <button id="p-clear" class="btn-del">清空</button>
      </div>
    </div>

    <div class="card">
      <h3>参与者列表 <span id="p-summary" class="muted"></span></h3>
      <table class="data-table">
        <thead><tr><th>#</th><th>姓名</th><th>部门</th><th>操作</th></tr></thead>
        <tbody id="p-tbody"></tbody>
      </table>
    </div>
  </div>
`;

function escapeHtml(s) {
  return String(s).replace(/[<>&"]/g, c => ({'<':'&lt;','>':'&gt;','&':'&amp;','"':'&quot;'}[c]));
}

function renderList() {
  const tbody = pane.querySelector('#p-tbody');
  pane.querySelector('#p-summary').textContent = `(共 ${state.participants.length} 人)`;
  if (state.participants.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" class="empty">暂无参与者</td></tr>';
    return;
  }
  tbody.innerHTML = state.participants.map(p => `
    <tr data-id="${p.id}">
      <td>${p.id}</td>
      <td>${escapeHtml(p.name)}</td>
      <td>${escapeHtml(p.department || '-')}</td>
      <td><button class="btn-del" data-id="${p.id}">删除</button></td>
    </tr>
  `).join('');
  tbody.querySelectorAll('.btn-del').forEach(b => {
    b.addEventListener('click', async () => {
      if (!confirm(`确认删除 ${b.closest('tr').children[1].textContent}？`)) return;
      try { await apiDel(`/api/participants/${b.dataset.id}`); await refresh(); }
      catch (e) { alert('删除失败: ' + e.message); }
    });
  });
}

pane.querySelector('#p-add').addEventListener('click', async () => {
  const name = pane.querySelector('#p-name').value.trim();
  const department = pane.querySelector('#p-dept').value.trim();
  if (!name) { alert('请输入姓名'); return; }
  try {
    await apiPost('/api/participants', { name, department });
    pane.querySelector('#p-name').value = '';
    pane.querySelector('#p-dept').value = '';
    await refresh();
  } catch (e) { alert('添加失败: ' + e.message); }
});

pane.querySelector('#p-batch-add').addEventListener('click', async () => {
  const text = pane.querySelector('#p-batch-text').value;
  const department = pane.querySelector('#p-batch-dept').value.trim();
  if (!text.trim()) { alert('请输入姓名列表'); return; }
  try {
    const r = await apiPost('/api/participants/batch', { text, department });
    pane.querySelector('#p-batch-text').value = '';
    pane.querySelector('#p-batch-dept').value = '';
    await refresh();
    alert(`已导入 ${r.added} 人`);
  } catch (e) { alert('批量导入失败: ' + e.message); }
});

pane.querySelector('#p-file').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const text = await file.text();
  const department = pane.querySelector('#p-batch-dept').value.trim();
  try {
    const r = await apiPost('/api/participants/batch', { text, department });
    alert(`从文件导入 ${r.added} 人`);
    await refresh();
  } catch (err) { alert('文件导入失败: ' + err.message); }
  e.target.value = '';
});

pane.querySelector('#p-export').addEventListener('click', () => {
  if (state.participants.length === 0) { alert('暂无参与者'); return; }
  const text = state.participants.map(p => p.name).join('\n');
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'participants.txt'; a.click();
  URL.revokeObjectURL(url);
});

pane.querySelector('#p-clear').addEventListener('click', async () => {
  if (!confirm('确认清空所有参与者？此操作不可恢复')) return;
  try { await apiDel('/api/participants'); await refresh(); }
  catch (e) { alert('清空失败: ' + e.message); }
});

export async function refresh() {
  try {
    state.participants = await apiGet('/api/participants');
    renderList();
  } catch (e) {
    console.error('[participants] refresh failed:', e);
  }
}
