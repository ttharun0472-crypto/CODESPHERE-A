const API_BASE_URL =
    import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";


// ======================================================
// TOKEN
// ======================================================

function getAuthToken() {
    return (
        localStorage.getItem("token") ||
        localStorage.getItem("access_token") ||
        localStorage.getItem("authToken")
    );
}


// ======================================================
// COMMON REQUEST
// ======================================================

async function apiRequest(endpoint, options = {}) {
    const token = getAuthToken();

    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {}),
    };

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
    });

    let data;
    try {
        data = await response.json();
    } catch {
        data = undefined;
    }

    if (!response.ok) {
        const message =
            data?.detail ||
            data?.message ||
            `Request failed with status ${response.status}`;
        throw new Error(message);
    }

    return data;
}


// ======================================================
// TOPICS
// ======================================================

// Student: get topics for a lesson with per-topic completion counts
export async function getTopicsForLesson(lessonId) {
    return apiRequest(`/topics/lesson/${lessonId}`);
}

// Admin: get plain topic list for a lesson
export async function adminGetTopicsForLesson(lessonId) {
    return apiRequest(`/topics/admin/lesson/${lessonId}`);
}

export async function getTopic(topicId) {
    return apiRequest(`/topics/${topicId}`);
}

export async function getNextTopic(topicId) {
    return apiRequest(`/topics/${topicId}/next`);
}

export async function getLessonTopicCompletion(lessonId) {
    return apiRequest(`/topics/lesson/${lessonId}/completion`);
}

export async function createTopic(topic) {
    return apiRequest("/topics", {
        method: "POST",
        body: JSON.stringify(topic),
    });
}

export async function updateTopic(topicId, topic) {
    return apiRequest(`/topics/${topicId}`, {
        method: "PUT",
        body: JSON.stringify(topic),
    });
}

export async function deleteTopic(topicId) {
    return apiRequest(`/topics/${topicId}`, {
        method: "DELETE",
    });
}


// ======================================================
// QUESTIONS
// ======================================================

export async function getQuestionsForTopic(topicId) {
    return apiRequest(`/questions/topic/${topicId}`);
}

export async function getQuestion(questionId) {
    return apiRequest(`/questions/${questionId}`);
}

export async function createQuestion(question) {
    return apiRequest("/questions", {
        method: "POST",
        body: JSON.stringify(question),
    });
}

export async function updateQuestion(questionId, question) {
    return apiRequest(`/questions/${questionId}`, {
        method: "PUT",
        body: JSON.stringify(question),
    });
}

export async function deleteQuestion(questionId) {
    return apiRequest(`/questions/${questionId}`, {
        method: "DELETE",
    });
}


// ======================================================
// QUESTION PROGRESS
// ======================================================

export async function markQuestionComplete(questionId) {
    return apiRequest("/questions/progress/complete", {
        method: "POST",
        body: JSON.stringify({ question_id: questionId }),
    });
}

export async function getCompletedQuestionsInTopic(topicId) {
    return apiRequest(`/questions/progress/topic/${topicId}`);
}

export async function getTopicCompletion(topicId) {
    return apiRequest(`/questions/completion/topic/${topicId}`);
}

export async function getLessonCompletion(lessonId) {
    return apiRequest(`/questions/completion/lesson/${lessonId}`);
}


// ======================================================
// DEFAULT EXPORT
// ======================================================

export default {
    getTopicsForLesson,
    adminGetTopicsForLesson,
    getTopic,
    getNextTopic,
    getLessonTopicCompletion,
    createTopic,
    updateTopic,
    deleteTopic,
    getQuestionsForTopic,
    getQuestion,
    createQuestion,
    updateQuestion,
    deleteQuestion,
    markQuestionComplete,
    getCompletedQuestionsInTopic,
    getTopicCompletion,
    getLessonCompletion,
};
