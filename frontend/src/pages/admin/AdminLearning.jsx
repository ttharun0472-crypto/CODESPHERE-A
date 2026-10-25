import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
    createCourse,
    createLesson,
    deleteCourse,
    deleteLesson,
    getCourseLessons,
    getCourses,
    updateCourse,
    updateLesson,
} from "../../services/learningApi";

const emptyCourse = { title: "", description: "" };
const emptyLesson = { course_id: "", title: "", notes: "", important_concepts: "", youtube_url: "", lesson_order: "" };

function AdminLearning() {
    const navigate = useNavigate();
    const [courses, setCourses] = useState([]);
    const [lessons, setLessons] = useState({});
    const [courseForm, setCourseForm] = useState(emptyCourse);
    const [lessonForm, setLessonForm] = useState(emptyLesson);
    const [editingCourse, setEditingCourse] = useState(null);
    const [editingLesson, setEditingLesson] = useState(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");

    const loadLearning = async () => {
        try {
            setLoading(true);
            setError("");
            const courseData = await getCourses();
            const courseList = Array.isArray(courseData) ? courseData : [];
            const lessonEntries = await Promise.all(courseList.map(async (course) => [
                course.id,
                await getCourseLessons(course.id),
            ]));
            setCourses(courseList);
            setLessons(Object.fromEntries(lessonEntries));
            if (!lessonForm.course_id && courseList[0]) {
                setLessonForm((current) => ({ ...current, course_id: String(courseList[0].id) }));
            }
        } catch (requestError) {
            if (requestError.message.toLowerCase().includes("admin") || requestError.message.toLowerCase().includes("denied")) {
                navigate("/dashboard");
                return;
            }
            setError(requestError.message || "Unable to load learning content.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (localStorage.getItem("is_admin") !== "true" || !localStorage.getItem("access_token")) {
            navigate("/dashboard");
            return;
        }
        void loadLearning();
    }, [navigate]);

    const submitCourse = async (event) => {
        event.preventDefault();
        try {
            setSaving(true);
            if (editingCourse) await updateCourse(editingCourse, courseForm);
            else await createCourse(courseForm);
            setCourseForm(emptyCourse);
            setEditingCourse(null);
            await loadLearning();
        } catch (requestError) {
            setError(requestError.message || "Unable to save course.");
        } finally {
            setSaving(false);
        }
    };

    const submitLesson = async (event) => {
        event.preventDefault();
        try {
            setSaving(true);
            const payload = {
                ...lessonForm,
                course_id: Number(lessonForm.course_id),
                lesson_order: lessonForm.lesson_order ? Number(lessonForm.lesson_order) : null,
            };
            if (editingLesson) await updateLesson(editingLesson, payload);
            else await createLesson(payload);
            setLessonForm({ ...emptyLesson, course_id: lessonForm.course_id });
            setEditingLesson(null);
            await loadLearning();
        } catch (requestError) {
            setError(requestError.message || "Unable to save lesson.");
        } finally {
            setSaving(false);
        }
    };

    const removeCourse = async (course) => {
        if (!window.confirm(`Delete course "${course.title}"?`)) return;
        try {
            await deleteCourse(course.id);
            await loadLearning();
        } catch (requestError) {
            setError(requestError.message || "Unable to delete course.");
        }
    };

    const removeLesson = async (lesson) => {
        if (!window.confirm(`Delete lesson "${lesson.title}"?`)) return;
        try {
            await deleteLesson(lesson.id);
            await loadLearning();
        } catch (requestError) {
            setError(requestError.message || "Unable to delete lesson.");
        }
    };

    const startCourseEdit = (course) => {
        setEditingCourse(course.id);
        setCourseForm({ title: course.title, description: course.description || "" });
    };

    const startLessonEdit = (lesson) => {
        setEditingLesson(lesson.id);
        setLessonForm({
            course_id: String(lesson.course_id),
            title: lesson.title,
            notes: lesson.notes || "",
            important_concepts: lesson.important_concepts || "",
            youtube_url: lesson.youtube_url || "",
            lesson_order: lesson.lesson_order ? String(lesson.lesson_order) : "",
        });
    };

    if (loading) return <main className="admin-page"><div className="admin-container"><p className="admin-empty">Loading learning content...</p></div></main>;

    return (
        <main className="admin-page">
            <div className="admin-container">
                <header className="admin-header admin-learning-header">
                    <div>
                        <Link to="/admin" className="back-link">Back to admin dashboard</Link>
                        <p className="eyebrow">Learning management</p>
                        <h1>Courses and Lessons</h1>
                    </div>
                </header>

                {error && <div className="admin-error">{error}</div>}

                <section className="admin-form-grid">
                    <form className="admin-panel-card admin-form" onSubmit={submitCourse}>
                        <h2>{editingCourse ? "Edit course" : "Create course"}</h2>
                        <input required minLength={2} placeholder="Course title" value={courseForm.title} onChange={(event) => setCourseForm({ ...courseForm, title: event.target.value })} />
                        <textarea placeholder="Course description" value={courseForm.description} onChange={(event) => setCourseForm({ ...courseForm, description: event.target.value })} />
                        <div className="admin-form-actions">
                            <button type="submit" disabled={saving}>{editingCourse ? "Update course" : "Add course"}</button>
                            {editingCourse && <button type="button" className="secondary-btn" onClick={() => { setEditingCourse(null); setCourseForm(emptyCourse); }}>Cancel</button>}
                        </div>
                    </form>

                    <form className="admin-panel-card admin-form" onSubmit={submitLesson}>
                        <h2>{editingLesson ? "Edit lesson" : "Create lesson"}</h2>
                        <select required value={lessonForm.course_id} onChange={(event) => setLessonForm({ ...lessonForm, course_id: event.target.value })}>
                            <option value="">Select course</option>
                            {courses.map((course) => <option key={course.id} value={course.id}>{course.title}</option>)}
                        </select>
                        <input required minLength={2} placeholder="Lesson title" value={lessonForm.title} onChange={(event) => setLessonForm({ ...lessonForm, title: event.target.value })} />
                        <input type="number" min={1} placeholder="Lesson order (blank adds to end)" value={lessonForm.lesson_order} onChange={(event) => setLessonForm({ ...lessonForm, lesson_order: event.target.value })} />
                        <textarea placeholder="Notes" value={lessonForm.notes} onChange={(event) => setLessonForm({ ...lessonForm, notes: event.target.value })} />
                        <textarea placeholder="Important concepts" value={lessonForm.important_concepts} onChange={(event) => setLessonForm({ ...lessonForm, important_concepts: event.target.value })} />
                        <input type="url" placeholder="YouTube URL" value={lessonForm.youtube_url} onChange={(event) => setLessonForm({ ...lessonForm, youtube_url: event.target.value })} />
                        <div className="admin-form-actions">
                            <button type="submit" disabled={saving || courses.length === 0}>{editingLesson ? "Update lesson" : "Add lesson"}</button>
                            {editingLesson && <button type="button" className="secondary-btn" onClick={() => { setEditingLesson(null); setLessonForm({ ...emptyLesson, course_id: lessonForm.course_id }); }}>Cancel</button>}
                        </div>
                    </form>
                </section>

                <section className="admin-panel-card">
                    <div className="admin-panel-header"><h2>Learning content</h2></div>
                    {courses.length === 0 ? <p className="admin-empty">No courses found.</p> : courses.map((course) => (
                        <article className="learning-admin-course" key={course.id}>
                            <div className="learning-admin-course-header">
                                <div><h3>{course.title}</h3><p>{course.description || "No description"}</p></div>
                                <div className="admin-form-actions"><button type="button" onClick={() => startCourseEdit(course)}>Edit</button><button type="button" className="delete-btn" onClick={() => removeCourse(course)}>Delete</button></div>
                            </div>
                            {(lessons[course.id] || []).map((lesson) => (
                                <div className="learning-admin-lesson" key={lesson.id}>
                                    <span>{String(lesson.lesson_order || "").padStart(2, "0")} · {lesson.title}</span><div className="admin-form-actions"><button type="button" onClick={() => startLessonEdit(lesson)}>Edit</button><button type="button" className="delete-btn" onClick={() => removeLesson(lesson)}>Delete</button></div>
                                </div>
                            ))}
                        </article>
                    ))}
                </section>
            </div>
        </main>
    );
}

export default AdminLearning;