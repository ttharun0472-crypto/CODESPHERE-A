import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
    getCourses,
    getAllProgress,
    getCourseLessons,
    calculateCourseProgress,
    getAuthToken,
} from "../../services/learningApi";

import "./learning.css";


function LearningAnalytics() {

    const [courses, setCourses] =
        useState([]);

    const [progress, setProgress] =
        useState([]);

    const [courseLessons, setCourseLessons] =
        useState({});

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState("");


    async function loadAnalytics() {

        try {

            setLoading(true);
            setError("");


            if (!getAuthToken()) {

                setError(
                    "Please login to view your learning analytics."
                );

                return;
            }


            const [
                coursesData,
                progressData,
            ] = await Promise.all([
                getCourses(),
                getAllProgress(),
            ]);


            setCourses(
                Array.isArray(coursesData)
                    ? coursesData
                    : []
            );

            setProgress(
                Array.isArray(progressData)
                    ? progressData
                    : []
            );


            const lessonsMap = {};


            await Promise.all(
                coursesData.map(
                    async (course) => {

                        try {

                            const lessons =
                                await getCourseLessons(
                                    course.id
                                );

                            lessonsMap[
                                course.id
                            ] =
                                Array.isArray(
                                    lessons
                                )
                                    ? lessons
                                    : [];

                        } catch {

                            lessonsMap[
                                course.id
                            ] = [];

                        }

                    }
                )
            );


            setCourseLessons(
                lessonsMap
            );

        } catch (err) {

            setError(
                err.message ||
                "Unable to load analytics."
            );

        } finally {

            setLoading(false);

        }
    }


    useEffect(() => {
        const load = window.setTimeout(() => {
            void loadAnalytics();
        }, 0);

        return () => window.clearTimeout(load);
    }, []);


    if (loading) {

        return (
            <main className="learning-page">

                <section className="learning-loading">

                    <div className="loading-spinner" />

                    <h2>
                        Analyzing your learning...
                    </h2>

                </section>

            </main>
        );
    }


    if (error) {

        return (
            <main className="learning-page">

                <section className="learning-state">

                    <div className="state-icon">
                        !
                    </div>

                    <h2>
                        Analytics unavailable
                    </h2>

                    <p>
                        {error}
                    </p>

                    <Link
                        to="/login"
                        className="retry-button"
                    >
                        Login
                    </Link>

                </section>

            </main>
        );
    }


    const totalLessons =
        Object.values(courseLessons)
            .reduce(
                (total, lessons) =>
                    total + lessons.length,
                0
            );


    const completedLessons =
        progress.filter(
            (item) =>
                Number(
                    item.completion_percentage
                ) >= 100
        ).length;


    const overallProgress =
        totalLessons > 0
            ? Math.round(
                (completedLessons /
                    totalLessons) *
                100
            )
            : 0;


    return (
        <main className="learning-page">

            <section className="analytics-hero">

                <span className="eyebrow">
                    LEARNING ANALYTICS
                </span>

                <h1>
                    Understand how
                    <br />
                    you're learning.
                </h1>

                <p>
                    Your analytics are calculated from
                    your actual lesson progress stored
                    by CodeSphere.
                </p>

            </section>


            <section className="analytics-stats">

                <div className="analytics-stat">

                    <span>
                        Overall Progress
                    </span>

                    <strong>
                        {overallProgress}%
                    </strong>

                </div>


                <div className="analytics-stat">

                    <span>
                        Completed Lessons
                    </span>

                    <strong>
                        {completedLessons}
                    </strong>

                </div>


                <div className="analytics-stat">

                    <span>
                        Total Lessons
                    </span>

                    <strong>
                        {totalLessons}
                    </strong>

                </div>


                <div className="analytics-stat">

                    <span>
                        Courses
                    </span>

                    <strong>
                        {courses.length}
                    </strong>

                </div>

            </section>


            <section className="analytics-courses">

                <div className="section-heading">

                    <div>

                        <span className="eyebrow">
                            COURSE PERFORMANCE
                        </span>

                        <h2>
                            Your learning journey
                        </h2>

                    </div>

                </div>


                <div className="analytics-course-list">

                    {courses.map((course) => {

                        const lessons =
                            courseLessons[
                            course.id
                            ] || [];

                        const percentage =
                            calculateCourseProgress(
                                lessons,
                                progress
                            );


                        return (
                            <Link
                                key={course.id}
                                to={`/learning/course/${course.id}`}
                                className="analytics-course"
                            >

                                <div>

                                    <span>
                                        {course.title}
                                    </span>

                                    <p>
                                        {lessons.length}{" "}
                                        lessons
                                    </p>

                                </div>


                                <div className="analytics-course-right">

                                    <div className="analytics-progress">

                                        <div
                                            style={{
                                                width: `${percentage}%`,
                                            }}
                                        />

                                    </div>

                                    <strong>
                                        {percentage}%
                                    </strong>

                                </div>

                            </Link>
                        );
                    })}

                </div>

            </section>

        </main>
    );
}

export default LearningAnalytics;