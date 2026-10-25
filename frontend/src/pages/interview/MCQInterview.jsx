import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  getActiveMCQAttempt,
  getMCQAttempt,
  getMCQHistory,
  getMCQOptions,
  getMCQProgress,
  startMCQAttempt,
  submitMCQAttempt,
} from "../../services/interviewApi";

function errorMessage(error) {
  return error instanceof Error ? error.message : "An unexpected error occurred.";
}

function parseAttemptCreatedAt(value) {
  const timestamp = String(value);
  return Date.parse(/[zZ]|[+-]\d{2}:\d{2}$/.test(timestamp) ? timestamp : `${timestamp}Z`);
}

function MCQInterview() {
  const [options, setOptions] = useState(null);
  const [subject, setSubject] = useState("");
  const [topic, setTopic] = useState("");
  const [difficulty, setDifficulty] = useState("Beginner");
  const [numberOfQuestions, setNumberOfQuestions] = useState(5);
  const [attempt, setAttempt] = useState(null);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [progress, setProgress] = useState(null);
  const [answers, setAnswers] = useState({});
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [clockNow, setClockNow] = useState(0);
  const expirationCheckFor = useRef(null);

  const selectedSubject = options?.subjects.find((item) => item.name === subject);
  const topics = selectedSubject?.topics || [];
  const selectedTopic = topics.find((item) => item.name === topic);
  const supportedCounts = selectedTopic?.available_counts?.[difficulty] || [];

  const refreshHistoryAndProgress = useCallback(async () => {
    const [savedHistory, savedProgress] = await Promise.all([
      getMCQHistory(),
      getMCQProgress(),
    ]);
    setHistory(savedHistory);
    setProgress(savedProgress);
  }, []);

  const loadMCQ = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [available, activeAttempt, savedHistory, savedProgress] =
        await Promise.all([
          getMCQOptions(),
          getActiveMCQAttempt(),
          getMCQHistory(),
          getMCQProgress(),
        ]);
      setOptions(available);
      setHistory(savedHistory);
      setProgress(savedProgress);
      const firstSubject = available.subjects[0];
      if (firstSubject) {
        setSubject(firstSubject.name);
        setTopic((current) =>
          firstSubject.topics.some((item) => item.name === current)
            ? current
            : firstSubject.topics[0]?.name || ""
        );
      }
      if (activeAttempt) {
        setAttempt(activeAttempt);
        setCurrentIndex(0);
      }
    } catch (requestError) {
      setError(`Unable to load MCQ interview data: ${errorMessage(requestError)}`);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadMCQ();
    }, 0);
    return () => window.clearTimeout(timer);
  }, [loadMCQ]);

  const attemptId = attempt?.id;
  useEffect(() => {
    if (!attemptId) return undefined;
    const updateClock = () => setClockNow(Date.now());
    const firstUpdate = window.setTimeout(updateClock, 0);
    const timer = window.setInterval(updateClock, 1000);
    return () => {
      window.clearTimeout(firstUpdate);
      window.clearInterval(timer);
    };
  }, [attemptId]);

  const question = attempt?.questions?.[currentIndex];
  const deadline = attempt?.expires_at
    ? parseAttemptCreatedAt(attempt.expires_at)
    : null;
  const remainingSeconds =
    deadline === null || !Number.isFinite(deadline) || clockNow === 0
      ? null
      : Math.max(0, Math.ceil((deadline - clockNow) / 1000));
  const timeExpired = remainingSeconds === 0;
  const timeRemainingLabel =
    remainingSeconds === null
      ? null
      : [
          Math.floor(remainingSeconds / 3600),
          Math.floor((remainingSeconds % 3600) / 60),
          remainingSeconds % 60,
        ]
          .map((unit) => String(unit).padStart(2, "0"))
          .join(":");
  const selectedOptionId = question ? answers[question.id] : null;
  const answeredCount = useMemo(
    () => Object.keys(answers).filter((questionId) => answers[questionId]).length,
    [answers]
  );

  useEffect(() => {
    if (!attempt || !timeExpired || expirationCheckFor.current === attempt.id) {
      return undefined;
    }
    expirationCheckFor.current = attempt.id;
    let cancelled = false;
    getActiveMCQAttempt()
      .then((activeAttempt) => {
        if (cancelled) return;
        if (!activeAttempt) {
          setAttempt(null);
          setAnswers({});
          setCurrentIndex(0);
          setError("This MCQ interview expired before it was submitted. Start a new interview.");
        } else {
          setError("The interview timer ended, but the server has not confirmed expiry. Refresh to retry.");
        }
      })
      .catch((requestError) => {
        if (!cancelled) {
          setError(`Unable to confirm interview expiry: ${errorMessage(requestError)}`);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [attempt, timeExpired]);

  function handleSubjectChange(value) {
    setSubject(value);
    const subjectTopics =
      options?.subjects.find((item) => item.name === value)?.topics || [];
    setTopic(subjectTopics[0]?.name || "");
  }

  async function handleStart(event) {
    event.preventDefault();
    if (starting) return;
    setError("");
    if (!subject || !topic || !difficulty) {
      setError("Select a supported subject, topic, and difficulty.");
      return;
    }
    if (!supportedCounts.includes(Number(numberOfQuestions))) {
      setError(
        `This selection has ${selectedTopic?.available_counts?.[difficulty]?.[0] || 0} validated questions. Choose an available question count.`
      );
      return;
    }

    setStarting(true);
    try {
      const created = await startMCQAttempt({
        subject,
        topic,
        difficulty,
        number_of_questions: Number(numberOfQuestions),
      });
      setAttempt(created);
      setResult(null);
      setAnswers({});
      setCurrentIndex(0);
    } catch (requestError) {
      setError(errorMessage(requestError));
    } finally {
      setStarting(false);
    }
  }

  async function handleSubmit() {
    if (!attempt || submitting || result) return;
    const unanswered = attempt.total_questions - answeredCount;
    if (
      !window.confirm(
        unanswered
          ? `You have ${unanswered} unanswered question${unanswered === 1 ? "" : "s"}. Submit this interview with those questions unanswered?`
          : "Submit your interview now?"
      )
    ) {
      return;
    }

    setSubmitting(true);
    setError("");
    try {
      const completed = await submitMCQAttempt(
        attempt.id,
        Object.entries(answers).map(([question_id, option_id]) => ({
          question_id,
          option_id,
        }))
      );
      setAttempt(null);
      setResult(completed);
      try {
        await refreshHistoryAndProgress();
      } catch (refreshError) {
        setError(
          `Your result was saved, but interview progress could not be refreshed: ${errorMessage(refreshError)}`
        );
      }
    } catch (requestError) {
      setError(errorMessage(requestError));
    } finally {
      setSubmitting(false);
    }
  }

  async function openSavedResult(attemptId) {
    setError("");
    try {
      const saved = await getMCQAttempt(attemptId);
      if (saved.status !== "completed") {
        setError("This attempt has not been submitted yet.");
        return;
      }
      setAttempt(null);
      setResult(saved);
    } catch (requestError) {
      setError(errorMessage(requestError));
    }
  }

  function startAnother() {
    setResult(null);
    setAttempt(null);
    setAnswers({});
    setCurrentIndex(0);
    setError("");
  }

  if (loading) {
    return <section className="mcq-panel" role="status">Loading MCQ interview…</section>;
  }

  const resultDetails = result?.result;

  return (
    <section className="mcq-layout" aria-labelledby="mcq-title">
      <div className="mcq-main">
        {error && <p className="mcq-error" role="alert">{error}</p>}

        {result ? (
          <section className="mcq-panel">
            <div className="mcq-section-heading">
              <div>
                <span className="mcq-eyebrow">COMPLETED INTERVIEW</span>
                <h2 id="mcq-title">Your results</h2>
                <p>{result.subject} · {result.topic} · {result.difficulty}</p>
              </div>
              <div className="mcq-grade-card">
                <strong>{resultDetails.grade}</strong>
                <span>{resultDetails.percentage}%</span>
                <small>{resultDetails.score}</small>
              </div>
            </div>
            <div className="mcq-result-stats">
              <div><strong>{resultDetails.total_questions}</strong><span>Total</span></div>
              <div><strong>{resultDetails.answered_questions}</strong><span>Answered</span></div>
              <div><strong>{resultDetails.correct_answers}</strong><span>Correct</span></div>
              <div><strong>{resultDetails.wrong_answers}</strong><span>Wrong</span></div>
              <div><strong>{resultDetails.unanswered_questions}</strong><span>Unanswered</span></div>
            </div>
            <div className="mcq-review-list">
              {resultDetails.questions.map((item, index) => (
                <article className="mcq-review-card" key={item.id}>
                  <div className="mcq-question-meta">
                    <span>QUESTION {index + 1}</span>
                    <span className={`mcq-result-status ${item.status}`}>{item.status}</span>
                  </div>
                  <h3>{item.question}</h3>
                  <ul className="mcq-review-options">
                    {item.options.map((option, optionIndex) => (
                      <li
                        className={[
                          option.id === item.correct_option_id ? "correct-option" : "",
                          option.id === item.selected_option_id && item.status !== "correct"
                            ? "selected-wrong-option"
                            : "",
                        ].filter(Boolean).join(" ")}
                        key={option.id}
                      >
                        <span>{String.fromCharCode(65 + optionIndex)}.</span> {option.text}
                      </li>
                    ))}
                  </ul>
                  <p><strong>Your answer:</strong> {item.selected_answer || "Unanswered"}</p>
                  <p><strong>Correct answer:</strong> {item.correct_answer}</p>
                  <p className="mcq-explanation"><strong>Explanation:</strong> {item.explanation}</p>
                  <small>{item.topic} · {item.difficulty}</small>
                </article>
              ))}
            </div>
            <button type="button" className="mcq-primary-button" onClick={startAnother}>
              Start another interview
            </button>
          </section>
        ) : attempt ? (
          <section className="mcq-panel" aria-labelledby="mcq-title">
            <div className="mcq-section-heading">
              <div>
                <span className="mcq-eyebrow">MCQ INTERVIEW</span>
                <h2 id="mcq-title">Question {currentIndex + 1} of {attempt.total_questions}</h2>
                <p>{attempt.subject} · {attempt.topic} · {attempt.difficulty}</p>
              </div>
              <div className="mcq-session-badges">
                {timeRemainingLabel !== null && (
                  <span
                    className={`mcq-timer-badge${timeExpired ? " expired" : ""}`}
                    role="timer"
                    aria-label={timeExpired ? "Interview time expired" : `Time remaining ${timeRemainingLabel}`}
                  >
                    {timeExpired ? "Time expired" : `Time left ${timeRemainingLabel}`}
                  </span>
                )}
                <span className="mcq-count-badge">{answeredCount} answered</span>
              </div>
            </div>
            <div
              className="mcq-progress-track"
              role="progressbar"
              aria-label="Interview progress"
              aria-valuemin="0"
              aria-valuemax={attempt.total_questions}
              aria-valuenow={answeredCount}
            >
              <span style={{ width: `${(answeredCount / attempt.total_questions) * 100}%` }} />
            </div>
            {question && (
              <article className="mcq-question-card">
                <div className="mcq-question-meta">
                  <span>QUESTION {currentIndex + 1}</span>
                  <span>{question.topic}</span>
                  <span>{question.difficulty}</span>
                </div>
                <h3>{question.question}</h3>
                <fieldset
                  className="mcq-options-list"
                  aria-label={`Answer options for question ${currentIndex + 1}`}
                >
                  {question.options.map((option, index) => (
                    <label
                      key={option.id}
                      className={`mcq-option${selectedOptionId === option.id ? " selected" : ""}`}
                    >
                      <input
                        type="radio"
                        name={`mcq-answer-${question.id}`}
                        value={option.id}
                        checked={selectedOptionId === option.id}
                        disabled={submitting || timeExpired}
                        onChange={() =>
                          setAnswers((current) => ({
                            ...current,
                            [question.id]: option.id,
                          }))
                        }
                      />
                      <span className="mcq-option-letter">{String.fromCharCode(65 + index)}</span>
                      <span className="mcq-option-text">{option.text}</span>
                    </label>
                  ))}
                </fieldset>
              </article>
            )}
            <div className="mcq-nav-row">
              <button
                type="button"
                className="mcq-secondary-button"
                disabled={currentIndex === 0 || submitting || timeExpired}
                onClick={() => setCurrentIndex((value) => Math.max(0, value - 1))}
              >
                Previous
              </button>
              <span>Question {currentIndex + 1} of {attempt.total_questions}</span>
              {currentIndex < attempt.total_questions - 1 ? (
                <button
                  type="button"
                  className="mcq-secondary-button"
                  disabled={submitting || timeExpired}
                  onClick={() =>
                    setCurrentIndex((value) =>
                      Math.min(attempt.total_questions - 1, value + 1)
                    )
                  }
                >
                  Next
                </button>
              ) : (
                <button
                  type="button"
                  className="mcq-primary-button"
                  disabled={submitting || timeExpired}
                  onClick={handleSubmit}
                >
                  {submitting ? "Submitting…" : "Submit Interview"}
                </button>
              )}
            </div>
            {currentIndex < attempt.total_questions - 1 && (
              <button
                type="button"
                className="mcq-submit-link"
                disabled={submitting || timeExpired}
                onClick={handleSubmit}
              >
                Submit Interview
              </button>
            )}
          </section>
        ) : (
          <section className="mcq-panel">
            <span className="mcq-eyebrow">RULE-BASED QUESTION SET</span>
            <h2 id="mcq-title">Start an MCQ interview</h2>
            <p className="mcq-muted">
              Select a supported topic and difficulty. Questions are generated and graded by the backend.
            </p>
            <form className="mcq-config-form" onSubmit={handleStart}>
              <label>
                Subject
                <select
                  value={subject}
                  onChange={(event) => handleSubjectChange(event.target.value)}
                  required
                >
                  {(options?.subjects || []).map((item) => (
                    <option value={item.name} key={item.name}>{item.name}</option>
                  ))}
                </select>
              </label>
              <label>
                Topic
                <select
                  value={topic}
                  onChange={(event) => setTopic(event.target.value)}
                  required
                >
                  {topics.map((item) => (
                    <option value={item.name} key={item.name}>{item.name}</option>
                  ))}
                </select>
              </label>
              <label>
                Difficulty
                <select
                  value={difficulty}
                  onChange={(event) => setDifficulty(event.target.value)}
                  required
                >
                  {(options?.difficulties || []).map((item) => (
                    <option value={item} key={item}>{item}</option>
                  ))}
                </select>
              </label>
              <label>
                Number of questions
                <select
                  value={numberOfQuestions}
                  onChange={(event) => setNumberOfQuestions(Number(event.target.value))}
                  required
                >
                  {(options?.question_counts || []).map((count) => (
                    <option
                      value={count}
                      key={count}
                      disabled={!supportedCounts.includes(count)}
                    >
                      {count}{supportedCounts.includes(count) ? "" : " — not available"}
                    </option>
                  ))}
                </select>
              </label>
              <p className="mcq-muted">
                {supportedCounts.length
                  ? `${selectedTopic.available_counts[difficulty][0]} validated unique questions available.`
                  : "No validated question templates are available for this selection."}
              </p>
              <button
                type="submit"
                className="mcq-primary-button"
                disabled={
                  starting ||
                  !supportedCounts.includes(Number(numberOfQuestions)) ||
                  !subject ||
                  !topic
                }
              >
                {starting ? "Preparing interview…" : "Start Interview"}
              </button>
            </form>
          </section>
        )}
      </div>

      <aside className="mcq-sidebar">
        <section className="mcq-panel">
          <span className="mcq-eyebrow">YOUR MCQ PROGRESS</span>
          {progress ? (
            <div className="mcq-progress-stats">
              <div><span>Completed interviews</span><strong>{progress.total_completed}</strong></div>
              <div><span>Questions attempted</span><strong>{progress.total_answered}/{progress.total_questions}</strong></div>
              <div><span>Correct answers</span><strong>{progress.correct_answers}</strong></div>
              <div><span>Overall accuracy</span><strong>{progress.overall_accuracy === null ? "—" : `${progress.overall_accuracy}%`}</strong></div>
              <div><span>Average interview score</span><strong>{progress.average_percentage === null ? "—" : `${progress.average_percentage}%`}</strong></div>
              <div><span>Best interview score</span><strong>{progress.best_percentage === null ? "—" : `${progress.best_percentage}%`}</strong></div>
            </div>
          ) : <p className="mcq-muted">No completed interview data yet.</p>}
        </section>
        <section className="mcq-panel">
          <div className="mcq-history-heading">
            <h2>Interview history</h2>
            <button type="button" onClick={loadMCQ} disabled={loading}>Refresh</button>
          </div>
          {history.length === 0 ? (
            <p className="mcq-muted">No completed MCQ interviews yet.</p>
          ) : (
            <ul className="mcq-history-list">
              {history.map((item) => (
                <li key={item.id}>
                  <button type="button" onClick={() => openSavedResult(item.id)}>
                    <strong>{item.topic}</strong>
                    <span>{new Date(item.completed_at).toLocaleDateString()} · {item.result.score}</span>
                    <span>{item.result.percentage}% · Grade {item.result.grade}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
        {progress?.topic_performance?.length > 0 && (
          <section className="mcq-panel">
            <span className="mcq-eyebrow">TOPIC PERFORMANCE</span>
            <ul className="mcq-history-list">
              {progress.topic_performance.map((item) => (
                <li key={`${item.subject}-${item.topic}`}>
                  <div>
                    <strong>{item.topic}</strong>
                    <span>{item.attempts} attempts · {item.questions} questions</span>
                    <span>{item.accuracy === null ? "No answered questions" : `${item.accuracy}% accuracy`}</span>
                  </div>
                </li>
              ))}
            </ul>
          </section>
        )}
      </aside>
    </section>
  );
}

export default MCQInterview;
