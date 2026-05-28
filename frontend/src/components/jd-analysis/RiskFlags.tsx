"use client";

import { AlertTriangle, ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";

interface RiskFlag {
  type: string;
  signal: string;
  severity: string;
}

interface RiskFlagsProps {
  flags: RiskFlag[] | null;
  riskScore: number | null;
}

const severityConfig: Record<string, { color: string; bg: string }> = {
  high: { color: "text-red-600", bg: "bg-red-50 border-red-200 dark:bg-red-950 dark:border-red-800" },
  medium: { color: "text-amber-600", bg: "bg-amber-50 border-amber-200 dark:bg-amber-950 dark:border-amber-800" },
  low: { color: "text-blue-600", bg: "bg-blue-50 border-blue-200 dark:bg-blue-950 dark:border-blue-800" },
};

const riskLabels: Record<string, string> = {
  "外包风险": "外包风险",
  "培训骗局": "培训骗局",
  "虚假高薪": "虚假高薪",
  "加班文化": "加班文化",
  "皮包公司": "皮包公司",
  "技术要求矛盾": "技术要求矛盾",
};

export function RiskFlags({ flags, riskScore }: RiskFlagsProps) {
  if (!flags || flags.length === 0) {
    return (
      <div className="flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 p-3 dark:bg-emerald-950 dark:border-emerald-800">
        <ShieldCheck className="h-4 w-4 text-emerald-600" />
        <span className="text-sm text-emerald-700 dark:text-emerald-300">
          未发现明显风险信号
        </span>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">风险识别</h3>
        {riskScore !== null && (
          <span className="text-xs text-muted-foreground">
            风险评分：{riskScore}/5
          </span>
        )}
      </div>
      <div className="space-y-2">
        {flags.map((flag, i) => {
          const config = severityConfig[flag.severity] || severityConfig.low;
          return (
            <div
              key={i}
              className={cn("flex items-start gap-2 rounded-lg border p-3", config.bg)}
            >
              <AlertTriangle className={cn("h-4 w-4 mt-0.5 shrink-0", config.color)} />
              <div>
                <span className={cn("text-sm font-medium", config.color)}>
                  {riskLabels[flag.type] || flag.type}
                </span>
                <p className="mt-0.5 text-xs text-muted-foreground">{flag.signal}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
