const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export function getAuthToken() {
  return (
    localStorage.getItem("token") ||
    localStorage.getItem("access_token") ||
    localStorage.getItem("authToken")
  );
}

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

// Get logged-in user's resume
export async function getMyResume() {
  return apiRequest("/resumes/me");
}

// Create or update resume
export async function saveResume(resumeData) {
  return apiRequest("/resumes", {
    method: "POST",
    body: JSON.stringify(resumeData),
  });
}

// Delete user's resume
export async function deleteResume() {
  return apiRequest("/resumes/me", {
    method: "DELETE",
  });
}

export default {
  getMyResume,
  saveResume,
  deleteResume,
};
