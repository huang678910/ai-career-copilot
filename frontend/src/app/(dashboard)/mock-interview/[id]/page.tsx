"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Send, Bot, User, PhoneOff, Loader2, FileDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useInterviewStore } from "@/stores/interview-store";
import { apiClient } from "@/lib/api-client";
import { API_ENDPOINTS } from "@/lib/api-endpoints";

const WS_BASE = typeof window !== "undefined"
  ? `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}`
  : "ws://localhost:8004";

interface Msg {
  id: string;
  role: "ai" | "user";
  content: string;
  timestamp: number;
}

export default function MockInterviewSessionPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.id as string;

  const [sessionInfo, setSessionInfo] = useState<any>(null);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Msg[]>([]);
  const [isAiTyping, setIsAiTyping] = useState(false);
  const [isEnding, setIsEnding] = useState(false);
  const [interviewComplete, setInterviewComplete] = useState(false);
  const [feedback, setFeedback] = useState<any>(null);
  const [questionsAsked, setQuestionsAsked] = useState(0);
  const wsRef = useRef<WebSocket | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const sessionInfoRef = useRef<any>(null);
  const connectedRef = useRef(false);

  // Connect WebSocket only once
  useEffect(() => {
    if (connectedRef.current) return;
    const token = localStorage.getItem("access_token");
    if (!token) return;

    connectedRef.current = true;

    // Fetch session info first, then connect
    apiClient.get(`${API_ENDPOINTS.interviewSessions}/${sessionId}`).then(({ data }) => {
      setSessionInfo(data);
      sessionInfoRef.current = data;
      setQuestionsAsked(data.questions_asked || 0);
      if (data.status === "completed") {
        setFeedback(data.feedback);
        setInterviewComplete(true);
      }
      if (data.messages && data.messages.length > 0) {
        setMessages(data.messages.map((m: any) => ({
          id: m.id,
          role: m.role,
          content: m.content,
          timestamp: new Date(m.created_at).getTime(),
        })));
      }

      // Only connect for active sessions
      if (data.status !== "completed") {
        const ws = new WebSocket(`${WS_BASE}/ws/interview/${sessionId}?token=${token}`);
        wsRef.current = ws;

        ws.onopen = () => {
          ws.send(JSON.stringify({
            type: "start_interview",
            data: { session_type: data.session_type || "technical", questions_total: data.questions_total || 10 },
          }));
        };

        ws.onmessage = (event) => {
          try {
            const msg = JSON.parse(event.data);
            switch (msg.type) {
              case "chunk":
                setMessages((prev) => {
                  const msgs = [...prev];
                  const last = msgs[msgs.length - 1];
                  if (last?.role === "ai") {
                    msgs[msgs.length - 1] = { ...last, content: last.content + msg.data.text };
                  } else {
                    msgs.push({ id: crypto.randomUUID(), role: "ai", content: msg.data.text, timestamp: Date.now() });
                  }
                  return msgs;
                });
                break;
              case "done":
                setIsAiTyping(false);
                break;
              case "counter_update":
                setQuestionsAsked(msg.data.questions_asked);
                break;
              case "interview_complete":
                setFeedback(msg.data);
                setInterviewComplete(true);
                setIsAiTyping(false);
                break;
              case "pong":
                break;
            }
          } catch { /* ignore */ }
        };

        ws.onclose = () => setIsAiTyping(false);
        ws.onerror = () => setIsAiTyping(false);
      }
    }).catch(() => router.push("/mock-interview"));

    return () => {
      wsRef.current?.close();
    };
  }, [sessionId, router]);

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
  }, [messages]);

  const handleSend = () => {
    if (!input.trim() || isAiTyping || interviewComplete) return;

    const userMsg: Msg = { id: crypto.randomUUID(), role: "user", content: input.trim(), timestamp: Date.now() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsAiTyping(true);

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "user_answer", data: { text: input.trim() } }));
    }
  };

  const handleEnd = async () => {
    setIsEnding(true);
    try {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: "end_interview" }));
      }
      await apiClient.post(`${API_ENDPOINTS.interviewSessions}/${sessionId}/end`);
    } catch {
      // ignore
    } finally {
      setIsEnding(false);
    }
  };

  if (!sessionInfo) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-5rem)] flex-col space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.push("/mock-interview")}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-lg font-bold">
              {sessionInfo.session_type === "technical" ? "技术面试" :
               sessionInfo.session_type === "hr" ? "HR 面试" :
               sessionInfo.session_type === "stress" ? "压力面试" : "项目深挖"}
            </h1>
            <p className="text-xs text-muted-foreground">
              {questionsAsked}/{sessionInfo?.questions_total || 10} 题
              {sessionInfo.status === "completed" && " · 已完成"}
            </p>
          </div>
        </div>
        {!interviewComplete && sessionInfo.status === "in_progress" && (
          <Button variant="destructive" size="sm" onClick={handleEnd} disabled={isEnding}>
            <PhoneOff className="mr-1 h-4 w-4" />
            {isEnding ? "结束中..." : "结束面试"}
          </Button>
        )}
      </div>

      <div className="grid flex-1 gap-6 lg:grid-cols-3">
        {/* Chat Area */}
        <div className="flex flex-col lg:col-span-2 rounded-lg border">
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg, i) => (
              <div key={i} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                {msg.role === "ai" && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
                    <Bot className="h-4 w-4 text-primary" />
                  </div>
                )}
                <div className={`max-w-[80%] rounded-lg px-4 py-2.5 text-sm ${msg.role === "ai" ? "bg-muted" : "bg-primary text-primary-foreground"}`}>
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                  {isAiTyping && i === messages.length - 1 && msg.role === "ai" && (
                    <span className="ml-1 inline-block h-4 w-1 animate-pulse bg-current" />
                  )}
                </div>
              </div>
            ))}
          </div>

          {!interviewComplete && (
            <div className="border-t p-3">
              <div className="flex gap-2">
                <Textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
                  placeholder="输入你的回答..."
                  rows={2}
                  className="min-h-[44px] resize-none"
                  disabled={isAiTyping}
                />
                <Button size="icon" onClick={handleSend} disabled={isAiTyping || !input.trim()}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* Feedback Panel */}
        <div>
          {interviewComplete && feedback ? (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">面试反馈</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {feedback.overall_score && (
                  <div className="text-center">
                    <div className="text-3xl font-bold text-primary">{Math.round(feedback.overall_score)}</div>
                    <p className="text-xs text-muted-foreground">总分</p>
                  </div>
                )}
                {feedback.strengths?.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-emerald-600">优势</h4>
                    <ul className="mt-1 space-y-1">
                      {feedback.strengths.map((s: string, i: number) => (
                        <li key={i} className="text-xs text-muted-foreground">• {s}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {feedback.improvements?.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-amber-600">待改进</h4>
                    <ul className="mt-1 space-y-1">
                      {feedback.improvements.map((s: string, i: number) => (
                        <li key={i} className="text-xs text-muted-foreground">• {s}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {feedback.raw_feedback && (
                  <div className="rounded bg-muted p-3 text-xs whitespace-pre-wrap">{feedback.raw_feedback}</div>
                )}
                <Button variant="outline" size="sm" className="w-full mt-2" onClick={async () => {
                  try {
                    const res = await apiClient.post(`/api/v1/export/interview/${sessionId}/txt`, {}, { responseType: "blob" });
                    const url = URL.createObjectURL(new Blob([res.data]));
                    const a = document.createElement("a"); a.href = url; a.download = `interview_${sessionId}.txt`; a.click();
                    URL.revokeObjectURL(url);
                  } catch { alert("导出失败"); }
                }}>
                  <FileDown className="mr-1 h-4 w-4" />导出对话记录
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="flex h-full items-center justify-center rounded-lg border border-dashed">
              <p className="text-xs text-muted-foreground text-center px-4">
                {sessionInfo.status === "completed" ? "加载反馈中..." : "面试结束后将在此显示反馈"}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
