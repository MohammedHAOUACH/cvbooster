"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { getToken, getSession, removeToken } from "@/lib/auth/client";

interface User {
  id: string;
  email?: string;
  full_name?: string;
  avatar_url?: string;
  provider?: string;
}

const SKIP_AUTH = process.env.NEXT_PUBLIC_SKIP_AUTH === "true";
const AUTH_PROVIDER = process.env.NEXT_PUBLIC_AUTH_PROVIDER || "google";

export function useAuth() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (SKIP_AUTH) {
      setUser({
        id: "demo-user",
        email: "demo@cvbooster.local",
        full_name: "Demo User",
        avatar_url: undefined,
        provider: "demo",
      });
      setLoading(false);
      return;
    }

    const checkSession = async () => {
      const session = await getSession();
      if (session?.user) {
        setUser({
          id: session.user.id,
          email: session.user.email,
          full_name: session.user.full_name,
          avatar_url: session.user.avatar_url,
          provider: session.user.provider,
        });
      }
      setLoading(false);
    };

    checkSession();
  }, []);

  const signIn = useCallback(
    (provider: "google" | "facebook" = AUTH_PROVIDER as any) => {
      window.location.href = `/api/auth/${provider}`;
    },
    []
  );

  const signOut = useCallback(async () => {
    if (!SKIP_AUTH) {
      try {
        await fetch("/api/auth/logout", {
          method: "POST",
        });
      } catch (err) {
        console.error("Sign out error:", err);
      }
      removeToken();
    }
    setUser(null);
    router.push("/login");
  }, [router]);

  return { user, loading, error, signIn, signOut };
}

export function useAuthToken(): string | null {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    if (SKIP_AUTH) {
      setToken("demo-token");
      return;
    }

    const t = getToken();
    setToken(t);
  }, []);

  return token;
}
