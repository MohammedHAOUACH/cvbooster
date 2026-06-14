export default function HomePage() {
  return (
    <div className="max-w-6xl mx-auto px-6 py-16">
      {/* Hero */}
      <section className="text-center py-16">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Boost Your Resume. Beat the ATS.
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Upload your CV, paste a job posting, and get an ATS-optimized resume
          tailored to the position — in seconds.
        </p>
        <div className="flex gap-4 justify-center">
          <a href="/login" className="btn btn-primary px-8 py-3 text-base">
            Get Started Free
          </a>
          <a href="#features" className="btn btn-outline px-8 py-3 text-base">
            Learn More
          </a>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-16">
        <h2 className="text-2xl font-bold text-center mb-12">How It Works</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="card p-6 text-center">
            <div className="text-3xl mb-4">📄</div>
            <h3 className="font-semibold text-lg mb-2">1. Upload Your CV</h3>
            <p className="text-gray-600">
              Upload your existing PDF resume. Our parser extracts all your experience, skills, and education.
            </p>
          </div>
          <div className="card p-6 text-center">
            <div className="text-3xl mb-4">🎯</div>
            <h3 className="font-semibold text-lg mb-2">2. Add Job Posting</h3>
            <p className="text-gray-600">
              Paste the job URL or text. We scrape the listing to identify key skills and requirements.
            </p>
          </div>
          <div className="card p-6 text-center">
            <div className="text-3xl mb-4">✨</div>
            <h3 className="font-semibold text-lg mb-2">3. Get Your CV</h3>
            <p className="text-gray-600">
              AI rewrites your resume to match the job. Choose from 8 ATS-friendly templates and download.
            </p>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16 bg-white rounded-2xl">
        <div className="grid md:grid-cols-3 gap-8 text-center">
          <div>
            <div className="text-3xl font-bold text-primary-600">8</div>
            <div className="text-gray-600">ATS-Friendly Templates</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-primary-600">95%</div>
            <div className="text-gray-600">Average ATS Score</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-primary-600">&lt;30s</div>
            <div className="text-gray-600">Generation Time</div>
          </div>
        </div>
      </section>
    </div>
  );
}
