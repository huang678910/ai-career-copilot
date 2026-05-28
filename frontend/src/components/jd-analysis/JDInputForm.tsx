"use client";

import { useState, useEffect } from "react";
import { Search, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface JDInputFormProps {
  onSubmit: (text: string) => Promise<void>;
  isLoading: boolean;
  clearTrigger: number;
}

export function JDInputForm({ onSubmit, isLoading, clearTrigger }: JDInputFormProps) {
  const [text, setText] = useState("");

  useEffect(() => {
    setText("");
  }, [clearTrigger]);

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!text.trim() || isLoading) return;
    await onSubmit(text.trim());
    setText("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="粘贴职位描述（JD）内容...&#10;&#10;支持中文和英文JD，最少10个字符&#10;按 Ctrl+Enter 提交分析"
        rows={10}
        className="min-h-[200px] resize-y"
      />
      <Button type="submit" disabled={isLoading || text.trim().length < 10}>
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            AI 分析中...
          </>
        ) : (
          <>
            <Search className="mr-2 h-4 w-4" />
            开始分析
          </>
        )}
      </Button>
    </form>
  );
}
