import { useEffect, useState } from "react";
import {
    Link,
    useNavigate,
    useParams,
} from "react-router-dom";

import {
    getCourse,
    getCourseLessons,
    getLesson,
    getLessonProgress,
    updateLessonProgress,
    getAuthToken,
} from "../../services/learningApi";

import { getTopicsForLesson } from "../../services/lmsApi";

import "./learning.css";
import "./lms.css";


function LessonDetails() {

    const {
        courseId,
        lessonId,
    } = useParams();

    const navigate = useNavigate();


    const [course, setCourse] =
        useState(null);

    const [lesson, setLesson] =
        useState(null);

    const [lessons, setLessons] =
        useState([]);

    const [currentProgress, setCurrentProgress] =
        useState(0);

    const [loading, setLoading] =
        useState(true);

    const [saving, setSaving] =
        useState(false);

    const [error, setError] =
        useState("");

    const [topics, setTopics] = useState([]);
    const [topicsLoading, setTopicsLoading] = useState(true);
    const [topicsError, setTopicsError] = useState("");

    // Topics are expanded by default; learners can collapse them when needed.
    const [expandedTopics, setExpandedTopics] = useState(true);

    async function loadTopics(selectedLessonId) {
        setTopics([]);
        setTopicsError("");
        setTopicsLoading(true);

        try {
            const topicsData =
                await getTopicsForLesson(selectedLessonId);

            if (!Array.isArray(topicsData)) {
                throw new Error("The topics response was not a list.");
            }

            setTopics(topicsData);
        } catch (err) {
            setTopicsError(
                err.message || "Unable to load topics for this lesson."
            );
        } finally {
            setTopicsLoading(false);
        }
    }


    async function loadLesson() {

        try {

            setLoading(true);
            setError("");

            const [
                courseData,
                lessonData,
                lessonsData,
            ] = await Promise.all([
                getCourse(courseId),
                getLesson(lessonId),
                getCourseLessons(courseId),
            ]);


            setCourse(courseData);

            setLesson(lessonData);

            setLessons(
                Array.isArray(lessonsData)
                    ? lessonsData
                    : []
            );


            if (getAuthToken()) {

                try {

                    const progressData =
                        await getLessonProgress(
                            lessonId
                        );

                    setCurrentProgress(
                        Number(
                            progressData
                                ?.completion_percentage ||
                            0
                        )
                    );

                } catch {

                    setCurrentProgress(0);

                }

            }

        } catch (err) {

            setError(
                err.message ||
                "Unable to load lesson."
            );

        } finally {

            setLoading(false);

        }

        // Topic loading stays independent of the lesson content and progress.
        void loadTopics(lessonId);
    }


    useEffect(() => {
        const load = window.setTimeout(() => {
            void loadLesson();
        }, 0);

        return () => window.clearTimeout(load);
    }, [courseId, lessonId]);


    async function markComplete() {

        if (!getAuthToken()) {

            alert(
                "Please login to save your progress."
            );

            navigate("/login");

            return;
        }


        try {

            setSaving(true);

            const result =
                await updateLessonProgress(
                    lessonId,
                    100
                );

            setCurrentProgress(
                Number(
                    result?.completion_percentage ||
                    100
                )
            );

        } catch (err) {

            alert(
                err.message ||
                "Unable to save progress."
            );

        } finally {

            setSaving(false);

        }
    }


    if (loading) {

        return (
            <main className="learning-page">

                <section className="learning-loading">

                    <div className="loading-spinner" />

                    <h2>
                        Loading lesson...
                    </h2>

                </section>

            </main>
        );
    }


    if (error || !lesson) {

        return (
            <main className="learning-page">

                <section className="learning-state">

                    <div className="state-icon">
                        !
                    </div>

                    <h2>
                        Unable to load lesson
                    </h2>

                    <p>
                        {error}
                    </p>

                    <Link
                        to={`/learning/course/${courseId}`}
                        className="retry-button"
                    >
                        Back to Course
                    </Link>

                </section>

            </main>
        );
    }


    const currentIndex =
        lessons.findIndex(
            (item) =>
                Number(item.id) ===
                Number(lessonId)
        );


    const previousLesson =
        currentIndex > 0
            ? lessons[currentIndex - 1]
            : null;


    const nextLesson =
        currentIndex >= 0 &&
            currentIndex < lessons.length - 1
            ? lessons[currentIndex + 1]
            : null;


    return (
        <main className="lesson-page">

            {/* =========================================
                TOP BAR
            ========================================== */}

            <div className="lesson-topbar">

                <Link
                    to={`/learning/course/${courseId}`}
                    className="back-link"
                >
                    ← {course?.title}
                </Link>

                <span>
                    Lesson{" "}
                    {currentIndex + 1} of{" "}
                    {lessons.length}
                </span>

            </div>


            {/* =========================================
                LESSON HEADER
            ========================================== */}

            <section className="lesson-header">

                <span className="eyebrow">
                    LESSON {String(
                        currentIndex + 1
                    ).padStart(2, "0")}
                </span>

                <h1>
                    {lesson.title}
                </h1>

                {lesson.important_concepts && (
                    <p className="lesson-concepts">
                        {lesson.important_concepts}
                    </p>
                )}

            </section>


            {/* =========================================
                VIDEO
            ========================================== */}

            {lesson.youtube_url && (

                <section className="lesson-video">

                    <iframe
                        src={getYoutubeEmbedUrl(
                            lesson.youtube_url
                        )}
                        title={lesson.title}
                        allowFullScreen
                    />

                </section>

            )}


            {/* =========================================
                NOTES
            ========================================== */}

            <section className="lesson-body">

                <div className="lesson-main-content">

                    <span className="eyebrow">
                        LESSON NOTES
                    </span>

                    <div className="lesson-notes">

                        {lesson.notes ? (
                            lesson.notes
                        ) : (
                            <p>
                                No notes have been
                                added for this lesson yet.
                            </p>
                        )}

                    </div>

                </div>


                {/* =====================================
                    PROGRESS PANEL
                ====================================== */}

                <aside className="lesson-sidebar">

                    <div className="progress-panel">

                        <span className="eyebrow">
                            YOUR PROGRESS
                        </span>

                        <strong>
                            {Math.round(
                                currentProgress
                            )}%
                        </strong>

                        <div className="progress-track">

                            <div
                                className="progress-fill"
                                style={{
                                    width: `${currentProgress}%`,
                                }}
                            />

                        </div>


                        {currentProgress >= 100 ? (

                            <div className="completed-message">
                                ✓ Lesson completed
                            </div>

                        ) : (

                            <button
                                className="complete-button"
                                onClick={
                                    markComplete
                                }
                                disabled={saving}
                            >
                                {saving
                                    ? "Saving..."
                                    : "Mark as Complete"}
                            </button>

                        )}

                    </div>

                </aside>

            </section>


            {/* =========================================
                NAVIGATION
            ========================================== */}

            <section className="lesson-navigation">

                {previousLesson ? (

                    <Link
                        to={`/learning/course/${courseId}/lesson/${previousLesson.id}`}
                        className="lesson-nav-button"
                    >
                        <span>
                            Previous
                        </span>

                        <strong>
                            ← {previousLesson.title}
                        </strong>
                    </Link>

                ) : (
                    <div />
                )}


                {nextLesson ? (

                    <Link
                        to={`/learning/course/${courseId}/lesson/${nextLesson.id}`}
                        className="lesson-nav-button next"
                    >
                        <span>
                            Next Lesson
                        </span>

                        <strong>
                            {nextLesson.title} →
                        </strong>
                    </Link>

                ) : (

                    <Link
                        to={`/learning/course/${courseId}`}
                        className="lesson-nav-button next"
                    >
                        <span>
                            Course
                        </span>

                        <strong>
                            Finish Course →
                        </strong>
                    </Link>

                )}

            </section>

            {/* =========================================
                TOPICS SECTION — expandable topic list
            ========================================== */}

            <section className="lesson-topics-section">
                <div className="lesson-topics-panel">
                    <button
                        type="button"
                        className="lesson-topics-toggle"
                        onClick={() => setExpandedTopics((expanded) => !expanded)}
                        aria-expanded={expandedTopics}
                        aria-controls="lesson-topics-content"
                    >
                        <span className="lesson-topics-toggle-copy">
                            <span className="lesson-topics-eyebrow">CONTINUE LEARNING</span>
                            <span className="lesson-topics-toggle-title">Topics in This Lesson</span>
                            <span className="lesson-topics-toggle-subtitle">
                                {topicsLoading
                                    ? "Loading lesson topics..."
                                    : topicsError
                                        ? "Topics could not be loaded."
                                        : topics.length === 0
                                            ? "No topics available for this lesson yet."
                                            : `${topics.length} ${topics.length === 1 ? "topic" : "topics"} · Learn step by step`}
                            </span>
                        </span>
                        <span className="lesson-topics-toggle-side">
                            <span className="lesson-topics-completion">
                                {topics.filter((topic) => {
                                    const total = Number(topic.total_questions || 0);
                                    const completed = Number(topic.completed_questions || 0);
                                    return total > 0 && completed >= total;
                                }).length}/{topics.length} completed
                            </span>
                            <span className={`lesson-topics-chevron ${expandedTopics ? "is-expanded" : ""}`} aria-hidden="true">
                               ⌄
                            </span>
                        </span>
                    </button>

                    <div
                        id="lesson-topics-content"
                        className={`lesson-topics-content ${expandedTopics ? "is-open" : "is-closed"}`}
                        hidden={!expandedTopics}
                    >
                        {topicsLoading ? (
                            <div className="no-topics-msg lesson-topics-empty-state" role="status">
                                <strong>Loading topics...</strong>
                            </div>
                        ) : topicsError ? (
                            <div className="no-topics-msg lesson-topics-empty-state" role="alert">
                                <strong>Unable to load topics</strong>
                                <span>{topicsError}</span>
                            </div>
                        ) : topics.length === 0 ? (
                            <div className="no-topics-msg lesson-topics-empty-state">
                                <span className="lesson-topics-empty-icon">📚</span>
                                <strong>No topics available for this lesson yet.</strong>
                            </div>
                        ) : (
                            <div className="topics-grid">
                                {topics.map((topic, index) => {
                                    const totalQuestions = Number(topic.total_questions || 0);
                                    const completedQuestions = Number(topic.completed_questions || 0);
                                    const pct = totalQuestions > 0
                                        ? Math.min(100, Math.round((completedQuestions / totalQuestions) * 100))
                                        : 0;
                                    const isDone = totalQuestions > 0 && pct >= 100;

                                    return (
                                        <Link
                                            key={topic.id}
                                            to={`/learning/course/${courseId}/lesson/${lessonId}/topic/${topic.id}`}
                                            className={`topic-card-link lesson-topic-card ${isDone ? "topic-completed" : ""}`}
                                        >
                                            <div className="topic-num-circle">
                                                {isDone ? "✓" : (topic.topic_number || index + 1)}
                                            </div>
                                            <div className="topic-card-info">
                                                <span className="topic-card-title">{topic.title}</span>
                                                {topic.description && (
                                                    <span className="lesson-topic-description">{topic.description}</span>
                                                )}
                                                <div className="topic-card-meta">
                                                    <span className="topic-card-qcount">
                                                        {completedQuestions}/{totalQuestions} questions completed
                                                    </span>
                                                    <span className="topic-card-pct">{pct}%</span>
                                                </div>
                                                <div
                                                    className="topic-mini-progress"
                                                    role="progressbar"
                                                    aria-label={`${topic.title} progress`}
                                                    aria-valuemin={0}
                                                    aria-valuemax={100}
                                                    aria-valuenow={pct}
                                                >
                                                    <div
                                                        className="topic-mini-fill"
                                                        style={{ width: `${pct}%` }}
                                                    />
                                                </div>
                                            </div>
                                            <span className="topic-card-arrow" aria-hidden="true">→</span>
                                        </Link>
                                    );
                                })}
                            </div>
                        )}
                    </div>
                </div>
            </section>

        </main>
    );
}


// ======================================================
// YOUTUBE URL HELPER
// ======================================================

function getYoutubeEmbedUrl(url) {

    if (!url) {
        return "";
    }

    try {

        const parsed =
            new URL(url);

        let videoId = "";


        if (
            parsed.hostname.includes(
                "youtube.com"
            )
        ) {

            videoId =
                parsed.searchParams.get(
                    "v"
                ) || "";

        } else if (
            parsed.hostname.includes(
                "youtu.be"
            )
        ) {

            videoId =
                parsed.pathname
                    .replace("/", "");
        }


        if (!videoId) {
            return url;
        }


        return `https://www.youtube.com/embed/${videoId}`;

    } catch {

        return url;

    }
}


export default LessonDetails;