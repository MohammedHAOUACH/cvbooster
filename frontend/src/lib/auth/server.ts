// Server-side auth utilities using cookies for JWT
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

const TOKEN_COOKIE = 'cvbooster_token';

export async function getToken(): Promise<string | null> {
  const cookieStore = await cookies();
  return cookieStore.get(TOKEN_COOKIE)?.value || null;
}

export function setTokenCookie(token: string): NextResponse {
  const response = NextResponse.next();
  response.cookies.set(TOKEN_COOKIE, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 7, // 7 days
    path: '/',
  });
  return response;
}

export function removeTokenCookie(): NextResponse {
  const response = NextResponse.next();
  response.cookies.set(TOKEN_COOKIE, '', {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: -1,
    path: '/',
  });
  return response;
}

export async function getSession(): Promise<{ user: any } | null> {
  const token = await getToken();
  if (!token) return null;

  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/auth/session`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: 'no-store',
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
