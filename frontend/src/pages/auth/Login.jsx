import { Link, useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";
import {
  adminLoginUser,
  loginUser,
  requestPasswordResetOtp,
  resetPasswordWithOtp,
  verifyPasswordResetOtp,
} from "../../services/authApi";

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/;

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [mode, setMode] = useState("login");
  const [otpRequested, setOtpRequested] = useState(false);
  const [otpVerified, setOtpVerified] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const persistAuth = (tokens) => {
    const finalRole = tokens.role || (tokens.is_admin ? "admin" : "user");
    localStorage.setItem("access_token", tokens.access_token);
    localStorage.setItem("refresh_token", tokens.refresh_token);
    localStorage.setItem("token", tokens.access_token);
    localStorage.setItem("role", finalRole);
    localStorage.setItem("is_admin", String(Boolean(tokens.is_admin)));
    localStorage.setItem("otp_verified", "true");
    window.dispatchEvent(new Event("auth-change"));

    const destination = location.state?.from;
    navigate(finalRole === "admin" ? "/admin" : destination || "/dashboard", {
      replace: true,
    });
  };

  const handleLogin = async (event) => {
    event.preventDefault();
    setError("");
    setNotice("");

    if (!emailPattern.test(email.trim())) {
      setError("Enter a valid email address.");
      return;
    }
    if (!password) {
      setError("Enter your password.");
      return;
    }

    try {
      setLoading(true);
      const tokens = await loginUser({ email: email.trim(), password });
      persistAuth(tokens);
    } catch (requestError) {
      setError(requestError.message || "Invalid email or password.");
    } finally {
      setLoading(false);
    }
  };

  const handleAdminLogin = async () => {
    try {
      setLoading(true);
      const tokens = await adminLoginUser({ email: email.trim(), password });
      persistAuth(tokens);
    } catch (requestError) {
      setError(requestError.message || "Admin sign-in failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleRequestResetOtp = async (event) => {
    event.preventDefault();
    setError("");
    setNotice("");

    if (!emailPattern.test(email.trim())) {
      setError("Enter a valid email address for password reset.");
      return;
    }

    try {
      setLoading(true);
      const response = await requestPasswordResetOtp(email.trim());
      setOtpRequested(true);
      setOtp("");
      setOtpVerified(false);
      setCountdown(response.retry_after_seconds || 60);
      setNotice(response.message || "A verification code has been sent to your email.");
    } catch (requestError) {
      setError(requestError.message || "Unable to send the verification code.");
      if (requestError.retryAfterSeconds) {
        setCountdown(requestError.retryAfterSeconds);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyResetOtp = async (event) => {
    event.preventDefault();
    setError("");
    setNotice("");

    if (!/^\d{6}$/.test(otp)) {
      setError("Enter the six-digit verification code.");
      return;
    }

    try {
      setLoading(true);
      await verifyPasswordResetOtp(email.trim(), otp);
      setOtpVerified(true);
      setNotice("OTP verified. Enter a new password.");
    } catch (requestError) {
      setOtp("");
      setError(requestError.message || "Unable to verify the code.");
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordReset = async (event) => {
    event.preventDefault();
    setError("");
    setNotice("");

    if (!otpVerified) {
      setError("Verify the OTP before setting a new password.");
      return;
    }
    if (!passwordPattern.test(newPassword)) {
      setError("Use at least 8 characters with uppercase, lowercase, a number, and a symbol.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("New passwords do not match.");
      return;
    }

    try {
      setLoading(true);
      const response = await resetPasswordWithOtp({
        email: email.trim(),
        otp,
        newPassword,
        confirmPassword,
      });
      setMode("login");
      setPassword("");
      setOtp("");
      setNewPassword("");
      setConfirmPassword("");
      setOtpRequested(false);
      setOtpVerified(false);
      setNotice(response.message || "Password reset successful.");
    } catch (requestError) {
      setError(requestError.message || "Unable to reset password.");
    } finally {
      setLoading(false);
    }
  };

  const resetFlow = () => {
    setMode("login");
    setOtpRequested(false);
    setOtpVerified(false);
    setOtp("");
    setNewPassword("");
    setConfirmPassword("");
    setError("");
    setNotice("");
    setCountdown(0);
  };

  return (
    <main className="auth-page login-page">
      <section className="auth-card login-card" aria-labelledby="login-title">
        <div className="login-brand" aria-label="CodeSphere AI">
          <span className="login-brand-mark">C</span>
          <span>CodeSphere <strong>AI</strong></span>
        </div>

        <div className="login-heading">
          <span className="login-eyebrow">SECURE SIGN IN</span>
          <h1 id="login-title">{mode === "forgot" ? "Reset your password" : "Welcome back"}</h1>
          <p>
            {mode === "forgot"
              ? "Verify your email and choose a new password."
              : "Sign in with your email and password."}
          </p>
        </div>

        {error && <p className="login-message login-error" role="alert">{error}</p>}
        {notice && <p className="login-message login-notice" role="status">{notice}</p>}

        {mode === "login" ? (
          <form onSubmit={handleLogin}>
            <div className="login-field">
              <label htmlFor="login-email">Email address</label>
              <input
                id="login-email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@example.com"
                autoComplete="email"
                required
                disabled={loading}
              />
            </div>

            <div className="login-field">
              <label htmlFor="login-password">Password</label>
              <input
                id="login-password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Enter your password"
                autoComplete="current-password"
                required
                disabled={loading}
              />
            </div>

            <button className="login-primary-button" type="submit" disabled={loading}>
              {loading ? "Signing in..." : "Sign In"}
            </button>

            <div className="login-otp-actions" style={{ marginTop: "12px" }}>
              <button type="button" className="login-text-button" onClick={handleAdminLogin} disabled={loading}>
                Admin Login
              </button>
              <button type="button" className="login-text-button" onClick={() => setMode("forgot")} disabled={loading}>
                Forgot password?
              </button>
            </div>
          </form>
        ) : (
          <form onSubmit={otpVerified ? handlePasswordReset : otpRequested ? handleVerifyResetOtp : handleRequestResetOtp}>
            <div className="login-field">
              <label htmlFor="reset-email">Email address</label>
              <input
                id="reset-email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@example.com"
                autoComplete="email"
                required
                disabled={loading}
              />
            </div>

            {otpRequested && !otpVerified && (
              <div className="login-field">
                <label htmlFor="reset-otp">Six-digit verification code</label>
                <input
                  id="reset-otp"
                  type="text"
                  value={otp}
                  onChange={(event) => setOtp(event.target.value.replace(/\D/g, "").slice(0, 6))}
                  placeholder="000000"
                  inputMode="numeric"
                  pattern="\d{6}"
                  maxLength={6}
                  required
                  disabled={loading}
                />
              </div>
            )}

            {otpVerified && (
              <>
                <div className="login-field">
                  <label htmlFor="reset-new-password">New password</label>
                  <input
                    id="reset-new-password"
                    type="password"
                    value={newPassword}
                    onChange={(event) => setNewPassword(event.target.value)}
                    placeholder="Enter a new password"
                    required
                    disabled={loading}
                  />
                </div>

                <div className="login-field">
                  <label htmlFor="reset-confirm-password">Confirm new password</label>
                  <input
                    id="reset-confirm-password"
                    type="password"
                    value={confirmPassword}
                    onChange={(event) => setConfirmPassword(event.target.value)}
                    placeholder="Confirm the new password"
                    required
                    disabled={loading}
                  />
                </div>
              </>
            )}

            <button className="login-primary-button" type="submit" disabled={loading}>
              {loading
                ? "Please wait..."
                : otpVerified
                  ? "Reset Password"
                  : otpRequested
                    ? "Verify OTP"
                    : "Send OTP"}
            </button>

            <div className="login-otp-actions" style={{ marginTop: "12px" }}>
              <button type="button" className="login-text-button" onClick={resetFlow} disabled={loading}>
                Back to login
              </button>
            </div>
          </form>
        )}

        <p className="auth-link login-register-link">
          Don’t have an account? <Link to="/register">Create an account</Link>
        </p>
      </section>
    </main>
  );
}

export default Login;