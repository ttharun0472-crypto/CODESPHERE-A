import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

import { getAuthToken } from "../services/learningApi";
import { API_BASE_URL } from "../services/apiClient";

function Navbar() {
    const navigate = useNavigate();
    const [isLoggedIn, setIsLoggedIn] = useState(Boolean(getAuthToken()));
    const role = (localStorage.getItem("role") || "user").toUpperCase();

    useEffect(() => {
        const updateAuthState = () => {
            setIsLoggedIn(Boolean(getAuthToken()));
        };

        window.addEventListener("auth-change", updateAuthState);
        window.addEventListener("storage", updateAuthState);

        updateAuthState();

        return () => {
            window.removeEventListener("auth-change", updateAuthState);
            window.removeEventListener("storage", updateAuthState);
        };
    }, []);

    const handleLogout = async () => {
        const token = getAuthToken();

        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("token");
        localStorage.removeItem("authToken");
        localStorage.removeItem("otp_verified");
        localStorage.removeItem("role");
        localStorage.removeItem("is_admin");

        window.dispatchEvent(new Event("auth-change"));

        if (token) {
            try {
                await fetch(`${API_BASE_URL}/auth/logout`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`,
                    },
                });
            } catch (err) {
                console.warn("Logout API call failed:", err);
            }
        }

        navigate("/login");
    };

    return (
        <nav className="navbar">
            <div className="navbar-container">
                <Link to="/" className="logo">
                    CodeSphere
                </Link>

                <div className="nav-links">
                    <Link to="/dashboard">Dashboard</Link>
                    <Link to="/learning">Learning</Link>
                    <Link to="/interview">Interview</Link>
                    <Link to="/resume">Resume</Link>
                    <Link to="/placements">Placements</Link>

                    {!isLoggedIn && (
                        <>
                            <Link to="/login">Login</Link>
                            <Link to="/register">Register</Link>
                        </>
                    )}

                    {isLoggedIn && (
                        <>
                            <span className="user-role">Role: {role}</span>
                            <button
                                type="button"
                                onClick={handleLogout}
                                className="logout-btn"
                            >
                                Logout
                            </button>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
}

export default Navbar;