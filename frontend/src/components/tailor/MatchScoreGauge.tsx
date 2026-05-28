"use client";

import { cn } from "@/lib/utils";

interface MatchScoreGaugeProps {
  score: number | null;
}

function getScoreColor(score: number): string {
  if (score >= 80) return "text-emerald-500 stroke-emerald-500";
  if (score >= 60) return "text-amber-500 stroke-amber-500";
  return "text-red-500 stroke-red-500";
}

function getScoreLabel(score: number): string {
  if (score >= 85) return "优秀匹配";
  if (score >= 70) return "良好匹配";
  if (score >= 55) return "中等匹配";
  if (score >= 40) return "匹配较低";
  return "需大幅优化";
}

export function MatchScoreGauge({ score }: MatchScoreGaugeProps) {
  if (score === null || score === undefined) return null;

  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-2">
      <h3 className="text-sm font-semibold">匹配度评分</h3>
      <div className="relative flex items-center justify-center">
        <svg width="100" height="100" className="-rotate-90">
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth="6"
            className="text-muted/20"
          />
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth="6"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className={cn("transition-all duration-1000", getScoreColor(score))}
          />
        </svg>
        <span className={cn("absolute text-xl font-bold", getScoreColor(score))}>
          {Math.round(score)}
        </span>
      </div>
      <span className="text-xs text-muted-foreground">{getScoreLabel(score)}</span>
    </div>
  );
}
