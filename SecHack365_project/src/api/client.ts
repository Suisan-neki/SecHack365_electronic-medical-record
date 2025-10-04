import axios from 'axios';
import { Patient, MedicalRecord, Tag, ApiResponse } from '../types';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-production-api.com' 
  : 'http://localhost:5002';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// リクエストインターセプター
apiClient.interceptors.request.use(
  (config) => {
    // 認証トークンがあれば追加
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// レスポンスインターセプター
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // 認証エラーの場合、ログインページにリダイレクト
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API 関数
export const api = {
  // 患者関連
  getPatients: (): Promise<Patient[]> =>
    apiClient.get('/api/patients').then(res => res.data),
  
  getPatient: (patientId: string): Promise<Patient> =>
    apiClient.get(`/api/patient/${patientId}`).then(res => res.data),

  // タグ関連
  getSymptomTags: (): Promise<ApiResponse<Tag[]>> =>
    apiClient.get('/api/symptom_tags').then(res => res.data),
  
  getDiagnosisTags: (): Promise<ApiResponse<Tag[]>> =>
    apiClient.get('/api/diagnosis_tags').then(res => res.data),

  // 診療記録関連
  submitMedicalRecord: (record: Partial<MedicalRecord>): Promise<ApiResponse<any>> =>
    apiClient.post('/api/import/record', record).then(res => res.data),

  // 患者表示関連
  setPatientDisplay: (data: any): Promise<ApiResponse<any>> =>
    apiClient.post('/api/set-patient-display', data).then(res => res.data),

  // 認証関連
  login: (credentials: { username: string; password: string }): Promise<ApiResponse<any>> =>
    apiClient.post('/api/login', credentials).then(res => res.data),
  
  logout: (): Promise<ApiResponse<any>> =>
    apiClient.post('/api/logout').then(res => res.data),

  // WebAuthn関連
  registerWebAuthn: (): Promise<ApiResponse<any>> =>
    apiClient.post('/api/webauthn/register').then(res => res.data),
  
  authenticateWebAuthn: (username: string): Promise<ApiResponse<any>> =>
    apiClient.post('/api/webauthn/authenticate', { username }).then(res => res.data),

  // FHIR関連
  importFHIR: (data: any): Promise<ApiResponse<any>> =>
    apiClient.post('/api/fhir/import', data).then(res => res.data),
  
  exportFHIR: (): Promise<ApiResponse<any>> =>
    apiClient.get('/api/fhir/export').then(res => res.data),

  // CSV関連
  importCSV: (data: any): Promise<ApiResponse<any>> =>
    apiClient.post('/api/csv/import', data).then(res => res.data),
  
  exportCSV: (): Promise<ApiResponse<any>> =>
    apiClient.get('/api/csv/export').then(res => res.data),
};

export default apiClient;
