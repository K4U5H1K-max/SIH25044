export const API_BASE =
  ((import.meta as any).env && (import.meta as any).env.VITE_API_BASE) ||
  (typeof process !== 'undefined' ? (process as any).env?.VITE_API_BASE : undefined) ||
  'http://127.0.0.1:5000';

if (!/^https?:\/\//.test(API_BASE)) {
  console.warn('[api] VITE_API_BASE is not a full URL. Using default http://127.0.0.1:5000. Current:', API_BASE);
}

function makeUrl(path: string) {
  return `${API_BASE}${path.startsWith('/') ? path : `/${path}`}`;
}

export async function getJson<T>(path: string): Promise<T> {
  const url = makeUrl(path);
  console.log('[api] GET', url);
  const res = await fetch(url, { method: 'GET', credentials: 'include' });
  console.log('[api] status', res.status, res.statusText);
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  console.log('[api] response body:', data);
  if (!res.ok) throw new Error((data as any)?.error || `HTTP ${res.status}`);
  return data as T;
}

export async function postJson<T>(path: string, body: any): Promise<T> {
  const url = makeUrl(path);
  console.log('[api] POST', url, 'payload:', body);
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(body),
  });
  console.log('[api] status', res.status, res.statusText);
  const text = await res.text();
  let data: any = text ? JSON.parse(text) : null;
  console.log('[api] response body:', data);
  if (!res.ok) throw new Error(data?.error || `HTTP ${res.status}`);
  return data as T;
}
