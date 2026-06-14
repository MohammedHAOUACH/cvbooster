export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-gray-600">Manage your CVs and job applications</p>
        </div>
        <a href="/create" className="btn btn-primary">
          + Create New CV
        </a>
      </header>
      {children}
    </div>
  );
}
