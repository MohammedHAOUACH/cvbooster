import { NextResponse, type NextRequest } from "next/server";

export async function middleware(request: NextRequest) {
  // When auth is skipped, allow all routes
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|api/).*)"],
};
