"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";

interface User {
  id: string;
  email?: string;
  full_name?: string;
  avatar_url?: string;
  provider?: string;
}

export function useAuth() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const supabase = createClient();

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user) {
        setUser({
          id: session.user.id,
          email: session.user.email,
          full_name: session.user.user_metadata?.full_name,
          avatar_url: session.user.user_metadata?.avatar_url,
          provider: session.user.app_metadata?.provider,
        });
      }
      setLoading(false);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (_event, session) => {
      if (session?.user) {
        setUser({
          id: session.user.id,
          email: session.user.email,
          full_name: session.user.user_metadata?.full_name,
          avatar_url: session.user.user_metadata?.avatar_url,
          provider: session.user.app_metadata?.provider,
        });
      } else {
        setUser(null);
        router.push("/login");
      }
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, [router, supabase]);

  const signIn = useCallback(
    (provider: "google" | "facebook" | "tiktok") => {
      supabase.auth
        .signInWithOAuth({
          provider: provider as "google" | "facebook" | "github" | "apple" | "discord" | "figma" | "github" | "gitlab" | "google" | "twitter" | "twitch" | "workos",
          options: {
            redirectTo: `${window.location.origin}/auth/callback`,
          },
        })
        .catch((err) => setError(err.message));
    },
    [supabase]
  );

  const signOut = useCallback(async () => {
    await supabase.auth.signOut();
    router.push("/login");
  }, [supabase, router]);

  return { user, loading, error, signIn, signOut };
}

export function useAuthToken(): string | null {
  const [token, setToken] = useState<string | null>(null);
  const supabase = createClient();

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setToken(session?.access_token || null);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setToken(session?.access_token || null);
    });

    return () => subscription.unsubscribe();
  }, [supabase]);

  return token;
}
