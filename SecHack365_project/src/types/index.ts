import React from 'react';

// 基本型定義
export interface Patient {
  patient_id: string;
  name: string;
  name_kana: string;
  birth_date: string;
  gender: string;
  address: string;
  phone: string;
  emergency_contact: string;
}

export interface MedicalRecord {
  record_id: string;
  patient_id: string;
  date: string;
  chief_complaint: string;
  diagnosis: string;
  treatment: string;
  notes: string;
  doctor_notes?: string;
}

export interface Tag {
  tag_id: string;
  tag_name: string;
  category: string;
  description?: string;
}

export interface MedicationCombination {
  id: string;
  drug_name: string;
  dosage: string;
  frequency: string;
  days: string;
  timing: string;
  instructions: string;
}

export interface FormData {
  symptoms: string;
  diagnosis: string;
  diagnosis_details: string;
  medication: string;
  medication_instructions: string;
  treatment_plan: string;
  follow_up: string;
  patient_explanation: string;
  doctor_notes: string;
}

export interface User {
  user_id: string;
  username: string;
  role: 'doctor' | 'admin' | 'patient';
  is_authenticated: boolean;
}

// API レスポンス型
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

// 状態管理用の型
export interface AppState {
  user: User | null;
  currentPatient: Patient | null;
  selectedTags: Tag[];
  medicationCombinations: MedicationCombination[];
  formData: FormData;
  isLoading: boolean;
  error: string | null;
}

// コンポーネント用の型
export interface ComponentProps {
  className?: string;
  children?: React.ReactNode;
}

export interface ButtonProps extends ComponentProps {
  onClick?: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary' | 'success' | 'danger';
  size?: 'small' | 'medium' | 'large';
  type?: 'button' | 'submit' | 'reset';
  style?: React.CSSProperties;
}

export interface InputProps extends ComponentProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: 'text' | 'email' | 'password' | 'textarea';
  required?: boolean;
  disabled?: boolean;
}

// カテゴリー型
export type SymptomCategory = 'cold' | 'pain' | 'gastro' | 'general' | 'cardio' | 'other';
export type DiagnosisCategory = 'internal' | 'surgical' | 'pediatric' | 'psychiatric' | 'other';

// プリセット型
export interface SymptomPreset {
  id: string;
  name: string;
  symptoms: string[];
  icon: string;
}

export interface MedicationPreset {
  id: string;
  name: string;
  combinations: Omit<MedicationCombination, 'id'>[];
}
