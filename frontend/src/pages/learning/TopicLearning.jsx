import { useEffect, useState, useCallback } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import {
    getCourse,
    getCourseLessons,
    getLesson,
} from "../../services/learningApi";

import {
    getTopic,
    getNextTopic,
    getQuestionsForTopic,
    getCompletedQuestionsInTopic,
    markQuestionComplete,
    getTopicCompletion,
    getLessonCompletion,
} from "../../services/lmsApi";

import "./lms.css";


// ======================================================
// HELPERS
// ======================================================

function parseLines(text) {
    if (!text) return [];
    return text.split("\n").filter((l) => l.trim().length > 0);
}

function detectLanguage(code) {
    if (!code) return "code";
    if (/import\s+React|jsx|useState|useEffect/.test(code)) return "jsx";
    if (/def |import |print\(|#/.test(code)) return "python";
    if (/const |let |var |function |=>/.test(code)) return "js";
    if (/SELECT|INSERT|FROM|WHERE/i.test(code)) return "sql";
    return "code";
}


// ======================================================
// TOPIC LEARNING PAGE
// ======================================================

function TopicLearning() {
    const { courseId, lessonId, topicId } = useParams();
    const navigate = useNavigate();

    // Data
    const [course, setCourse] = useState(null);
    const [lesson, setLesson] = useState(null);
    const [lessons, setLessons] = useState([]);
    const [topic, setTopic] = useState(null);
    const [questions, setQuestions] = useState([]);
    const [nextTopicData, setNextTopicData] = useState(null);

    // State
    const [currentIndex, setCurrentIndex] = useState(0);
    const [completedIds, setCompletedIds] = useState(new Set());
    const [topicCompletion, setTopicCompletion] = useState(null);
    const [lessonCompletion, setLessonCompletion] = useState(null);
    const [showTopicDone, setShowTopicDone] = useState(false);
    const [showLessonDone, setShowLessonDone] = useState(false);
    const [showCourseDone, setShowCourseDone] = useState(false);

    const [loading, setLoading] = useState(true);
    const [marking, setMarking] = useState(false);
    const [error, setError] = useState("");


    // ======================================================
    // LOAD ALL DATA
    // ======================================================

    const loadData = useCallback(async () => {
        try {
            setLoading(true);
            setError("");

            const [
                courseData,
                lessonData,
                lessonsData,
                topicData,
                questionsData,
            ] = await Promise.all([
                getCourse(courseId),
                getLesson(lessonId),
                getCourseLessons(courseId),
                getTopic(topicId),
                getQuestionsForTopic(topicId),
            ]);

            setCourse(courseData);
            setLesson(lessonData);
            setLessons(Array.isArray(lessonsData) ? lessonsData : []);
            setTopic(topicData);

            const qs = Array.isArray(questionsData) ? questionsData : [];
            setQuestions(qs);

            // Completed question IDs for this topic
            try {
                const compData = await getCompletedQuestionsInTopic(topicId);
                const ids = new Set(
                    (compData?.completed_question_ids || []).map(Number)
                );
                setCompletedIds(ids);
            } catch {
                setCompletedIds(new Set());
            }

            // Next topic
            try {
                const nt = await getNextTopic(topicId);
                setNextTopicData(nt);
            } catch {
                setNextTopicData(null);
            }

            // Topic completion
            try {
                const tc = await getTopicCompletion(topicId);
                setTopicCompletion(tc);
                if (tc.is_complete) setShowTopicDone(true);
            } catch {
                setTopicCompletion(null);
            }

            // Lesson completion
            try {
                const lc = await getLessonCompletion(lessonId);
                setLessonCompletion(lc);
            } catch {
                setLessonCompletion(null);
            }

        } catch (err) {
            setError(err.message || "Unable to load topic content.");
        } finally {
            setLoading(false);
        }
    }, [courseId, lessonId, topicId]);

    useEffect(() => {
        setCurrentIndex(0);
        setShowTopicDone(false);
        setShowLessonDone(false);
        setShowCourseDone(false);
        void loadData();
    }, [loadData]);


    // ======================================================
    // MARK QUESTION COMPLETE
    // ======================================================

    const handleMarkComplete = async () => {
        if (!currentQuestion) return;
        const qId = currentQuestion.id;

        if (completedIds.has(qId)) {
            // Already done — just advance
            advanceAfterComplete();
            return;
        }

        try {
            setMarking(true);
            await markQuestionComplete(qId);

            const newCompleted = new Set(completedIds);
            newCompleted.add(qId);
            setCompletedIds(newCompleted);

            // Refresh completion data
            const [tc, lc] = await Promise.all([
                getTopicCompletion(topicId),
                getLessonCompletion(lessonId),
            ]);
            setTopicCompletion(tc);
            setLessonCompletion(lc);

            advanceAfterComplete(tc, lc, newCompleted);
        } catch (err) {
            alert(err.message || "Unable to save progress.");
        } finally {
            setMarking(false);
        }
    };

    const advanceAfterComplete = (tc, lc, newCompleted) => {
        const isLastQuestion = currentIndex >= questions.length - 1;

        if (!isLastQuestion) {
            setCurrentIndex((i) => i + 1);
            return;
        }

        // Last question — check topic / lesson / course completion
        const topicDone = tc?.is_complete ?? (
            newCompleted && questions.every((q) => newCompleted.has(q.id))
        );

        if (topicDone) {
            const lessonDone = lc?.is_complete ?? false;
            if (lessonDone) {
                // Check if there's a next lesson
                const lessonIndex = lessons.findIndex(
                    (l) => Number(l.id) === Number(lessonId)
                );
                const hasNextLesson =
                    lessonIndex >= 0 && lessonIndex < lessons.length - 1;

                if (!hasNextLesson) {
                    setShowCourseDone(true);
                } else {
                    setShowLessonDone(true);
                }
            } else {
                setShowTopicDone(true);
            }
        } else {
            setShowTopicDone(false);
        }
    };


    // ======================================================
    // DERIVED STATE
    // ======================================================

    const currentQuestion = questions[currentIndex] || null;
    const progressPct =
        questions.length > 0
            ? Math.round((completedIds.size / questions.length) * 100)
            : 0;

    const lessonIndex = lessons.findIndex(
        (l) => Number(l.id) === Number(lessonId)
    );
    const nextLesson =
        lessonIndex >= 0 && lessonIndex < lessons.length - 1
            ? lessons[lessonIndex + 1]
            : null;


    // ======================================================
    // RENDER LOADING / ERROR
    // ======================================================

    if (loading) {
        return (
            <main className="topic-page">
                <div className="lms-loading">
                    <div className="lms-spinner" />
                    <h2>Loading topic...</h2>
                </div>
            </main>
        );
    }

    if (error || !topic) {
        return (
            <main className="topic-page">
                <div className="lms-error">
                    <span style={{ fontSize: 48 }}>⚠️</span>
                    <h2>Unable to load topic</h2>
                    <p>{error}</p>
                    <Link
                        to={`/learning/course/${courseId}/lesson/${lessonId}`}
                        className="btn-review"
                    >
                        ← Back to Lesson
                    </Link>
                </div>
            </main>
        );
    }

    // Empty topic
    if (questions.length === 0) {
        return (
            <main className="topic-page">
                <TopBar
                    course={course}
                    lesson={lesson}
                    topic={topic}
                    courseId={courseId}
                    lessonId={lessonId}
                    progressPct={0}
                    completedCount={0}
                    totalCount={0}
                />
                <div className="lms-error">
                    <span style={{ fontSize: 48 }}>📭</span>
                    <h2>No questions yet</h2>
                    <p>The administrator hasn't added any questions to this topic.</p>
                    <Link
                        to={`/learning/course/${courseId}/lesson/${lessonId}`}
                        className="btn-review"
                    >
                        ← Back to Lesson
                    </Link>
                </div>
            </main>
        );
    }


    // ======================================================
    // RENDER COURSE COMPLETED
    // ======================================================

    if (showCourseDone) {
        return (
            <main className="topic-page">
                <TopBar
                    course={course}
                    lesson={lesson}
                    topic={topic}
                    courseId={courseId}
                    lessonId={lessonId}
                    progressPct={100}
                    completedCount={questions.length}
                    totalCount={questions.length}
                />
                <div className="topic-layout" style={{ gridTemplateColumns: "1fr" }}>
                    <div className="completion-card">
                        <span className="completion-icon">🎓</span>
                        <h2>Course Completed!</h2>
                        <p>
                            Outstanding work! You've completed every lesson in{" "}
                            <strong>{course?.title}</strong>.
                        </p>
                        <div className="completion-actions">
                            <Link
                                to={`/learning/course/${courseId}`}
                                className="btn-next-topic"
                            >
                                View Course Summary →
                            </Link>
                            <Link to="/learning" className="btn-review">
                                All Courses
                            </Link>
                        </div>
                    </div>
                </div>
            </main>
        );
    }


    // ======================================================
    // RENDER LESSON COMPLETED
    // ======================================================

    if (showLessonDone) {
        return (
            <main className="topic-page">
                <TopBar
                    course={course}
                    lesson={lesson}
                    topic={topic}
                    courseId={courseId}
                    lessonId={lessonId}
                    progressPct={100}
                    completedCount={questions.length}
                    totalCount={questions.length}
                />
                <div className="topic-layout" style={{ gridTemplateColumns: "1fr" }}>
                    <div className="completion-card">
                        <span className="completion-icon">🏆</span>
                        <h2>Lesson Completed!</h2>
                        <p>
                            Excellent! You've mastered all topics in{" "}
                            <strong>{lesson?.title}</strong>.
                        </p>
                        <div className="completion-actions">
                            {nextLesson && (
                                <Link
                                    to={`/learning/course/${courseId}/lesson/${nextLesson.id}`}
                                    className="btn-next-topic"
                                >
                                    Next Lesson: {nextLesson.title} →
                                </Link>
                            )}
                            <Link
                                to={`/learning/course/${courseId}/lesson/${lessonId}`}
                                className="btn-review"
                            >
                                Review Lesson
                            </Link>
                        </div>
                    </div>
                </div>
            </main>
        );
    }


    // ======================================================
    // RENDER TOPIC COMPLETED
    // ======================================================

    if (showTopicDone) {
        return (
            <main className="topic-page">
                <TopBar
                    course={course}
                    lesson={lesson}
                    topic={topic}
                    courseId={courseId}
                    lessonId={lessonId}
                    progressPct={100}
                    completedCount={questions.length}
                    totalCount={questions.length}
                />
                <div className="topic-layout" style={{ gridTemplateColumns: "1fr" }}>
                    <div className="completion-card">
                        <span className="completion-icon">✅</span>
                        <h2>Topic Completed!</h2>
                        <p>
                            Great job! You've answered all questions in{" "}
                            <strong>{topic?.title}</strong>.
                        </p>
                        <div className="completion-actions">
                            {nextTopicData ? (
                                <Link
                                    to={`/learning/course/${courseId}/lesson/${lessonId}/topic/${nextTopicData.id}`}
                                    className="btn-next-topic"
                                >
                                    Next Topic: {nextTopicData.title} →
                                </Link>
                            ) : (
                                <Link
                                    to={`/learning/course/${courseId}/lesson/${lessonId}`}
                                    className="btn-next-topic"
                                >
                                    Back to Lesson →
                                </Link>
                            )}
                            <button
                                className="btn-review"
                                onClick={() => {
                                    setShowTopicDone(false);
                                    setCurrentIndex(0);
                                }}
                            >
                                Review Questions
                            </button>
                        </div>
                    </div>
                </div>
            </main>
        );
    }


    // ======================================================
    // RENDER QUESTION VIEW
    // ======================================================

    const isCurrentDone = currentQuestion
        ? completedIds.has(currentQuestion.id)
        : false;

    return (
        <main className="topic-page">
            <TopBar
                course={course}
                lesson={lesson}
                topic={topic}
                courseId={courseId}
                lessonId={lessonId}
                progressPct={progressPct}
                completedCount={completedIds.size}
                totalCount={questions.length}
            />

            <div className="topic-layout">
                {/* ======= SIDEBAR ======= */}
                <aside className="topic-sidebar">
                    <div className="sidebar-title">Questions</div>
                    <div className="sidebar-topic-name">{topic.title}</div>
                    <div className="sidebar-questions-list">
                        {questions.map((q, idx) => (
                            <button
                                key={q.id}
                                className={`sidebar-q-item ${idx === currentIndex ? "active" : ""} ${completedIds.has(q.id) ? "completed-q" : ""}`}
                                onClick={() => {
                                    setShowTopicDone(false);
                                    setCurrentIndex(idx);
                                }}
                            >
                                <span className="sq-num">{idx + 1}</span>
                                <span className="sq-text">{q.question}</span>
                                {completedIds.has(q.id) && (
                                    <span className="sq-check">✓</span>
                                )}
                            </button>
                        ))}
                    </div>
                </aside>

                {/* ======= MAIN CONTENT ======= */}
                <section className="topic-content">
                    <QuestionCard
                        question={currentQuestion}
                        questionNumber={currentIndex + 1}
                        topicTitle={topic.title}
                    />

                    {/* Mark Complete */}
                    <div className="mark-complete-bar">
                        {isCurrentDone ? (
                            <span className="btn-already-done">
                                ✓ Completed
                            </span>
                        ) : (
                            <button
                                className="btn-mark-complete"
                                onClick={handleMarkComplete}
                                disabled={marking}
                            >
                                {marking ? "Saving..." : "✓ Mark as Complete & Continue"}
                            </button>
                        )}
                    </div>

                    {/* Previous / Next Navigation */}
                    <div className="question-nav">
                        <button
                            className={`q-nav-btn ${currentIndex === 0 ? "invisible" : ""}`}
                            onClick={() => setCurrentIndex((i) => i - 1)}
                            disabled={currentIndex === 0}
                        >
                            ← Previous Question
                        </button>

                        <button
                            className={`q-nav-btn primary ${currentIndex >= questions.length - 1 ? "invisible" : ""}`}
                            onClick={() => setCurrentIndex((i) => i + 1)}
                            disabled={currentIndex >= questions.length - 1}
                        >
                            Next Question →
                        </button>
                    </div>
                </section>
            </div>
        </main>
    );
}


// ======================================================
// TOP BAR COMPONENT
// ======================================================

function TopBar({ course, lesson, topic, courseId, lessonId, progressPct, completedCount, totalCount }) {
    return (
        <div className="topic-topbar">
            <nav className="topic-breadcrumb">
                <Link to="/learning">Learning</Link>
                <span className="bc-sep">›</span>
                <Link to={`/learning/course/${courseId}`}>
                    {course?.title || "Course"}
                </Link>
                <span className="bc-sep">›</span>
                <Link to={`/learning/course/${courseId}/lesson/${lessonId}`}>
                    {lesson?.title || "Lesson"}
                </Link>
                <span className="bc-sep">›</span>
                <span className="bc-current">{topic?.title || "Topic"}</span>
            </nav>

            <div className="topic-progress-bar-wrap">
                <span>{completedCount}/{totalCount}</span>
                <div className="topic-prog-track">
                    <div
                        className="topic-prog-fill"
                        style={{ width: `${progressPct}%` }}
                    />
                </div>
                <span>{progressPct}%</span>
            </div>
        </div>
    );
}


// ======================================================
// QUESTION CARD COMPONENT
// ======================================================

function QuestionCard({ question, questionNumber, topicTitle }) {
    if (!question) return null;

    const keyPoints = question.key_points
        ? question.key_points
            .split("\n")
            .filter((l) => l.trim().length > 0)
        : [];

    const lang = detectLanguage(question.code_example);

    return (
        <article className="question-card">
            {/* Header */}
            <header className="question-card-header">
                <div className="q-meta">
                    <span className="q-number-badge">Q{questionNumber}</span>
                    <span className="q-topic-badge">{topicTitle}</span>
                </div>
                <h1 className="q-title">{question.question}</h1>
            </header>

            {/* Quick Answer */}
            {question.quick_answer && (
                <div className="quick-answer-box">
                    <div className="qa-label">Quick Answer</div>
                    <p>{question.quick_answer}</p>
                </div>
            )}

            <div className="question-sections">
                {/* Explanation */}
                {question.explanation && (
                    <Section icon="📖" label="Detailed Explanation">
                        <div className="q-section-body">
                            {question.explanation.split("\n").map((line, i) => (
                                line.trim() ? <p key={i}>{line}</p> : null
                            ))}
                        </div>
                    </Section>
                )}

                {/* Real World Example */}
                {question.real_world_example && (
                    <Section icon="🌍" label="Real-World Application">
                        <div className="q-section-body">
                            {question.real_world_example
                                .split("\n")
                                .map((line, i) =>
                                    line.trim() ? <p key={i}>{line}</p> : null
                                )}
                        </div>
                    </Section>
                )}

                {/* Code Example */}
                {question.code_example && (
                    <Section icon="💻" label="Code Example">
                        <div className="code-block-wrap">
                            <div className="code-block-header">
                                <span className="code-lang-tag">{lang}</span>
                            </div>
                            <pre>
                                <code>{question.code_example}</code>
                            </pre>
                        </div>
                    </Section>
                )}

                {/* Expected Output */}
                {question.expected_output && (
                    <Section icon="🖥️" label="Expected Output">
                        <div className="output-block">
                            <div className="output-label">Output</div>
                            <pre>{question.expected_output}</pre>
                        </div>
                    </Section>
                )}

                {/* Flowchart */}
                {question.flowchart && (
                    <Section icon="📊" label="Flow / Diagram">
                        <div className="flowchart-block">
                            <pre>{question.flowchart}</pre>
                        </div>
                    </Section>
                )}

                {/* Key Points */}
                {keyPoints.length > 0 && (
                    <Section icon="🔑" label="Key Points">
                        <ul className="key-points-list">
                            {keyPoints.map((point, i) => (
                                <li key={i}>{point}</li>
                            ))}
                        </ul>
                    </Section>
                )}

                {/* Remember This */}
                {question.remember_this && (
                    <Section icon="💡" label="Remember This">
                        <div className="remember-box">
                            <span className="remember-icon">💡</span>
                            <p className="remember-text">
                                {question.remember_this}
                            </p>
                        </div>
                    </Section>
                )}
            </div>
        </article>
    );
}


// ======================================================
// SECTION WRAPPER
// ======================================================

function Section({ icon, label, children }) {
    return (
        <div className="q-section">
            <div className="q-section-label">
                <span className="section-icon">{icon}</span>
                {label}
            </div>
            {children}
        </div>
    );
}


export default TopicLearning;
