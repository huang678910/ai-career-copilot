"use client";

import { useAuthStore } from "@/stores/auth-store";
import { FileText, Search, PenTool, MessageSquare } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const features = [
  { icon: FileText, title: "简历生成", desc: "AI 对话式简历构建，自动生成 STAR 描述" },
  { icon: Search, title: "JD 分析", desc: "智能职位描述分析，识别技术要求与风险" },
  { icon: PenTool, title: "简历定制", desc: "根据 JD 动态优化简历，提升匹配率" },
  { icon: MessageSquare, title: "模拟面试", desc: "AI 模拟真实面试场景，精准反馈" },
];

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">你好，{user?.name || "用户"}</h1>
        <p className="text-muted-foreground mt-1">欢迎使用 AI Career Copilot，开启你的智能求职之旅</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {features.map((f) => (
          <Card key={f.title} className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                <f.icon className="h-5 w-5 text-primary" />
              </div>
            </CardHeader>
            <CardContent>
              <CardTitle className="text-base">{f.title}</CardTitle>
              <CardDescription className="mt-1 text-xs">{f.desc}</CardDescription>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>快速开始</CardTitle>
          <CardDescription>选择以下功能开始使用</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 text-sm text-muted-foreground">
            <p>• 前往简历管理创建你的第一份 AI 驱动简历</p>
            <p>• 粘贴职位描述进行智能 JD 分析</p>
            <p>• 根据目标 JD 定制优化简历</p>
            <p>• 开始 AI 模拟面试练习</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
