// SSE 客户端连接

export function connectSSE(handlers) {
  const es = new EventSource('/api/stream');

  // 默认事件: connected
  es.addEventListener('connected', (e) => {
    console.log('[SSE] connected');
  });

  // 业务事件
  for (const [name, fn] of Object.entries(handlers || {})) {
    es.addEventListener(name, (e) => {
      try {
        const data = JSON.parse(e.data);
        fn(data);
      } catch (err) {
        console.error(`[SSE] parse ${name} failed:`, err, e.data);
      }
    });
  }

  es.onerror = (e) => {
    // EventSource 自带重连, 这里只打日志
    console.warn('[SSE] connection error, browser will auto-reconnect', e);
  };

  return es;
}
