import { apiRequest } from "./apiClient";

export function loginUser(credentials) {
    return apiRequest("/auth/login", {
        method: "POST",
        body: JSON.stringify(credentials),
    });
}

export function adminLoginUser(credentials) {
    return apiRequest("/auth/admin/login", {
        method: "POST",
        body: JSON.stringify(credentials),
    });
}

export function registerUser(user) {
    return apiRequest("/auth/register", {
        method: "POST",
        body: JSON.stringify(user),
    });
}

export function requestRegistrationOtp(email) {
    return apiRequest("/auth/register/request-otp", {
        method: "POST",
        body: JSON.stringify({ email }),
    });
}

export function verifyRegistrationOtp(email, otp) {
    return apiRequest("/auth/register/verify-otp", {
        method: "POST",
        body: JSON.stringify({ email, otp }),
    });
}

export function requestEmailOtp(email) {
    return apiRequest("/auth/otp/request", {
        method: "POST",
        body: JSON.stringify({ email }),
    });
}

export function verifyEmailOtp(email, otp) {
    return apiRequest("/auth/otp/verify", {
        method: "POST",
        body: JSON.stringify({ email, otp }),
    });
}

export function requestPasswordResetOtp(email) {
    return apiRequest("/auth/password-reset/request", {
        method: "POST",
        body: JSON.stringify({ email }),
    });
}

export function verifyPasswordResetOtp(email, otp) {
    return apiRequest("/auth/password-reset/verify", {
        method: "POST",
        body: JSON.stringify({ email, otp }),
    });
}

export function resetPasswordWithOtp({ email, otp, newPassword, confirmPassword }) {
    return apiRequest("/auth/password-reset", {
        method: "POST",
        body: JSON.stringify({
            email,
            otp,
            new_password: newPassword,
            confirm_password: confirmPassword,
        }),
    });
}
