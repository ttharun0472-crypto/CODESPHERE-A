import { useEffect, useState, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";

import {
    getCourses,
    getCourseLessons,
} from "../../services/learningApi";

import {
    adminGetTopicsForLesson,
    createTopic,
    updateTopic,
    deleteTopic,
    getQuestionsForTopic,
    createQuestion,
    updateQuestion,
    deleteQuestion,
} from "../../services/lmsApi";

import "./lms.css";


// ======================================================
// EMPTY STATES
// ======================================================

const emptyTopic = { lesson_id: "", title: "", description: "", topic_number: "" };

const emptyQuestion = {
    topic_id: "",
    question: "",
    quick_answer: "",
    explanation: "",
    real_world_example: "",
    code_example: "",
    expected_output: "",
    flowchart: "",
    key_points: "",
    remember_this: "",
    question_number: "",
};


// ======================================================
// ADMIN TOPICS PAGE
// ======================================================

function AdminTopics() {
    const navigate = useNavigate();

    // Selectors
    const [courses, setCourses] = useState([]);
    const [selectedCourseId, setSelectedCourseId] = useState("");
    const [lessons, setLessons] = useState([]);
    const [selectedLessonId, setSelectedLessonId] = useState("");

    // Topics
    const [topics, setTopics] = useState([]);
    const [selectedTopicId, setSelectedTopicId] = useState("");
    const [topicForm, setTopicForm] = useState(emptyTopic);
    const [editingTopicId, setEditingTopicId] = useState(null);

    // Questions
    const [questions, setQuestions] = useState([]);
    const [questionForm, setQuestionForm] = useState(emptyQuestion);
    const [editingQuestionId, setEditingQuestionId] = useState(null);

    // UI State
    const [activeTab, setActiveTab] = useState("topics"); // "topics" | "questions"
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [topicsLoading, setTopicsLoading] = useState(true);
    const [questionsLoading, setQuestionsLoading] = useState(false);
    const [topicsError, setTopicsError] = useState("");
    const [questionsError, setQuestionsError] = useState("");
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");


    // ======================================================
    // AUTH GUARD
    // ======================================================

    useEffect(() => {
        if (
            localStorage.getItem("is_admin") !== "true" ||
            !localStorage.getItem("access_token")
        ) {
            navigate("/dashboard");
        }
    }, [navigate]);


    // ======================================================
    // LOAD COURSES
    // ======================================================

    const loadCourses = useCallback(async () => {
        try {
            setLoading(true);
            const data = await getCourses();
            const list = Array.isArray(data) ? data : [];
            setCourses(list);
            if (list.length > 0 && !selectedCourseId) {
                setSelectedCourseId(String(list[0].id));
            }
        } catch (err) {
            setError(err.message || "Unable to load courses.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        void loadCourses();
    }, [loadCourses]);


    // ======================================================
    // LOAD LESSONS WHEN COURSE CHANGES
    // ======================================================

    useEffect(() => {
        if (!selectedCourseId) return;

        const load = async () => {
            try {
                setLessons([]);
                setSelectedLessonId("");
                setTopics([]);
                setSelectedTopicId("");
                setQuestions([]);
                setEditingTopicId(null);
                setTopicForm(emptyTopic);
                setEditingQuestionId(null);
                setQuestionForm(emptyQuestion);
                const data = await getCourseLessons(selectedCourseId);
                const list = Array.isArray(data) ? data : [];
                setLessons(list);
                setSelectedLessonId(list.length > 0 ? String(list[0].id) : "");
            } catch (err) {
                setLessons([]);
                setSelectedLessonId("");
                setTopics([]);
                setSelectedTopicId("");
                setQuestions([]);
                setError(err.message || "Unable to load lessons.");
            }
        };
        void load();
    }, [selectedCourseId]);


    // ======================================================
    // LOAD TOPICS WHEN LESSON CHANGES
    // ======================================================

    const loadTopics = useCallback(async () => {
        if (!selectedLessonId) return;
        try {
            const data = await adminGetTopicsForLesson(selectedLessonId);
            const list = Array.isArray(data) ? data : [];
            setTopics(list);
            setSelectedTopicId(list.length > 0 ? String(list[0].id) : "");
            setTopicsError("");
            setQuestionsLoading(list.length > 0);
        } catch (err) {
            setTopics([]);
            setSelectedTopicId("");
            setTopicsError(err.message || "Unable to load topics.");
            setError(err.message || "Unable to load topics.");
        } finally {
            setTopicsLoading(false);
        }
    }, [selectedLessonId]);

    useEffect(() => {
        void loadTopics();
    }, [loadTopics]);


    // ======================================================
    // LOAD QUESTIONS WHEN TOPIC CHANGES
    // ======================================================

    const loadQuestions = useCallback(async () => {
        if (!selectedTopicId) return;
        try {
            const data = await getQuestionsForTopic(selectedTopicId);
            setQuestions(Array.isArray(data) ? data : []);
            setQuestionsError("");
        } catch (err) {
            setQuestions([]);
            setQuestionsError(err.message || "Unable to load questions.");
            setError(err.message || "Unable to load questions.");
        } finally {
            setQuestionsLoading(false);
        }
    }, [selectedTopicId]);

    useEffect(() => {
        void loadQuestions();
    }, [loadQuestions]);


    // ======================================================
    // TOPIC FORM SUBMIT
    // ======================================================

    const handleTopicSubmit = async (e) => {
        e.preventDefault();
        if (!selectedLessonId) {
            setError("Please select a lesson first.");
            return;
        }
        clearMessages();

        try {
            setSaving(true);
            const payload = {
                ...topicForm,
                lesson_id: Number(selectedLessonId),
                topic_number: topicForm.topic_number ? Number(topicForm.topic_number) : null,
            };

            if (editingTopicId) {
                await updateTopic(editingTopicId, {
                    title: payload.title,
                    description: payload.description,
                    topic_number: payload.topic_number,
                });
                setSuccess("Topic updated successfully.");
            } else {
                await createTopic(payload);
                setSuccess("Topic created successfully.");
            }

            resetTopicForm();
            await loadTopics();
        } catch (err) {
            setError(err.message || "Unable to save topic.");
        } finally {
            setSaving(false);
        }
    };

    const handleDeleteTopic = async (topic) => {
        if (!window.confirm(`Delete topic "${topic.title}" and all its questions?`)) return;
        clearMessages();
        try {
            await deleteTopic(topic.id);
            setSuccess("Topic deleted.");
            if (String(selectedTopicId) === String(topic.id)) {
                setSelectedTopicId("");
                setQuestions([]);
            }
            await loadTopics();
        } catch (err) {
            setError(err.message || "Unable to delete topic.");
        }
    };

    const startEditTopic = (topic) => {
        setEditingTopicId(topic.id);
        setTopicForm({
            lesson_id: String(topic.lesson_id),
            title: topic.title,
            description: topic.description || "",
            topic_number: topic.topic_number,
        });
        setActiveTab("topics");
    };

    const resetTopicForm = () => {
        setEditingTopicId(null);
        setTopicForm(emptyTopic);
    };


    // ======================================================
    // QUESTION FORM SUBMIT
    // ======================================================

    const handleQuestionSubmit = async (e) => {
        e.preventDefault();
        if (!selectedTopicId) {
            setError("Please select a topic first.");
            return;
        }
        clearMessages();

        try {
            setSaving(true);
            const payload = {
                ...questionForm,
                question_number: questionForm.question_number ? Number(questionForm.question_number) : null,
            };

            if (editingQuestionId) {
                await updateQuestion(editingQuestionId, payload);
                setSuccess("Question updated successfully.");
            } else {
                await createQuestion({
                    ...payload,
                    topic_id: Number(selectedTopicId),
                });
                setSuccess("Question created successfully.");
            }

            resetQuestionForm();
            await loadQuestions();
        } catch (err) {
            setError(err.message || "Unable to save question.");
        } finally {
            setSaving(false);
        }
    };

    const handleDeleteQuestion = async (q) => {
        if (!window.confirm(`Delete question "${q.question}"?`)) return;
        clearMessages();
        try {
            await deleteQuestion(q.id);
            setSuccess("Question deleted.");
            await loadQuestions();
        } catch (err) {
            setError(err.message || "Unable to delete question.");
        }
    };

    const startEditQuestion = (q) => {
        setEditingQuestionId(q.id);
        setQuestionForm({
            topic_id: String(q.topic_id),
            question: q.question || "",
            quick_answer: q.quick_answer || "",
            explanation: q.explanation || "",
            real_world_example: q.real_world_example || "",
            code_example: q.code_example || "",
            expected_output: q.expected_output || "",
            flowchart: q.flowchart || "",
            key_points: q.key_points || "",
            remember_this: q.remember_this || "",
            question_number: q.question_number || 1,
        });
        setActiveTab("questions");
    };

    const resetQuestionForm = () => {
        setEditingQuestionId(null);
        setQuestionForm(emptyQuestion);
    };


    // ======================================================
    // HELPERS
    // ======================================================

    const clearMessages = () => { setError(""); setSuccess(""); };

    const tf = (field, val) => setTopicForm((f) => ({ ...f, [field]: val }));
    const qf = (field, val) => setQuestionForm((f) => ({ ...f, [field]: val }));


    // ======================================================
    // RENDER
    // ======================================================

    if (loading) {
        return (
            <main className="admin-topics-page">
                <div className="lms-loading">
                    <div className="lms-spinner" />
                    <h2>Loading...</h2>
                </div>
            </main>
        );
    }

    const selectedTopic = topics.find((t) => String(t.id) === String(selectedTopicId));

    return (
        <main className="admin-topics-page">
            <div className="admin-topics-container">

                {/* Header */}
                <Link to="/admin/learning" className="admin-back-link">
                    ← Back to Course &amp; Lesson Management
                </Link>
                <div className="admin-topics-header">
                    <div>
                        <p className="eyebrow" style={{ color: "var(--lms-blue)", fontSize: 11, fontWeight: 800, letterSpacing: "0.14em", textTransform: "uppercase", marginBottom: 6 }}>
                            Admin — Learning Management
                        </p>
                        <h1>Topics &amp; Questions</h1>
                        <p>Manage the topic and question hierarchy for your courses.</p>
                    </div>
                </div>

                {/* Alerts */}
                {error && <div className="admin-lms-error">{error}</div>}
                {success && <div className="admin-lms-success">✓ {success}</div>}

                {/* Course + Lesson Selectors */}
                <div className="admin-selectors">
                    <div className="admin-select-card">
                        <label htmlFor="admin-course-select">Course</label>
                        <select
                            id="admin-course-select"
                            value={selectedCourseId}
                            onChange={(e) => {
                                setSelectedCourseId(e.target.value);
                                setTopicsLoading(true);
                                setTopicsError("");
                                clearMessages();
                            }}
                        >
                            <option value="">Select a course</option>
                            {courses.map((c) => (
                                <option key={c.id} value={c.id}>{c.title}</option>
                            ))}
                        </select>
                    </div>

                    <div className="admin-select-card">
                        <label htmlFor="admin-lesson-select">Lesson</label>
                        <select
                            id="admin-lesson-select"
                            value={selectedLessonId}
                            onChange={(e) => {
                                setSelectedLessonId(e.target.value);
                                setTopicsLoading(true);
                                setTopicsError("");
                                setTopics([]);
                                setSelectedTopicId("");
                                setQuestions([]);
                                setQuestionsLoading(true);
                                setQuestionsError("");
                                setEditingTopicId(null);
                                setTopicForm(emptyTopic);
                                setEditingQuestionId(null);
                                setQuestionForm(emptyQuestion);
                                clearMessages();
                            }}
                            disabled={!selectedCourseId || lessons.length === 0}
                        >
                            <option value="">
                                {lessons.length === 0
                                    ? "No lessons — add a lesson first"
                                    : "Select a lesson"}
                            </option>
                            {lessons.map((l) => (
                                <option key={l.id} value={l.id}>{l.title}</option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Tab Bar */}
                <div className="section-tab-bar">
                    <button
                        className={`section-tab ${activeTab === "topics" ? "active" : ""}`}
                        onClick={() => setActiveTab("topics")}
                    >
                        📚 Topics
                    </button>
                    <button
                        className={`section-tab ${activeTab === "questions" ? "active" : ""}`}
                        onClick={() => setActiveTab("questions")}
                        disabled={!selectedTopicId}
                    >
                        ❓ Questions {selectedTopic ? `— ${selectedTopic.title}` : ""}
                    </button>
                </div>

                {/* ======= TOPICS TAB ======= */}
                {activeTab === "topics" && (
                    <div className="admin-content-grid">

                        {/* Topic List */}
                        <div className="admin-lms-card">
                            <h2>Topics in Lesson</h2>
                            {!selectedLessonId ? (
                                <p className="admin-empty-state">Select a lesson to see its topics.</p>
                            ) : topicsLoading ? (
                                <p className="admin-empty-state">Loading topics...</p>
                            ) : topicsError ? (
                                <p className="admin-empty-state">{topicsError}</p>
                            ) : topics.length === 0 ? (
                                <p className="admin-empty-state">No topics available for this lesson yet.</p>
                            ) : (
                                <div className="topic-list">
                                    {topics.map((t) => (
                                        <div
                                            key={t.id}
                                            className={`topic-list-item ${String(selectedTopicId) === String(t.id) ? "selected" : ""}`}
                                            onClick={() => {
                                                setSelectedTopicId(String(t.id));
                                                setQuestionsLoading(true);
                                                setQuestionsError("");
                                                setQuestions([]);
                                                setEditingQuestionId(null);
                                                setQuestionForm(emptyQuestion);
                                                clearMessages();
                                            }}
                                        >
                                            <div className="topic-item-header">
                                                <span className="topic-item-name">
                                                    {t.topic_number}. {t.title}
                                                </span>
                                                <div className="topic-item-actions">
                                                    <button
                                                        className="btn-edit"
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            startEditTopic(t);
                                                        }}
                                                    >
                                                        Edit
                                                    </button>
                                                    <button
                                                        className="btn-danger"
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            void handleDeleteTopic(t);
                                                        }}
                                                    >
                                                        Delete
                                                    </button>
                                                </div>
                                            </div>
                                            {t.description && (
                                                <p className="topic-item-desc">{t.description}</p>
                                            )}
                                            <p className="topic-q-count">
                                                Click to manage questions
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Topic Form */}
                        <div className="admin-lms-card">
                            <h2>{editingTopicId ? "Edit Topic" : "Create Topic"}</h2>
                            <form className="admin-lms-form" onSubmit={handleTopicSubmit}>
                                <div className="form-field">
                                    <label htmlFor="topic-title">Topic Title *</label>
                                    <input
                                        id="topic-title"
                                        required
                                        minLength={2}
                                        placeholder="e.g. Introduction to React"
                                        value={topicForm.title}
                                        onChange={(e) => tf("title", e.target.value)}
                                    />
                                </div>

                                <div className="form-field">
                                    <label htmlFor="topic-desc">Description</label>
                                    <textarea
                                        id="topic-desc"
                                        placeholder="Brief overview of what this topic covers"
                                        value={topicForm.description}
                                        onChange={(e) => tf("description", e.target.value)}
                                    />
                                </div>

                                <div className="form-field">
                                    <label htmlFor="topic-order">Topic Order</label>
                                    <input
                                        id="topic-order"
                                        type="number"
                                        min={1}
                                        placeholder="Blank adds to end"
                                        value={topicForm.topic_number}
                                        onChange={(e) => tf("topic_number", e.target.value)}
                                    />
                                </div>

                                <div className="admin-form-row">
                                    <button type="submit" className="btn-primary" disabled={saving || !selectedLessonId}>
                                        {saving ? "Saving..." : editingTopicId ? "Update Topic" : "Add Topic"}
                                    </button>
                                    {editingTopicId && (
                                        <button type="button" className="btn-secondary" onClick={resetTopicForm}>
                                            Cancel
                                        </button>
                                    )}
                                </div>
                            </form>

                            {selectedTopicId && (
                                <>
                                    <div className="divider" />
                                    <button
                                        className="btn-primary"
                                        style={{ width: "100%" }}
                                        onClick={() => setActiveTab("questions")}
                                    >
                                        ❓ Manage Questions for Selected Topic →
                                    </button>
                                </>
                            )}
                        </div>
                    </div>
                )}

                {/* ======= QUESTIONS TAB ======= */}
                {activeTab === "questions" && (
                    <div className="admin-content-grid">

                        {/* Question List */}
                        <div className="admin-lms-card">
                            <h2>
                                Questions
                                {selectedTopic ? ` — ${selectedTopic.title}` : ""}
                            </h2>

                            {!selectedTopicId ? (
                                <p className="admin-empty-state">Select a topic first.</p>
                            ) : questionsLoading ? (
                                <p className="admin-empty-state">Loading questions...</p>
                            ) : questionsError ? (
                                <p className="admin-empty-state">{questionsError}</p>
                            ) : questions.length === 0 ? (
                                <p className="admin-empty-state">No questions yet. Add one →</p>
                            ) : (
                                <div className="question-list">
                                    {questions.map((q) => (
                                        <div key={q.id} className="question-list-item">
                                            <span className="q-list-num">#{q.question_number}</span>
                                            <span className="q-list-text">{q.question}</span>
                                            <div className="q-list-actions">
                                                <button
                                                    className="btn-edit"
                                                    onClick={() => startEditQuestion(q)}
                                                >
                                                    Edit
                                                </button>
                                                <button
                                                    className="btn-danger"
                                                    onClick={() => void handleDeleteQuestion(q)}
                                                >
                                                    Delete
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Question Form */}
                        <div className="admin-lms-card" style={{ maxHeight: "90vh", overflowY: "auto" }}>
                            <h2>{editingQuestionId ? "Edit Question" : "Add Question"}</h2>
                            <form className="admin-lms-form" onSubmit={handleQuestionSubmit}>

                                <div className="form-field">
                                    <label htmlFor="q-title">Question *</label>
                                    <input
                                        id="q-title"
                                        required
                                        minLength={2}
                                        placeholder="e.g. What is React?"
                                        value={questionForm.question}
                                        onChange={(e) => qf("question", e.target.value)}
                                    />
                                </div>

                                <div className="form-field">
                                    <label htmlFor="q-order">Question Number</label>
                                    <input
                                        id="q-order"
                                        type="number"
                                        min={1}
                                        placeholder="Blank adds to end"
                                        value={questionForm.question_number}
                                        onChange={(e) => qf("question_number", e.target.value)}
                                    />
                                </div>

                                <div className="form-field">
                                    <label htmlFor="q-quick">Quick Answer</label>
                                    <textarea
                                        id="q-quick"
                                        placeholder="One-sentence answer"
                                        value={questionForm.quick_answer}
                                        onChange={(e) => qf("quick_answer", e.target.value)}
                                    />
                                </div>

                                <div className="form-field">
                                    <label htmlFor="q-expl">Detailed Explanation</label>
                                    <textarea
                                        id="q-expl"
                                        className="tall"
                                        placeholder="Full explanation (use line breaks for paragraphs)"
                                        value={questionForm.explanation}
                                        onChange={(e) => qf("explanation", e.target.value)}
                                    />
                                </div>

                                <div className="form-field">
                                    <label htmlFor="q-rwe">Real-World Example</label>
                                    <textarea
                                        id="q-rwe"
                                        placeholder="How is this used in a real application?"
                                        value={questionForm.real_world_example}
                                        onChange={(e) => qf("real_world_example", e.target.value)}
                                    />
                                </div>

                                <div className="form-field">
                                    <label htmlFor="q-code">Code Example</label>
                                    <textarea
                                        id="q-code"
                                        className="tall"
                                        placeholder="Paste code here (preserve indentation)"
                                        style={{ fontFamily: "monospace" }}
                                        value={questionForm.code_example}
                                        onChange={(e) => qf("code_example", e.target.value)}
                                    />
                                </div>

                                <div className="form-field">
                                    <label htmlFor="q-out">Expected Output</label>
                                    <textarea
                                        id="q-out"
                                        placeholder="What does the code print/return?"
                                        style={{ fontFamily: "monospace" }}
                                        value={questionForm.expected_output}
                                        onChange={(e) => qf("expected_output", e.target.value)}
                                    />
                                </div>

                                <div className="form-field">
                                    <label htmlFor="q-flow">Flowchart / Diagram (optional)</label>
                                    <textarea
                                        id="q-flow"
                                        placeholder={"e.g.\nUser Input\n↓\nReact Component\n↓\nState Update\n↓\nRe-render"}
                                        style={{ fontFamily: "monospace" }}
                                        value={questionForm.flowchart}
                                        onChange={(e) => qf("flowchart", e.target.value)}
                                    />
                                </div>

                                <div className="form-field">
                                    <label htmlFor="q-kp">Key Points (one per line)</label>
                                    <textarea
                                        id="q-kp"
                                        placeholder={"React is declarative\nVirtual DOM improves performance\nComponent-based architecture"}
                                        value={questionForm.key_points}
                                        onChange={(e) => qf("key_points", e.target.value)}
                                    />
                                </div>

                                <div className="form-field">
                                    <label htmlFor="q-rem">Remember This</label>
                                    <textarea
                                        id="q-rem"
                                        placeholder="The key takeaway students must not forget"
                                        value={questionForm.remember_this}
                                        onChange={(e) => qf("remember_this", e.target.value)}
                                    />
                                </div>

                                <div className="admin-form-row">
                                    <button
                                        type="submit"
                                        className="btn-primary"
                                        disabled={saving || !selectedTopicId}
                                    >
                                        {saving
                                            ? "Saving..."
                                            : editingQuestionId
                                            ? "Update Question"
                                            : "Add Question"}
                                    </button>
                                    {editingQuestionId && (
                                        <button
                                            type="button"
                                            className="btn-secondary"
                                            onClick={resetQuestionForm}
                                        >
                                            Cancel
                                        </button>
                                    )}
                                </div>
                            </form>
                        </div>
                    </div>
                )}
            </div>
        </main>
    );
}

export default AdminTopics;
