import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CVBooster - ATS-Optimized Resume Generator",
  description: "Create ATS-friendly resumes tailored to any job posting",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">
        <nav className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="max-w-6xl mx-auto flex items-center justify-between">
            <a href="/" className="text-xl font-bold text-primary-600">CVBooster</a>
            <div className="flex items-center gap-4">
              <a href="/login" className="btn btn-outline text-sm">Login</a>
              <a href="/dashboard" className="btn btn-primary text-sm">Get Started</a>
            </div>
          </div>
        </nav>
        <main className="min-h-[calc(100vh-80px)]">
          {children}
        </main>
        <footer className="bg-white border-t border-gray-200 px-6 py-6 text-center text-sm text-gray-500">
          CVBooster &copy; 2025 - ATS-Optimized Resume Generator
        </footer>
      </body>
    </html>
  );
}
