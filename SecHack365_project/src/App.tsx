import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAppStore } from './store/useAppStore';
import DashboardPage from './pages/DashboardPage';
import InputFormPage from './pages/InputFormPage';
import PatientDisplayPage from './pages/PatientDisplayPage';
import PatientSelectionModal from './components/PatientSelectionModal';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorMessage from './components/ErrorMessage';

const App: React.FC = () => {
  const { error } = useAppStore();

  return (
    <Router>
      <div className="App">
        {error && <ErrorMessage message={error} />}
        
        <Routes>
          <Route 
            path="/dashboard" 
            element={<DashboardPage />} 
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
            element={<Navigate to="/dashboard" replace />} 
          />
        </Routes>
        
        <PatientSelectionModal />
      </div>
    </Router>
  );
};

export default App;
