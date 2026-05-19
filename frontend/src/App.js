import "@/App.css";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { AuthProvider } from "@/context/AuthContext";
import ProtectedRoute from "@/components/ProtectedRoute";
import LandingPage from "@/pages/LandingPage";
import GetStarted from "@/pages/GetStarted";
import AuthCallback from "@/pages/AuthCallback";
import Onboarding from "@/pages/Onboarding";
import Dashboard from "@/pages/Dashboard";
import PostOpportunity from "@/pages/PostOpportunity";
import OpportunityDetail from "@/pages/OpportunityDetail";
import Profile from "@/pages/Profile";
import Connections from "@/pages/Connections";

function AppRouter() {
  const location = useLocation();
  // Detect session_id callback synchronously (handles OAuth landing on any route)
  if (location.hash?.includes("session_id=")) return <AuthCallback />;
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/get-started" element={<GetStarted />} />
      <Route path="/onboarding" element={<ProtectedRoute><Onboarding /></ProtectedRoute>} />
      <Route path="/dashboard" element={<ProtectedRoute requireProfile><Dashboard /></ProtectedRoute>} />
      <Route path="/opportunities/new" element={<ProtectedRoute requireProfile><PostOpportunity /></ProtectedRoute>} />
      <Route path="/opportunities/:id" element={<ProtectedRoute requireProfile><OpportunityDetail /></ProtectedRoute>} />
      <Route path="/profile" element={<ProtectedRoute requireProfile><Profile /></ProtectedRoute>} />
      <Route path="/profile/:userId" element={<ProtectedRoute requireProfile><Profile /></ProtectedRoute>} />
      <Route path="/connections" element={<ProtectedRoute requireProfile><Connections /></ProtectedRoute>} />
      <Route path="*" element={<LandingPage />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRouter />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
