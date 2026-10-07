import { useState, useEffect, useCallback } from 'react';

const STORAGE_KEY_GUIDE_OPEN = 'susetodroid_guide_tour_open';
const STORAGE_KEY_GUIDE_STEP = 'susetodroid_guide_tour_step';

export function useGuideState(totalSteps: number = 6) {
  const [isOpen, setIsOpen] = useState<boolean>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_GUIDE_OPEN);
      return saved !== null ? JSON.parse(saved) : true;
    } catch {
      return true;
    }
  });

  const [currentStep, setCurrentStep] = useState<number>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_GUIDE_STEP);
      if (saved !== null) {
        const stepNum = parseInt(saved, 10);
        return !isNaN(stepNum) && stepNum >= 0 && stepNum < totalSteps ? stepNum : 0;
      }
      return 0;
    } catch {
      return 0;
    }
  });

  // Sync open state to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY_GUIDE_OPEN, JSON.stringify(isOpen));
    } catch {
      // Ignore localStorage errors
    }
  }, [isOpen]);

  // Sync step state to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY_GUIDE_STEP, currentStep.toString());
    } catch {
      // Ignore localStorage errors
    }
  }, [currentStep]);

  const openGuide = useCallback((step?: number) => {
    if (typeof step === 'number' && step >= 0 && step < totalSteps) {
      setCurrentStep(step);
    }
    setIsOpen(true);
  }, [totalSteps]);

  const closeGuide = useCallback(() => {
    setIsOpen(false);
  }, []);

  const changeStep = useCallback((step: number) => {
    if (step >= 0 && step < totalSteps) {
      setCurrentStep(step);
    }
  }, [totalSteps]);

  const nextStep = useCallback(() => {
    setCurrentStep(prev => (prev < totalSteps - 1 ? prev + 1 : prev));
  }, [totalSteps]);

  const prevStep = useCallback(() => {
    setCurrentStep(prev => (prev > 0 ? prev - 1 : 0));
  }, []);

  const resetGuide = useCallback(() => {
    setCurrentStep(0);
    setIsOpen(true);
  }, []);

  return {
    isOpen,
    currentStep,
    openGuide,
    closeGuide,
    changeStep,
    nextStep,
    prevStep,
    resetGuide
  };
}
