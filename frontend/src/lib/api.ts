import { IntentRequest, IntentResponse, RouteRequest, RouteResponse } from './types';

const BASE = 'http://127.0.0.1:8000';
const TIMEOUT = 30_000; // 30s

async function fetchWithTimeout(url: string, options: RequestInit = {}, timeout = TIMEOUT) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  const merged = { ...options, signal: controller.signal } as RequestInit;

  try {
    const res = await fetch(url, merged);
    clearTimeout(id);
    if (!res.ok) {
      let detail = undefined;
      try { detail = await res.json(); } catch (e) { /* ignore */ }
      const err = new Error(detail?.detail || res.statusText || 'Request failed');
      // @ts-ignore
      err.status = res.status;
      // @ts-ignore
      err.detail = detail;
      throw err;
    }
    return res.json();
  } catch (err) {
    clearTimeout(id);
    throw err;
  }
}

export async function classifyIntent(text: string, language: IntentRequest['language'], session_id: string = 'default') {
  return fetchWithTimeout(`${BASE}/intent/classify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, language, session_id }),
  });
}

export async function route(text: string, language: RouteRequest['language'], session_id: string = 'default', context?: RouteRequest['context']) {
  return fetchWithTimeout(`${BASE}/route`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, language, session_id, context }),
  });
}