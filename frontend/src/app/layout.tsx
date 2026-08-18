import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CVBooster — AI-Powered Resume Optimization",
  description:
    "Upload your CV, paste a job posting, and get an ATS-optimized resume tailored to the position in seconds.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen bg-surface text-foreground font-body antialiased">
        <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-border">
          <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
            <a href="/" className="flex items-center gap-2 text-xl font-heading font-bold text-foreground group">
              <svg
                className="w-8 h-8 text-primary transition-transform group-hover:scale-105"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M6 3v12" />
                <path d="M18 9a3 3 0 1 0 0-6 3 3 0 0 0 0 6z" />
                <path d="M6 21a3 3 0 1 0 0-6 3 3 0 0 0 0 6z" />
                <path d="M18 9a9 9 0 0 1-9 9" />
                <path d="M6 21v-9a3 3 0 0 1 3-3" />
              </svg>
              <span>CVBooster</span>
            </a>
            <div className="flex items-center gap-3">
              <a href="/login" className="btn btn-ghost text-sm">
                Login
              </a>
              <a href="/dashboard" className="btn btn-primary text-sm">
                Get Started Free
              </a>
            </div>
          </div>
        </nav>
        <main className="min-h-[calc(100vh-80px)]">{children}</main>
        <footer className="bg-white border-t border-border px-6 py-8">
          <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-muted">
            <span>CVBooster &copy; {new Date().getFullYear()} — ATS-Optimized Resume Generator</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
