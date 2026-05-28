"use client";

import { useState, useEffect } from "react";
import { History, Plus, MessageSquare, Clock, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { apiClient } from "@/lib/api-client";

interface Conversation {
  id: string;
  first_message: string;
  message_count: number;
  started_at: string;
  last_message_at: string;
}

interface ChatHistorySidebarProps {
  resumeId: string;
  onSelectConversation: (startId: string) => void;
  onNewChat: () => void;
  activeConversationId: string | null;
}

export function ChatHistorySidebar({
  resumeId,
  onSelectConversation,
  onNewChat,
  activeConversationId,
}: ChatHistorySidebarProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    apiClient
      .get(`/api/v1/resumes/${resumeId}/chat-conversations`)
      .then(({ data }) => setConversations(data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [resumeId]);

  // Group by date
  const grouped: Record<string, Conversation[]> = {};
  for (const c of conversations) {
    const d = new Date(c.started_at);
    const today = new Date();
    let label: string;
    if (d.toDateString() === today.toDateString()) {
      label = "今天";
    } else if (new Date(today.getTime() - 86400000).toDateString() === d.toDateString()) {
      label = "昨天";
    } else {
      label = d.toLocaleDateString("zh-CN", { month: "short", day: "numeric" });
    }
    if (!grouped[label]) grouped[label] = [];
    grouped[label].push(c);
  }

  if (collapsed) {
    return (
      <button
        onClick={() => setCollapsed(false)}
        className="flex h-full w-10 shrink-0 flex-col items-center border-r pt-2 text-muted-foreground hover:bg-accent"
        title="展开对话历史"
      >
        <History className="h-4 w-4" />
        <span className="mt-1 text-[10px]">{conversations.length}</span>
      </button>
    );
  }

  return (
    <div className="flex h-full w-48 shrink-0 flex-col border-r">
      <div className="flex items-center justify-between px-3 py-2 border-b">
        <span className="text-xs font-medium text-muted-foreground">对话历史</span>
        <div className="flex gap-1">
          <Button variant="ghost" size="icon" className="h-6 w-6" onClick={onNewChat} title="新建对话">
            <Plus className="h-3.5 w-3.5" />
          </Button>
          <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => setCollapsed(true)} title="收起">
            <span className="text-xs">×</span>
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
          </div>
        ) : conversations.length === 0 ? (
          <div className="px-3 py-8 text-center text-xs text-muted-foreground">
            暂无历史对话
          </div>
        ) : (
          <div className="p-2 space-y-3">
            {Object.entries(grouped).map(([label, convs]) => (
              <div key={label}>
                <p className="px-2 text-[10px] font-medium text-muted-foreground mb-1">{label}</p>
                {convs.map((c) => (
                  <button
                    key={c.id}
                    onClick={() => onSelectConversation(c.id)}
                    className={`w-full rounded-md px-2 py-1.5 text-left text-xs transition-colors ${
                      activeConversationId === c.id
                        ? "bg-primary/10 text-primary"
                        : "hover:bg-accent text-muted-foreground"
                    }`}
                  >
                    <div className="flex items-center gap-1.5">
                      <MessageSquare className="h-3 w-3 shrink-0" />
                      <span className="truncate">{c.first_message}</span>
                    </div>
                    <div className="mt-0.5 flex items-center gap-2 text-[10px] text-muted-foreground/70">
                      <Clock className="h-2.5 w-2.5" />
                      <span>{new Date(c.started_at).toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" })}</span>
                      <span>{c.message_count} 条消息</span>
                    </div>
                  </button>
                ))}
              </div>
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  );
}
