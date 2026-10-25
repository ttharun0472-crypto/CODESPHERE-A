import { useEffect, useState } from "react";
import {
    Link,
    useParams,
} from "react-router-dom";

import {
    getCourse,
    getCourseLessons,
    getAllProgress,
    getProgressForLesson,
    calculateCourseProgress,
    getAuthToken,
} from "../../services/learningApi";

import "./learning.css";


function CourseDetails() {

    const { courseId } = useParams();

    const [course, setCourse] =
        useState(null);

    const [lessons, setLessons] =
        useState([]);

    const [progress, setProgress] =
        useState([]);

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState("");


    async function loadCourse() {

        try {

            setLoading(true);
            setError("");

            const courseData =
                await getCourse(courseId);

            const lessonsData =
                await getCourseLessons(courseId);

            setCourse(courseData);

            setLessons(
                Array.isArray(lessonsData)
                    ? lessonsData
                    : []
            );


            if (getAuthToken()) {

                try {

                    const progressData =
                        await getAllProgress();

                    setProgress(
                        Array.isArray(progressData)
                            ? progressData
                            : []
                    );

                } catch {

                    setProgress([]);

                }

            }

        } catch (err) {

            setError(
                err.message ||
                "Unable to load course."
            );

        } finally {

            setLoading(false);

        }
    }


    useEffect(() => {
        const load = window.setTimeout(() => {
            void loadCourse();
        }, 0);

        return () => window.clearTimeout(load);
    }, [courseId]);


    if (loading) {

        return (
            <main className="learning-page">

                <section className="learning-loading">

                    <div className="loading-spinner" />

                    <h2>
                        Loading course...
                    </h2>

                </section>

            </main>
        );
    }


    if (error || !course) {

        return (
            <main className="learning-page">

                <section className="learning-state">

                    <div className="state-icon">
                        !
                    </div>

                    <h2>
                        Course not found
                    </h2>

                    <p>
                        {error}
                    </p>

                    <Link
                        to="/learning"
                        className="retry-button"
                    >
                        Back to Learning
                    </Link>

                </section>

            </main>
        );
    }


    const courseProgress =
        calculateCourseProgress(
            lessons,
            progress
        );


    const completedLessons =
        lessons.filter(
            (lesson) =>
                getProgressForLesson(
                    progress,
                    lesson.id
                ) >= 100
        ).length;


    return (
        <main className="learning-page">

            <section className="course-detail-hero">

                <div>

                    <Link
                        to="/learning"
                        className="back-link"
                    >
                        ← Back to courses
                    </Link>

                    <span className="eyebrow">
                        COURSE
                    </span>

                    <h1>
                        {course.title}
                    </h1>

                    <p>
                        {course.description ||
                            "Start this course and build your knowledge step by step."}
                    </p>

                </div>


                <div className="course-progress-circle">

                    <div>

                        <strong>
                            {courseProgress}%
                        </strong>

                        <span>
                            Complete
                        </span>

                    </div>

                </div>

            </section>


            <section className="course-content">

                <div className="course-content-header">

                    <div>

                        <span className="eyebrow">
                            COURSE CONTENT
                        </span>

                        <h2>
                            Lessons
                        </h2>

                    </div>

                    <span className="lesson-summary">
                        {completedLessons} /{" "}
                        {lessons.length} completed
                    </span>

                </div>


                {lessons.length === 0 ? (

                    <div className="empty-state">

                        <div className="empty-icon">
                            +
                        </div>

                        <h3>
                            No lessons available
                        </h3>

                        <p>
                            Lessons will appear here when
                            the administrator adds them.
                        </p>

                    </div>

                ) : (

                    <div className="lesson-list">

                        {lessons.map(
                            (lesson, index) => {

                                const lessonProgress =
                                    getProgressForLesson(
                                        progress,
                                        lesson.id
                                    );

                                return (
                                    <Link
                                        key={lesson.id}
                                        to={`/learning/course/${course.id}/lesson/${lesson.id}`}
                                        className="lesson-row"
                                    >

                                        <div className="lesson-number">
                                            {String(
                                                index + 1
                                            ).padStart(
                                                2,
                                                "0"
                                            )}
                                        </div>


                                        <div className="lesson-info">

                                            <h3>
                                                {lesson.title}
                                            </h3>

                                            <p>
                                                {lesson.important_concepts ||
                                                    "Continue this lesson to build your skills."}
                                            </p>

                                        </div>


                                        <div className="lesson-progress">

                                            <div className="mini-progress">

                                                <div
                                                    style={{
                                                        width: `${lessonProgress}%`,
                                                    }}
                                                />

                                            </div>

                                            <span>
                                                {Math.round(
                                                    lessonProgress
                                                )}%
                                            </span>

                                        </div>


                                        <div className="lesson-arrow">
                                            →
                                        </div>

                                    </Link>
                                );
                            }
                        )}

                    </div>

                )}

            </section>

        </main>
    );
}

export default CourseDetails;