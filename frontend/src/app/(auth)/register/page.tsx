"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Briefcase } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuthStore } from "@/stores/auth-store";
import { useUIStore } from "@/stores/ui-store";

const registerSchema = z.object({
  name: z.string().min(1, "请输入你的姓名"),
  email: z.string().email("请输入有效的邮箱地址"),
  password: z.string().min(8, "密码至少8个字符"),
  confirmPassword: z.string(),
}).refine((d) => d.password === d.confirmPassword, {
  message: "两次密码不一致",
  path: ["confirmPassword"],
});

type RegisterForm = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const registerFn = useAuthStore((s) => s.register);
  const addToast = useUIStore((s) => s.addToast);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterForm) => {
    setIsSubmitting(true);
    try {
      await registerFn({ name: data.name, email: data.email, password: data.password });
      router.push("/dashboard");
    } catch {
      addToast({ title: "注册失败", description: "该邮箱可能已被注册", variant: "destructive" });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-surface-50 to-brand-50 px-4 dark:from-surface-950 dark:to-brand-950">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-primary shadow-lg">
            <Briefcase className="h-6 w-6 text-primary-foreground" />
          </div>
          <h1 className="mt-4 text-2xl font-bold tracking-tight">AI Career Copilot</h1>
          <p className="mt-1 text-sm text-muted-foreground">智能求职助手 — 创建你的账户</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>注册新账户</CardTitle>
            <CardDescription>填写以下信息创建账户</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">姓名</Label>
                <Input id="name" type="text" placeholder="你的姓名" {...register("name")} />
                {errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">邮箱</Label>
                <Input id="email" type="email" placeholder="you@example.com" {...register("email")} />
                {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">密码</Label>
                <Input id="password" type="password" placeholder="••••••••" {...register("password")} />
                {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">确认密码</Label>
                <Input id="confirmPassword" type="password" placeholder="••••••••" {...register("confirmPassword")} />
                {errors.confirmPassword && <p className="text-xs text-destructive">{errors.confirmPassword.message}</p>}
              </div>

              <Button type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting ? "注册中..." : "注册"}
              </Button>
            </form>

            <p className="mt-4 text-center text-sm text-muted-foreground">
              已有账户？{" "}
              <Link href="/login" className="font-medium text-primary hover:underline">
                去登录
              </Link>
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
