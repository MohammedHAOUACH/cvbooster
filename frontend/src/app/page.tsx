import {
  FileText,
  Target,
  Sparkles,
  BarChart3,
  ShieldCheck,
  Clock,
  ChevronRight,
  ArrowRight,
  CheckCircle2,
  Briefcase,
  GraduationCap,
  Zap,
} from "lucide-react";

export default function HomePage() {
  return (
    <div className="overflow-hidden">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-b from-primary-50 via-white to-white">
        <div className="max-w-6xl mx-auto px-6 py-24 lg:py-32 text-center">
          <div className="inline-flex items-center gap-2 bg-primary-50 text-primary text-sm font-medium px-4 py-2 rounded-full mb-8 animate-fade-in">
            <Sparkles className="w-4 h-4" />
            AI-Powered Resume Optimization
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-heading font-bold text-foreground leading-tight tracking-tight max-w-4xl mx-auto mb-6">
            Beat the ATS. Land{" "}
            <span className="text-gradient">More Interviews.</span>
          </h1>

          <p className="text-lg sm:text-xl text-muted max-w-2xl mx-auto mb-10 leading-relaxed">
            Upload your CV, paste a job posting, and get an ATS-optimized resume
            tailored to the position — in seconds, not hours.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <a
              href="/dashboard"
              className="btn btn-primary px-8 py-4 text-base flex items-center gap-2 group"
            >
              Get Started Free
              <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
            </a>
            <a
              href="#how-it-works"
              className="btn btn-outline px-8 py-4 text-base"
            >
              See How It Works
            </a>
          </div>

          {/* Trust badges */}
          <div className="mt-12 flex flex-wrap items-center justify-center gap-6 text-sm text-muted">
            <span className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-success" />
              No credit card required
            </span>
            <span className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-success" />
              Free forever plan
            </span>
            <span className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-success" />
              ATS-optimized output
            </span>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-surface border-y border-border">
        <div className="max-w-6xl mx-auto px-6 py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-3xl lg:text-4xl font-heading font-bold text-primary mb-1">
                70K+
              </div>
              <div className="text-sm text-muted">Resumes Optimized</div>
            </div>
            <div>
              <div className="text-3xl lg:text-4xl font-heading font-bold text-primary mb-1">
                95%
              </div>
              <div className="text-sm text-muted">Avg. ATS Score</div>
            </div>
            <div>
              <div className="text-3xl lg:text-4xl font-heading font-bold text-primary mb-1">
                8
              </div>
              <div className="text-sm text-muted">Professional Templates</div>
            </div>
            <div>
              <div className="text-3xl lg:text-4xl font-heading font-bold text-primary mb-1">
                &lt;30s
              </div>
              <div className="text-sm text-muted">Generation Time</div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-24 lg:py-32">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <span className="text-sm font-medium text-primary uppercase tracking-wider">
              How It Works
            </span>
            <h2 className="text-3xl lg:text-4xl font-heading font-bold text-foreground mt-3 mb-4">
              Three Steps to Your Perfect Resume
            </h2>
            <p className="text-lg text-muted max-w-2xl mx-auto">
              Our AI analyzes your experience and the job requirements to create
              a perfectly matched resume every time.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <div className="card p-8 text-center group hover:shadow-elevated transition-all duration-300">
              <div className="w-14 h-14 rounded-xl bg-primary-100 text-primary flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                <FileText className="w-7 h-7" />
              </div>
              <div className="text-sm font-medium text-primary mb-2">
                Step 1
              </div>
              <h3 className="text-xl font-heading font-semibold text-foreground mb-3">
                Upload Your CV
              </h3>
              <p className="text-muted leading-relaxed">
                Upload your existing PDF resume. Our parser extracts all your
                experience, skills, and education automatically.
              </p>
            </div>

            {/* Step 2 */}
            <div className="card p-8 text-center group hover:shadow-elevated transition-all duration-300">
              <div className="w-14 h-14 rounded-xl bg-primary-100 text-primary flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                <Target className="w-7 h-7" />
              </div>
              <div className="text-sm font-medium text-primary mb-2">
                Step 2
              </div>
              <h3 className="text-xl font-heading font-semibold text-foreground mb-3">
                Add Job Posting
              </h3>
              <p className="text-muted leading-relaxed">
                Paste the job URL or description. We scrape the listing to
                identify key skills and requirements.
              </p>
            </div>

            {/* Step 3 */}
            <div className="card p-8 text-center group hover:shadow-elevated transition-all duration-300">
              <div className="w-14 h-14 rounded-xl bg-primary-100 text-primary flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                <Sparkles className="w-7 h-7" />
              </div>
              <div className="text-sm font-medium text-primary mb-2">
                Step 3
              </div>
              <h3 className="text-xl font-heading font-semibold text-foreground mb-3">
                Get Your CV
              </h3>
              <p className="text-muted leading-relaxed">
                AI rewrites your resume to match the job. Choose from 8 ATS-friendly
                templates and download your optimized PDF.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="bg-surface border-y border-border py-24 lg:py-32">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <span className="text-sm font-medium text-primary uppercase tracking-wider">
              Why CVBooster
            </span>
            <h2 className="text-3xl lg:text-4xl font-heading font-bold text-foreground mt-3 mb-4">
              Built for Job Seekers, Not HR Software
            </h2>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: <BarChart3 className="w-6 h-6" />,
                title: "ATS Score Analysis",
                desc: "Get a real-time ATS compatibility score with keyword matching insights before you apply.",
              },
              {
                icon: <ShieldCheck className="w-6 h-6" />,
                title: "ATS-Optimized Format",
                desc: "Every template is designed to pass through ATS systems without formatting issues.",
              },
              {
                icon: <Clock className="w-6 h-6" />,
                title: "Under 30 Seconds",
                desc: "Generate a tailored resume faster than you can write a cover letter.",
              },
              {
                icon: <Briefcase className="w-6 h-6" />,
                title: "Job-Matched Keywords",
                desc: "AI identifies and integrates the exact keywords hiring managers are looking for.",
              },
              {
                icon: <GraduationCap className="w-6 h-6" />,
                title: "Smart Section Ordering",
                desc: "Automatically reorders your experience to highlight the most relevant information first.",
              },
              {
                icon: <Zap className="w-6 h-6" />,
                title: "One-Click Download",
                desc: "Export your optimized CV as a polished, print-ready PDF instantly.",
              },
            ].map((feature, i) => (
              <div key={i} className="card p-6 group hover:shadow-elevated transition-all duration-300">
                <div className="w-10 h-10 rounded-lg bg-primary-100 text-primary flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-heading font-semibold text-foreground mb-2">
                  {feature.title}
                </h3>
                <p className="text-muted leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials / Social Proof */}
      <section className="py-24 lg:py-32">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <span className="text-sm font-medium text-primary uppercase tracking-wider">
              Trusted by Job Seekers
            </span>
            <h2 className="text-3xl lg:text-4xl font-heading font-bold text-foreground mt-3 mb-4">
              What Our Users Say
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                quote:
                  "I went from 2 interviews per month to 8 after using CVBooster. The ATS optimization is incredible.",
                name: "Sarah M.",
                role: "Software Engineer",
              },
              {
                quote:
                  "The AI actually understood what skills to highlight for my target role. Saved me hours of manual editing.",
                name: "James K.",
                role: "Product Manager",
              },
              {
                quote:
                  "Finally a tool that doesn't just reformat — it genuinely improves how ATS systems read your resume.",
                name: "Priya R.",
                role: "Data Analyst",
              },
            ].map((testimonial, i) => (
              <div key={i} className="card p-6">
                <div className="flex items-center gap-1 mb-4">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <svg
                      key={star}
                      className="w-4 h-4 text-amber-400 fill-current"
                      viewBox="0 0 20 20"
                    >
                      <path d="M10 1l2.39 4.84 5.34.78-3.87 3.77.91 5.33L10 13.27l-4.77 2.51.91-5.33L2.27 6.69l5.34-.78L10 1z" />
                    </svg>
                  ))}
                </div>
                <p className="text-foreground leading-relaxed mb-6 italic">
                  "{testimonial.quote}"
                </p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary-100 text-primary flex items-center justify-center font-semibold text-sm">
                    {testimonial.name.charAt(0)}
                  </div>
                  <div>
                    <div className="font-medium text-foreground text-sm">
                      {testimonial.name}
                    </div>
                    <div className="text-muted text-xs">{testimonial.role}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-br from-primary-600 to-primary-700 py-24 lg:py-32">
        <div className="max-w-3xl mx-auto px-6 text-center">
          <h2 className="text-3xl lg:text-4xl font-heading font-bold text-white mb-4">
            Ready to Land Your Dream Job?
          </h2>
          <p className="text-lg text-white/80 mb-8 max-w-xl mx-auto">
            Join thousands of job seekers who use CVBooster to create resumes
            that actually get read by hiring managers.
          </p>
          <a
            href="/dashboard"
            className="btn btn-secondary px-8 py-4 text-base inline-flex items-center gap-2 group"
          >
            Start Free Now
            <ChevronRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
          </a>
        </div>
      </section>
    </div>
  );
}
