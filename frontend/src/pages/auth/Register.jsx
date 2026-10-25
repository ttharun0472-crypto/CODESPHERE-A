import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Register.css";
import {
  registerUser,
  requestRegistrationOtp,
  verifyRegistrationOtp,
} from "../../services/authApi";

const passwordPolicyMessage =
  "Use at least 8 characters with uppercase, lowercase, a number, and a symbol.";

function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [otpVerified, setOtpVerified] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const validatePassword = (value) => /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/.test(value);

  const handleRequestOtp = async (event) => {
    event.preventDefault();
    setError("");
    setNotice("");

    if (!username.trim() || !email.trim()) {
      setError("Enter your full name and email address.");
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      setError("Enter a valid email address.");
      return;
    }
    if (!validatePassword(password)) {
      setError(passwordPolicyMessage);
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      const response = await requestRegistrationOtp(email.trim());
      setOtpSent(true);
      setOtp("");
      setNotice(response.message || "A verification code has been sent to your email.");
    } catch (requestError) {
      setError(requestError.message || "Unable to send the verification code.");
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (event) => {
    event.preventDefault();
    setError("");
    setNotice("");

    if (!/^\d{6}$/.test(otp)) {
      setError("Enter the six-digit verification code.");
      return;
    }

    setLoading(true);
    try {
      await verifyRegistrationOtp(email.trim(), otp);
      setOtpVerified(true);
      setNotice("Email verified. Complete account creation.");
    } catch (requestError) {
      setOtp("");
      setError(requestError.message || "Unable to verify the code.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setNotice("");

    if (!otpVerified) {
      setError("Verify your email before creating an account.");
      return;
    }

    setLoading(true);
    try {
      await registerUser({ username: username.trim(), email: email.trim(), password });
      navigate("/login", { replace: true });
    } catch (requestError) {
      setError(requestError.message || "Unable to create account.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="register-page">
      <section className="register-card" aria-labelledby="register-title">
        <div className="register-brand" aria-label="CodeSphere AI">
          <span className="register-brand-mark">C</span>
          <span>CodeSphere <strong>AI</strong></span>
        </div>

        <div className="register-heading">
          <span className="register-eyebrow">CREATE ACCOUNT</span>
          <h1 id="register-title">Create Account</h1>
          <p>Create your CodeSphere account</p>
        </div>

        {error && <p className="register-message register-error">{error}</p>}
        {notice && <p className="register-message register-notice">{notice}</p>}

        <form onSubmit={otpVerified ? handleSubmit : otpSent ? handleVerifyOtp : handleRequestOtp}>
          <div className="register-field">
            <label htmlFor="register-name">Full name</label>
            <input
              id="register-name"
              type="text"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              placeholder="Enter your full name"
              minLength={3}
              maxLength={50}
              required
            />
          </div>

          <div className="register-field">
            <label htmlFor="register-email">Email address</label>
            <input
              id="register-email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="Enter your email"
              required
            />
          </div>

          <div className="register-field">
            <label htmlFor="register-password">Password</label>
            <input
              id="register-password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Enter your password"
              minLength={8}
              required
            />
          </div>

          <div className="register-field">
            <label htmlFor="register-confirm-password">Confirm password</label>
            <input
              id="register-confirm-password"
              type="password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              placeholder="Confirm your password"
              minLength={8}
              required
            />
          </div>

          {otpSent && !otpVerified && (
            <div className="register-field">
              <label htmlFor="register-otp">Verification code</label>
              <input
                id="register-otp"
                className="register-otp-input"
                type="text"
                value={otp}
                onChange={(event) => setOtp(event.target.value.replace(/\D/g, "").slice(0, 6))}
                placeholder="000000"
                inputMode="numeric"
                pattern="\d{6}"
                maxLength={6}
                required
              />
            </div>
          )}

          {!otpVerified ? (
            <button className="register-primary-button" type="submit" disabled={loading}>
              {loading ? "Please wait..." : otpSent ? "Verify OTP" : "Send OTP"}
            </button>
          ) : (
            <button className="register-primary-button" type="submit" disabled={loading}>
              {loading ? "Creating account..." : "Create Account"}
            </button>
          )}
        </form>

        <p className="register-link">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </section>
    </main>
  );
}

export default Register;