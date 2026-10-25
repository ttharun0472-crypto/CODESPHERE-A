import { Link } from "react-router-dom";

function CourseCard({
  course,
  progress = 0,
  completedLessons = 0,
  totalLessons = 0,
}) {
  const isCompleted = progress >= 100 && totalLessons > 0;
  const isInProgress = progress > 0 && progress < 100;

  // Generate dynamic icon / badge initial
  const iconLetter = course.title?.charAt(0)?.toUpperCase() || "C";

  // Categorize badge color theme based on ID/title
  const getBadgeStyle = (id) => {
    const styles = [
      { bg: "linear-gradient(135deg, #6366f1, #4f46e5)", text: "#ffffff" },
      { bg: "linear-gradient(135deg, #0ea5e9, #0284c7)", text: "#ffffff" },
      { bg: "linear-gradient(135deg, #10b981, #059669)", text: "#ffffff" },
      { bg: "linear-gradient(135deg, #8b5cf6, #7c3aed)", text: "#ffffff" },
      { bg: "linear-gradient(135deg, #f59e0b, #d97706)", text: "#ffffff" },
    ];
    return styles[(id || 0) % styles.length];
  };

  const badgeStyle = getBadgeStyle(course.id);

  return (
    <article className="course-card-v2">
      <div className="course-card-banner" style={{ background: badgeStyle.bg }}>
        <div className="course-icon-v2">
          {iconLetter}
        </div>

        <div className="course-status-pill">
          {isCompleted && <span className="status-badge status-completed">Completed ✓</span>}
          {isInProgress && <span className="status-badge status-in-progress">In Progress</span>}
          {!isCompleted && !isInProgress && <span className="status-badge status-new">Start Course</span>}
        </div>
      </div>

      <div className="course-card-body">
        <h3 className="course-card-title">{course.title || "Untitled Course"}</h3>

        <p className="course-card-desc">
          {course.description || "Master core concepts through hands-on structured lessons and real-world code examples."}
        </p>

        <div className="course-progress-wrapper">
          <div className="progress-label-row">
            <span className="progress-text">{completedLessons} of {totalLessons} Lessons</span>
            <span className="progress-percent">{progress}%</span>
          </div>

          <div className="progress-bar-bg">
            <div
              className={`progress-bar-fill ${isCompleted ? "fill-completed" : ""}`}
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <div className="course-card-footer">
          <Link to={`/learning/course/${course.id}`} className="btn-course-action">
            <span>{isCompleted ? "Review Course" : isInProgress ? "Continue Learning" : "Start Course"}</span>
            <span className="btn-arrow">→</span>
          </Link>
        </div>
      </div>
    </article>
  );
}

export default CourseCard;