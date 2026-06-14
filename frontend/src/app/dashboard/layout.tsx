"use client";

import { useAuth } from "@/hooks/use-auth";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, loading, signOut } = useAuth();

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="animate-pulse h-8 w-48 bg-gray-200 rounded mb-8" />
        <div className="animate-pulse h-64 bg-gray-200 rounded" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">
            Dashboard
            {user?.full_name && (
              <span className="text-base font-normal text-gray-500 ml-2">
                — {user.full_name}
              </span>
            )}
          </h1>
          <p className="text-gray-600">Manage your CVs and job applications</p>
        </div>
        <div className="flex items-center gap-3">
          <a href="/create" className="btn btn-primary">
            + Create New CV
          </a>
          <button onClick={signOut} className="btn btn-ghost text-sm">
            Sign out
          </button>
        </div>
      </header>
      {children}
    </div>
  );
}
