import { create } from "zustand";
import type { ChatMessage, ResumeDetail } from "@/types/resume";

interface GuidedState {
  currentSection: string;
  completedSections: string[];
  collectedData: Record<string, any>;
  isReady: boolean;
}

interface ResumeState {
  currentResume: ResumeDetail | null;
  chatMessages: ChatMessage[];
  isStreaming: boolean;
  guided: GuidedState;

  setCurrentResume: (r: ResumeDetail | null) => void;
  addChatMessage: (m: ChatMessage) => void;
  appendToLastMessage: (text: string) => void;
  setStreaming: (s: boolean) => void;
  clearChat: () => void;
  setGuidedProgress: (p: Partial<GuidedState>) => void;
  setCollectedData: (data: Record<string, any>) => void;
  resetGuided: () => void;
}

export const useResumeStore = create<ResumeState>((set) => ({
  currentResume: null,
  chatMessages: [],
  isStreaming: false,
  guided: {
    currentSection: "",
    completedSections: [],
    collectedData: {},
    isReady: false,
  },

  setCurrentResume: (resume) => set({ currentResume: resume }),

  addChatMessage: (message) =>
    set((state) => ({ chatMessages: [...state.chatMessages, message] })),

  appendToLastMessage: (text) =>
    set((state) => {
      const messages = [...state.chatMessages];
      if (messages.length > 0) {
        const last = messages[messages.length - 1];
        messages[messages.length - 1] = { ...last, content: last.content + text };
      }
      return { chatMessages: messages };
    }),

  setStreaming: (streaming) => set({ isStreaming: streaming }),

  clearChat: () => set({ chatMessages: [] }),

  setGuidedProgress: (progress) =>
    set((state) => ({
      guided: { ...state.guided, ...progress },
    })),

  setCollectedData: (data) =>
    set((state) => ({
      guided: { ...state.guided, collectedData: data },
    })),

  resetGuided: () =>
    set({
      guided: {
        currentSection: "",
        completedSections: [],
        collectedData: {},
        isReady: false,
      },
    }),
}));
