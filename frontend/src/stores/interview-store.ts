import { create } from "zustand";

interface InterviewMessage {
  id: string;
  role: "ai" | "user";
  content: string;
  timestamp: number;
}

interface InterviewState {
  currentSessionId: string | null;
  sessionType: string;
  messages: InterviewMessage[];
  isAiTyping: boolean;
  isActive: boolean;
  overallScore: number | null;

  setSession: (id: string, type: string) => void;
  addMessage: (m: InterviewMessage) => void;
  appendToLastMessage: (text: string) => void;
  setAiTyping: (t: boolean) => void;
  setActive: (a: boolean) => void;
  setScore: (s: number | null) => void;
  clearSession: () => void;
}

export const useInterviewStore = create<InterviewState>((set) => ({
  currentSessionId: null,
  sessionType: "technical",
  messages: [],
  isAiTyping: false,
  isActive: false,
  overallScore: null,

  setSession: (id, type) => set({ currentSessionId: id, sessionType: type, messages: [], isActive: true }),
  addMessage: (m) => set((s) => ({ messages: [...s.messages, m] })),
  appendToLastMessage: (text) =>
    set((s) => {
      const msgs = [...s.messages];
      if (msgs.length > 0) {
        const last = msgs[msgs.length - 1];
        msgs[msgs.length - 1] = { ...last, content: last.content + text };
      }
      return { messages: msgs };
    }),
  setAiTyping: (t) => set({ isAiTyping: t }),
  setActive: (a) => set({ isActive: a }),
  setScore: (s) => set({ overallScore: s }),
  clearSession: () =>
    set({ currentSessionId: null, messages: [], isAiTyping: false, isActive: false, overallScore: null }),
}));
