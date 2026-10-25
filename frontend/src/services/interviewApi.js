import { apiRequest } from "./apiClient";

// Get all interview questions
export async function getInterviews() {
  return apiRequest("/interviews");
}

// Get questions by category
export async function getInterviewsByCategory(category) {
  return apiRequest(`/interviews/category/${encodeURIComponent(category)}`);
}

// Get questions by difficulty
export async function getInterviewsByDifficulty(difficulty) {
  return apiRequest(`/interviews/difficulty/${encodeURIComponent(difficulty)}`);
}

export async function getCompletedInterviewCourses() {
  return apiRequest("/progress/completed-courses");
}

export async function getAvailableInterviewQuestions({
  courseId,
  category,
  difficulty,
}) {
  const query = new URLSearchParams({ category, difficulty });
  if (courseId) query.set("course_id", String(courseId));
  return apiRequest(`/interview/sessions/available-questions?${query}`);
}

export async function startInterview(configuration) {
  return apiRequest("/interview/sessions", {
    method: "POST",
    body: JSON.stringify(configuration),
  });
}

export async function getInterviewSummary() {
  return apiRequest("/interview/sessions/summary");
}

export async function getInterviewHistory() {
  return apiRequest("/interview/sessions");
}

export async function getActiveInterview() {
  return apiRequest("/interview/sessions/active");
}

export async function getInterviewSession(sessionId) {
  return apiRequest(`/interview/sessions/${sessionId}`);
}

export async function submitInterviewAnswer(sessionId, questionIndex, answer) {
  return apiRequest(
    `/interview/sessions/${sessionId}/answers/${questionIndex}`,
    {
      method: "POST",
      body: JSON.stringify({ answer }),
    }
  );
}

export async function completeInterview(sessionId) {
  return apiRequest(`/interview/sessions/${sessionId}/complete`, {
    method: "POST",
  });
}

export function getMCQOptions() {
  return apiRequest("/interview/mcq/options");
}

export function getActiveMCQAttempt() {
  return apiRequest("/interview/mcq/attempts/active");
}

export function startMCQAttempt(configuration) {
  return apiRequest("/interview/mcq/attempts", {
    method: "POST",
    body: JSON.stringify(configuration),
  });
}

export function getMCQAttempt(attemptId) {
  return apiRequest(`/interview/mcq/attempts/${attemptId}`);
}

export function submitMCQAttempt(attemptId, answers) {
  return apiRequest(`/interview/mcq/attempts/${attemptId}/submit`, {
    method: "POST",
    body: JSON.stringify({ answers }),
  });
}

export function getMCQHistory() {
  return apiRequest("/interview/mcq/history");
}

export function getMCQProgress() {
  return apiRequest("/interview/mcq/progress");
}

export default {
  getInterviews,
  getInterviewsByCategory,
  getInterviewsByDifficulty,
  getCompletedInterviewCourses,
  getAvailableInterviewQuestions,
  startInterview,
  getInterviewSummary,
  getInterviewHistory,
  getActiveInterview,
  getInterviewSession,
  submitInterviewAnswer,
  completeInterview,
  getMCQOptions,
  getActiveMCQAttempt,
  startMCQAttempt,
  getMCQAttempt,
  submitMCQAttempt,
  getMCQHistory,
  getMCQProgress,
};
