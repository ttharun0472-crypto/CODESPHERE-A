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

// Get all placement job postings
export async function getPlacements() {
  return apiRequest("/placements");
}

// Get single placement details
export async function getPlacement(id) {
  return apiRequest(`/placements/${id}`);
}

// Create new placement job (Admin)
export async function createPlacement(placementData) {
  return apiRequest("/placements", {
    method: "POST",
    body: JSON.stringify(placementData),
  });
}

// Update existing placement (Admin)
export async function updatePlacement(id, placementData) {
  return apiRequest(`/placements/${id}`, {
    method: "PUT",
    body: JSON.stringify(placementData),
  });
}

// Delete placement job (Admin)
export async function deletePlacement(id) {
  return apiRequest(`/placements/${id}`, {
    method: "DELETE",
  });
}

// Get AI-powered placement recommendations
export async function getPlacementRecommendations(filters = {}) {
  return apiRequest("/api/jev/placement/recommend", {
    method: "POST",
    body: JSON.stringify(filters),
  });
}

export default {
  getPlacements,
  getPlacement,
  createPlacement,
  updatePlacement,
  deletePlacement,
  getPlacementRecommendations,
};
