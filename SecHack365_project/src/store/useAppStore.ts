import { create } from 'zustand';
import { AppState, Patient, Tag, MedicationCombination, FormData, User } from '../types';

interface AppStore extends AppState {
  // Actions
  setUser: (user: User | null) => void;
  setCurrentPatient: (patient: Patient | null) => void;
  setSelectedTags: (tags: Tag[]) => void;
  addSelectedTag: (tag: Tag) => void;
  removeSelectedTag: (tagId: string) => void;
  setMedicationCombinations: (combinations: MedicationCombination[]) => void;
  addMedicationCombination: (combination: MedicationCombination) => void;
  removeMedicationCombination: (id: string) => void;
  updateMedicationCombination: (id: string, updates: Partial<MedicationCombination>) => void;
  setFormData: (formData: Partial<FormData>) => void;
  updateFormField: (field: keyof FormData, value: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  resetForm: () => void;
}

const initialFormData: FormData = {
  symptoms: '',
  diagnosis: '',
  diagnosis_details: '',
  medication: '',
  medication_instructions: '',
  treatment_plan: '',
  follow_up: '',
  patient_explanation: '',
  doctor_notes: ''
};

export const useAppStore = create<AppStore>((set, get) => ({
  // Initial state
  user: null,
  currentPatient: null,
  selectedTags: [],
  medicationCombinations: [],
  formData: initialFormData,
  isLoading: false,
  error: null,

  // Actions
  setUser: (user) => set({ user }),
  
  setCurrentPatient: (patient) => set({ currentPatient: patient }),
  
  setSelectedTags: (tags) => set({ selectedTags: tags }),
  
  addSelectedTag: (tag) => {
    const { selectedTags } = get();
    if (!selectedTags.some(t => t.tag_id === tag.tag_id)) {
      set({ selectedTags: [...selectedTags, tag] });
    }
  },
  
  removeSelectedTag: (tagId) => {
    const { selectedTags } = get();
    set({ selectedTags: selectedTags.filter(t => t.tag_id !== tagId) });
  },
  
  setMedicationCombinations: (combinations) => set({ medicationCombinations: combinations }),
  
  addMedicationCombination: (combination) => {
    const { medicationCombinations } = get();
    set({ medicationCombinations: [...medicationCombinations, combination] });
  },
  
  removeMedicationCombination: (id) => {
    const { medicationCombinations } = get();
    set({ medicationCombinations: medicationCombinations.filter(c => c.id !== id) });
  },
  
  updateMedicationCombination: (id, updates) => {
    const { medicationCombinations } = get();
    set({
      medicationCombinations: medicationCombinations.map(c =>
        c.id === id ? { ...c, ...updates } : c
      )
    });
  },
  
  setFormData: (formData) => {
    const { formData: currentFormData } = get();
    set({ formData: { ...currentFormData, ...formData } });
  },
  
  updateFormField: (field, value) => {
    const { formData } = get();
    set({ formData: { ...formData, [field]: value } });
  },
  
  setLoading: (loading) => set({ isLoading: loading }),
  
  setError: (error) => set({ error }),
  
  resetForm: () => set({
    selectedTags: [],
    medicationCombinations: [],
    formData: initialFormData,
    error: null
  })
}));
