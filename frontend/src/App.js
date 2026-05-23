import React from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, useLocation, Navigate } from "react-router-dom";
import { Toaster } from "sonner";
import { AuthProvider } from "@/context/AuthContext";
import Layout from "@/components/Layout";
import Landing from "@/pages/Landing";
import Ideas from "@/pages/Ideas";
import IdeaDetail from "@/pages/IdeaDetail";
import Dashboard from "@/pages/Dashboard";
import Login from "@/pages/Login";
import AuthCallback from "@/pages/AuthCallback";
import Opportunities from "@/pages/Opportunities";

function AppRouter() {
  const location = useLocation();
  // CRITICAL: Detect session_id during render (synchronous) BEFORE any other auth check.
  // useEffect would run after first render — race conditions with /auth/me.
  if (location.hash?.includes("session_id=")) {
    return <AuthCallback />;
  }
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/ideas" element={<Ideas />} />
        <Route path="/ideas/:slug" element={<IdeaDetail />} />
        <Route path="/opportunities" element={<Opportunities />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/login" element={<Login />} />
        {/* Backward compat: old /business-ideas route -> /ideas */}
        <Route path="/business-ideas" element={<Navigate to="/ideas" replace />} />
        <Route path="/business-ideas/:slug" element={<RedirectBusinessIdea />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Layout>
  );
}

function RedirectBusinessIdea() {
  const location = useLocation();
  const slug = location.pathname.split("/").pop();
  return <Navigate to={`/ideas/${slug}`} replace />;
}

function NotFound() {
  return (
    <div className="vw-container py-24 text-center" data-testid="not-found-page">
      <h1 className="text-3xl font-bold mb-3">Page not found</h1>
      <a href="/" className="vw-btn-primary inline-flex">Go home</a>
    </div>
  );
}

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <AuthProvider>
          <AppRouter />
          <Toaster position="top-center" richColors closeButton />
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;
