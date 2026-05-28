"use client";

import { Badge } from "@/components/ui/badge";

interface TechStackBadgesProps {
  techStack: Record<string, string[]> | null;
}

const categoryLabels: Record<string, string> = {
  languages: "编程语言",
  frameworks: "框架",
  databases: "数据库",
  cloud: "云服务",
  tools: "工具链",
  other: "其他",
};

const categoryColors: Record<string, "default" | "secondary" | "success" | "warning"> = {
  languages: "default",
  frameworks: "success",
  databases: "warning",
  cloud: "secondary",
  tools: "secondary",
  other: "secondary",
};

export function TechStackBadges({ techStack }: TechStackBadgesProps) {
  if (!techStack || Object.keys(techStack).length === 0) return null;

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">技术栈分析</h3>
      {Object.entries(techStack).map(([category, items]) => {
        if (!items || items.length === 0) return null;
        return (
          <div key={category} className="space-y-1">
            <span className="text-xs text-muted-foreground">
              {categoryLabels[category] || category}
            </span>
            <div className="flex flex-wrap gap-1.5">
              {items.map((item) => (
                <Badge key={item} variant={categoryColors[category] || "secondary"}>
                  {item}
                </Badge>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
