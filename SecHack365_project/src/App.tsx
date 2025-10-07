import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAppStore } from './store/useAppStore';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import AdminDashboardPage from './pages/AdminDashboardPage';
import Phase1ManagementPage from './pages/Phase1ManagementPage';
import InputFormPage from './pages/InputFormPage';
import PatientDisplayPage from './pages/PatientDisplayPage';
import PatientSelectionModal from './components/PatientSelectionModal';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorMessage from './components/ErrorMessage';

const App: React.FC = () => {
  const { error, user } = useAppStore();

  return (
    <Router>
      <div className="App">
        {error && <ErrorMessage message={error} />}
        
        <Routes>
          <Route 
            path="/login" 
            element={<LoginPage />} 
          />
          <Route 
            path="/dashboard" 
            element={<DashboardPage />} 
          />
          <Route 
            path="/admin/dashboard" 
            element={<AdminDashboardPage />} 
          />
          <Route 
            path="/admin/phase1" 
            element={<Phase1ManagementPage />} 
          />
          <Route 
            path="/input-form" 
            element={<InputFormPage />} 
          />
          <Route 
            path="/patient-display" 
            element={<PatientDisplayPage />} 
          />
          <Route 
            path="/" 
            element={<Navigate to={user ? (user.role === 'admin' ? '/admin/dashboard' : '/dashboard') : '/login'} replace />} 
          />
        </Routes>
        
        <PatientSelectionModal />
      </div>
    </Router>
  );
};

export default App;
