"use client";

import { Badge } from "@/components/ui/badge";

interface SkillGap {
  skill: string;
  importance: string;
  suggestion: string;
}

interface SkillMatch {
  skill: string;
  status: "matched" | "partial" | "missing";
  evidence?: string;
  recommendation?: string;
}

interface SkillGapListProps {
  gaps: SkillGap[] | null;
  matches?: SkillMatch[] | null;
}

export function SkillGapList({ gaps, matches }: SkillGapListProps) {
  return (
    <div className="space-y-4">
      {matches && matches.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold">技能匹配详情</h3>
          <div className="space-y-1.5">
            {matches.map((m, i) => (
              <div key={i} className="flex items-center justify-between rounded border p-2 text-sm">
                <span className="font-medium">{m.skill}</span>
                <Badge
                  variant={
                    m.status === "matched" ? "success" : m.status === "partial" ? "warning" : "destructive"
                  }
                >
                  {m.status === "matched" ? "已匹配" : m.status === "partial" ? "部分匹配" : "缺失"}
                </Badge>
              </div>
            ))}
          </div>
        </div>
      )}

      {gaps && gaps.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold">技能差距</h3>
          <div className="space-y-2">
            {gaps.map((gap, i) => (
              <div key={i} className="rounded-lg border p-3 text-sm">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{gap.skill}</span>
                  <Badge variant="outline">{gap.importance}</Badge>
                </div>
                <p className="mt-1 text-xs text-muted-foreground">{gap.suggestion}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
