export default function DashboardPage() {
  return (
    <div>
      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="card p-4">
          <div className="text-2xl font-bold text-primary-600">0</div>
          <div className="text-sm text-gray-600">CVs Generated</div>
        </div>
        <div className="card p-4">
          <div className="text-2xl font-bold text-primary-600">0</div>
          <div className="text-sm text-gray-600">Original CVs</div>
        </div>
        <div className="card p-4">
          <div className="text-2xl font-bold text-primary-600">0</div>
          <div className="text-sm text-gray-600">Job Postings</div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold mb-4">Get Started</h2>
        <div className="grid md:grid-cols-3 gap-4">
          <a href="/create" className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition text-center">
            <div className="text-2xl mb-2">📄</div>
            <div className="font-medium">Upload Your CV</div>
            <div className="text-sm text-gray-500">Upload your existing PDF resume</div>
          </a>
          <a href="/create" className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition text-center">
            <div className="text-2xl mb-2">🎯</div>
            <div className="font-medium">Add Job Posting</div>
            <div className="text-sm text-gray-500">Paste a URL or job description</div>
          </a>
          <a href="/create" className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition text-center">
            <div className="text-2xl mb-2">✨</div>
            <div className="font-medium">Generate CV</div>
            <div className="text-sm text-gray-500">Create your ATS-optimized resume</div>
          </a>
        </div>
      </div>

      {/* Recent CVs */}
      <div className="card p-6 mt-6">
        <h2 className="text-lg font-semibold mb-4">Recent Generated CVs</h2>
        <div className="text-center py-8 text-gray-400">
          No CVs generated yet. Click "Create New CV" to get started!
        </div>
      </div>
    </div>
  );
}
