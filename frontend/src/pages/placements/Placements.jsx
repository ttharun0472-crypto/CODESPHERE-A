import { useState, useEffect, useMemo } from "react";
import { Link } from "react-router-dom";
import {
  getPlacements,
  createPlacement,
  getPlacementRecommendations,
} from "../../services/placementApi";
import "./Placements.css";

const LOADING_STAGES = [
  "Analyzing your profile...",
  "Checking your skills...",
  "Comparing your resume...",
  "Matching companies...",
  "Preparing recommendations...",
];

const DEFAULT_JOBS = [
  {
    id: 201,
    company_name: "CloudSphere Systems",
    job_title: "Senior Full-Stack Engineer",
    location: "San Francisco, CA • Remote",
    job_type: "Full-time",
    salary: "$130,000 - $160,000 / yr",
    skills_required: "Python, FastAPI, React, PostgreSQL, Docker",
    description:
      "We are seeking a Senior Full-Stack Engineer to architect microservices and build user-centric dashboards. You will work closely with product teams to design scalable APIs and modern frontends.",
    application_url: "https://careers.example.com/fullstack-engineer",
  },
  {
    id: 202,
    company_name: "DataPulse AI",
    job_title: "Backend FastAPI Developer",
    location: "New York, NY • Hybrid",
    job_type: "Full-time",
    salary: "$120,000 - $145,000 / yr",
    skills_required: "Python, FastAPI, Redis, SQLAlchemy, AWS",
    description:
      "Join DataPulse AI to build high-throughput data processing endpoints. Responsible for API performance optimization, security, and cloud deployment pipelines.",
    application_url: "https://careers.example.com/backend-developer",
  },
  {
    id: 203,
    company_name: "NextGen Digital",
    job_title: "Frontend React Specialist",
    location: "Austin, TX • Remote",
    job_type: "Remote",
    salary: "$110,000 - $135,000 / yr",
    skills_required: "React.js, TypeScript, Tailwind CSS, Vite, Redux",
    description:
      "Looking for a passionate Frontend Engineer to craft sleek, responsive web applications with state-of-the-art UI/UX standards.",
    application_url: "https://careers.example.com/frontend-specialist",
  },
  {
    id: 204,
    company_name: "NeuralLabs AI",
    job_title: "AI Infrastructure Engineer",
    location: "Seattle, WA • On-site",
    job_type: "Full-time",
    salary: "$140,000 - $180,000 / yr",
    skills_required: "Python, PyTorch, Docker, Kubernetes, MLOps",
    description:
      "Build model inference pipelines and scalable GPU cluster workloads for generative AI enterprise solutions.",
    application_url: "https://careers.example.com/ai-engineer",
  },
  {
    id: 205,
    company_name: "Innovate Software",
    job_title: "Software Engineering Intern",
    location: "Remote",
    job_type: "Internship",
    salary: "$45 / hr",
    skills_required: "JavaScript, Python, Git, HTML/CSS",
    description:
      "Great opportunity for students and junior developers to gain hands-on experience building production features alongside senior mentors.",
    application_url: "https://careers.example.com/internship",
  },
];

function Placements() {
  // Navigation tabs: 'recommendations' | 'browse'
  const [activeTab, setActiveTab] = useState("recommendations");

  // AI Recommendation State
  const [aiData, setAiData] = useState(null);
  const [aiLoading, setAiLoading] = useState(true);
  const [loadingStageIdx, setLoadingStageIdx] = useState(0);
  const [aiError, setAiError] = useState("");
  const [selectedMatch, setSelectedMatch] = useState(null);

  // Job Board State (preserving existing feature)
  const [jobs, setJobs] = useState(DEFAULT_JOBS);
  const [jobsLoading, setJobsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [jobTypeFilter, setJobTypeFilter] = useState("All");
  const [selectedJob, setSelectedJob] = useState(null);
  const [showPostModal, setShowPostModal] = useState(false);
  const [submittingJob, setSubmittingJob] = useState(false);

  const [newJobForm, setNewJobForm] = useState({
    company_name: "",
    job_title: "",
    location: "",
    job_type: "Full-time",
    salary: "",
    skills_required: "",
    description: "",
    application_url: "",
  });

  // Saved / Bookmarked Job IDs
  const [savedJobIds, setSavedJobIds] = useState(() => {
    try {
      const saved = localStorage.getItem("codesphere_saved_jobs");
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  // Loading animation stages
  useEffect(() => {
    let interval;
    if (aiLoading) {
      setLoadingStageIdx(0);
      interval = setInterval(() => {
        setLoadingStageIdx((prev) => (prev < LOADING_STAGES.length - 1 ? prev + 1 : prev));
      }, 700);
    }
    return () => clearInterval(interval);
  }, [aiLoading]);

  // Initial Data Load
  useEffect(() => {
    loadAiRecommendations();
    loadPlacementsDirectory();
  }, []);

  const loadAiRecommendations = async () => {
    setAiLoading(true);
    setAiError("");
    try {
      const data = await getPlacementRecommendations();
      setAiData(data);
      if (data && data.recommendations && data.recommendations.length > 0) {
        setSelectedMatch(data.recommendations[0]);
      }
    } catch (err) {
      console.warn("AI Placement Recommendations error:", err);
      setAiError(err.message || "Failed to load placement recommendations. Please try again.");
    } finally {
      setAiLoading(false);
    }
  };

  const loadPlacementsDirectory = async () => {
    setJobsLoading(true);
    try {
      const data = await getPlacements();
      if (Array.isArray(data) && data.length > 0) {
        const combined = [...data, ...DEFAULT_JOBS.filter((dj) => !data.some((d) => d.id === dj.id))];
        setJobs(combined);
      }
    } catch {
      setJobs(DEFAULT_JOBS);
    } finally {
      setJobsLoading(false);
    }
  };

  const toggleSaveJob = (id) => {
    let updated;
    if (savedJobIds.includes(id)) {
      updated = savedJobIds.filter((item) => item !== id);
    } else {
      updated = [...savedJobIds, id];
    }
    setSavedJobIds(updated);
    localStorage.setItem("codesphere_saved_jobs", JSON.stringify(updated));
  };

  const handleCreateJob = async (e) => {
    e.preventDefault();
    setSubmittingJob(true);
    try {
      const created = await createPlacement(newJobForm);
      setJobs((prev) => [created, ...prev]);
      setShowPostModal(false);
      setNewJobForm({
        company_name: "",
        job_title: "",
        location: "",
        job_type: "Full-time",
        salary: "",
        skills_required: "",
        description: "",
        application_url: "",
      });
      // Refresh AI recommendations with new DB company
      loadAiRecommendations();
    } catch {
      const mockCreated = {
        ...newJobForm,
        id: Date.now(),
      };
      setJobs((prev) => [mockCreated, ...prev]);
      setShowPostModal(false);
    } finally {
      setSubmittingJob(false);
    }
  };

  const filteredJobs = useMemo(() => {
    return jobs.filter((job) => {
      const searchLower = searchTerm.toLowerCase();
      const matchesSearch =
        job.job_title?.toLowerCase().includes(searchLower) ||
        job.company_name?.toLowerCase().includes(searchLower) ||
        job.location?.toLowerCase().includes(searchLower) ||
        job.skills_required?.toLowerCase().includes(searchLower);

      if (!matchesSearch) return false;

      if (jobTypeFilter === "Saved") {
        return savedJobIds.includes(job.id);
      }

      if (jobTypeFilter !== "All") {
        return (
          job.job_type?.toLowerCase().includes(jobTypeFilter.toLowerCase()) ||
          job.location?.toLowerCase().includes(jobTypeFilter.toLowerCase())
        );
      }

      return true;
    });
  }, [jobs, searchTerm, jobTypeFilter, savedJobIds]);

  const getLogoStyle = (id) => {
    const styles = [
      "linear-gradient(135deg, #059669, #10b981)",
      "linear-gradient(135deg, #2563eb, #3b82f6)",
      "linear-gradient(135deg, #7c3aed, #8b5cf6)",
      "linear-gradient(135deg, #d97706, #f59e0b)",
      "linear-gradient(135deg, #0284c7, #38bdf8)",
    ];
    return styles[(id || 0) % styles.length];
  };

  const getMatchBadgeClass = (level) => {
    switch (level) {
      case "Strong Match":
        return "badge-match-strong";
      case "Good Match":
        return "badge-match-good";
      case "Partial Match":
        return "badge-match-partial";
      default:
        return "badge-match-low";
    }
  };

  const getChecklistIcon = (status) => {
    if (status === "Ready") return <span className="status-ico ready">✓ Ready</span>;
    if (status === "Needs Improvement") return <span className="status-ico needs">⚠ Needs Improvement</span>;
    return <span className="status-ico missing">✕ Missing</span>;
  };

  return (
    <div className="placements-page">
      <div className="placements-container">
        {/* Hero Section */}
        <header className="placements-hero">
          <div className="hero-info-area">
            <div className="hero-badge-row">
              <span className="hero-tag-badge">💼 PLACEMENT ASSISTANCE</span>
              <span className="ai-powered-pill">✨ AI POWERED</span>
            </div>
            <h1>
              Placement Assistance
              <br />
              <span className="hero-emerald-gradient">
                Discover Companies Matched to Your Skills & Career Goals.
              </span>
            </h1>
            <p>
              Smart recommendation engine analyzing your CodeSphere LMS achievements, project portfolio,
              and Resume Builder data to connect you with top technology employers.
            </p>
          </div>

          <div className="hero-quick-links">
            <Link to="/resume" className="btn-hero-link">
              📄 ATS Resume Builder
            </Link>
            <Link to="/interview" className="btn-hero-link">
              🎙️ Practice Interviews
            </Link>
            <button
              onClick={() => setShowPostModal(true)}
              className="btn-hero-link"
              style={{ background: "#059669", border: "1px solid #10b981", cursor: "pointer" }}
            >
              ➕ Post Job Opening
            </button>
          </div>
        </header>

        {/* View Switcher Tabs */}
        <div className="placement-tab-nav">
          <button
            className={`tab-toggle-btn ${activeTab === "recommendations" ? "active" : ""}`}
            onClick={() => setActiveTab("recommendations")}
          >
            🤖 AI Placement Recommendations
          </button>
          <button
            className={`tab-toggle-btn ${activeTab === "browse" ? "active" : ""}`}
            onClick={() => setActiveTab("browse")}
          >
            💼 Browse All Job Postings ({jobs.length})
          </button>
        </div>

        {/* ============================================================== */}
        {/* TAB 1: AI RECOMMENDATIONS ENGINE */}
        {/* ============================================================== */}
        {activeTab === "recommendations" && (
          <div className="ai-recommendations-wrapper">
            {/* Loading State with Stage Indicators */}
            {aiLoading && (
              <div className="ai-loading-container">
                <div className="loading-spinner-ring"></div>
                <h3 className="loading-stage-title">{LOADING_STAGES[loadingStageIdx]}</h3>
                <p className="loading-stage-subtitle">
                  Synthesizing your CodeSphere learning records, resume metrics, and company requirements...
                </p>
                <div className="loading-steps-dots">
                  {LOADING_STAGES.map((stage, idx) => (
                    <div
                      key={idx}
                      className={`loading-dot-item ${idx <= loadingStageIdx ? "active" : ""}`}
                    >
                      <span className="dot-circle"></span>
                      <span className="dot-label">{stage}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Error State Banner */}
            {!aiLoading && aiError && (
              <div className="ai-error-banner">
                <div className="error-icon">⚠️</div>
                <div className="error-body">
                  <h4>Unable to load placement recommendations</h4>
                  <p>{aiError}</p>
                </div>
                <button onClick={loadAiRecommendations} className="btn-retry">
                  🔄 Retry
                </button>
              </div>
            )}

            {!aiLoading && aiData && (
              <>
                {/* Resume Status Card */}
                <section className="resume-status-card">
                  {aiData.resume_status?.exists ? (
                    <div className="resume-ready-banner">
                      <div className="resume-status-left">
                        <div className="resume-status-icon ready">✓</div>
                        <div>
                          <div className="resume-status-heading">
                            <h3>Resume Ready ✓</h3>
                            <span className="resume-strength-tag">
                              Strength: {aiData.resume_status.strength}%
                            </span>
                          </div>
                          <p className="resume-status-sub">
                            Your CodeSphere ATS resume is integrated into company recommendations.
                          </p>
                          <div className="resume-stats-chips">
                            <span className="chip-metric">
                              🛠️ <strong>{aiData.resume_status.skills_detected}</strong> Skills Detected
                            </span>
                            <span className="chip-metric">
                              🚀 <strong>{aiData.resume_status.projects_detected}</strong> Projects Detected
                            </span>
                            <span className="chip-metric">
                              🏆 <strong>{aiData.resume_status.certifications_detected}</strong> Certifications
                            </span>
                          </div>
                        </div>
                      </div>
                      <Link to="/resume" className="btn-resume-action primary">
                        View Resume →
                      </Link>
                    </div>
                  ) : (
                    <div className="resume-missing-banner">
                      <div className="resume-status-left">
                        <div className="resume-status-icon missing">ℹ️</div>
                        <div>
                          <div className="resume-status-heading">
                            <h3>Resume Not Created</h3>
                            <span className="resume-alert-tag">Action Recommended</span>
                          </div>
                          <p className="resume-status-sub">
                            Create your CodeSphere resume to get more accurate placement recommendations.
                          </p>
                        </div>
                      </div>
                      <Link to="/resume" className="btn-resume-action create">
                        Build My Resume →
                      </Link>
                    </div>
                  )}
                </section>

                {/* Profile Readiness Section */}
                <section className="profile-readiness-panel">
                  <div className="readiness-panel-header">
                    <div>
                      <span className="section-eyebrow">STUDENT EVALUATION METRICS</span>
                      <h2>Overall Placement Readiness</h2>
                    </div>
                    <div className="overall-readiness-gauge">
                      <div className="gauge-num">{aiData.readiness?.overall || 0}%</div>
                      <div className="gauge-lbl">Readiness Score</div>
                    </div>
                  </div>

                  <div className="readiness-breakdown-grid">
                    <div className="metric-box">
                      <div className="metric-head">
                        <span>Technical Skills</span>
                        <strong className="metric-value">
                          {aiData.readiness?.breakdown?.technical_skills?.score ?? "Not available"}%
                        </strong>
                      </div>
                      <div className="metric-bar-bg">
                        <div
                          className="metric-bar-fill"
                          style={{
                            width: `${aiData.readiness?.breakdown?.technical_skills?.score || 0}%`,
                          }}
                        ></div>
                      </div>
                      <span className="metric-status-lbl">
                        {aiData.readiness?.breakdown?.technical_skills?.status || "Developing"}
                      </span>
                    </div>

                    <div className="metric-box">
                      <div className="metric-head">
                        <span>Learning Progress</span>
                        <strong className="metric-value">
                          {aiData.readiness?.breakdown?.learning_progress?.score ?? "Not available"}%
                        </strong>
                      </div>
                      <div className="metric-bar-bg">
                        <div
                          className="metric-bar-fill"
                          style={{
                            width: `${aiData.readiness?.breakdown?.learning_progress?.score || 0}%`,
                          }}
                        ></div>
                      </div>
                      <span className="metric-status-lbl">
                        {aiData.readiness?.breakdown?.learning_progress?.status || "In Progress"}
                      </span>
                    </div>

                    <div className="metric-box">
                      <div className="metric-head">
                        <span>Projects</span>
                        <strong className="metric-value">
                          {aiData.readiness?.breakdown?.projects?.score ?? "Not available"}%
                        </strong>
                      </div>
                      <div className="metric-bar-bg">
                        <div
                          className="metric-bar-fill"
                          style={{
                            width: `${aiData.readiness?.breakdown?.projects?.score || 0}%`,
                          }}
                        ></div>
                      </div>
                      <span className="metric-status-lbl">
                        {aiData.readiness?.breakdown?.projects?.status || "Developing"}
                      </span>
                    </div>

                    <div className="metric-box">
                      <div className="metric-head">
                        <span>Resume Strength</span>
                        <strong className="metric-value">
                          {aiData.readiness?.breakdown?.resume_strength?.score ?? "Not available"}%
                        </strong>
                      </div>
                      <div className="metric-bar-bg">
                        <div
                          className="metric-bar-fill"
                          style={{
                            width: `${aiData.readiness?.breakdown?.resume_strength?.score || 0}%`,
                          }}
                        ></div>
                      </div>
                      <span className="metric-status-lbl">
                        {aiData.readiness?.breakdown?.resume_strength?.status || "Not Created"}
                      </span>
                    </div>

                    <div className="metric-box">
                      <div className="metric-head">
                        <span>Communication</span>
                        <strong className="metric-value">
                          {aiData.readiness?.breakdown?.communication?.score ?? "Not available"}%
                        </strong>
                      </div>
                      <div className="metric-bar-bg">
                        <div
                          className="metric-bar-fill"
                          style={{
                            width: `${aiData.readiness?.breakdown?.communication?.score || 0}%`,
                          }}
                        ></div>
                      </div>
                      <span className="metric-status-lbl">
                        {aiData.readiness?.breakdown?.communication?.status || "Developing"}
                      </span>
                    </div>

                    <div className="metric-box">
                      <div className="metric-head">
                        <span>Interview Readiness</span>
                        <strong className="metric-value">
                          {aiData.readiness?.breakdown?.interview_readiness?.score ?? "Not available"}%
                        </strong>
                      </div>
                      <div className="metric-bar-bg">
                        <div
                          className="metric-bar-fill"
                          style={{
                            width: `${aiData.readiness?.breakdown?.interview_readiness?.score || 0}%`,
                          }}
                        ></div>
                      </div>
                      <span className="metric-status-lbl">
                        {aiData.readiness?.breakdown?.interview_readiness?.status || "Developing"}
                      </span>
                    </div>
                  </div>
                </section>

                {/* Top Company Matches */}
                <section className="top-matches-section">
                  <div className="section-title-row">
                    <div>
                      <span className="section-eyebrow">RANKED OPPORTUNITIES</span>
                      <h2>Top Company Matches</h2>
                      <p>
                        Algorithmic matching comparing your verified skills, resume projects, and course completions.
                      </p>
                    </div>
                    <span className="matches-count-badge">
                      {aiData.recommendations?.length || 0} Matches Found
                    </span>
                  </div>

                  <div className="ranked-companies-list">
                    {aiData.recommendations?.map((comp, idx) => (
                      <div key={comp.id || idx} className="ranked-company-card">
                        <div className="company-card-top">
                          <div className="company-brand-group">
                            <div className="rank-number-badge">#{idx + 1}</div>
                            <div
                              className="company-logo-badge"
                              style={{ background: getLogoStyle(comp.id) }}
                            >
                              {comp.company_name?.charAt(0)?.toUpperCase()}
                            </div>
                            <div>
                              <h3 className="company-title">{comp.job_title}</h3>
                              <div className="company-sub-meta">
                                🏢 <strong>{comp.company_name}</strong> • 📍 {comp.location} • 💼 {comp.job_type}
                              </div>
                            </div>
                          </div>

                          <div className="match-scores-group">
                            <span className={`match-level-pill ${getMatchBadgeClass(comp.match_level)}`}>
                              {comp.match_level}
                            </span>
                            <div className="pct-scores">
                              <span className="score-badge match">
                                <strong>{comp.match_percentage}%</strong> Match
                              </span>
                              <span className="score-badge ready">
                                <strong>{comp.readiness_percentage}%</strong> Ready
                              </span>
                            </div>
                          </div>
                        </div>

                        {/* Matched vs Missing Skills */}
                        <div className="skills-comparison-row">
                          <div className="skill-col">
                            <span className="col-label matched">
                              ✓ Matched Skills ({comp.matched_skills?.length || 0})
                            </span>
                            <div className="skills-chips-flow">
                              {comp.matched_skills?.length > 0 ? (
                                comp.matched_skills.map((skill, sIdx) => (
                                  <span key={sIdx} className="skill-chip matched">
                                    {skill}
                                  </span>
                                ))
                              ) : (
                                <span className="no-skills-msg">No direct skill overlap</span>
                              )}
                            </div>
                          </div>

                          <div className="skill-col">
                            <span className="col-label missing">
                              ✕ Missing Skills ({comp.missing_skills?.length || 0})
                            </span>
                            <div className="skills-chips-flow">
                              {comp.missing_skills?.length > 0 ? (
                                comp.missing_skills.map((skill, sIdx) => (
                                  <span key={sIdx} className="skill-chip missing">
                                    {skill}
                                  </span>
                                ))
                              ) : (
                                <span className="no-skills-msg success">Full skill alignment!</span>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Why This Company */}
                        <div className="why-company-box">
                          <span className="why-label">💡 Why Recommended:</span>
                          <p className="why-text">{comp.why_recommended}</p>
                        </div>

                        {/* Actions */}
                        <div className="company-card-foot">
                          <button
                            className="btn-company-details"
                            onClick={() => setSelectedMatch(comp)}
                          >
                            🔍 View Details & Readiness
                          </button>

                          <a
                            href={comp.application_url || "#"}
                            target="_blank"
                            rel="noreferrer"
                            className="btn-company-apply"
                          >
                            <span>Apply Now</span>
                            <span>↗</span>
                          </a>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>

                {/* Skill Gap Analysis Section */}
                <section className="skill-gap-section">
                  <div className="section-title-row">
                    <div>
                      <span className="section-eyebrow">CAREER ACCELERATION</span>
                      <h2>Skills You Need to Improve</h2>
                      <p>
                        Top missing skills across your targeted opportunities and direct links to CodeSphere LMS courses.
                      </p>
                    </div>
                  </div>

                  <div className="skill-gap-grid">
                    {aiData.skill_gap_analysis?.slice(0, 6).map((gap, idx) => (
                      <div key={idx} className="gap-card">
                        <div className="gap-card-head">
                          <h4 className="gap-skill-title">{gap.skill}</h4>
                          <span
                            className={`priority-pill ${
                              gap.priority === "High Priority" ? "high" : "med"
                            }`}
                          >
                            {gap.priority}
                          </span>
                        </div>

                        <p className="gap-companies-note">
                          Required by <strong>{gap.companies_requiring?.slice(0, 2).join(", ")}</strong>
                          {gap.companies_requiring?.length > 2 && ` and ${gap.companies_requiring.length - 2} more`}
                        </p>

                        {gap.recommended_course ? (
                          <div className="lms-course-recommendation">
                            <div className="rec-course-label">Recommended CodeSphere Course:</div>
                            <Link
                              to={`/learning/course/${gap.recommended_course.id}`}
                              className="lms-course-link"
                            >
                              📚 {gap.recommended_course.title} →
                            </Link>
                          </div>
                        ) : (
                          <div className="lms-course-recommendation null">
                            <span>No dedicated LMS course found. Recommended for portfolio projects.</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </section>

                {/* Preparation Recommendations */}
                <section className="prep-recommendations-section">
                  <div className="section-title-row">
                    <div>
                      <span className="section-eyebrow">ACTIONABLE NEXT STEPS</span>
                      <h2>Preparation Recommendations</h2>
                      <p>Prioritized action plan calculated from your current progress and target companies.</p>
                    </div>
                  </div>

                  <div className="prep-steps-grid">
                    {aiData.preparation_recommendations?.map((step) => (
                      <div key={step.priority} className="prep-step-card">
                        <div className="step-num-circle">P{step.priority}</div>
                        <div className="step-content">
                          <div className="step-cat">{step.category}</div>
                          <h4 className="step-title">{step.title}</h4>
                          <p className="step-desc">{step.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              </>
            )}
          </div>
        )}

        {/* ============================================================== */}
        {/* TAB 2: ALL PLACEMENT DRIVES & DIRECTORY (PRESERVED) */}
        {/* ============================================================== */}
        {activeTab === "browse" && (
          <div className="browse-directory-wrapper">
            {/* Metric Statistics Cards */}
            <section className="placements-stats-grid">
              <div className="plc-stat-card">
                <div className="plc-stat-icon icon-emerald">💼</div>
                <div>
                  <div className="plc-stat-num">{jobs.length}</div>
                  <div className="plc-stat-lbl">Active Openings</div>
                </div>
              </div>

              <div className="plc-stat-card">
                <div className="plc-stat-icon icon-blue">💰</div>
                <div>
                  <div className="plc-stat-num">$135k</div>
                  <div className="plc-stat-lbl">Avg Salary Offer</div>
                </div>
              </div>

              <div className="plc-stat-card">
                <div className="plc-stat-icon icon-amber">⭐</div>
                <div>
                  <div className="plc-stat-num">{savedJobIds.length}</div>
                  <div className="plc-stat-lbl">Saved Bookmarks</div>
                </div>
              </div>

              <div className="plc-stat-card">
                <div className="plc-stat-icon icon-purple">🏢</div>
                <div>
                  <div className="plc-stat-num">50+</div>
                  <div className="plc-stat-lbl">Hiring Partners</div>
                </div>
              </div>
            </section>

            {/* Toolbar Search & Job Filters */}
            <section className="placements-toolbar">
              <div className="search-input-box">
                <span className="plc-search-icon">🔍</span>
                <input
                  type="text"
                  placeholder="Search by job title, company name, skill, or location..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="plc-search-input"
                />
              </div>

              <div className="job-type-pills">
                <button
                  className={`pill-btn ${jobTypeFilter === "All" ? "active" : ""}`}
                  onClick={() => setJobTypeFilter("All")}
                >
                  All Jobs ({jobs.length})
                </button>
                <button
                  className={`pill-btn ${jobTypeFilter === "Full-time" ? "active" : ""}`}
                  onClick={() => setJobTypeFilter("Full-time")}
                >
                  Full-time
                </button>
                <button
                  className={`pill-btn ${jobTypeFilter === "Remote" ? "active" : ""}`}
                  onClick={() => setJobTypeFilter("Remote")}
                >
                  Remote
                </button>
                <button
                  className={`pill-btn ${jobTypeFilter === "Internship" ? "active" : ""}`}
                  onClick={() => setJobTypeFilter("Internship")}
                >
                  Internship
                </button>
                <button
                  className={`pill-btn ${jobTypeFilter === "Saved" ? "active" : ""}`}
                  onClick={() => setJobTypeFilter("Saved")}
                >
                  ⭐ Saved ({savedJobIds.length})
                </button>
              </div>
            </section>

            {/* Job Cards Display */}
            <section className="placements-jobs-grid">
              {filteredJobs.length === 0 ? (
                <div className="no-jobs-found-box">
                  <div style={{ fontSize: "36px", marginBottom: "12px" }}>📂</div>
                  <h3>No opportunities match your search</h3>
                  <p>Try adjusting your search terms or filter selection.</p>
                </div>
              ) : (
                filteredJobs.map((job) => {
                  const isSaved = savedJobIds.includes(job.id);
                  const skillTags = job.skills_required
                    ? job.skills_required.split(",").map((s) => s.trim())
                    : [];

                  return (
                    <div key={job.id} className="job-card">
                      <div>
                        <div className="job-card-header">
                          <div
                            className="company-logo-badge"
                            style={{ background: getLogoStyle(job.id) }}
                          >
                            {job.company_name?.charAt(0)?.toUpperCase() || "C"}
                          </div>

                          <div className="job-main-info">
                            <h3 className="job-title-text">{job.job_title}</h3>
                            <div className="company-name-text">🏢 {job.company_name}</div>
                          </div>

                          <button
                            className={`job-bookmark-btn ${isSaved ? "saved" : ""}`}
                            onClick={() => toggleSaveJob(job.id)}
                            title={isSaved ? "Remove Bookmark" : "Save Job"}
                          >
                            {isSaved ? "★" : "☆"}
                          </button>
                        </div>

                        <div className="job-meta-badges">
                          {job.location && <span className="meta-badge badge-location">📍 {job.location}</span>}
                          {job.job_type && <span className="meta-badge badge-type">💼 {job.job_type}</span>}
                          {job.salary && <span className="meta-badge badge-salary">💵 {job.salary}</span>}
                        </div>

                        <p className="job-description-preview">{job.description}</p>

                        {skillTags.length > 0 && (
                          <div className="skills-tags-row">
                            {skillTags.map((tag, idx) => (
                              <span key={idx} className="skill-req-tag">
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>

                      <div className="job-card-actions">
                        <button
                          className="btn-details-secondary"
                          onClick={() => setSelectedJob(job)}
                        >
                          View Details
                        </button>

                        <a
                          href={job.application_url || "#"}
                          target="_blank"
                          rel="noreferrer"
                          className="btn-apply-primary"
                        >
                          <span>Apply Now</span>
                          <span>↗</span>
                        </a>
                      </div>
                    </div>
                  );
                })
              )}
            </section>
          </div>
        )}

        {/* ============================================================== */}
        {/* MODAL 1: AI COMPANY DETAILS & APPLICATION READINESS */}
        {/* ============================================================== */}
        {selectedMatch && (
          <div className="modal-overlay" onClick={() => setSelectedMatch(null)}>
            <div className="modal-content-card ai-details-modal" onClick={(e) => e.stopPropagation()}>
              <button className="modal-close-btn" onClick={() => setSelectedMatch(null)}>
                ✕
              </button>

              <div className="modal-header-hero">
                <div
                  className="company-logo-badge large"
                  style={{ background: getLogoStyle(selectedMatch.id) }}
                >
                  {selectedMatch.company_name?.charAt(0)?.toUpperCase()}
                </div>
                <div>
                  <div className="modal-title-row">
                    <h2>{selectedMatch.job_title}</h2>
                    <span className={`match-level-pill ${getMatchBadgeClass(selectedMatch.match_level)}`}>
                      {selectedMatch.match_level}
                    </span>
                  </div>
                  <div className="modal-company-sub">
                    🏢 {selectedMatch.company_name} • 📍 {selectedMatch.location} • 💼 {selectedMatch.job_type}
                  </div>
                </div>
              </div>

              {/* Score Badges */}
              <div className="modal-score-banner">
                <div className="score-block">
                  <span className="sc-lbl">Match Score</span>
                  <span className="sc-val match">{selectedMatch.match_percentage}%</span>
                </div>
                <div className="score-divider"></div>
                <div className="score-block">
                  <span className="sc-lbl">Candidate Readiness</span>
                  <span className="sc-val ready">{selectedMatch.readiness_percentage}%</span>
                </div>
                {selectedMatch.salary && (
                  <>
                    <div className="score-divider"></div>
                    <div className="score-block">
                      <span className="sc-lbl">Compensation</span>
                      <span className="sc-val salary">{selectedMatch.salary}</span>
                    </div>
                  </>
                )}
              </div>

              {/* Why Recommended */}
              <div className="modal-section-block">
                <h4>💡 Why Recommended:</h4>
                <p className="modal-why-text">{selectedMatch.why_recommended}</p>
              </div>

              {/* Application Readiness Checklist */}
              {selectedMatch.application_readiness && (
                <div className="modal-section-block">
                  <h4>📋 Application Readiness Checklist:</h4>
                  <div className="app-readiness-checklist">
                    <div className="checklist-item">
                      <div className="chk-label">
                        <strong>ATS Resume:</strong>
                        <span>{selectedMatch.application_readiness.resume?.detail}</span>
                      </div>
                      {getChecklistIcon(selectedMatch.application_readiness.resume?.status)}
                    </div>

                    <div className="checklist-item">
                      <div className="chk-label">
                        <strong>Technical Skills:</strong>
                        <span>{selectedMatch.application_readiness.skills?.detail}</span>
                      </div>
                      {getChecklistIcon(selectedMatch.application_readiness.skills?.status)}
                    </div>

                    <div className="checklist-item">
                      <div className="chk-label">
                        <strong>Portfolio Projects:</strong>
                        <span>{selectedMatch.application_readiness.projects?.detail}</span>
                      </div>
                      {getChecklistIcon(selectedMatch.application_readiness.projects?.status)}
                    </div>

                    <div className="checklist-item">
                      <div className="chk-label">
                        <strong>Education:</strong>
                        <span>{selectedMatch.application_readiness.education?.detail}</span>
                      </div>
                      {getChecklistIcon(selectedMatch.application_readiness.education?.status)}
                    </div>

                    <div className="checklist-item">
                      <div className="chk-label">
                        <strong>Certifications:</strong>
                        <span>{selectedMatch.application_readiness.certifications?.detail}</span>
                      </div>
                      {getChecklistIcon(selectedMatch.application_readiness.certifications?.status)}
                    </div>

                    <div className="checklist-item">
                      <div className="chk-label">
                        <strong>Interview Preparation:</strong>
                        <span>{selectedMatch.application_readiness.interview?.detail}</span>
                      </div>
                      {getChecklistIcon(selectedMatch.application_readiness.interview?.status)}
                    </div>
                  </div>
                </div>
              )}

              {/* Required vs Matched Skills */}
              <div className="modal-section-block">
                <h4>Stack Alignment:</h4>
                <div className="skills-comparison-row modal-comp">
                  <div className="skill-col">
                    <span className="col-label matched">✓ Matched Stack</span>
                    <div className="skills-chips-flow">
                      {selectedMatch.matched_skills?.map((s, idx) => (
                        <span key={idx} className="skill-chip matched">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="skill-col">
                    <span className="col-label missing">✕ Skills to Cover</span>
                    <div className="skills-chips-flow">
                      {selectedMatch.missing_skills?.map((s, idx) => (
                        <span key={idx} className="skill-chip missing">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Description */}
              <div className="modal-section-block">
                <h4>Job Description & Requirements:</h4>
                <p className="modal-desc-text">{selectedMatch.description}</p>
              </div>

              {/* Preparation Suggestions */}
              {selectedMatch.preparation_suggestions?.length > 0 && (
                <div className="modal-section-block">
                  <h4>Recommended Preparation Steps:</h4>
                  <ul className="modal-prep-list">
                    {selectedMatch.preparation_suggestions.map((sug, idx) => (
                      <li key={idx}>🎯 {sug}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="modal-action-footer">
                <a
                  href={selectedMatch.application_url || "#"}
                  target="_blank"
                  rel="noreferrer"
                  className="btn-apply-primary"
                  style={{ padding: "12px 28px", fontSize: "15px" }}
                >
                  🚀 Apply Directly on Company Site ↗
                </a>
                <Link
                  to="/resume"
                  className="btn-details-secondary"
                  style={{ padding: "12px 20px" }}
                >
                  Tailor ATS Resume
                </Link>
              </div>
            </div>
          </div>
        )}

        {/* ============================================================== */}
        {/* MODAL 2: DIRECTORY JOB DETAILS (PRESERVED) */}
        {/* ============================================================== */}
        {selectedJob && (
          <div className="modal-overlay" onClick={() => setSelectedJob(null)}>
            <div className="modal-content-card" onClick={(e) => e.stopPropagation()}>
              <button className="modal-close-btn" onClick={() => setSelectedJob(null)}>
                ✕
              </button>

              <div style={{ display: "flex", alignItems: "center", gap: "16px", marginBottom: "20px" }}>
                <div
                  className="company-logo-badge"
                  style={{
                    background: getLogoStyle(selectedJob.id),
                    width: "60px",
                    height: "60px",
                    fontSize: "26px",
                  }}
                >
                  {selectedJob.company_name?.charAt(0)?.toUpperCase()}
                </div>
                <div>
                  <h2 style={{ fontSize: "22px", fontWeight: "800", color: "#0f172a" }}>
                    {selectedJob.job_title}
                  </h2>
                  <div style={{ fontSize: "15px", color: "#475569", fontWeight: "600" }}>
                    {selectedJob.company_name}
                  </div>
                </div>
              </div>

              <div className="job-meta-badges" style={{ marginBottom: "20px" }}>
                {selectedJob.location && <span className="meta-badge badge-location">📍 {selectedJob.location}</span>}
                {selectedJob.job_type && <span className="meta-badge badge-type">💼 {selectedJob.job_type}</span>}
                {selectedJob.salary && <span className="meta-badge badge-salary">💵 {selectedJob.salary}</span>}
              </div>

              <h4 style={{ fontSize: "15px", fontWeight: "700", marginBottom: "8px", color: "#0f172a" }}>
                Job Description & Scope:
              </h4>
              <p style={{ fontSize: "14.5px", color: "#334155", lineHeight: "1.7", marginBottom: "20px" }}>
                {selectedJob.description}
              </p>

              {selectedJob.skills_required && (
                <div style={{ marginBottom: "24px" }}>
                  <h4 style={{ fontSize: "15px", fontWeight: "700", marginBottom: "8px", color: "#0f172a" }}>
                    Required Technical Stack:
                  </h4>
                  <div className="skills-tags-row">
                    {selectedJob.skills_required.split(",").map((skill, idx) => (
                      <span
                        key={idx}
                        className="skill-chip"
                        style={{
                          background: "#e0e7ff",
                          color: "#3730a3",
                          fontSize: "13px",
                          padding: "4px 12px",
                          borderRadius: "20px",
                        }}
                      >
                        {skill.trim()}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div style={{ display: "flex", gap: "12px", marginTop: "20px" }}>
                <a
                  href={selectedJob.application_url || "#"}
                  target="_blank"
                  rel="noreferrer"
                  className="btn-apply-primary"
                  style={{ padding: "12px 24px", fontSize: "15px" }}
                >
                  🚀 Apply Directly on Company Site
                </a>
              </div>
            </div>
          </div>
        )}

        {/* ============================================================== */}
        {/* MODAL 3: POST JOB OPENING (PRESERVED) */}
        {/* ============================================================== */}
        {showPostModal && (
          <div className="modal-overlay" onClick={() => setShowPostModal(false)}>
            <div className="modal-content-card" onClick={(e) => e.stopPropagation()}>
              <button className="modal-close-btn" onClick={() => setShowPostModal(false)}>
                ✕
              </button>

              <h2 style={{ fontSize: "22px", fontWeight: "800", color: "#0f172a", marginBottom: "8px" }}>
                Post a Job Opening
              </h2>
              <p style={{ color: "#64748b", fontSize: "14px", marginBottom: "20px" }}>
                Add new verified placement positions for CodeSphere students.
              </p>

              <form onSubmit={handleCreateJob}>
                <div className="post-job-form-grid">
                  <div>
                    <label className="form-lbl">Company Name *</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Acme Corp"
                      value={newJobForm.company_name}
                      onChange={(e) => setNewJobForm({ ...newJobForm, company_name: e.target.value })}
                      className="form-input"
                    />
                  </div>

                  <div>
                    <label className="form-lbl">Job Title *</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Full-Stack Engineer"
                      value={newJobForm.job_title}
                      onChange={(e) => setNewJobForm({ ...newJobForm, job_title: e.target.value })}
                      className="form-input"
                    />
                  </div>

                  <div>
                    <label className="form-lbl">Location</label>
                    <input
                      type="text"
                      placeholder="e.g. San Francisco, CA / Remote"
                      value={newJobForm.location}
                      onChange={(e) => setNewJobForm({ ...newJobForm, location: e.target.value })}
                      className="form-input"
                    />
                  </div>

                  <div>
                    <label className="form-lbl">Job Type</label>
                    <select
                      value={newJobForm.job_type}
                      onChange={(e) => setNewJobForm({ ...newJobForm, job_type: e.target.value })}
                      className="form-input"
                    >
                      <option value="Full-time">Full-time</option>
                      <option value="Remote">Remote</option>
                      <option value="Hybrid">Hybrid</option>
                      <option value="Internship">Internship</option>
                      <option value="Contract">Contract</option>
                    </select>
                  </div>

                  <div>
                    <label className="form-lbl">Salary Range</label>
                    <input
                      type="text"
                      placeholder="e.g. $120,000 - $150,000"
                      value={newJobForm.salary}
                      onChange={(e) => setNewJobForm({ ...newJobForm, salary: e.target.value })}
                      className="form-input"
                    />
                  </div>

                  <div>
                    <label className="form-lbl">Application URL</label>
                    <input
                      type="url"
                      placeholder="https://company.com/apply"
                      value={newJobForm.application_url}
                      onChange={(e) => setNewJobForm({ ...newJobForm, application_url: e.target.value })}
                      className="form-input"
                    />
                  </div>

                  <div style={{ gridColumn: "1 / -1" }}>
                    <label className="form-lbl">Skills Required (comma-separated) *</label>
                    <input
                      type="text"
                      required
                      placeholder="Python, React, FastAPI, Docker"
                      value={newJobForm.skills_required}
                      onChange={(e) => setNewJobForm({ ...newJobForm, skills_required: e.target.value })}
                      className="form-input"
                    />
                  </div>

                  <div style={{ gridColumn: "1 / -1" }}>
                    <label className="form-lbl">Description</label>
                    <textarea
                      rows={3}
                      placeholder="Responsibilities, qualifications, and overview..."
                      value={newJobForm.description}
                      onChange={(e) => setNewJobForm({ ...newJobForm, description: e.target.value })}
                      className="form-input"
                    ></textarea>
                  </div>
                </div>

                <div style={{ display: "flex", justifyContent: "flex-end", gap: "12px", marginTop: "20px" }}>
                  <button
                    type="button"
                    onClick={() => setShowPostModal(false)}
                    className="btn-details-secondary"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submittingJob}
                    className="btn-apply-primary"
                    style={{ padding: "10px 24px" }}
                  >
                    {submittingJob ? "Posting..." : "Publish Job Opening"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Placements;
