import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import CourseCard from "../../components/CourseCard";

import {
  getCourses,
  getAllProgress,
  getCourseLessons,
  calculateCourseProgress,
  getCompletedLessonCount,
  getAuthToken,
} from "../../services/learningApi";

import "./learning.css";

function Courses() {
  const [courses, setCourses] = useState([]);
  const [progress, setProgress] = useState([]);
  const [courseLessons, setCourseLessons] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [searchTerm, setSearchTerm] = useState("");
  const [filterTab, setFilterTab] = useState("all");

  async function loadLearningData() {
    try {
      setLoading(true);
      setError("");

      const coursesData = await getCourses();
      const loadedCourses = Array.isArray(coursesData) ? coursesData : [];
      setCourses(loadedCourses);

      // Progress requires authentication
      if (getAuthToken()) {
        try {
          const progressData = await getAllProgress();
          setProgress(Array.isArray(progressData) ? progressData : []);
        } catch (progressError) {
          console.warn("Progress could not be loaded:", progressError);
          setProgress([]);
        }
      } else {
        setProgress([]);
      }

      // Fetch lessons for each course
      const lessonsMap = {};
      await Promise.all(
        loadedCourses.map(async (course) => {
          try {
            const lessons = await getCourseLessons(course.id);
            lessonsMap[course.id] = Array.isArray(lessons) ? lessons : [];
          } catch {
            lessonsMap[course.id] = [];
          }
        })
      );

      setCourseLessons(lessonsMap);
    } catch (err) {
      setError(err.message || "Unable to load courses space.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadLearningData();
    }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  const totalLessons = useMemo(() => {
    return Object.values(courseLessons).reduce(
      (total, lessons) => total + lessons.length,
      0
    );
  }, [courseLessons]);

  const completedLessons = useMemo(() => {
    return Object.values(courseLessons).reduce(
      (total, lessons) => total + getCompletedLessonCount(lessons, progress),
      0
    );
  }, [courseLessons, progress]);

  const overallPercent = useMemo(() => {
    if (totalLessons === 0) return 0;
    return Math.round((completedLessons / totalLessons) * 100);
  }, [completedLessons, totalLessons]);

  // Filtered courses based on search & tab selection
  const filteredCourses = useMemo(() => {
    return courses.filter((course) => {
      const matchesSearch =
        course.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        course.description?.toLowerCase().includes(searchTerm.toLowerCase());

      if (!matchesSearch) return false;

      const lessons = courseLessons[course.id] || [];
      const courseProgress = calculateCourseProgress(lessons, progress);

      if (filterTab === "in-progress") {
        return courseProgress > 0 && courseProgress < 100;
      }
      if (filterTab === "completed") {
        return courseProgress >= 100 && lessons.length > 0;
      }

      return true;
    });
  }, [courses, searchTerm, filterTab, courseLessons, progress]);

  if (loading) {
    return (
      <main className="learning-page-v2">
        <div className="learning-container">
          <section className="learning-loading-v2">
            <div className="loading-spinner-v2" />
            <h2>Preparing your Learning Hub...</h2>
            <p>Fetching courses, lessons, and progress data.</p>
          </section>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="learning-page-v2">
        <div className="learning-container">
          <section className="learning-state-v2">
            <div className="state-icon-v2">⚠️</div>
            <h2>Unable to load learning space</h2>
            <p>{error}</p>
            <button className="retry-btn-v2" onClick={loadLearningData}>
              Try Again
            </button>
          </section>
        </div>
      </main>
    );
  }

  return (
    <main className="learning-page-v2">
      <div className="learning-container">
        {/* Hero Section */}
        <section className="learning-hero-v2">
          <div className="hero-v2-info">
            <span className="hero-eyebrow">🚀 CODESPHERE LEARNING HUB</span>
            <h1>
              Master technical skills.
              <br />
              <span className="hero-gradient-text">Build real-world software.</span>
            </h1>
            <p>
              Interactive structured courses, real code lessons, and automated progress tracking to accelerate your engineering career.
            </p>
          </div>

          <div className="hero-v2-actions">
            <Link to="/learning/analytics" className="btn-analytics-link">
              <span>📊 View Learning Analytics</span>
              <span>→</span>
            </Link>
          </div>
        </section>

        {/* Statistics Metric Cards */}
        <section className="overview-stats-grid">
          <div className="stat-card-v2">
            <div className="stat-card-icon stat-icon-blue">📚</div>
            <div className="stat-card-data">
              <span className="stat-num">{courses.length}</span>
              <span className="stat-lbl">Available Courses</span>
            </div>
          </div>

          <div className="stat-card-v2">
            <div className="stat-card-icon stat-icon-purple">📑</div>
            <div className="stat-card-data">
              <span className="stat-num">{totalLessons}</span>
              <span className="stat-lbl">Total Lessons</span>
            </div>
          </div>

          <div className="stat-card-v2">
            <div className="stat-card-icon stat-icon-green">✅</div>
            <div className="stat-card-data">
              <span className="stat-num">{completedLessons}</span>
              <span className="stat-lbl">Completed Lessons</span>
            </div>
          </div>

          <div className="stat-card-v2">
            <div className="stat-card-icon stat-icon-amber">⚡</div>
            <div className="stat-card-data">
              <span className="stat-num">{overallPercent}%</span>
              <span className="stat-lbl">Overall Completion</span>
            </div>
          </div>
        </section>

        {/* Toolbar: Search & Category Filter */}
        <section className="learning-toolbar">
          <div className="search-box-wrap">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              placeholder="Search courses by title or keyword..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            {searchTerm && (
              <button className="clear-search-btn" onClick={() => setSearchTerm("")}>
                ✕
              </button>
            )}
          </div>

          <div className="filter-tab-group">
            <button
              className={`filter-tab-btn ${filterTab === "all" ? "active" : ""}`}
              onClick={() => setFilterTab("all")}
            >
              All Courses ({courses.length})
            </button>
            <button
              className={`filter-tab-btn ${filterTab === "in-progress" ? "active" : ""}`}
              onClick={() => setFilterTab("in-progress")}
            >
              In Progress
            </button>
            <button
              className={`filter-tab-btn ${filterTab === "completed" ? "active" : ""}`}
              onClick={() => setFilterTab("completed")}
            >
              Completed
            </button>
          </div>
        </section>

        {/* Courses Section */}
        <section className="courses-display-section">
          {filteredCourses.length === 0 ? (
            <div className="empty-courses-card">
              <div className="empty-icon-circle">📂</div>
              <h3>
                {searchTerm
                  ? `No courses matching "${searchTerm}"`
                  : filterTab !== "all"
                  ? `No courses in "${filterTab}"`
                  : "No courses available yet"}
              </h3>
              <p>
                {courses.length === 0
                  ? "New courses will appear here automatically when published by your administrator."
                  : "Try resetting your search query or switching tabs."}
              </p>
              {(searchTerm || filterTab !== "all") && (
                <button
                  className="reset-filters-btn"
                  onClick={() => {
                    setSearchTerm("");
                    setFilterTab("all");
                  }}
                >
                  Reset Search & Filters
                </button>
              )}
            </div>
          ) : (
            <div className="courses-grid-v2">
              {filteredCourses.map((course) => {
                const lessons = courseLessons[course.id] || [];
                const courseProgress = calculateCourseProgress(lessons, progress);
                const completed = getCompletedLessonCount(lessons, progress);

                return (
                  <CourseCard
                    key={course.id}
                    course={course}
                    progress={courseProgress}
                    completedLessons={completed}
                    totalLessons={lessons.length}
                  />
                );
              })}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}

export default Courses;