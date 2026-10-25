import { BrowserRouter, Routes, Route } from "react-router-dom";

import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";

import Home from "./pages/Landingpage/Home";
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import Dashboard from "./pages/dashboard/Dashboard";
import AdminPanel from "./pages/admin/AdminPanel";
import AdminLearning from "./pages/admin/AdminLearning";
import AdminTopics from "./pages/admin/AdminTopics";

import Courses from "./pages/learning/Courses";
import CourseDetails from "./pages/learning/CourseDetails";
import LessonDetails from "./pages/learning/LessonDetails";
import LearningAnalytics from "./pages/learning/learningAnalytics";
import TopicLearning from "./pages/learning/TopicLearning";

import Resume from "./pages/resume/Resume";
import Interview from "./pages/interview/Interview";
import Placements from "./pages/placements/Placements";
import AIInterview from "./pages/interview/AIInterview";


function App() {
  return (
    <BrowserRouter>
      <Navbar />

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/home" element={<Home />} />

        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/learning"
          element={
            <ProtectedRoute>
              <Courses />
            </ProtectedRoute>
          }
        />

        <Route
          path="/learning/course/:courseId"
          element={
            <ProtectedRoute>
              <CourseDetails />
            </ProtectedRoute>
          }
        />

        <Route
          path="/learning/course/:courseId/lesson/:lessonId"
          element={
            <ProtectedRoute>
              <LessonDetails />
            </ProtectedRoute>
          }
        />

        <Route
          path="/learning/analytics"
          element={
            <ProtectedRoute>
              <LearningAnalytics />
            </ProtectedRoute>
          }
        />

        <Route
          path="/interview"
          element={
            <ProtectedRoute>
              <Interview />
            </ProtectedRoute>
          }
        />
        <Route
          path="/interview/ai"
          element={
            <ProtectedRoute>
              <AIInterview />
            </ProtectedRoute>
          }
        />
        <Route
          path="/interview/questions"
          element={
            <ProtectedRoute>
              <Interview />
            </ProtectedRoute>
          }
        />
        <Route
          path="/resume"
          element={
            <ProtectedRoute>
              <Resume />
            </ProtectedRoute>
          }
        />
        <Route
          path="/placements"
          element={
            <ProtectedRoute>
              <Placements />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute>
              <AdminPanel />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/learning"
          element={
            <ProtectedRoute>
              <AdminLearning />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/topics"
          element={
            <ProtectedRoute>
              <AdminTopics />
            </ProtectedRoute>
          }
        />
        <Route
          path="/learning/course/:courseId/lesson/:lessonId/topic/:topicId"
          element={
            <ProtectedRoute>
              <TopicLearning />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;