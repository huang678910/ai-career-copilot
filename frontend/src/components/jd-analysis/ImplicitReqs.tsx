"use client";

import { Lightbulb } from "lucide-react";

interface ImplicitReqsProps {
  requirements: string[] | null;
}

export function ImplicitReqs({ requirements }: ImplicitReqsProps) {
  if (!requirements || requirements.length === 0) return null;

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold">隐含要求分析</h3>
      <ul className="space-y-1.5">
        {requirements.map((req, i) => (
          <li key={i} className="flex items-start gap-2 text-sm">
            <Lightbulb className="h-4 w-4 mt-0.5 shrink-0 text-amber-500" />
            <span className="text-muted-foreground">{req}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
