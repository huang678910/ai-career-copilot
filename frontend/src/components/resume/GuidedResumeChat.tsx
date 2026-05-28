"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Send, Bot, User, Loader2, RefreshCw, CheckCircle2, Circle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useResumeStore } from "@/stores/resume-store";
import { apiClient } from "@/lib/api-client";

const WS_BASE = typeof window !== "undefined"
  ? `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}`
  : "ws://localhost:8004";

const SECTIONS = [
  { key: "basic_info", label: "基本信息", icon: "📋" },
  { key: "job_target", label: "求职意向", icon: "🎯" },
  { key: "education", label: "教育背景", icon: "🎓" },
  { key: "skills", label: "专业技能", icon: "⚡" },
  { key: "projects", label: "项目经历", icon: "🚀" },
  { key: "work_experience", label: "工作经历", icon: "💼" },
];

interface Props {
  resumeId: string;
}

export function GuidedResumeChat({ resumeId }: Props) {
  const {
    chatMessages, isStreaming, guided,
    addChatMessage, appendToLastMessage, setStreaming, clearChat,
    setGuidedProgress, setCollectedData, resetGuided,
  } = useResumeStore();

  const [input, setInput] = useState("");
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const connectedRef = useRef(false);
  const genRef = useRef(0); // generation counter to ignore stale async responses
  const scrollRef = useRef<HTMLDivElement>(null);

  const connect = useCallback(async () => {
    if (connectedRef.current) return;
    connectedRef.current = true;
    const gen = ++genRef.current; // capture current generation

    const token = localStorage.getItem("access_token");
    if (!token) return;

    // Clear old messages and load chat history for this specific resume
    clearChat();
    let hasHistory = false;
    try {
      const { data } = await apiClient.get(`/api/v1/resumes/${resumeId}/chat-history`);
      // Ignore stale responses from previous StrictMode mounts
      if (gen !== genRef.current) return;
      if (data && Array.isArray(data) && data.length > 0) {
        hasHistory = true;
        for (const m of data) {
          addChatMessage({
            id: m.id,
            role: m.role,
            content: m.content,
            timestamp: new Date(m.created_at).getTime(),
          });
        }
      }
    } catch {
      // No history — start fresh
    }

    const ws = new WebSocket(`${WS_BASE}/ws/resume/${resumeId}?token=${token}`);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);

      // Check if this resume already has content (from DB or previous chat)
      let existingData: Record<string, any> | null = null;
      const resume = useResumeStore.getState().currentResume;
      if (resume) {
        const r = resume as any;

        // Priority 1: Guided data persisted from previous AI conversation
        if (r.guided_data && Object.keys(r.guided_data).length > 0) {
          existingData = r.guided_data;
        }

        // Priority 2: Build from resume fields if no guided data
        if (!existingData) {
          const hasContent =
            (r.basic_info && (r.basic_info.name || r.basic_info.email)) ||
            r.target_position ||
            (r.education && r.education.length > 0) ||
            (r.skills && r.skills.length > 0) ||
            (r.work_experiences && r.work_experiences.length > 0) ||
            (r.projects && r.projects.length > 0) ||
            r.summary;
          if (hasContent || hasHistory) {
            const info = r.basic_info || {};
            existingData = {};
            if (info.name || info.email || info.phone) existingData.basic_info = info;
            if (r.target_position) existingData.job_target = { target_position: r.target_position };
            if (r.education?.length) {
              existingData.education = r.education.map((e: any) => ({
                school: e.school, degree: e.degree, major: e.major,
                start_date: e.start_date, end_date: e.end_date, gpa: e.gpa,
              }));
            }
            if (r.skills?.length) {
              existingData.skills = r.skills.map((s: any) => ({
                category: s.category, name: s.name, level: s.level,
              }));
            }
            if (r.projects?.length) {
              existingData.projects = r.projects.map((p: any) => ({
                name: p.name, role: p.role, start_date: p.start_date, end_date: p.end_date,
                description: p.description, tech_stack: p.tech_stack, highlights: p.highlights,
              }));
            }
            if (r.work_experiences?.length) {
              existingData.work_experience = r.work_experiences.map((w: any) => ({
                company: w.company, title: w.title, location: w.location,
                start_date: w.start_date, end_date: w.end_date,
                description: w.description, highlights: w.highlights,
              }));
            }
            if (r.summary) existingData.summary = r.summary;
          }
        }
      }

      const hasExistingContent = existingData && Object.keys(existingData).length > 0;
      if (hasHistory) {
        // Returning visit with chat history — init silently, wait for user input
        ws.send(JSON.stringify({
          type: "resume_session",
          data: { collected_data: existingData },
        }));
      } else if (hasExistingContent) {
        // First visit with resume content — AI acknowledges existing content
        addChatMessage({ id: crypto.randomUUID(), role: "ai", content: "", timestamp: Date.now() });
        ws.send(JSON.stringify({
          type: "start_guided",
          data: { collected_data: existingData },
        }));
      } else {
        // Fresh resume — start guided flow with AI first message
        addChatMessage({ id: crypto.randomUUID(), role: "ai", content: "", timestamp: Date.now() });
        ws.send(JSON.stringify({
          type: "start_guided",
          data: { collected_data: null },
        }));
      }
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        switch (msg.type) {
          case "chunk":
            setStreaming(true);
            appendToLastMessage(msg.data.text);
            break;
          case "progress":
            setGuidedProgress({
              currentSection: msg.data.current_section,
              completedSections: msg.data.completed || [],
            });
            break;
          case "resume_update":
            setCollectedData(msg.data);
            break;
          case "resume_ready":
            if (msg.data) {
              setCollectedData(msg.data);
            }
            setGuidedProgress({ isReady: true });
            setStreaming(false);
            break;
          case "done":
            setStreaming(false);
            break;
          case "error":
            setStreaming(false);
            break;
          case "pong":
            break;
        }
      } catch { /* ignore */ }
    };

    ws.onclose = () => {
      setConnected(false);
      connectedRef.current = false;
      setStreaming(false);
    };
    ws.onerror = () => {
      setConnected(false);
      setStreaming(false);
    };
  }, [resumeId, addChatMessage, appendToLastMessage, setStreaming, setGuidedProgress, setCollectedData, clearChat, resetGuided]);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
      connectedRef.current = false;
    };
  }, [connect]);

  // Heartbeat
  useEffect(() => {
    const interval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: "ping" }));
      }
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [chatMessages]);

  const handleSend = () => {
    if (!input.trim() || isStreaming) return;
    const text = input.trim();
    addChatMessage({ id: crypto.randomUUID(), role: "user", content: text, timestamp: Date.now() });
    addChatMessage({ id: crypto.randomUUID(), role: "ai", content: "", timestamp: Date.now() });
    setInput("");
    setStreaming(true);
    wsRef.current?.send(JSON.stringify({ type: "chat_message", data: { text } }));
  };

  const handleReset = async () => {
    if (!confirm("确定要重新开始吗？当前对话进度将丢失。")) return;
    wsRef.current?.send(JSON.stringify({ type: "reset" }));
    clearChat();
    resetGuided();
    // Re-start guided session
    setTimeout(() => {
      wsRef.current?.send(JSON.stringify({ type: "start_guided" }));
    }, 500);
  };

  const currentSectionIdx = SECTIONS.findIndex(s => s.key === guided.currentSection);
  const completedCount = guided.completedSections.filter(s => s !== "intro").length;

  return (
    <div className="flex flex-col h-full rounded-lg border">
      {/* Header with progress */}
      <div className="border-b p-4 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-sm">AI 简历助手</h3>
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">{completedCount}/6 步</span>
            <Button variant="ghost" size="icon" onClick={handleReset} title="重新开始">
              <RefreshCw className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
        {/* Progress dots */}
        <div className="flex items-center gap-1.5">
          {SECTIONS.map((s, i) => {
            const done = guided.completedSections.includes(s.key);
            const active = s.key === guided.currentSection;
            return (
              <div key={s.key} className="flex items-center gap-1">
                {i > 0 && <div className={`h-0.5 w-3 rounded ${done ? "bg-primary" : "bg-muted"}`} />}
                <div className={`flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] transition-colors ${
                  active ? "bg-primary text-primary-foreground" :
                  done ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300" :
                  "bg-muted text-muted-foreground"
                }`}>
                  {done ? <CheckCircle2 className="h-2.5 w-2.5" /> : <Circle className="h-2.5 w-2.5" />}
                  <span className="hidden sm:inline">{s.label}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
        {chatMessages.length === 0 && !isStreaming && (
          <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground gap-2">
            <Bot className="h-8 w-8" />
            <p className="text-sm">AI 简历助手将引导你逐步完成专业简历</p>
            <p className="text-xs">
              {connected ? "连接已建立，开始对话..." : "正在连接..."}
            </p>
          </div>
        )}
        {chatMessages.map((msg, i) => (
          <div key={msg.id || i} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            {msg.role === "ai" && (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
                <Bot className="h-4 w-4 text-primary" />
              </div>
            )}
            <div className={`max-w-[85%] rounded-lg px-3 py-2 text-sm ${
              msg.role === "ai" ? "bg-muted" : "bg-primary text-primary-foreground"
            }`}>
              <p className="whitespace-pre-wrap">{msg.content || (isStreaming && i === chatMessages.length - 1 ? "..." : "")}</p>
            </div>
            {msg.role === "user" && (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary">
                <User className="h-4 w-4 text-primary-foreground" />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Input */}
      <div className="border-t p-3">
        <div className="flex gap-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
            placeholder={isStreaming ? "AI 正在回复..." : "输入你的信息..."}
            rows={2}
            className="min-h-[44px] resize-none"
            disabled={isStreaming}
          />
          <Button size="icon" onClick={handleSend} disabled={isStreaming || !input.trim()}>
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
