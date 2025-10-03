import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAppStore } from './store/useAppStore';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import InputFormPage from './pages/InputFormPage';
import PatientDisplayPage from './pages/PatientDisplayPage';
import PatientSelectionModal from './components/PatientSelectionModal';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorMessage from './components/ErrorMessage';

const App: React.FC = () => {
  const { user, isLoading, error } = useAppStore();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <Router>
      <div className="App">
        {error && <ErrorMessage message={error} />}
        
        <Routes>
          <Route 
            path="/login" 
            element={user ? <Navigate to="/dashboard" replace /> : <LoginPage />} 
          />
          <Route 
            path="/dashboard" 
            element={user ? <DashboardPage /> : <Navigate to="/login" replace />} 
          />
          <Route 
            path="/input-form" 
            element={user ? <InputFormPage /> : <Navigate to="/login" replace />} 
          />
          <Route 
            path="/patient-display" 
            element={<PatientDisplayPage />} 
          />
          <Route 
            path="/" 
            element={<Navigate to={user ? "/dashboard" : "/login"} replace />} 
          />
        </Routes>
        
        <PatientSelectionModal />
      </div>
    </Router>
  );
};

export default App;
