import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  completeInterview,
  getActiveInterview,
  getAvailableInterviewQuestions,
  getCompletedInterviewCourses,
  getInterviewHistory,
  getInterviewSummary,
  startInterview,
  submitInterviewAnswer,
} from "../../services/interviewApi";
import { getCourses } from "../../services/learningApi";
import "./AIInterview.css";

const EMPTY_SUMMARY = {
  total_completed: 0,
  average_score: null,
  recent_sessions: [],
};

function errorMessage(error) {
  return error instanceof Error ? error.message : "An unexpected error occurred.";
}

function sessionAnswers(session) {
  return Object.fromEntries(
    (session?.questions || []).map((question) => [
      question.question_index,
      question.answer || "",
    ])
  );
}

function AIInterview() {
  const [courses, setCourses] = useState([]);
  const [completedCourses, setCompletedCourses] = useState([]);
  const [selectedCourseId, setSelectedCourseId] = useState("");
  const [availableQuestionData, setAvailableQuestionData] = useState(null);
  const [loadingQuestionBank, setLoadingQuestionBank] = useState(false);
  const [summary, setSummary] = useState(EMPTY_SUMMARY);
  const [history, setHistory] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [selectedResult, setSelectedResult] = useState(null);
  const [draftAnswers, setDraftAnswers] = useState({});
  const [currentIndex, setCurrentIndex] = useState(0);

  const [category, setCategory] = useState("technical");
  const [difficulty, setDifficulty] = useState("medium");
  const [numberOfQuestions, setNumberOfQuestions] = useState(5);
  const [durationMinutes, setDurationMinutes] = useState("30");

  const [loadingData, setLoadingData] = useState(true);
  const [starting, setStarting] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [finishing, setFinishing] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [learningWarning, setLearningWarning] = useState("");
  const [clockNow, setClockNow] = useState(0);

  const loadDashboard = useCallback(async () => {
    setLoadingData(true);
    setError("");
    const [
      coursesResult,
      completedCoursesResult,
      summaryResult,
      historyResult,
      activeResult,
    ] =
      await Promise.allSettled([
        getCourses(),
        getCompletedInterviewCourses(),
        getInterviewSummary(),
        getInterviewHistory(),
        getActiveInterview(),
      ]);

    if (coursesResult.status === "fulfilled") {
      setCourses(coursesResult.value);
    } else {
      setCourses([]);
      setError(`Unable to load Learning Module courses: ${errorMessage(coursesResult.reason)}`);
    }

    if (completedCoursesResult.status === "fulfilled") {
      setCompletedCourses(completedCoursesResult.value?.completed_courses || []);
      setLearningWarning("");
    } else {
      setCompletedCourses([]);
      setLearningWarning(
        "Course completion data is unavailable right now. Available courses can still be used for interview practice."
      );
    }

    if (summaryResult.status === "fulfilled") {
      setSummary(summaryResult.value);
    } else {
      setSummary(EMPTY_SUMMARY);
      setError((previous) =>
        [previous, `Unable to load interview statistics: ${errorMessage(summaryResult.reason)}`]
          .filter(Boolean)
          .join(" ")
      );
    }

    if (historyResult.status === "fulfilled") {
      setHistory(historyResult.value);
    } else {
      setHistory([]);
      setError((previous) =>
        [previous, `Unable to load interview history: ${errorMessage(historyResult.reason)}`]
          .filter(Boolean)
          .join(" ")
      );
    }

    if (activeResult.status === "fulfilled") {
      setActiveSession(activeResult.value);
      setDraftAnswers(sessionAnswers(activeResult.value));
      if (activeResult.value?.course_id) {
        setSelectedCourseId(String(activeResult.value.course_id));
      }
      const firstUnanswered = activeResult.value?.questions?.findIndex(
        (question) => !question.evaluation
      );
      setCurrentIndex(firstUnanswered >= 0 ? firstUnanswered : 0);
    } else {
      setActiveSession(null);
      setError((previous) =>
        [previous, `Unable to restore your active interview: ${errorMessage(activeResult.reason)}`]
          .filter(Boolean)
          .join(" ")
      );
    }
    setLoadingData(false);
  }, []);

  useEffect(() => {
    const loadTimer = window.setTimeout(() => loadDashboard(), 0);
    return () => window.clearTimeout(loadTimer);
  }, [loadDashboard]);

  useEffect(() => {
    if (!activeSession?.duration_minutes) return undefined;
    const updateClock = () => setClockNow(Date.now());
    const firstUpdate = window.setTimeout(updateClock, 0);
    const timer = window.setInterval(updateClock, 1000);
    return () => {
      window.clearTimeout(firstUpdate);
      window.clearInterval(timer);
    };
  }, [activeSession]);

  useEffect(() => {
    let cancelled = false;
    const timer = window.setTimeout(async () => {
      const courseRequired = category === "technical" || category === "mixed";
      if (courseRequired && !selectedCourseId) {
        setAvailableQuestionData(null);
        setLoadingQuestionBank(false);
        return;
      }
      setLoadingQuestionBank(true);
      try {
        const data = await getAvailableInterviewQuestions({
          courseId:
            courseRequired && selectedCourseId ? Number(selectedCourseId) : null,
          category,
          difficulty,
        });
        if (!cancelled) {
          setAvailableQuestionData(data);
          setNumberOfQuestions((current) =>
            Math.min(Math.max(1, current), data.available_count)
          );
        }
      } catch (requestError) {
        if (!cancelled) {
          setAvailableQuestionData(null);
          setError(`Unable to load default interview questions: ${errorMessage(requestError)}`);
        }
      } finally {
        if (!cancelled) setLoadingQuestionBank(false);
      }
    }, 0);
    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [category, difficulty, selectedCourseId]);

  const activeQuestion = activeSession?.questions?.[currentIndex];
  const resultSession = selectedResult;
  const answeredQuestionCount =
    activeSession?.questions?.filter((question) => question.evaluation).length || 0;
  const deadline = activeSession?.duration_minutes
    ? new Date(activeSession.created_at).getTime() +
      activeSession.duration_minutes * 60 * 1000
    : null;
  const remainingSeconds =
    deadline === null || clockNow === 0
      ? null
      : Math.max(0, Math.ceil((deadline - clockNow) / 1000));
  const timeExpired = remainingSeconds === 0;
  const timeRemainingLabel =
    remainingSeconds === null
      ? null
      : `${Math.floor(remainingSeconds / 60)}:${String(remainingSeconds % 60).padStart(2, "0")}`;

  async function handleStartInterview(event) {
    event.preventDefault();
    const courseRequired = category === "technical" || category === "mixed";
    if (courseRequired && !selectedCourseId) {
      setError("Select a Learning Module course before starting this interview.");
      return;
    }
    if (
      !availableQuestionData ||
      numberOfQuestions < 1 ||
      numberOfQuestions > availableQuestionData.available_count
    ) {
      setError("Choose a question count within the available default question bank.");
      return;
    }
    const duration = durationMinutes === "" ? null : Number(durationMinutes);
    if (duration !== null && (!Number.isInteger(duration) || duration < 5 || duration > 180)) {
      setError("Interview duration must be between 5 and 180 minutes.");
      return;
    }

    setStarting(true);
    setError("");
    setNotice("");
    try {
      const session = await startInterview({
        category,
        course_id: courseRequired ? Number(selectedCourseId) : null,
        difficulty,
        number_of_questions: Number(numberOfQuestions),
        duration_minutes: duration,
      });
      setActiveSession(session);
      setSelectedCourseId(session.course_id ? String(session.course_id) : "");
      setDraftAnswers(sessionAnswers(session));
      setCurrentIndex(0);
      setSelectedResult(null);
      setNotice(
        session.question_source === "ai"
          ? "Your AI-generated interview is ready."
          : "Your interview is ready using the course question bank."
      );
    } catch (requestError) {
      setError(errorMessage(requestError));
    } finally {
      setStarting(false);
    }
  }

  async function handleSubmitAnswer(event) {
    event.preventDefault();
    if (!activeSession || !activeQuestion || submitting) return;
    const answer = (draftAnswers[currentIndex] || "").trim();
    if (!answer) {
      setError("Write an answer before submitting it.");
      return;
    }

    setSubmitting(true);
    setError("");
    setNotice("");
    try {
      const updatedSession = await submitInterviewAnswer(
        activeSession.id,
        currentIndex,
        answer
      );
      setActiveSession(updatedSession);
      setDraftAnswers(sessionAnswers(updatedSession));
      setNotice("Answer evaluated and saved.");
    } catch (requestError) {
      setError(errorMessage(requestError));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleFinishInterview() {
    if (!activeSession || finishing) return;
    const unanswered = activeSession.questions.length - answeredQuestionCount;
    if (
      unanswered > 0 &&
      !window.confirm(
        `You have ${unanswered} unanswered question${unanswered === 1 ? "" : "s"}. Finish this interview early?`
      )
    ) {
      return;
    }

    setFinishing(true);
    setError("");
    setNotice("");
    try {
      const completed = await completeInterview(activeSession.id);
      setActiveSession(null);
      setSelectedResult(completed);
      setHistory((current) => [
        completed,
        ...current.filter((item) => item.id !== completed.id),
      ]);
      try {
        setSummary(await getInterviewSummary());
      } catch (refreshError) {
        setError(
          `Interview completed, but dashboard statistics could not be refreshed: ${errorMessage(refreshError)}`
        );
      }
    } catch (requestError) {
      setError(errorMessage(requestError));
    } finally {
      setFinishing(false);
    }
  }

  function openResult(session) {
    setSelectedResult(session);
    setError("");
    setNotice("");
  }

  function startNewFromResults() {
    setSelectedResult(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  const resultQuestions = resultSession?.questions || [];
  const resultStrengths = [
    ...new Set(resultQuestions.flatMap((question) => question.evaluation?.strengths || [])),
  ];
  const resultImprovements = [
    ...new Set(
      resultQuestions.flatMap((question) => [
        ...(question.evaluation?.missing_concepts || []),
        ...(question.evaluation?.areas_for_improvement || []),
      ])
    ),
  ];
  const recommendedTopics = [
    ...new Set(
      (history[0]?.questions || []).flatMap((question) => [
        ...(question.evaluation?.missing_concepts || []),
        ...(question.evaluation?.areas_for_improvement || []),
      ])
    ),
  ].slice(0, 6);
  const recommendedLessons = completedCourses
    .flatMap((course) =>
      (course.lessons || [])
        .filter((lesson) => {
          const lessonTopics = [
            lesson.title,
            ...(lesson.topics || []).map((topic) => topic.title),
          ]
            .filter(Boolean)
            .map((title) => title.toLowerCase());
          return recommendedTopics.some((recommendation) => {
            const normalized = recommendation.toLowerCase();
            return lessonTopics.some(
              (title) =>
                title.includes(normalized) ||
                (normalized.length >= 4 && normalized.includes(title))
            );
          });
        })
        .map((lesson) => ({
          courseId: course.course_id,
          courseTitle: course.course_title,
          lessonId: lesson.lesson_id,
          lessonTitle: lesson.title,
        }))
    )
    .slice(0, 5);

  return (
    <main className="ai-interview-page">
      <div className="ai-interview-container">
        <header className="ai-interview-hero">
          <div className="ai-hero-content">
            <span className="ai-hero-badge">Welcome back · CODESPHERE AI</span>
            <h1>
              Prepare smarter.
              <br />
              <span>Interview with confidence.</span>
            </h1>
            <p>
              Practice tailored technical, HR, and communication interviews.
              Answer one question at a time and get structured, actionable feedback.
            </p>
            <div className="ai-hero-pills">
              <span>Course-based questions</span>
              <span>AI-evaluated answers</span>
              <span>Private interview history</span>
            </div>
            <Link className="ai-question-bank-link" to="/interview/questions">
              Browse question bank
            </Link>
          </div>
          <div className="ai-hero-visual" aria-hidden="true">
            <div className="ai-visual-orbit orbit-one"></div>
            <div className="ai-visual-orbit orbit-two"></div>
            <div className="ai-visual-center">
              <span>AI</span>
              <small>INTERVIEW</small>
            </div>
            <div className="ai-floating-icon ai-icon-one">✦</div>
            <div className="ai-floating-icon ai-icon-two">{"</>"}</div>
            <div className="ai-floating-icon ai-icon-three">✓</div>
          </div>
        </header>

        <section className="ai-overview-grid" aria-label="Interview statistics">
          <div className="ai-overview-card">
            <div className="ai-overview-icon purple">✦</div>
            <div>
              <span className="ai-overview-label">Interviews completed</span>
              <strong>{summary.total_completed}</strong>
              <small>Saved to your private history</small>
            </div>
          </div>
          <div className="ai-overview-card">
            <div className="ai-overview-icon blue">◎</div>
            <div>
              <span className="ai-overview-label">Average score</span>
              <strong>
                {summary.average_score === null ? "—" : `${summary.average_score}%`}
              </strong>
              <small>
                {summary.average_score === null
                  ? "Complete an interview to see your score"
                  : "Across completed interviews"}
              </small>
            </div>
          </div>
          <div className="ai-overview-card">
            <div className="ai-overview-icon green">▤</div>
            <div>
              <span className="ai-overview-label">Completed courses</span>
              <strong>{courses.length}</strong>
              <small>Available from the Learning Module</small>
            </div>
          </div>
        </section>

        {error && (
          <div className="ai-alert ai-alert-error" role="alert">
            <span>!</span>
            <div>{error}</div>
            <button type="button" onClick={() => setError("")} aria-label="Dismiss error">
              ×
            </button>
          </div>
        )}
        {notice && (
          <div className="ai-alert ai-alert-success" role="status">
            <span>✓</span>
            <div>{notice}</div>
            <button type="button" onClick={() => setNotice("")} aria-label="Dismiss message">
              ×
            </button>
          </div>
        )}
        {learningWarning && (
          <div className="ai-alert ai-alert-warning" role="status">
            <span>i</span>
            <div>{learningWarning}</div>
          </div>
        )}

        {loadingData ? (
          <div className="ai-panel ai-loading-panel" role="status">
            Loading your interview dashboard…
          </div>
        ) : resultSession ? (
          <section className="ai-panel ai-results-panel" aria-labelledby="ai-results-title">
            <div className="ai-section-heading">
              <div>
                <span className="ai-section-eyebrow">INTERVIEW REVIEW</span>
                <h2 id="ai-results-title">Your results</h2>
              </div>
              <div className="ai-result-score">
                <strong>
                  {resultSession.overall_score === null
                    ? "—"
                    : `${resultSession.overall_score}%`}
                </strong>
                <span>Overall score</span>
              </div>
            </div>
            <p className="ai-muted-text">
              {resultSession.course_title && `${resultSession.course_title} · `}
              {resultSession.category} · {resultSession.difficulty} ·{" "}
              {resultQuestions.filter((item) => item.evaluation).length} of{" "}
              {resultSession.total_questions} questions answered. Overall score is the
              arithmetic mean of evaluated answers.
            </p>
            <p className="ai-muted-text">
              Questions generated with{" "}
              {resultSession.question_source === "ai" ? "AI" : "the course question bank"}.
            </p>

            <div className="ai-feedback-columns">
              <section>
                <h3>Strengths</h3>
                {resultStrengths.length ? (
                  <ul>{resultStrengths.map((item) => <li key={item}>{item}</li>)}</ul>
                ) : (
                  <p>No evaluated answers are available.</p>
                )}
              </section>
              <section>
                <h3>Topics to improve</h3>
                {resultImprovements.length ? (
                  <ul>{resultImprovements.map((item) => <li key={item}>{item}</li>)}</ul>
                ) : (
                  <p>No improvement topics were identified.</p>
                )}
              </section>
            </div>

            <div className="ai-result-question-list">
              {resultQuestions.map((question) => (
                <article className="ai-result-question" key={question.question_index}>
                  <div className="ai-question-meta">
                    <span className="ai-question-number">
                      QUESTION {String(question.question_index + 1).padStart(2, "0")}
                    </span>
                    <span className="ai-question-category">{question.category}</span>
                    {question.evaluation && (
                      <span className="ai-result-question-score">
                        {question.evaluation.score}%
                      </span>
                    )}
                  </div>
                  <h3>{question.question}</h3>
                  <p className="ai-submitted-answer">
                    <strong>Your answer</strong>
                    {question.answer || "Not answered"}
                  </p>
                  {question.evaluation && (
                    <div className="ai-evaluation-detail">
                      <div className="ai-feedback-columns">
                        <section>
                          <h4>What went well</h4>
                          <ul>
                            {question.evaluation.strengths.map((item) => (
                              <li key={item}>{item}</li>
                            ))}
                          </ul>
                        </section>
                        <section>
                          <h4>Next attempt</h4>
                          <p>{question.evaluation.next_attempt_suggestion}</p>
                          <ul>
                            {question.evaluation.areas_for_improvement.map((item) => (
                              <li key={item}>{item}</li>
                            ))}
                          </ul>
                        </section>
                      </div>
                      <details>
                        <summary>View reference explanation</summary>
                        <p>{question.evaluation.model_answer}</p>
                      </details>
                    </div>
                  )}
                </article>
              ))}
            </div>
            <button type="button" className="ai-primary-button" onClick={startNewFromResults}>
              Back to interview dashboard
            </button>
          </section>
        ) : (
          <div className="ai-interview-layout">
            <aside className="ai-sidebar">
              <section className="ai-panel ai-courses-panel">
                <div className="ai-section-heading">
                  <div>
                    <span className="ai-section-eyebrow">LEARNING MODULE</span>
                    <h2>Available courses</h2>
                  </div>
                  <span className="ai-count-badge">{courses.length}</span>
                </div>
                <p className="ai-muted-text">
                  Choose a course to focus technical questions on its lessons and topics.
                </p>
                {courses.length ? (
                  <div className="ai-course-list">
                    {courses.map((course) => (
                      <button
                        type="button"
                        className={`ai-course-option${String(course.id) === selectedCourseId ? " selected" : ""}`}
                        key={course.id}
                        onClick={() => setSelectedCourseId(String(course.id))}
                      >
                        <strong>{course.title}</strong>
                        <small>{course.description || "Course-specific questions use its available lessons and topics."}</small>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="ai-empty-small">
                    <p>No Learning Module courses are available.</p>
                    <small>HR and communication interviews can still use general questions.</small>
                  </div>
                )}
              </section>
            </aside>

            <section className="ai-main-content">
              {activeSession ? (
                <section className="ai-panel ai-session-panel" aria-labelledby="ai-session-title">
                  <div className="ai-section-heading">
                    <div>
                      <span className="ai-section-eyebrow">INTERVIEW IN PROGRESS</span>
                      <h2 id="ai-session-title">Question {currentIndex + 1} of {activeSession.total_questions}</h2>
                    </div>
                    <div className="ai-session-badges">
                      {timeRemainingLabel !== null && (
                        <span className={`ai-timer-badge${timeExpired ? " expired" : ""}`}>
                          {timeExpired ? "Time expired" : `Time left ${timeRemainingLabel}`}
                        </span>
                      )}
                      <span className="ai-count-badge">{answeredQuestionCount} answered</span>
                    </div>
                  </div>
                  <div
                    className="ai-session-progress"
                    role="progressbar"
                    aria-label="Interview progress"
                    aria-valuemin="0"
                    aria-valuemax={activeSession.total_questions}
                    aria-valuenow={answeredQuestionCount}
                  >
                    <span
                      style={{
                        width: `${(answeredQuestionCount / activeSession.total_questions) * 100}%`,
                      }}
                    ></span>
                  </div>
                  {activeQuestion && (
                    <article className="ai-session-question">
                      <div className="ai-question-meta">
                        <span className="ai-question-number">
                          QUESTION {String(currentIndex + 1).padStart(2, "0")}
                        </span>
                        <span className="ai-question-category">{activeQuestion.category}</span>
                        <span className={`ai-question-difficulty ${activeQuestion.difficulty}`}>
                          {activeQuestion.difficulty}
                        </span>
                      </div>
                      <h3>{activeQuestion.question}</h3>
                      <form onSubmit={handleSubmitAnswer}>
                        <label htmlFor="ai-interview-answer">Your answer</label>
                        <textarea
                          id="ai-interview-answer"
                          rows={7}
                          maxLength={10000}
                          value={
                            draftAnswers[currentIndex] ?? activeQuestion.answer ?? ""
                          }
                          onChange={(event) =>
                            setDraftAnswers((current) => ({
                              ...current,
                              [currentIndex]: event.target.value,
                            }))
                          }
                          disabled={
                            Boolean(activeQuestion.evaluation) || submitting || timeExpired
                          }
                          placeholder="Explain your approach and reasoning…"
                        />
                        <div className="ai-answer-actions">
                          {activeQuestion.evaluation ? (
                            <span className="ai-answer-saved" role="status">
                              Evaluated · {activeQuestion.evaluation.score}%
                            </span>
                          ) : (
                            <button
                              type="submit"
                              className="ai-primary-button"
                              disabled={
                                submitting ||
                                timeExpired ||
                                !(draftAnswers[currentIndex] || "").trim()
                              }
                            >
                              {submitting ? "Evaluating answer…" : "Submit answer"}
                            </button>
                          )}
                          <span className="ai-character-count">
                            {(draftAnswers[currentIndex] || "").length}/10000
                          </span>
                        </div>
                      </form>
                      {activeQuestion.evaluation && (
                        <div className="ai-live-feedback">
                          <h4>Feedback</h4>
                          <p>
                            <strong>Strengths:</strong>{" "}
                            {activeQuestion.evaluation.strengths.join(" · ")}
                          </p>
                          {activeQuestion.evaluation.missing_concepts.length > 0 && (
                            <p>
                              <strong>Missing concepts:</strong>{" "}
                              {activeQuestion.evaluation.missing_concepts.join(" · ")}
                            </p>
                          )}
                          <p>
                            <strong>Try next:</strong>{" "}
                            {activeQuestion.evaluation.next_attempt_suggestion}
                          </p>
                        </div>
                      )}
                      <div className="ai-question-navigation">
                        <button
                          type="button"
                          className="ai-secondary-button"
                          onClick={() => setCurrentIndex((index) => Math.max(0, index - 1))}
                          disabled={currentIndex === 0 || submitting}
                        >
                          Previous
                        </button>
                        <span>{currentIndex + 1} of {activeSession.total_questions}</span>
                        <button
                          type="button"
                          className="ai-primary-button"
                          onClick={() =>
                            setCurrentIndex((index) =>
                              Math.min(activeSession.total_questions - 1, index + 1)
                            )
                          }
                          disabled={
                            currentIndex === activeSession.total_questions - 1 || submitting
                          }
                        >
                          Next question
                        </button>
                      </div>
                      <button
                        type="button"
                        className="ai-finish-button"
                        onClick={handleFinishInterview}
                        disabled={finishing}
                      >
                        {finishing ? "Saving results…" : "Finish interview"}
                      </button>
                    </article>
                  )}
                </section>
              ) : (
                <section className="ai-panel ai-generator-panel">
                  <div className="ai-section-heading">
                    <div>
                      <span className="ai-section-eyebrow">AI INTERVIEW STUDIO</span>
                      <h2>Build your interview</h2>
                    </div>
                    <div className="ai-live-indicator">
                      <span></span>AI with course-bank fallback
                    </div>
                  </div>
                  <p className="ai-muted-text">
                    Questions are based on the selected course's actual Learning Module
                    content. HR and communication formats use course-independent questions.
                  </p>
                  <form onSubmit={handleStartInterview} className="ai-config-form">
                    <div className="ai-generator-fields">
                      <div className="ai-form-field">
                        <label htmlFor="ai-category">Interview category</label>
                        <select
                          id="ai-category"
                          value={category}
                          onChange={(event) => setCategory(event.target.value)}
                        >
                          <option value="technical">Technical</option>
                          <option value="hr">HR / Behavioral</option>
                          <option value="communication">Communication</option>
                          <option value="mixed">Mixed</option>
                        </select>
                      </div>
                      <div className="ai-form-field">
                        <label htmlFor="ai-course">
                          Learning course{category === "hr" || category === "communication" ? " (optional)" : ""}
                        </label>
                        <select
                          id="ai-course"
                          value={selectedCourseId}
                          onChange={(event) => setSelectedCourseId(event.target.value)}
                          required={category === "technical" || category === "mixed"}
                          disabled={courses.length === 0}
                        >
                          <option value="">Choose a course</option>
                          {courses.map((course) => (
                            <option key={course.id} value={course.id}>{course.title}</option>
                          ))}
                        </select>
                        {selectedCourseId && (
                          <small className="ai-course-description">
                            {courses.find((course) => String(course.id) === selectedCourseId)?.description ||
                              "Questions use this course's available lessons and topics."}
                          </small>
                        )}
                      </div>
                      <div className="ai-form-field">
                        <label htmlFor="ai-difficulty">Difficulty</label>
                        <select
                          id="ai-difficulty"
                          value={difficulty}
                          onChange={(event) => setDifficulty(event.target.value)}
                        >
                          <option value="easy">Easy — Beginner</option>
                          <option value="medium">Medium — Intermediate</option>
                          <option value="hard">Hard — Advanced</option>
                        </select>
                      </div>
                      <div className="ai-form-field">
                        <label htmlFor="ai-question-count">Number of questions</label>
                        <select
                          id="ai-question-count"
                          disabled={loadingQuestionBank || !availableQuestionData?.available_count}
                          value={numberOfQuestions}
                          onChange={(event) => setNumberOfQuestions(Number(event.target.value))}
                        >
                          {Array.from(
                            { length: Math.min(20, availableQuestionData?.available_count || 0) },
                            (_, index) => index + 1
                          ).map((count) => (
                            <option key={count} value={count}>{count} {count === 1 ? "question" : "questions"}</option>
                          ))}
                        </select>
                      </div>
                      <div className="ai-form-field">
                        <label htmlFor="ai-duration">Duration in minutes (optional)</label>
                        <input
                          id="ai-duration"
                          type="number"
                          min="5"
                          max="180"
                          value={durationMinutes}
                          onChange={(event) => setDurationMinutes(event.target.value)}
                        />
                      </div>
                    </div>
                    <div className="ai-generation-summary">
                      <div>
                        <span className="ai-summary-icon">✦</span>
                        <div>
                          <strong>Interview focus</strong>
                          <p>
                            {selectedCourseId
                              ? courses.find((course) => String(course.id) === selectedCourseId)?.title
                              : "General interview questions"}
                          </p>
                        </div>
                      </div>
                      <span className="ai-summary-level">{difficulty.toUpperCase()}</span>
                    </div>
                    {activeSession && (
                      <p className="ai-active-notice">
                        You have an interview in progress. Resume or finish it before
                        starting another.
                      </p>
                    )}
                    {loadingQuestionBank ? (
                      <p className="ai-muted-text" role="status">Loading course question bank…</p>
                    ) : availableQuestionData ? (
                      <div className="ai-default-question-preview">
                        <div className="ai-section-heading">
                          <div>
                            <span className="ai-section-eyebrow">DEFAULT QUESTION BANK</span>
                            <h3>{availableQuestionData.available_count} questions available</h3>
                          </div>
                        </div>
                        <ol>
                          {availableQuestionData.questions.slice(0, 5).map((question, index) => (
                            <li key={`${question.course_id}-${question.question}`}>
                              <span>{index + 1}. {question.question}</span>
                            </li>
                          ))}
                        </ol>
                        {availableQuestionData.available_count > 5 && (
                          <small>More questions are available for the selected difficulty.</small>
                        )}
                      </div>
                    ) : null}
                    <button
                      type="submit"
                      className="ai-generate-button"
                      disabled={
                        starting ||
                        Boolean(activeSession) ||
                        loadingQuestionBank ||
                        !availableQuestionData ||
                        numberOfQuestions < 1 ||
                        numberOfQuestions > (availableQuestionData?.available_count || 0)
                      }
                    >
                      {starting ? "Preparing your interview…" : "Start interview"}
                    </button>
                  </form>
                  <p className="ai-privacy-note">
                    Answers and feedback are saved to your account so you can review
                    your progress later. AI provider credentials remain on the server.
                  </p>
                </section>
              )}

              <section className="ai-panel ai-history-panel">
                <div className="ai-section-heading">
                  <div>
                    <span className="ai-section-eyebrow">YOUR PROGRESS</span>
                    <h2>Recent interviews</h2>
                  </div>
                  <button
                    type="button"
                    className="ai-refresh-button"
                    onClick={loadDashboard}
                    disabled={loadingData}
                  >
                    Refresh
                  </button>
                </div>
                {history.length === 0 ? (
                  <div className="ai-empty-small">
                    <p>No completed interviews yet.</p>
                    <small>Your completed sessions and results will appear here.</small>
                  </div>
                ) : (
                  <div className="ai-history-list">
                    {history.map((item) => (
                      <button
                        type="button"
                        className="ai-history-item"
                        key={item.id}
                        onClick={() => openResult(item)}
                      >
                        <span>
                          <strong>
                            {item.course_title || "General interview"} · {item.category}
                          </strong>
                          <small>
                            {new Date(item.completed_at).toLocaleDateString()} ·{" "}
                            {item.questions.filter((question) => question.evaluation).length}{" "}
                            answers evaluated
                          </small>
                        </span>
                        <strong className="ai-history-score">
                          {item.overall_score === null ? "—" : `${item.overall_score}%`}
                        </strong>
                      </button>
                    ))}
                  </div>
                )}
              </section>
              <section className="ai-panel ai-recommendations-panel">
                <div className="ai-section-heading">
                  <div>
                    <span className="ai-section-eyebrow">NEXT STEPS</span>
                    <h2>Interview preparation recommendations</h2>
                  </div>
                </div>
                {recommendedTopics.length ? (
                  <>
                    <p className="ai-muted-text">
                      Focus areas identified from your latest completed interview:
                    </p>
                    <ul className="ai-recommendation-list">
                      {recommendedTopics.map((topic) => <li key={topic}>{topic}</li>)}
                    </ul>
                    {recommendedLessons.length > 0 && (
                      <div className="ai-related-lessons">
                        <strong>Related lessons to revisit</strong>
                        <ul className="ai-recommendation-list">
                          {recommendedLessons.map((lesson) => (
                            <li key={lesson.lessonId}>
                              <Link
                                to={`/learning/course/${lesson.courseId}/lesson/${lesson.lessonId}`}
                              >
                                {lesson.courseTitle}: {lesson.lessonTitle}
                              </Link>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </>
                ) : (
                  <p className="ai-muted-text">
                    Complete an interview to get recommendations based on your own answers.
                    Course content and default interview questions are provided by the Learning Module.
                  </p>
                )}
              </section>
            </section>
          </div>
        )}

        <footer className="ai-interview-footer">
          <span>✦</span>
          <p>Keep learning. Keep practicing. Your next opportunity is closer than you think.</p>
        </footer>
      </div>
    </main>
  );
}

export default AIInterview;
