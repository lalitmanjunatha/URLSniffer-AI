import { supabase } from '../supabase';

const apiUrl = import.meta.env.VITE_API_URL;

export async function request<T = unknown>(
  endpoint: string,
  body?: Record<string, unknown>,
  opts: { method?: 'GET' | 'POST' | 'DELETE' } = {}
): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  const session = await supabase.auth.getSession();
  const access_token = session.data.session?.access_token;
  if (access_token) {
    headers.Authorization = `Bearer ${access_token}`;
  }

  const res = await fetch(`${apiUrl}${endpoint}`, {
    method: opts.method ?? (body ? 'POST' : 'GET'),
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const message =
      errorData.error?.message ||
      errorData.message ||
      `HTTP error! status: ${res.status}`;
    const err: any = new Error(message);
    err.status = res.status;
    throw err;
  }

  // Handle empty response (e.g., 204 No Content)
  if (res.status === 204) {
    return {} as T;
  }

  return res.json();
}