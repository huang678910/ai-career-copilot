"use client";

import { cn } from "@/lib/utils";

interface DifficultyMeterProps {
  score: number | null;
}

const labels: Record<number, string> = {
  1: "初级",
  2: "初中级",
  3: "中级",
  4: "中高级",
  5: "专家级",
};

const colors: Record<number, string> = {
  1: "bg-emerald-500",
  2: "bg-green-500",
  3: "bg-amber-500",
  4: "bg-orange-500",
  5: "bg-red-500",
};

export function DifficultyMeter({ score }: DifficultyMeterProps) {
  if (score === null || score === undefined) return null;

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold">岗位难度</h3>
      <div className="flex items-center gap-3">
        <div className="flex gap-1">
          {[1, 2, 3, 4, 5].map((i) => (
            <div
              key={i}
              className={cn(
                "h-2 w-6 rounded-full transition-colors",
                i <= score ? colors[score] || "bg-muted" : "bg-muted",
              )}
            />
          ))}
        </div>
        <span className="text-sm font-medium">{labels[score] || score}</span>
      </div>
    </div>
  );
}
