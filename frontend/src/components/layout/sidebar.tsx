"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useUIStore } from "@/stores/ui-store";
import {
  Briefcase,
  FileText,
  Search,
  PenTool,
  BookOpen,
  MessageSquare,
  Settings,
  ChevronLeft,
} from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "仪表盘", icon: Briefcase },
  { href: "/resumes", label: "简历管理", icon: FileText },
  { href: "/jd-analysis", label: "JD 分析", icon: Search },
  { href: "/tailor", label: "简历定制", icon: PenTool },
  { href: "/mock-interview", label: "AI 模拟面试", icon: MessageSquare },
  { href: "/settings", label: "设置", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { sidebarCollapsed, toggleSidebar } = useUIStore();

  return (
    <aside
      className={cn(
        "flex flex-col border-r bg-card transition-all duration-300",
        sidebarCollapsed ? "w-16" : "w-60",
      )}
    >
      <div className="flex h-14 items-center justify-between px-4 border-b">
        {!sidebarCollapsed && (
          <Link href="/dashboard" className="flex items-center gap-2 font-semibold text-sm">
            <Briefcase className="h-5 w-5 text-primary" />
            <span>Career Copilot</span>
          </Link>
        )}
        <button
          onClick={toggleSidebar}
          className={cn("rounded-lg p-1.5 hover:bg-accent transition-colors", sidebarCollapsed && "mx-auto")}
        >
          <ChevronLeft className={cn("h-4 w-4 transition-transform", sidebarCollapsed && "rotate-180")} />
        </button>
      </div>

      <nav className="flex-1 space-y-1 p-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
              )}
            >
              <item.icon className="h-4 w-4 shrink-0" />
              {!sidebarCollapsed && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
