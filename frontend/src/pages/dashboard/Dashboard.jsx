import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { apiRequest, getAuthToken } from "../../services/apiClient";
import "./Dashboard.css";

function readMetric(value, label) {
    const metric = Number(value);

    if (value === null || value === undefined || value === "" || !Number.isFinite(metric)) {
        throw new Error(`Dashboard data is missing a valid ${label} value.`);
    }

    return metric;
}

function getDashboardMetrics(data) {
    if (!data || typeof data !== "object" || !data.courses || !data.learning_progress) {
        throw new Error("Dashboard data is incomplete. Please try again.");
    }

    const courses = readMetric(data.courses.total_courses, "available courses");
    const lessons = readMetric(data.courses.total_lessons, "total lessons");
    const completed = readMetric(data.learning_progress.lessons_completed, "completed lessons");
    const progress = readMetric(data.learning_progress.average_progress, "average progress");

    if (courses < 0 || lessons < 0 || completed < 0 || progress < 0 || progress > 100) {
        throw new Error("Dashboard data contains invalid learning statistics.");
    }

    return { courses, lessons, completed, progress };
}

function Dashboard() {
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [reloadKey, setReloadKey] = useState(0);

    useEffect(() => {
        let isMounted = true;

        async function loadDashboard() {
            setLoading(true);
            setError("");

            if (!getAuthToken()) {
                setError("Your session is no longer valid. Please sign in again.");
                setDashboardData(null);
                setLoading(false);
                return;
            }

            try {
                const data = await apiRequest("/dashboard");
                getDashboardMetrics(data);

                if (isMounted) {
                    setDashboardData(data);
                }
            } catch (err) {
                if (isMounted) {
                    setError(err.message || "Unable to load dashboard data.");
                    setDashboardData(null);
                }
            } finally {
                if (isMounted) {
                    setLoading(false);
                }
            }
        }

        void loadDashboard();

        return () => {
            isMounted = false;
        };
    }, [reloadKey]);

    if (loading) {
        return (
            <main className="dashboard-page">
                <div className="dashboard-shell" aria-busy="true">
                    <p className="dashboard-eyebrow">YOUR LEARNING SPACE</p>
                    <h1 className="dashboard-loading-title">Preparing your dashboard</h1>
                    <p className="dashboard-intro">Loading your learning snapshot...</p>
                    <div className="dashboard-stats" aria-hidden="true">
                        {["Courses", "Lessons", "Completed lessons", "Average progress"].map((label) => (
                            <div className="dashboard-stat dashboard-stat-loading" key={label}>
                                <span>{label}</span>
                                <strong>—</strong>
                            </div>
                        ))}
                    </div>
                </div>
            </main>
        );
    }

    if (error) {
        return (
            <main className="dashboard-page">
                <div className="dashboard-shell">
                    <section className="dashboard-error" role="alert">
                        <p className="dashboard-eyebrow">DASHBOARD UNAVAILABLE</p>
                        <h1>We couldn&apos;t load your learning snapshot.</h1>
                        <p>{error}</p>
                        <button
                            type="button"
                            className="dashboard-primary-button"
                            onClick={() => setReloadKey((current) => current + 1)}
                        >
                            Try again
                        </button>
                    </section>
                </div>
            </main>
        );
    }

    const stats = getDashboardMetrics(dashboardData);
    const progress = Math.round(stats.progress);
    const username = typeof dashboardData.user?.username === "string"
        ? dashboardData.user.username.trim()
        : "";
    const greeting = username ? `Welcome back, ${username}.` : "Welcome back.";
    const hasResume = dashboardData.resume?.created === true;
    const remainingLessons = stats.completed <= stats.lessons
        ? stats.lessons - stats.completed
        : null;

    return (
        <main className="dashboard-page">
            <div className="dashboard-shell">
                <section className="dashboard-welcome">
                    <div className="dashboard-welcome-content">
                        <p className="dashboard-eyebrow">
                            <span aria-hidden="true" />
                            YOUR LEARNING SPACE
                        </p>
                        <h1>{greeting}</h1>
                        <p className="dashboard-intro">
                            A little progress each day adds up. Pick up where you left off and keep
                            building skills for your future.
                        </p>
                        <div className="dashboard-actions">
                            <Link to="/learning" className="dashboard-primary-button">
                                Continue learning <span aria-hidden="true">↗</span>
                            </Link>
                            <Link to="/learning" className="dashboard-secondary-link">
                                Explore courses
                            </Link>
                        </div>
                    </div>
                    <div className="dashboard-welcome-art" aria-hidden="true">
                        <div className="dashboard-art-ring dashboard-art-ring-outer" />
                        <div className="dashboard-art-ring dashboard-art-ring-inner" />
                        <div className="dashboard-art-core">
                            <span>YOUR</span>
                            <strong>next<br />chapter</strong>
                            <i>✦</i>
                        </div>
                        <span className="dashboard-art-label">LEARN · PRACTICE · GROW</span>
                    </div>
                </section>

                <section className="dashboard-section" aria-labelledby="learning-snapshot-heading">
                    <div className="dashboard-section-heading">
                        <div>
                            <p className="dashboard-eyebrow">THE BIG PICTURE</p>
                            <h2 id="learning-snapshot-heading">Your learning snapshot</h2>
                        </div>
                        <Link to="/learning" className="dashboard-inline-link">
                            Go to learning <span aria-hidden="true">→</span>
                        </Link>
                    </div>

                    <div className="dashboard-stats">
                        <article className="dashboard-stat">
                            <span className="dashboard-stat-index" aria-hidden="true">01</span>
                            <p>Available courses</p>
                            <strong>{stats.courses}</strong>
                            <span className="dashboard-stat-caption">Ready when you are</span>
                        </article>
                        <article className="dashboard-stat">
                            <span className="dashboard-stat-index" aria-hidden="true">02</span>
                            <p>Total lessons</p>
                            <strong>{stats.lessons}</strong>
                            <span className="dashboard-stat-caption">Across the platform</span>
                        </article>
                        <article className="dashboard-stat">
                            <span className="dashboard-stat-index" aria-hidden="true">03</span>
                            <p>Completed lessons</p>
                            <strong>{stats.completed}</strong>
                            <span className="dashboard-stat-caption">Lessons finished</span>
                        </article>
                        <article className="dashboard-stat dashboard-stat-highlight">
                            <span className="dashboard-stat-index" aria-hidden="true">04</span>
                            <p>Average progress</p>
                            <strong>{progress}<small>%</small></strong>
                            <span className="dashboard-stat-caption">On lessons you&apos;ve started</span>
                        </article>
                    </div>
                </section>

                <section className="dashboard-content-grid" aria-label="Learning and career tools">
                    <article className="dashboard-progress-panel">
                        <div className="dashboard-panel-heading">
                            <div>
                                <p className="dashboard-eyebrow">KEEP YOUR MOMENTUM</p>
                                <h2>Learning progress</h2>
                            </div>
                            <span className="dashboard-progress-value">{progress}%</span>
                        </div>
                        <p className="dashboard-progress-copy">
                            Average completion across the lessons you&apos;ve started.
                        </p>
                        <div
                            className="dashboard-progress-track"
                            role="progressbar"
                            aria-label="Average learning progress"
                            aria-valuemin="0"
                            aria-valuemax="100"
                            aria-valuenow={progress}
                        >
                            <span style={{ width: `${progress}%` }} />
                        </div>
                        <div className="dashboard-progress-counts">
                            <span><strong>{stats.completed}</strong> completed</span>
                            <span><strong>{stats.lessons}</strong> total lessons</span>
                            {remainingLessons !== null && (
                                <span><strong>{remainingLessons}</strong> remaining</span>
                            )}
                        </div>
                        <Link to="/learning" className="dashboard-inline-link">
                            View your learning modules <span aria-hidden="true">→</span>
                        </Link>
                    </article>

                    <article className="dashboard-feature dashboard-feature-resume">
                        <p className="dashboard-eyebrow">CAREER TOOLKIT · 01</p>
                        <h2>Resume Builder</h2>
                        <p>
                            {hasResume
                                ? "Your resume is saved. Keep it up to date as your skills grow."
                                : "Bring your skills and projects together in a professional resume."}
                        </p>
                        <Link to="/resume" className="dashboard-feature-link">
                            {hasResume ? "Continue your resume" : "Open Resume Builder"}
                            <span aria-hidden="true">↗</span>
                        </Link>
                    </article>

                    <article className="dashboard-feature">
                        <p className="dashboard-eyebrow">CAREER TOOLKIT · 02</p>
                        <h2>Interview preparation</h2>
                        <p>Practice technical and communication skills at your own pace.</p>
                        <Link to="/interview" className="dashboard-feature-link">
                            Start practicing <span aria-hidden="true">↗</span>
                        </Link>
                    </article>

                    <article className="dashboard-feature">
                        <p className="dashboard-eyebrow">CAREER TOOLKIT · 03</p>
                        <h2>Placement assistance</h2>
                        <p>Explore opportunities and find out what employers are looking for.</p>
                        <Link to="/placements" className="dashboard-feature-link">
                            Explore placements <span aria-hidden="true">↗</span>
                        </Link>
                    </article>
                </section>
            </div>
        </main>
    );
}

export default Dashboard;
