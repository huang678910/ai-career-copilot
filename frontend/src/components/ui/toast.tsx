"use client";

import { useUIStore } from "@/stores/ui-store";
import { cn } from "@/lib/utils";
import { X } from "lucide-react";

export function ToastContainer() {
  const { toasts, removeToast } = useUIStore();

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={cn(
            "animate-slide-up rounded-lg px-4 py-3 text-sm shadow-lg",
            toast.variant === "destructive"
              ? "bg-destructive text-destructive-foreground"
              : "bg-card text-card-foreground border",
          )}
        >
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="font-medium">{toast.title}</p>
              {toast.description && <p className="text-xs opacity-80">{toast.description}</p>}
            </div>
            <button onClick={() => removeToast(toast.id)} className="shrink-0 opacity-60 hover:opacity-100">
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
