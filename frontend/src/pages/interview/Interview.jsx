import { useState, useEffect, useMemo, useCallback } from "react";
import { Link } from "react-router-dom";
import { getInterviews } from "../../services/interviewApi";
import MCQInterview from "./MCQInterview";
import "./Interview.css";

const DEFAULT_QUESTIONS = [
  {
    id: 101,
    question: "How does FastAPI achieve high performance, and how does async/await work under the hood?",
    answer:
      "FastAPI leverages Starlette and Pydantic on top of Uvicorn (an ASGI server). Async functions run on an event loop without blocking thread executions during I/O operations (database queries, network requests), enabling high concurrency similar to Node.js and Go.",
    category: "Python & FastAPI",
    difficulty: "Medium",
  },
  {
    id: 102,
    question: "What is Dependency Injection in FastAPI and what are its main advantages?",
    answer:
      "Dependency Injection in FastAPI uses `Depends()` to automatically inject shared logic, database sessions, or authentication users into route handlers. Advantages include code reuse, testability, and clean separation of concerns.",
    category: "Python & FastAPI",
    difficulty: "Easy",
  },
  {
    id: 103,
    question: "Explain the difference between SQL indexing (B-Tree) vs Hash Indexing.",
    answer:
      "B-Tree indexes maintain a balanced search tree supporting range queries (`BETWEEN`, `>`, `<`), equality checks, and sorting. Hash indexes map keys directly via hash functions for O(1) exact equality lookups, but do NOT support range queries.",
    category: "Database & System Design",
    difficulty: "Hard",
  },
  {
    id: 104,
    question: "How does React's Virtual DOM and Reconciliation algorithm work?",
    answer:
      "React keeps a lightweight memory tree representation of the DOM. When state changes, React creates a new Virtual DOM tree, runs the Diffing algorithm (heuristic O(n) comparison) against the previous tree, and batches minimal real DOM updates.",
    category: "React & Frontend",
    difficulty: "Medium",
  },
  {
    id: 105,
    question: "What is the difference between Process vs Thread, and how does Python's GIL affect multi-threading?",
    answer:
      "A process has its own dedicated memory address space, while threads share the process memory. Python's Global Interpreter Lock (GIL) permits only one thread to execute CPython bytecode at a time, limiting CPU-bound tasks in multi-threading. Use multiprocessing or async for concurrency.",
    category: "Python & FastAPI",
    difficulty: "Hard",
  },
  {
    id: 106,
    question: "How would you design a rate limiter for an API service?",
    answer:
      "Common algorithms include Token Bucket or Leaky Bucket. Using Redis with sliding window counter logs or atomic INCR/EXPIRE operations allows distributed, low-latency rate limiting across multiple server instances.",
    category: "Database & System Design",
    difficulty: "Hard",
  },
  {
    id: 107,
    question: "Describe a challenging bug you encountered and how you systematically solved it.",
    answer:
      "Structure using the STAR method: Situation (Context), Task (Objective), Action (Isolated issue via logs, reproduced unit test, applied fix), Result (Impact, metrics, and prevented recurrence).",
    category: "Behavioral",
    difficulty: "Easy",
  },
];

function Interview() {
  const [questions, setQuestions] = useState(DEFAULT_QUESTIONS);
  const [loading, setLoading] = useState(false);

  // Active practice mode: flashcards or the question bank.
  const [mode, setMode] = useState("mcq");

  // Flashcard Drill state
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [masteredCount, setMasteredCount] = useState(0);
  const [reviewCount, setReviewCount] = useState(0);

  // Question Bank filters
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [selectedDifficulty, setSelectedDifficulty] = useState("All");
  const [expandedId, setExpandedId] = useState(null);

  const loadQuestions = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getInterviews();
      if (Array.isArray(data) && data.length > 0) {
        // Merge backend data with default questions ensuring unique IDs
        const combined = [...data, ...DEFAULT_QUESTIONS.filter((dq) => !data.some((d) => d.id === dq.id))];
        setQuestions(combined);
      }
    } catch {
      // Fallback to default high-yield questions
      setQuestions(DEFAULT_QUESTIONS);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => loadQuestions(), 0);
    return () => window.clearTimeout(timer);
  }, [loadQuestions]);

  // Filtered question bank.
  const filteredQuestions = useMemo(() => {
    return questions.filter((q) => {
      const matchesSearch =
        q.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
        q.answer.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesCat = selectedCategory === "All" || q.category === selectedCategory;
      const matchesDiff =
        selectedDifficulty === "All" ||
        q.difficulty.toLowerCase() === selectedDifficulty.toLowerCase();

      return matchesSearch && matchesCat && matchesDiff;
    });
  }, [questions, searchTerm, selectedCategory, selectedDifficulty]);

  // Unique Categories
  const categories = useMemo(() => {
    const cats = new Set(questions.map((q) => q.category));
    return ["All", ...Array.from(cats)];
  }, [questions]);

  // Current Active Flashcard
  const currentCard = filteredQuestions[currentIndex] || filteredQuestions[0] || questions[0];

  // Flashcard Actions
  const handleNextCard = () => {
    setShowAnswer(false);
    setCurrentIndex((prev) => (prev + 1) % filteredQuestions.length);
  };

  const handlePrevCard = () => {
    setShowAnswer(false);
    setCurrentIndex((prev) => (prev - 1 + filteredQuestions.length) % filteredQuestions.length);
  };

  const handleScoreCard = (isCorrect) => {
    if (isCorrect) {
      setMasteredCount((prev) => prev + 1);
    } else {
      setReviewCount((prev) => prev + 1);
    }
    handleNextCard();
  };

  return (
    <div className="interview-page">
      <div className="interview-container">
        {/* Hero Section */}
        <header className="interview-hero">
          <div className="hero-content">
            <span className="hero-badge-ai">Rule-Based MCQ Interview</span>
            <h1>
              Ace Your Code & System Interviews.
              <br />
              <span className="hero-gradient-title">Practice at your own pace.</span>
            </h1>
            <p>
              Practice with rule-based, backend-graded multiple-choice interviews. Flashcards and the searchable question bank are also available.
            </p>
          </div>
        </header>
        {loading && <p role="status">Loading question bank…</p>}

        {/* Metric Statistics */}
        <section className="interview-stats-grid">
          <div className="int-stat-card">
            <div className="int-stat-icon icon-purple">📚</div>
            <div>
              <div className="int-stat-num">{questions.length}</div>
              <div className="int-stat-lbl">Question Bank</div>
            </div>
          </div>

          <div className="int-stat-card">
            <div className="int-stat-icon icon-green">🎯</div>
            <div>
              <div className="int-stat-num">{masteredCount}</div>
              <div className="int-stat-lbl">Questions Mastered</div>
            </div>
          </div>

          <div className="int-stat-card">
            <div className="int-stat-icon icon-amber">🔄</div>
            <div>
              <div className="int-stat-num">{reviewCount}</div>
              <div className="int-stat-lbl">Needs Review</div>
            </div>
          </div>

          <div className="int-stat-card">
            <div className="int-stat-icon icon-indigo">⚡</div>
            <div>
              <div className="int-stat-num">
                {masteredCount + reviewCount > 0
                  ? `${Math.round((masteredCount / (masteredCount + reviewCount)) * 100)}%`
                  : "—"}
              </div>
              <div className="int-stat-lbl">Accuracy Rate</div>
            </div>
          </div>
        </section>

        {/* Practice Mode Navigation */}
        <nav className="mode-nav-tabs">
          <button
            className={`mode-tab-btn ${mode === "flashcard" ? "active" : ""}`}
            onClick={() => setMode("flashcard")}
          >
            🎴 Flashcard Drill Mode
          </button>
          <button
            className={`mode-tab-btn ${mode === "bank" ? "active" : ""}`}
            onClick={() => setMode("bank")}
          >
            📚 Question Bank ({filteredQuestions.length})
          </button>
          <button
            className={`mode-tab-btn ${mode === "mcq" ? "active" : ""}`}
            onClick={() => setMode("mcq")}
          >
            ✓ MCQ Interview
          </button>
          <Link className="mode-tab-btn ai-mock-interview-link" to="/interview/ai">
            Written AI Mock Interview
          </Link>
        </nav>

        {mode === "mcq" && <MCQInterview />}

        {/* MODE 1: FLASHCARD DRILL */}
        {mode === "flashcard" && (
          <div className="flashcard-wrapper">
            {currentCard ? (
              <div className="flashcard-card">
                <div>
                  <div className="flashcard-meta-row">
                    <span className="category-chip">{currentCard.category}</span>
                    <span
                      className={`difficulty-tag ${
                        currentCard.difficulty === "Easy"
                          ? "diff-easy"
                          : currentCard.difficulty === "Medium"
                          ? "diff-medium"
                          : "diff-hard"
                      }`}
                    >
                      {currentCard.difficulty}
                    </span>
                  </div>

                  <h2 className="flashcard-question-text">{currentCard.question}</h2>

                  {showAnswer ? (
                    <div className="flashcard-answer-box">
                      <strong>💡 Model Answer & Solution Breakdown:</strong>
                      <p style={{ marginTop: "8px" }}>{currentCard.answer}</p>
                    </div>
                  ) : (
                    <button
                      className="btn-reveal-answer"
                      onClick={() => setShowAnswer(true)}
                    >
                      👁️ Click to Reveal Model Answer
                    </button>
                  )}
                </div>

                <div>
                  {showAnswer && (
                    <div className="flashcard-feedback-actions">
                      <button
                        className="btn-drill-action btn-drill-correct"
                        onClick={() => handleScoreCard(true)}
                      >
                        ✓ Got It Right
                      </button>
                      <button
                        className="btn-drill-action btn-drill-review"
                        onClick={() => handleScoreCard(false)}
                      >
                        ⚠️ Needs Review
                      </button>
                    </div>
                  )}

                  <div className="flashcard-nav-row" style={{ marginTop: "20px" }}>
                    <button className="btn-nav-arrow" onClick={handlePrevCard}>
                      ← Previous
                    </button>
                    <span style={{ fontSize: "13px", fontWeight: "700", color: "#64748b" }}>
                      Card {currentIndex + 1} of {filteredQuestions.length}
                    </span>
                    <button className="btn-nav-arrow" onClick={handleNextCard}>
                      Next →
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div style={{ textAlign: "center", padding: "40px" }}>No questions match your filter.</div>
            )}
          </div>
        )}

        {/* MODE 2: QUESTION BANK */}
        {mode === "bank" && (
          <div>
            <div className="bank-toolbar">
              <div className="search-field-wrap">
                <input
                  type="text"
                  placeholder="Search questions by keyword or topic..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="search-field-input"
                />
              </div>

              <div className="filter-pills-row">
                <span style={{ fontSize: "13px", fontWeight: "700", color: "#64748b", alignSelf: "center" }}>
                  Category:
                </span>
                {categories.map((cat, i) => (
                  <button
                    key={i}
                    className={`filter-pill ${selectedCategory === cat ? "active" : ""}`}
                    onClick={() => setSelectedCategory(cat)}
                  >
                    {cat}
                  </button>
                ))}
              </div>
              <label className="difficulty-filter">
                Difficulty:
                <select
                  value={selectedDifficulty}
                  onChange={(event) => setSelectedDifficulty(event.target.value)}
                >
                  <option value="All">All levels</option>
                  <option value="Easy">Easy</option>
                  <option value="Medium">Medium</option>
                  <option value="Hard">Hard</option>
                </select>
              </label>
            </div>

            <div className="question-accordion-list">
              {filteredQuestions.map((q) => (
                <div key={q.id} className="question-accordion-item">
                  <div
                    className="accordion-header"
                    onClick={() => setExpandedId(expandedId === q.id ? null : q.id)}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                      <span className="category-chip">{q.category}</span>
                      <span className="accordion-title">{q.question}</span>
                    </div>

                    <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                      <span
                        className={`difficulty-tag ${
                          q.difficulty === "Easy"
                            ? "diff-easy"
                            : q.difficulty === "Medium"
                            ? "diff-medium"
                            : "diff-hard"
                        }`}
                      >
                        {q.difficulty}
                      </span>
                      <span style={{ fontWeight: "bold" }}>{expandedId === q.id ? "▲" : "▼"}</span>
                    </div>
                  </div>

                  {expandedId === q.id && (
                    <div className="accordion-body">
                      <strong>💡 Model Answer:</strong>
                      <p style={{ marginTop: "8px" }}>{q.answer}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

export default Interview;
