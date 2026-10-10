import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import App from './App';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import DashboardPage from './pages/DashboardPage';
import ScannerPage from './pages/ScannerPage';
import ScanResultPage from './pages/ScanResultPage';
import HistoryPage from './pages/HistoryPage';
import AnalyticsPage from './pages/AnalyticsPage';
import ReportsPage from './pages/ReportsPage';
import SettingsPage from './pages/SettingsPage';
import NotificationsPage from './pages/NotificationsPage';
import AdminPage from './pages/AdminPage';
import AdminUsersPage from './pages/AdminUsersPage';
import AdminScansPage from './pages/AdminScansPage';
import AdminModelsPage from './pages/AdminModelsPage';
import AdminAnalyticsPage from './pages/AdminAnalyticsPage';
import { ProtectedRoute, RedirectIfAuthenticatedRoute, AdminProtectedRoute } from './lib/auth/ProtectedRoute';

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        {/* Auth pages - redirect authenticated users away */}
        <Route
          path="/login"
          element={
            <RedirectIfAuthenticatedRoute>
              <LoginPage />
            </RedirectIfAuthenticatedRoute>
          }
        />
        <Route
          path="/signup"
          element={
            <RedirectIfAuthenticatedRoute>
              <SignupPage />
            </RedirectIfAuthenticatedRoute>
          }
        />
        <Route
          path="/forgot-password"
          element={
            <RedirectIfAuthenticatedRoute>
              <ForgotPasswordPage />
            </RedirectIfAuthenticatedRoute>
          }
        />
        <Route
          path="/reset-password"
          element={
            <RedirectIfAuthenticatedRoute>
              <ResetPasswordPage />
            </RedirectIfAuthenticatedRoute>
          }
        />

        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/scan"
          element={
            <ProtectedRoute>
              <ScannerPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/scan/:id"
          element={
            <ProtectedRoute>
              <ScanResultPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/history"
          element={
            <ProtectedRoute>
              <HistoryPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/analytics"
          element={
            <ProtectedRoute>
              <AnalyticsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/reports"
          element={
            <ProtectedRoute>
              <ReportsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <SettingsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/notifications"
          element={
            <ProtectedRoute>
              <NotificationsPage />
            </ProtectedRoute>
          }
        />
        {/* Admin Routes - require admin role */}
        <Route
          path="/admin"
          element={
            <AdminProtectedRoute>
              <AdminPage />
            </AdminProtectedRoute>
          }
        />
        <Route
          path="/admin/users"
          element={
            <AdminProtectedRoute>
              <AdminUsersPage />
            </AdminProtectedRoute>
          }
        />
        <Route
          path="/admin/scans"
          element={
            <AdminProtectedRoute>
              <AdminScansPage />
            </AdminProtectedRoute>
          }
        />
        <Route
          path="/admin/models"
          element={
            <AdminProtectedRoute>
              <AdminModelsPage />
            </AdminProtectedRoute>
          }
        />
        <Route
          path="/admin/analytics"
          element={
            <AdminProtectedRoute>
              <AdminAnalyticsPage />
            </AdminProtectedRoute>
          }
        />
        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}