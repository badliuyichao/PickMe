// PickMe Web - 前端入口
// 负责 tab 切换 + 各模块懒加载 + 首次挂载时 refresh

const tabButtons = document.querySelectorAll('.tab-btn');
const tabPanes = document.querySelectorAll('.tab-pane');

// 各 tab 模块: dynamic import() 实现按需加载
const loaders = {
  prizes: () => import('./tabs/prizes.js'),
  participants: () => import('./tabs/participants.js'),
  lottery: () => import('./tabs/lottery.js'),
  results: () => import('./tabs/results.js'),
};

const loaded = new Set();

async function activateTab(name) {
  tabButtons.forEach(b => b.classList.toggle('active', b.dataset.tab === name));
  tabPanes.forEach(p => p.classList.toggle('hidden', p.dataset.tab !== name));

  if (loaders[name] && !loaded.has(name)) {
    try {
      const mod = await loaders[name]();
      loaded.add(name);
      if (typeof mod.refresh === 'function') await mod.refresh();
    } catch (e) {
      console.error(`[PickMe] load tab "${name}" failed:`, e);
    }
  } else if (loaded.has(name)) {
    // 二次切换到已加载 tab 时重新 refresh（数据可能被其他 tab 改了）
    const mod = await loaders[name]();
    if (typeof mod.refresh === 'function') await mod.refresh();
  }
}

tabButtons.forEach(btn => {
  btn.addEventListener('click', () => activateTab(btn.dataset.tab));
});

// 默认激活第一个 tab 并加载
activateTab('prizes');

console.log('[PickMe] 前端已加载');
