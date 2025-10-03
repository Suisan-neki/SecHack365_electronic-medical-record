import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface User {
  user_id: string;
  username: string;
  role: 'doctor' | 'admin' | 'patient';
  is_authenticated: boolean;
}

interface PatientData {
  patient_name: string;
  chief_complaint: string;
  diagnosis: string;
  treatment: string;
  notes: string;
  date: string;
}

interface AppState {
  user: User | null;
  patientData: PatientData | null;
  isLoading: boolean;
  error: string | null;
}

interface AppStore extends AppState {
  setUser: (user: User | null) => void;
  setPatientData: (data: PatientData | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  loadPatientData: () => Promise<void>;
}

export const useAppStore = create<AppStore>((set, get) => ({
  user: null,
  patientData: null,
  isLoading: false,
  error: null,

  setUser: (user) => {
    set({ user });
    if (user) {
      AsyncStorage.setItem('user', JSON.stringify(user));
    } else {
      AsyncStorage.removeItem('user');
    }
  },

  setPatientData: (patientData) => set({ patientData }),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error }),

  login: async (username: string, password: string) => {
    set({ isLoading: true, error: null });
    
    try {
      // 実際のAPI呼び出し
      const response = await fetch('http://localhost:5001/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();
      
      if (data.success) {
        const user: User = {
          user_id: data.data.user.user_id,
          username: data.data.user.username,
          role: data.data.user.role,
          is_authenticated: true,
        };
        set({ user, isLoading: false });
        return true;
      } else {
        set({ error: data.message || 'ログインに失敗しました', isLoading: false });
        return false;
      }
    } catch (error) {
      set({ error: 'ネットワークエラーが発生しました', isLoading: false });
      return false;
    }
  },

  logout: async () => {
    set({ user: null, patientData: null });
    await AsyncStorage.removeItem('user');
  },

  loadPatientData: async () => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await fetch('http://localhost:5001/api/get-patient-display');
      const data = await response.json();
      
      if (data.success) {
        set({ patientData: data.data, isLoading: false });
      } else {
        set({ error: data.message || 'データの取得に失敗しました', isLoading: false });
      }
    } catch (error) {
      set({ error: 'ネットワークエラーが発生しました', isLoading: false });
    }
  },
}));
