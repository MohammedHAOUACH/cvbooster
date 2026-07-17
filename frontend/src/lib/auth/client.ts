// Client-side auth utilities using localStorage for JWT
const TOKEN_KEY = 'cvbooster_token';

export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(TOKEN_KEY, token);
}

export function removeToken(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(TOKEN_KEY);
}

export async function getSession(): Promise<{ user: any } | null> {
  const token = getToken();
  if (!token) return null;

  try {
    const res = await fetch('/api/auth/session', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (res.ok) {
      const data = await res.json();
      return data.user ? { user: data.user } : null;
    }
    return null;
  } catch {
    return null;
  }
}
