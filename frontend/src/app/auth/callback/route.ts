import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const url = new URL(request.url);
  const code = url.searchParams.get("code");
  const next = url.searchParams.get("next") || "/dashboard";

  if (code) {
    try {
      // Call backend to exchange code for token
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${backendUrl}/api/auth/google/callback?code=${code}`, {
        redirect: "manual",
      });

      if (res.ok) {
        const data = await res.json();
        const token = data.access_token;

        // Set token in cookie and redirect
        const response = NextResponse.redirect(new URL(next, request.url));
        response.cookies.set("cvbooster_token", token, {
          httpOnly: true,
          secure: process.env.NODE_ENV === "production",
          sameSite: "lax",
          maxAge: 60 * 60 * 24 * 7, // 7 days
          path: "/",
        });
        return response;
      }
    } catch (err) {
      console.error("Auth callback error:", err);
    }
  }

  return NextResponse.redirect(new URL("/login?error=auth_failed", request.url));
}
