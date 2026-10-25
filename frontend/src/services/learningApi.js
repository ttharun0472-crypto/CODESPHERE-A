import { apiRequest, getAuthToken } from "./apiClient";

export { getAuthToken };


// ======================================================
// COURSES
// ======================================================

export async function getCourses() {
    return apiRequest("/learning/courses");
}


export async function getCourse(courseId) {
    return apiRequest(`/learning/courses/${courseId}`);
}

export async function createCourse(course) {
    return apiRequest("/learning/courses", {
        method: "POST",
        body: JSON.stringify(course),
    });
}

export async function updateCourse(courseId, course) {
    return apiRequest(`/learning/courses/${courseId}`, {
        method: "PUT",
        body: JSON.stringify(course),
    });
}

export async function deleteCourse(courseId) {
    return apiRequest(`/learning/courses/${courseId}`, {
        method: "DELETE",
    });
}


// ======================================================
// LESSONS
// ======================================================

export async function getCourseLessons(courseId) {
    return apiRequest(
        `/learning/courses/${courseId}/lessons`
    );
}


export async function getLesson(lessonId) {
    return apiRequest(
        `/learning/lessons/${lessonId}`
    );
}

export async function createLesson(lesson) {
    return apiRequest("/learning/lessons", {
        method: "POST",
        body: JSON.stringify(lesson),
    });
}

export async function updateLesson(lessonId, lesson) {
    return apiRequest(`/learning/lessons/${lessonId}`, {
        method: "PUT",
        body: JSON.stringify(lesson),
    });
}

export async function deleteLesson(lessonId) {
    return apiRequest(`/learning/lessons/${lessonId}`, {
        method: "DELETE",
    });
}


// ======================================================
// PROGRESS
// ======================================================

export async function getAllProgress() {
    return apiRequest("/progress");
}


export async function getLessonProgress(lessonId) {
    return apiRequest(
        `/progress/lesson/${lessonId}`
    );
}


export async function updateLessonProgress(
    lessonId,
    completionPercentage
) {
    return apiRequest(
        "/progress",
        {
            method: "POST",
            body: JSON.stringify({
                lesson_id: Number(lessonId),
                completion_percentage:
                    Number(completionPercentage),
            }),
        }
    );
}


// ======================================================
// HELPERS
// ======================================================

export function getProgressForLesson(
    progressList,
    lessonId
) {
    if (!Array.isArray(progressList)) {
        return 0;
    }

    const progress = progressList.find(
        (item) =>
            Number(item.lesson_id) ===
            Number(lessonId)
    );

    return progress
        ? Number(progress.completion_percentage || 0)
        : 0;
}


export function calculateCourseProgress(
    lessons,
    progressList
) {
    if (!Array.isArray(lessons) || lessons.length === 0) {
        return 0;
    }

    const total = lessons.reduce(
        (sum, lesson) => {
            const lessonProgress =
                getProgressForLesson(
                    progressList,
                    lesson.id
                );

            return sum + lessonProgress;
        },
        0
    );

    return Math.round(total / lessons.length);
}


export function getCompletedLessonCount(
    lessons,
    progressList
) {
    if (!Array.isArray(lessons)) {
        return 0;
    }

    return lessons.filter(
        (lesson) =>
            getProgressForLesson(
                progressList,
                lesson.id
            ) >= 100
    ).length;
}


export default {
    getCourses,
    getCourse,
    createCourse,
    updateCourse,
    deleteCourse,
    getCourseLessons,
    getLesson,
    createLesson,
    updateLesson,
    deleteLesson,
    getAllProgress,
    getLessonProgress,
    updateLessonProgress,
    getProgressForLesson,
    calculateCourseProgress,
    getCompletedLessonCount,
};