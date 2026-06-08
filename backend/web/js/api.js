// 轻量 fetch 封装，统一处理 JSON / 错误
async function api(method, url, body) {
  const opts = { method, headers: {} };
  if (body !== undefined) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(url, opts);
  if (!res.ok) {
    const txt = await res.text().catch(() => '');
    throw new Error(`${res.status} ${res.statusText}: ${txt}`);
  }
  return res.status === 204 ? null : res.json();
}

export const apiGet = (url) => api('GET', url);
export const apiPost = (url, body) => api('POST', url, body);
export const apiPut = (url, body) => api('PUT', url, body);
export const apiDel = (url) => api('DELETE', url);
