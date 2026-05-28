"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Send, RefreshCw, History } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChatMessageBubble } from "./ChatMessage";
import { ChatHistorySidebar } from "./ChatHistorySidebar";
import { useResumeStore } from "@/stores/resume-store";
import { apiClient } from "@/lib/api-client";
import type { ChatMessage } from "@/types/resume";

interface ResumeChatProps {
  resumeId: string;
}

const WS_BASE = typeof window !== "undefined"
  ? `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}`
  : "ws://localhost:8004";

export function ResumeChat({ resumeId }: ResumeChatProps) {
  const [input, setInput] = useState("");
  const wsRef = useRef<WebSocket | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const { chatMessages, isStreaming, addChatMessage, appendToLastMessage, setStreaming, clearChat } =
    useResumeStore();

  const connect = useCallback(() => {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    const ws = new WebSocket(`${WS_BASE}/ws/resume/${resumeId}?token=${token}`);
    wsRef.current = ws;

    ws.onopen = () => {
      // Connection established
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        switch (msg.type) {
          case "chunk":
            appendToLastMessage(msg.data.text);
            break;
          case "structured":
            // Structured AI suggestion — can be handled by parent
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
      } catch {
        // ignore parse errors
      }
    };

    ws.onclose = () => {
      setStreaming(false);
    };

    ws.onerror = () => {
      setStreaming(false);
    };
  }, [resumeId, appendToLastMessage, setStreaming]);

  // Load chat history on mount
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) return;
    apiClient.get(`/api/v1/resumes/${resumeId}/chat-history`)
      .then(({ data }) => {
        if (data && data.length > 0) {
          // Replace current messages with history
          useResumeStore.setState({ chatMessages: data.map((m: any) => ({
            id: m.id,
            role: m.role as "user" | "ai",
            content: m.content,
            timestamp: new Date(m.created_at).getTime(),
          }))});
        }
      })
      .catch(() => { /* ignore */ });
  }, [resumeId]);

  useEffect(() => {
    connect();
    // Ping every 30 seconds
    const interval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: "ping" }));
      }
    }, 30000);
    return () => {
      clearInterval(interval);
      wsRef.current?.close();
    };
  }, [connect]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [chatMessages]);

  const handleSend = () => {
    const text = input.trim();
    if (!text || isStreaming) return;

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
      timestamp: Date.now(),
    };
    addChatMessage(userMsg);
    setInput("");

    const aiMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "ai",
      content: "",
      timestamp: Date.now(),
    };
    addChatMessage(aiMsg);
    setStreaming(true);

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "chat_message", data: { text } }));
    } else {
      setStreaming(false);
    }
  };

  const handleReset = async () => {
    if (!confirm("确定清空所有对话记录？此操作不可撤销。")) return;
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "reset" }));
    }
    clearChat();
    try { await apiClient.delete(`/api/v1/resumes/${resumeId}/chat-history`); } catch {}
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);

  const handleSelectConversation = (startId: string) => {
    setActiveConversationId(startId);
    apiClient.get(`/api/v1/resumes/${resumeId}/chat-history?start_id=${startId}`)
      .then(({ data }) => {
        if (data && data.length > 0) {
          useResumeStore.setState({ chatMessages: data.map((m: any) => ({
            id: m.id, role: m.role as "user" | "ai",
            content: m.content, timestamp: new Date(m.created_at).getTime(),
          }))});
        }
      })
      .catch(() => {});
  };

  const handleNewChat = () => {
    setActiveConversationId(null);
    clearChat();
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "reset" }));
    }
  };

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold">AI 简历助手</span>
          {activeConversationId && (
            <span className="text-[10px] text-muted-foreground bg-muted px-1.5 py-0.5 rounded">历史对话</span>
          )}
        </div>
        <div className="flex items-center gap-1">
          {activeConversationId && (
            <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={handleNewChat}>新建对话</Button>
          )}
          <Button variant="ghost" size="icon" onClick={handleReset} title="清空所有记录">
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        <ChatHistorySidebar
          resumeId={resumeId}
          onSelectConversation={handleSelectConversation}
          onNewChat={handleNewChat}
          activeConversationId={activeConversationId}
        />

        <div className="flex flex-1 flex-col overflow-hidden">
          <div ref={scrollRef} className="flex-1 overflow-y-auto px-4">
            {chatMessages.length === 0 && (
              <div className="flex h-full flex-col items-center justify-center text-center text-muted-foreground">
                <History className="h-8 w-8 mb-2 opacity-30" />
                <p className="text-sm">我是你的 AI 简历助手</p>
                <p className="mt-1 text-xs">左侧选择历史对话，或直接输入开始新对话</p>
              </div>
            )}
            {chatMessages.map((msg) => (
              <ChatMessageBubble
                key={msg.id}
                message={msg}
                isStreaming={isStreaming && msg.role === "ai" && msg === chatMessages[chatMessages.length - 1]}
              />
            ))}
          </div>

          <div className="border-t p-3">
            <div className="flex gap-2">
              <Textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="描述你的经历..."
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
      </div>
    </div>
  );
}
