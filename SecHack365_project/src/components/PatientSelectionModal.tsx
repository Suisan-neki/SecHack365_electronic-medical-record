import React, { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Patient } from '../types';
import { api } from '../api/client';
import { useAppStore } from '../store/useAppStore';
import Button from './Button';
import LoadingSpinner from './LoadingSpinner';

const PatientSelectionModal: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { setCurrentPatient, setLoading, setError } = useAppStore();

  const { data: patients, isLoading, error } = useQuery({
    queryKey: ['patients'],
    queryFn: () => api.getPatients(),
    enabled: isOpen,
  });

  const handlePatientSelect = async (patient: Patient) => {
    try {
      setLoading(true);
      const response = await api.getPatient(patient.patient_id);
      if (response.success && response.data) {
        setCurrentPatient(response.data);
        setIsOpen(false);
      }
    } catch (err) {
      setError('患者データの取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setIsOpen(false);
  };

  // グローバルな患者選択モーダル表示関数を定義
  useEffect(() => {
    (window as any).showPatientSelectionModal = () => setIsOpen(true);
  }, []);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div className="modal-content" style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        padding: '20px',
        maxWidth: '600px',
        width: '90%',
        maxHeight: '80vh',
        overflow: 'auto'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2>患者選択</h2>
          <Button variant="secondary" onClick={handleClose}>
            ×
          </Button>
        </div>

        {isLoading && <LoadingSpinner />}
        
        {error && (
          <div className="alert alert-error">
            患者データの取得に失敗しました
          </div>
        )}

        {patients?.data && (
          <div className="patient-list">
            {patients.data.map((patient) => (
              <div
                key={patient.patient_id}
                className="patient-item"
                style={{
                  padding: '15px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  marginBottom: '10px',
                  cursor: 'pointer',
                  transition: 'background-color 0.2s'
                }}
                onClick={() => handlePatientSelect(patient)}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f5f5f5'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'white'}
              >
                <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                  {patient.name} ({patient.name_kana})
                </div>
                <div style={{ fontSize: '14px', color: '#666' }}>
                  {patient.gender} | {patient.birth_date} | ID: {patient.patient_id}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default PatientSelectionModal;
