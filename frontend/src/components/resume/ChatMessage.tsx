"use client";

import { cn } from "@/lib/utils";
import { Bot, User } from "lucide-react";
import type { ChatMessage as ChatMessageType } from "@/types/resume";

interface ChatMessageProps {
  message: ChatMessageType;
  isStreaming?: boolean;
}

export function ChatMessageBubble({ message, isStreaming }: ChatMessageProps) {
  const isAi = message.role === "ai";

  return (
    <div className={cn("flex gap-3 py-3", isAi ? "justify-start" : "justify-end")}>
      {isAi && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
          <Bot className="h-4 w-4 text-primary" />
        </div>
      )}
      <div
        className={cn(
          "max-w-[80%] rounded-lg px-4 py-2.5 text-sm leading-relaxed",
          isAi ? "bg-muted text-foreground" : "bg-primary text-primary-foreground",
        )}
      >
        <div className="whitespace-pre-wrap break-words">{message.content}</div>
        {isStreaming && (
          <span className="ml-1 inline-block h-4 w-1 animate-pulse bg-current" />
        )}
      </div>
      {!isAi && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-foreground/10">
          <User className="h-4 w-4" />
        </div>
      )}
    </div>
  );
}
