"use client";

import { cn } from "@/lib/utils";
import React, { useState, useRef, useEffect } from "react";

function TooltipProvider({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}

function Tooltip({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const triggerRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      if (
        triggerRef.current && !triggerRef.current.contains(e.target as Node) &&
        contentRef.current && !contentRef.current.contains(e.target as Node)
      ) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  return (
    <div className="relative inline-block">
      <div ref={triggerRef} onMouseEnter={() => setOpen(true)} onMouseLeave={() => setOpen(false)}>
        {React.Children.toArray(children).find((c: any) => c?.type?.displayName === "TooltipTrigger")}
      </div>
      {open && (
        <div
          ref={contentRef}
          className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-50"
        >
          {React.Children.toArray(children).find((c: any) => c?.type?.displayName === "TooltipContent")}
        </div>
      )}
    </div>
  );
}

function TooltipTrigger({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
TooltipTrigger.displayName = "TooltipTrigger";

function TooltipContent({ className, children }: { className?: string; children: React.ReactNode }) {
  return (
    <div className={cn("rounded-md border bg-popover px-3 py-1.5 text-sm text-popover-foreground shadow-md animate-in fade-in-0 zoom-in-95", className)}>
      {children}
    </div>
  );
}
TooltipContent.displayName = "TooltipContent";

export { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider };
