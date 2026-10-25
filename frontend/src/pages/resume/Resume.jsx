import { useState, useEffect } from "react";
import { getMyResume, saveResume, deleteResume } from "../../services/resumeApi";
import "./Resume.css";

const SAMPLE_RESUME = {
  full_name: "Alex Rivera",
  phone: "+1 (555) 382-9102",
  location: "San Francisco, CA",
  linkedin_url: "https://linkedin.com/in/alex-rivera-tech",
  github_url: "https://github.com/alexrivera-dev",
  career_objective:
    "Driven Full-Stack Engineer with 3+ years of experience crafting high-throughput web apps, microservices, and AI-powered platform solutions. Passionate about automated workflows, API design, and intuitive UX.",
  skills: [
    "Python",
    "FastAPI",
    "React.js",
    "TypeScript",
    "Node.js",
    "PostgreSQL",
    "Docker",
    "AWS",
    "RESTful APIs",
    "Git",
    "Tailwind CSS",
    "GraphQL",
  ],
  experiences: [
    {
      title: "Senior Full Stack Developer",
      company: "CloudSphere Tech",
      location: "San Francisco, CA",
      duration: "2023 - Present",
      description:
        "Architected scalable microservices serving 200k+ monthly users using FastAPI & React. Optimized database queries, reducing API latency by 42%. Led cross-functional team of 5 developers.",
    },
    {
      title: "Software Engineer",
      company: "Innovate Labs",
      location: "San Jose, CA",
      duration: "2021 - 2023",
      description:
        "Engineered responsive UI components in React and integrated OAuth2 security protocols. Built automated CI/CD pipelines reducing deployment friction by 60%.",
    },
  ],
  projects: [
    {
      title: "AI Resume & Career Hub",
      tech_stack: "FastAPI, React, PostgreSQL, Tailwind",
      link: "https://github.com/alexrivera/resume-hub",
      description:
        "Real-time resume builder with instant ATS scoring and live PDF generator. Built dynamic template system and JWT authentication.",
    },
    {
      title: "DevMetrics Dashboard",
      tech_stack: "Python, Docker, Prometheus, Grafana",
      link: "https://github.com/alexrivera/dev-metrics",
      description:
        "Monitored server health metrics and dispatched alerts with sub-second accuracy across multi-cloud environments.",
    },
  ],
  education: [
    {
      degree: "B.S. in Computer Science",
      institution: "University of California, Berkeley",
      year: "2017 - 2021",
      score: "GPA 3.8 / 4.0",
    },
  ],
  certifications: "AWS Certified Solutions Architect, Meta Front-End Developer Specialization",
  achievements: "1st Place Winner at HackSF 2023, Open Source Contributor to FastAPI ecosystem",
};

function Resume() {
  const [formData, setFormData] = useState({
    full_name: "",
    phone: "",
    location: "",
    linkedin_url: "",
    github_url: "",
    career_objective: "",
    skills: [],
    experiences: [],
    projects: [],
    education: [],
    certifications: "",
    achievements: "",
  });

  const [newSkill, setNewSkill] = useState("");
  const [activeTab, setActiveTab] = useState("personal");
  const [theme, setTheme] = useState("modern");
  const [status, setStatus] = useState({ message: "", type: "" });
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Load existing user resume on mount
  useEffect(() => {
    loadUserResume();
  }, []);

  const loadUserResume = async () => {
    setIsLoading(true);
    try {
      const data = await getMyResume();
      if (data) {
        parseAndSetBackendData(data);
        showStatus("Saved resume loaded successfully.", "success");
      }
    } catch {
      // Check local storage backup
      const localBackup = localStorage.getItem("codesphere_resume_data");
      if (localBackup) {
        try {
          setFormData(JSON.parse(localBackup));
        } catch (e) {
          console.error("Failed to parse local resume backup", e);
        }
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Convert backend string representation back to frontend state
  const parseAndSetBackendData = (data) => {
    let parsedSkills = [];
    if (data.skills) {
      try {
        parsedSkills = JSON.parse(data.skills);
      } catch {
        parsedSkills = data.skills.split(",").map((s) => s.trim()).filter(Boolean);
      }
    }

    let parsedExp = [];
    if (data.experience) {
      try {
        parsedExp = JSON.parse(data.experience);
      } catch {
        parsedExp = [{ title: "Experience", company: "", duration: "", description: data.experience }];
      }
    }

    let parsedProj = [];
    if (data.projects) {
      try {
        parsedProj = JSON.parse(data.projects);
      } catch {
        parsedProj = [{ title: "Project", tech_stack: "", link: "", description: data.projects }];
      }
    }

    let parsedEdu = [];
    if (data.education) {
      try {
        parsedEdu = JSON.parse(data.education);
      } catch {
        parsedEdu = [{ degree: data.education, institution: "", year: "", score: "" }];
      }
    }

    const updated = {
      full_name: data.full_name || "",
      phone: data.phone || "",
      location: data.location || "",
      linkedin_url: data.linkedin_url || "",
      github_url: data.github_url || "",
      career_objective: data.career_objective || "",
      skills: Array.isArray(parsedSkills) ? parsedSkills : [],
      experiences: Array.isArray(parsedExp) ? parsedExp : [],
      projects: Array.isArray(parsedProj) ? parsedProj : [],
      education: Array.isArray(parsedEdu) ? parsedEdu : [],
      certifications: data.certifications || "",
      achievements: data.achievements || "",
    };

    setFormData(updated);
  };

  const showStatus = (message, type = "success") => {
    setStatus({ message, type });
    setTimeout(() => {
      setStatus({ message: "", type: "" });
    }, 4000);
  };

  // Handle Input Changes
  const handleTextChange = (e) => {
    const { name, value } = e.target;
    const updated = { ...formData, [name]: value };
    setFormData(updated);
    localStorage.setItem("codesphere_resume_data", JSON.stringify(updated));
  };

  // Skill Chip Management
  const handleAddSkill = (e) => {
    if ((e.key === "Enter" || e.type === "click") && newSkill.trim()) {
      e.preventDefault();
      if (!formData.skills.includes(newSkill.trim())) {
        const updatedSkills = [...formData.skills, newSkill.trim()];
        const updated = { ...formData, skills: updatedSkills };
        setFormData(updated);
        localStorage.setItem("codesphere_resume_data", JSON.stringify(updated));
      }
      setNewSkill("");
    }
  };

  const handleRemoveSkill = (skillToRemove) => {
    const updatedSkills = formData.skills.filter((s) => s !== skillToRemove);
    const updated = { ...formData, skills: updatedSkills };
    setFormData(updated);
    localStorage.setItem("codesphere_resume_data", JSON.stringify(updated));
  };

  // Dynamic Array Handlers (Experiences, Projects, Education)
  const handleItemChange = (category, index, field, value) => {
    const list = [...formData[category]];
    list[index] = { ...list[index], [field]: value };
    const updated = { ...formData, [category]: list };
    setFormData(updated);
    localStorage.setItem("codesphere_resume_data", JSON.stringify(updated));
  };

  const handleAddItem = (category, defaultItem) => {
    const list = [...formData[category], defaultItem];
    const updated = { ...formData, [category]: list };
    setFormData(updated);
    localStorage.setItem("codesphere_resume_data", JSON.stringify(updated));
  };

  const handleRemoveItem = (category, index) => {
    const list = formData[category].filter((_, i) => i !== index);
    const updated = { ...formData, [category]: list };
    setFormData(updated);
    localStorage.setItem("codesphere_resume_data", JSON.stringify(updated));
  };

  // Populate Sample Data
  const handleLoadSample = () => {
    setFormData(SAMPLE_RESUME);
    localStorage.setItem("codesphere_resume_data", JSON.stringify(SAMPLE_RESUME));
    showStatus("Sample software developer resume loaded!", "success");
  };

  // Clear All Data
  const handleClear = () => {
    if (window.confirm("Are you sure you want to clear your resume form?")) {
      const emptyState = {
        full_name: "",
        phone: "",
        location: "",
        linkedin_url: "",
        github_url: "",
        career_objective: "",
        skills: [],
        experiences: [],
        projects: [],
        education: [],
        certifications: "",
        achievements: "",
      };
      setFormData(emptyState);
      localStorage.removeItem("codesphere_resume_data");
      showStatus("Resume form reset.", "success");
    }
  };

  // Save Resume to Backend
  const handleSaveToBackend = async () => {
    if (!formData.full_name.trim()) {
      showStatus("Full Name is required to save your resume.", "error");
      setActiveTab("personal");
      return;
    }

    setIsSaving(true);
    try {
      const payload = {
        full_name: formData.full_name,
        phone: formData.phone || null,
        location: formData.location || null,
        linkedin_url: formData.linkedin_url || null,
        github_url: formData.github_url || null,
        career_objective: formData.career_objective || null,
        skills: JSON.stringify(formData.skills),
        experience: JSON.stringify(formData.experiences),
        projects: JSON.stringify(formData.projects),
        education: JSON.stringify(formData.education),
        certifications: formData.certifications || null,
        achievements: formData.achievements || null,
      };

      await saveResume(payload);
      showStatus("Resume saved successfully to server!", "success");
    } catch (err) {
      showStatus(`Saved locally! Server sync note: ${err.message}`, "error");
    } finally {
      setIsSaving(false);
    }
  };

  // Handle Print PDF
  const handlePrint = () => {
    window.print();
  };

  // Calculate ATS Score & AI Feedback Tips
  const calculateAtsScore = () => {
    let score = 20;
    const tips = [];

    if (formData.full_name) score += 10;
    if (formData.phone && formData.location) score += 10;
    else tips.push("Add location and phone number for recruiter contact.");

    if (formData.career_objective && formData.career_objective.length > 50) {
      score += 15;
    } else {
      tips.push("Expand summary objective to highlights key technical strengths.");
    }

    if (formData.skills.length >= 6) {
      score += 15;
    } else {
      tips.push("Include at least 6 core technical skills (e.g. React, Python, SQL).");
    }

    if (formData.experiences.length > 0) {
      score += 15;
    } else {
      tips.push("Add work or internship experience with quantitative impact.");
    }

    if (formData.projects.length > 0) {
      score += 10;
    } else {
      tips.push("Add key personal or open-source projects with repo links.");
    }

    if (formData.education.length > 0) {
      score += 5;
    }

    if (formData.linkedin_url && formData.github_url) {
      score += 0;
    } else {
      tips.push("Add LinkedIn and GitHub URLs to enhance online presence.");
    }

    return { score: Math.min(score, 100), tips };
  };

  const { score: atsScore, tips: aiTips } = calculateAtsScore();

  return (
    <div className="resume-page">
      <div className="resume-container">
        {/* Header Banner */}
        <header className="resume-header">
          <div className="resume-header-info">
            <h1>
              <span>AI Resume Studio</span>
              <span className="resume-badge-ai">Live ATS Optimizer</span>
            </h1>
            <p>
              Design recruiter-approved technical resumes. Edit details, optimize ATS score in real-time, pick high-contrast themes, and print pristine PDF downloads.
            </p>
          </div>

          <div className="resume-header-actions">
            <button
              onClick={handleSaveToBackend}
              disabled={isSaving}
              className="btn-resume btn-resume-primary"
            >
              {isSaving ? "Saving..." : "💾 Save to Account"}
            </button>

            <button onClick={handlePrint} className="btn-resume btn-resume-secondary">
              🖨️ Download / Print PDF
            </button>

            <button onClick={handleLoadSample} className="btn-resume btn-resume-outline">
              ⚡ Load Sample Resume
            </button>

            <button onClick={handleClear} className="btn-resume btn-resume-outline">
              🗑️ Clear
            </button>
          </div>
        </header>

        {/* Status Toast Alert */}
        {status.message && (
          <div
            className={`resume-status-bar ${status.type === "success" ? "resume-status-success" : "resume-status-error"
              }`}
          >
            <span>{status.message}</span>
            <button
              onClick={() => setStatus({ message: "", type: "" })}
              style={{ background: "none", border: "none", cursor: "pointer", fontWeight: "bold" }}
            >
              ✕
            </button>
          </div>
        )}

        {/* Main Grid: Form Editor (Left) & Paper Preview (Right) */}
        <main className="resume-grid">
          {/* Left Column: Form Editor */}
          <section className="editor-card">
            {/* Editor Navigation Tabs */}
            <div className="editor-nav-tabs">
              <button
                className={`tab-button ${activeTab === "personal" ? "active" : ""}`}
                onClick={() => setActiveTab("personal")}
              >
                👤 Personal
              </button>
              <button
                className={`tab-button ${activeTab === "summary" ? "active" : ""}`}
                onClick={() => setActiveTab("summary")}
              >
                🎯 Summary
              </button>
              <button
                className={`tab-button ${activeTab === "skills" ? "active" : ""}`}
                onClick={() => setActiveTab("skills")}
              >
                💻 Skills ({formData.skills.length})
              </button>
              <button
                className={`tab-button ${activeTab === "experience" ? "active" : ""}`}
                onClick={() => setActiveTab("experience")}
              >
                💼 Experience ({formData.experiences.length})
              </button>
              <button
                className={`tab-button ${activeTab === "projects" ? "active" : ""}`}
                onClick={() => setActiveTab("projects")}
              >
                🚀 Projects ({formData.projects.length})
              </button>
              <button
                className={`tab-button ${activeTab === "education" ? "active" : ""}`}
                onClick={() => setActiveTab("education")}
              >
                🎓 Education
              </button>
              <button
                className={`tab-button ${activeTab === "ai" ? "active" : ""}`}
                onClick={() => setActiveTab("ai")}
              >
                🤖 AI Audit ({atsScore}%)
              </button>
            </div>

            <div className="tab-content-area">
              {/* Tab 1: Personal Info */}
              {activeTab === "personal" && (
                <div>
                  <h3 className="editor-section-title">Personal & Contact Info</h3>
                  <p className="editor-section-desc">
                    Your contact info forms the top header of your resume.
                  </p>

                  <div className="form-row">
                    <div>
                      <label className="input-label">Full Name *</label>
                      <input
                        type="text"
                        name="full_name"
                        value={formData.full_name}
                        onChange={handleTextChange}
                        placeholder="e.g. Alex Rivera"
                        className="input-field"
                      />
                    </div>
                    <div>
                      <label className="input-label">Phone Number</label>
                      <input
                        type="text"
                        name="phone"
                        value={formData.phone}
                        onChange={handleTextChange}
                        placeholder="e.g. +1 (555) 019-2834"
                        className="input-field"
                      />
                    </div>
                  </div>

                  <div className="form-row">
                    <div>
                      <label className="input-label">Location (City, Country)</label>
                      <input
                        type="text"
                        name="location"
                        value={formData.location}
                        onChange={handleTextChange}
                        placeholder="e.g. San Francisco, CA"
                        className="input-field"
                      />
                    </div>
                    <div>
                      <label className="input-label">LinkedIn Profile URL</label>
                      <input
                        type="text"
                        name="linkedin_url"
                        value={formData.linkedin_url}
                        onChange={handleTextChange}
                        placeholder="https://linkedin.com/in/username"
                        className="input-field"
                      />
                    </div>
                  </div>

                  <div className="form-group-full">
                    <label className="input-label">GitHub / Portfolio URL</label>
                    <input
                      type="text"
                      name="github_url"
                      value={formData.github_url}
                      onChange={handleTextChange}
                      placeholder="https://github.com/username"
                      className="input-field"
                    />
                  </div>
                </div>
              )}

              {/* Tab 2: Professional Summary */}
              {activeTab === "summary" && (
                <div>
                  <h3 className="editor-section-title">Professional Summary</h3>
                  <p className="editor-section-desc">
                    Write 2-4 compelling sentences highlighting your experience level, core stack, and top career accomplishments.
                  </p>

                  <div className="form-group-full">
                    <label className="input-label">Summary / Career Objective</label>
                    <textarea
                      name="career_objective"
                      value={formData.career_objective}
                      onChange={handleTextChange}
                      rows={5}
                      placeholder="e.g. Innovative Full-Stack Developer with 3+ years experience building web applications..."
                      className="input-field"
                    />
                  </div>
                </div>
              )}

              {/* Tab 3: Technical Skills */}
              {activeTab === "skills" && (
                <div>
                  <h3 className="editor-section-title">Technical Skills & Tools</h3>
                  <p className="editor-section-desc">
                    Add tags for technologies, languages, frameworks, and tools you excel at.
                  </p>

                  <div className="form-group-full">
                    <label className="input-label">Add a Skill Tag (Press Enter)</label>
                    <div style={{ display: "flex", gap: "8px" }}>
                      <input
                        type="text"
                        value={newSkill}
                        onChange={(e) => setNewSkill(e.target.value)}
                        onKeyDown={handleAddSkill}
                        placeholder="e.g. FastAPI, React, Docker, Python"
                        className="input-field"
                      />
                      <button
                        type="button"
                        onClick={handleAddSkill}
                        className="btn-resume btn-resume-primary"
                      >
                        Add
                      </button>
                    </div>

                    <div className="skills-tag-container">
                      {formData.skills.map((skill, i) => (
                        <span key={i} className="skill-chip">
                          {skill}
                          <span
                            className="skill-chip-remove"
                            onClick={() => handleRemoveSkill(skill)}
                          >
                            ×
                          </span>
                        </span>
                      ))}

                      {formData.skills.length === 0 && (
                        <span style={{ color: "#94a3b8", fontSize: "13px" }}>
                          No skill tags added yet. Type a skill above and press Add!
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 4: Work Experience */}
              {activeTab === "experience" && (
                <div>
                  <h3 className="editor-section-title">Work & Internship Experience</h3>
                  <p className="editor-section-desc">
                    Highlight your roles, accomplishments, and quantifiable metrics.
                  </p>

                  <div className="item-card-list">
                    {formData.experiences.map((exp, i) => (
                      <div key={i} className="item-box">
                        <div className="item-box-header">
                          <span className="item-box-title">
                            {exp.title || `Experience #${i + 1}`}
                          </span>
                          <button
                            type="button"
                            onClick={() => handleRemoveItem("experiences", i)}
                            className="btn-remove-item"
                          >
                            Remove
                          </button>
                        </div>

                        <div className="form-row">
                          <div>
                            <label className="input-label">Job Title / Role</label>
                            <input
                              type="text"
                              value={exp.title || ""}
                              onChange={(e) =>
                                handleItemChange("experiences", i, "title", e.target.value)
                              }
                              placeholder="e.g. Senior Software Engineer"
                              className="input-field"
                            />
                          </div>
                          <div>
                            <label className="input-label">Company / Organization</label>
                            <input
                              type="text"
                              value={exp.company || ""}
                              onChange={(e) =>
                                handleItemChange("experiences", i, "company", e.target.value)
                              }
                              placeholder="e.g. Google / Startup Inc"
                              className="input-field"
                            />
                          </div>
                        </div>

                        <div className="form-row">
                          <div>
                            <label className="input-label">Location</label>
                            <input
                              type="text"
                              value={exp.location || ""}
                              onChange={(e) =>
                                handleItemChange("experiences", i, "location", e.target.value)
                              }
                              placeholder="e.g. San Francisco, CA"
                              className="input-field"
                            />
                          </div>
                          <div>
                            <label className="input-label">Duration</label>
                            <input
                              type="text"
                              value={exp.duration || ""}
                              onChange={(e) =>
                                handleItemChange("experiences", i, "duration", e.target.value)
                              }
                              placeholder="e.g. 2022 - Present"
                              className="input-field"
                            />
                          </div>
                        </div>

                        <div>
                          <label className="input-label">Description & Achievements</label>
                          <textarea
                            value={exp.description || ""}
                            onChange={(e) =>
                              handleItemChange("experiences", i, "description", e.target.value)
                            }
                            rows={3}
                            placeholder="e.g. Developed REST APIs serving 100k+ requests. Improved page load time by 30%."
                            className="input-field"
                          />
                        </div>
                      </div>
                    ))}
                  </div>

                  <button
                    type="button"
                    onClick={() =>
                      handleAddItem("experiences", {
                        title: "",
                        company: "",
                        location: "",
                        duration: "",
                        description: "",
                      })
                    }
                    className="btn-add-item"
                  >
                    + Add Experience Position
                  </button>
                </div>
              )}

              {/* Tab 5: Projects */}
              {activeTab === "projects" && (
                <div>
                  <h3 className="editor-section-title">Projects</h3>
                  <p className="editor-section-desc">
                    Showcase key technical projects with tech stack and live/repo links.
                  </p>

                  <div className="item-card-list">
                    {formData.projects.map((proj, i) => (
                      <div key={i} className="item-box">
                        <div className="item-box-header">
                          <span className="item-box-title">
                            {proj.title || `Project #${i + 1}`}
                          </span>
                          <button
                            type="button"
                            onClick={() => handleRemoveItem("projects", i)}
                            className="btn-remove-item"
                          >
                            Remove
                          </button>
                        </div>

                        <div className="form-row">
                          <div>
                            <label className="input-label">Project Name</label>
                            <input
                              type="text"
                              value={proj.title || ""}
                              onChange={(e) =>
                                handleItemChange("projects", i, "title", e.target.value)
                              }
                              placeholder="e.g. AI Resume Builder"
                              className="input-field"
                            />
                          </div>
                          <div>
                            <label className="input-label">Tech Stack Used</label>
                            <input
                              type="text"
                              value={proj.tech_stack || ""}
                              onChange={(e) =>
                                handleItemChange("projects", i, "tech_stack", e.target.value)
                              }
                              placeholder="e.g. React, Python, PostgreSQL"
                              className="input-field"
                            />
                          </div>
                        </div>

                        <div className="form-group-full">
                          <label className="input-label">Link (GitHub / Demo URL)</label>
                          <input
                            type="text"
                            value={proj.link || ""}
                            onChange={(e) =>
                              handleItemChange("projects", i, "link", e.target.value)
                            }
                            placeholder="e.g. https://github.com/myrepo"
                            className="input-field"
                          />
                        </div>

                        <div>
                          <label className="input-label">Description & Highlights</label>
                          <textarea
                            value={proj.description || ""}
                            onChange={(e) =>
                              handleItemChange("projects", i, "description", e.target.value)
                            }
                            rows={3}
                            placeholder="e.g. Built full-stack dashboard featuring user auth, real-time metrics, and clean UI."
                            className="input-field"
                          />
                        </div>
                      </div>
                    ))}
                  </div>

                  <button
                    type="button"
                    onClick={() =>
                      handleAddItem("projects", {
                        title: "",
                        tech_stack: "",
                        link: "",
                        description: "",
                      })
                    }
                    className="btn-add-item"
                  >
                    + Add Technical Project
                  </button>
                </div>
              )}

              {/* Tab 6: Education & Certifications */}
              {activeTab === "education" && (
                <div>
                  <h3 className="editor-section-title">Education & Certifications</h3>
                  <p className="editor-section-desc">
                    Add your academic degrees, certifications, and major awards.
                  </p>

                  <div className="item-card-list">
                    {formData.education.map((edu, i) => (
                      <div key={i} className="item-box">
                        <div className="item-box-header">
                          <span className="item-box-title">
                            {edu.degree || `Education #${i + 1}`}
                          </span>
                          <button
                            type="button"
                            onClick={() => handleRemoveItem("education", i)}
                            className="btn-remove-item"
                          >
                            Remove
                          </button>
                        </div>

                        <div className="form-row">
                          <div>
                            <label className="input-label">Degree / Field of Study</label>
                            <input
                              type="text"
                              value={edu.degree || ""}
                              onChange={(e) =>
                                handleItemChange("education", i, "degree", e.target.value)
                              }
                              placeholder="e.g. B.S. in Computer Science"
                              className="input-field"
                            />
                          </div>
                          <div>
                            <label className="input-label">University / Institution</label>
                            <input
                              type="text"
                              value={edu.institution || ""}
                              onChange={(e) =>
                                handleItemChange("education", i, "institution", e.target.value)
                              }
                              placeholder="e.g. Stanford University"
                              className="input-field"
                            />
                          </div>
                        </div>

                        <div className="form-row">
                          <div>
                            <label className="input-label">Year / Grad Date</label>
                            <input
                              type="text"
                              value={edu.year || ""}
                              onChange={(e) =>
                                handleItemChange("education", i, "year", e.target.value)
                              }
                              placeholder="e.g. 2020 - 2024"
                              className="input-field"
                            />
                          </div>
                          <div>
                            <label className="input-label">Score / Honors (Optional)</label>
                            <input
                              type="text"
                              value={edu.score || ""}
                              onChange={(e) =>
                                handleItemChange("education", i, "score", e.target.value)
                              }
                              placeholder="e.g. GPA 3.9 / Magna Cum Laude"
                              className="input-field"
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  <button
                    type="button"
                    onClick={() =>
                      handleAddItem("education", {
                        degree: "",
                        institution: "",
                        year: "",
                        score: "",
                      })
                    }
                    className="btn-add-item"
                  >
                    + Add Education Entry
                  </button>

                  <hr style={{ margin: "24px 0", borderColor: "#e2e8f0" }} />

                  <div className="form-group-full">
                    <label className="input-label">Certifications (Comma separated)</label>
                    <input
                      type="text"
                      name="certifications"
                      value={formData.certifications}
                      onChange={handleTextChange}
                      placeholder="e.g. AWS Certified Developer, Meta React Certificate"
                      className="input-field"
                    />
                  </div>

                  <div className="form-group-full">
                    <label className="input-label">Achievements & Awards</label>
                    <input
                      type="text"
                      name="achievements"
                      value={formData.achievements}
                      onChange={handleTextChange}
                      placeholder="e.g. 1st Place Hackathon Winner, Dean's List 2023"
                      className="input-field"
                    />
                  </div>
                </div>
              )}

              {/* Tab 7: AI Audit & ATS Score */}
              {activeTab === "ai" && (
                <div>
                  <h3 className="editor-section-title">AI ATS Optimization Audit</h3>
                  <p className="editor-section-desc">
                    Real-time analysis of your resume formatting, keyword density, and completeness.
                  </p>

                  <div className="ai-score-card">
                    <div className="ai-score-header">
                      <div>
                        <span style={{ fontSize: "13px", fontWeight: "600", color: "#475569" }}>
                          ATS Compatibility Score
                        </span>
                        <div
                          className={`ai-score-value ${atsScore >= 80 ? "score-high" : atsScore >= 60 ? "score-mid" : "score-low"
                            }`}
                        >
                          {atsScore} / 100
                        </div>
                      </div>

                      <div
                        style={{
                          background: atsScore >= 80 ? "#dcfce7" : atsScore >= 60 ? "#fef3c7" : "#fee2e2",
                          color: atsScore >= 80 ? "#166534" : atsScore >= 60 ? "#92400e" : "#991b1b",
                          padding: "6px 14px",
                          borderRadius: "20px",
                          fontWeight: "700",
                          fontSize: "13px",
                        }}
                      >
                        {atsScore >= 80 ? "Great Resume!" : atsScore >= 60 ? "Good Start" : "Needs Improvement"}
                      </div>
                    </div>

                    <div className="ai-score-bar-bg">
                      <div
                        className="ai-score-bar-fill"
                        style={{
                          width: `${atsScore}%`,
                          background:
                            atsScore >= 80 ? "#10b981" : atsScore >= 60 ? "#f59e0b" : "#ef4444",
                        }}
                      />
                    </div>

                    <h4 style={{ fontSize: "14px", fontWeight: "700", marginBottom: "10px", color: "#1e293b" }}>
                      AI Recommended Action Items:
                    </h4>

                    {aiTips.length > 0 ? (
                      <div className="ai-tips-list">
                        {aiTips.map((tip, idx) => (
                          <div key={idx} className="ai-tip-item">
                            <span className="ai-tip-icon">💡</span>
                            <span>{tip}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div style={{ color: "#059669", fontSize: "13px", fontWeight: "600" }}>
                        🎉 Excellent! Your resume contains all essential contact details, skills, experience, and project highlights.
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </section>

          {/* Right Column: Live Paper Preview */}
          <section className="preview-card">
            {/* Toolbar / Theme Switcher */}
            <div className="preview-toolbar">
              <div className="template-selector">
                <span>Theme:</span>
                <div className="template-pill-group">
                  <button
                    className={`template-pill ${theme === "modern" ? "active" : ""}`}
                    onClick={() => setTheme("modern")}
                  >
                    Modern Blue
                  </button>
                  <button
                    className={`template-pill ${theme === "slate" ? "active" : ""}`}
                    onClick={() => setTheme("slate")}
                  >
                    Dark Slate
                  </button>
                  <button
                    className={`template-pill ${theme === "emerald" ? "active" : ""}`}
                    onClick={() => setTheme("emerald")}
                  >
                    Emerald Executive
                  </button>
                </div>
              </div>

              <button onClick={handlePrint} className="btn-resume btn-resume-secondary" style={{ padding: "6px 12px", fontSize: "12px" }}>
                🖨️ Print View
              </button>
            </div>

            {/* Paper Sheet Document */}
            <div className={`resume-paper theme-${theme}`}>
              {/* Paper Header */}
              <div className="paper-header">
                <h1 className="paper-name">{formData.full_name || "Your Name"}</h1>

                <div className="paper-contact">
                  {formData.phone && <span>📞 {formData.phone}</span>}
                  {formData.location && <span>📍 {formData.location}</span>}
                  {formData.linkedin_url && (
                    <span>
                      🔗 <a href={formData.linkedin_url} target="_blank" rel="noreferrer">LinkedIn</a>
                    </span>
                  )}
                  {formData.github_url && (
                    <span>
                      💻 <a href={formData.github_url} target="_blank" rel="noreferrer">GitHub</a>
                    </span>
                  )}
                </div>
              </div>

              {/* Objective / Summary */}
              {formData.career_objective && (
                <div>
                  <h3 className="paper-section-heading">Professional Summary</h3>
                  <p className="paper-summary">{formData.career_objective}</p>
                </div>
              )}

              {/* Technical Skills */}
              {formData.skills.length > 0 && (
                <div>
                  <h3 className="paper-section-heading">Technical Skills</h3>
                  <div className="paper-skills-grid">
                    {formData.skills.map((skill, idx) => (
                      <span key={idx} className="paper-skill-badge">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Work Experience */}
              {formData.experiences.length > 0 && (
                <div>
                  <h3 className="paper-section-heading">Experience</h3>
                  {formData.experiences.map((exp, idx) => (
                    <div key={idx} className="paper-item">
                      <div className="paper-item-header">
                        <span>{exp.title || "Job Title"}</span>
                        <span>{exp.duration}</span>
                      </div>
                      <div className="paper-item-sub">
                        {exp.company} {exp.location ? `• ${exp.location}` : ""}
                      </div>
                      {exp.description && (
                        <p style={{ fontSize: "12.5px", color: "#334155", margin: "4px 0" }}>
                          {exp.description}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Projects */}
              {formData.projects.length > 0 && (
                <div>
                  <h3 className="paper-section-heading">Key Projects</h3>
                  {formData.projects.map((proj, idx) => (
                    <div key={idx} className="paper-item">
                      <div className="paper-item-header">
                        <span>
                          {proj.title || "Project Name"}{" "}
                          {proj.tech_stack && (
                            <span style={{ fontWeight: "normal", color: "#64748b", fontSize: "11.5px" }}>
                              ({proj.tech_stack})
                            </span>
                          )}
                        </span>
                        {proj.link && (
                          <a
                            href={proj.link}
                            target="_blank"
                            rel="noreferrer"
                            style={{ fontSize: "11.5px", color: "#2563eb", textDecoration: "underline" }}
                          >
                            Link ↗
                          </a>
                        )}
                      </div>
                      {proj.description && (
                        <p style={{ fontSize: "12.5px", color: "#334155", margin: "4px 0" }}>
                          {proj.description}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Education */}
              {formData.education.length > 0 && (
                <div>
                  <h3 className="paper-section-heading">Education</h3>
                  {formData.education.map((edu, idx) => (
                    <div key={idx} className="paper-item">
                      <div className="paper-item-header">
                        <span>{edu.degree || "Degree"}</span>
                        <span>{edu.year}</span>
                      </div>
                      <div className="paper-item-sub">
                        {edu.institution} {edu.score ? `• ${edu.score}` : ""}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Certifications & Achievements */}
              {(formData.certifications || formData.achievements) && (
                <div>
                  <h3 className="paper-section-heading">Certifications & Honors</h3>
                  {formData.certifications && (
                    <p style={{ fontSize: "12.5px", color: "#334155", marginBottom: "4px" }}>
                      <strong>Certifications:</strong> {formData.certifications}
                    </p>
                  )}
                  {formData.achievements && (
                    <p style={{ fontSize: "12.5px", color: "#334155" }}>
                      <strong>Achievements:</strong> {formData.achievements}
                    </p>
                  )}
                </div>
              )}
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}

export default Resume;
