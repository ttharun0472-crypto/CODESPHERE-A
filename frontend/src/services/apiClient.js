export const API_BASE_URL = import.meta.env.VITE_API_URL?.trim().replace(/\/+$/, "");

export function getAuthToken() {
  if (localStorage.getItem("otp_verified") !== "true") {
    return null;
  }
  return (
    localStorage.getItem("token") ||
    localStorage.getItem("access_token") ||
    localStorage.getItem("authToken")
  );
}

function getResponseError(data, status) {
  if (status === 401) {
    return "Your session is no longer valid. Please sign in again.";
  }

  const detail = data?.detail ?? data?.message;
  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const location = Array.isArray(item?.loc) ? item.loc.join(".") : "";
        return [location, item?.msg].filter(Boolean).join(": ");
      })
      .filter(Boolean)
      .join(" ");
  }
  return `Request failed with status ${status}.`;
}

export async function apiRequest(endpoint, options = {}) {
  if (!API_BASE_URL) {
    throw new Error(
      "VITE_API_URL is not configured. Set it in frontend/.env to the FastAPI base URL."
    );
  }

  const token = getAuthToken();
  const headers = new Headers(options.headers || {});
  headers.set("Accept", "application/json");
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });
  } catch (error) {
    if (error?.name === "AbortError") {
      throw new Error("The request to the CodeSphere API was cancelled.", {
        cause: error,
      });
    }
    throw new Error(
      `Unable to connect to the FastAPI backend at ${API_BASE_URL}. Check that the backend is running and VITE_API_URL is correct.`,
      { cause: error }
    );
  }

  const contentType = response.headers.get("content-type") || "";
  let data;
  if (contentType.includes("application/json")) {
    try {
      data = await response.json();
    } catch {
      throw new Error("The API returned invalid JSON.");
    }
  } else if (response.status !== 204) {
    const text = await response.text();
    if (text) {
      data = { message: text };
    }
  }

  if (!response.ok) {
    const error = new Error(getResponseError(data, response.status));
    const retryAfter = Number(response.headers.get("retry-after"));
    if (Number.isFinite(retryAfter) && retryAfter > 0) {
      error.retryAfterSeconds = retryAfter;
    }
    throw error;
  }

  return data;
}
