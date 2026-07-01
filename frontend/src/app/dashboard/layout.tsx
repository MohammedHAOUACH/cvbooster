"use client";

import { useAuth } from "@/hooks/use-auth";
import { LogOut, Plus, Sparkles } from "lucide-react";

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
      <header className="mb-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-heading font-bold text-foreground">
            Dashboard
            {user?.full_name && (
              <span className="text-base font-normal text-muted ml-2">
                — {user.full_name}
              </span>
            )}
          </h1>
          <p className="text-muted">Manage your CVs and job applications</p>
        </div>
        <div className="flex items-center gap-3">
          <a href="/create" className="btn btn-primary flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Create New CV
          </a>
          <button onClick={signOut} className="btn btn-ghost text-sm flex items-center gap-2">
            <LogOut className="w-4 h-4" />
            <span className="hidden sm:inline">Sign out</span>
          </button>
        </div>
      </header>
      {children}
    </div>
  );
}
