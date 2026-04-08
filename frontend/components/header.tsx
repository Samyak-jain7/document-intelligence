"use client";

import React, { useEffect, useState } from "react";
import { Loader2, CheckCircle, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";

export function Header() {
  const [status, setStatus] = useState<{
    chroma_connected: boolean;
    openai_configured: boolean;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await api.healthCheck();
        setStatus({
          chroma_connected: health.chroma_connected,
          openai_configured: health.openai_configured,
        });
      } catch (err) {
        setStatus(null);
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className="w-6 h-6 text-primary-foreground"
            >
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
              <polyline points="10 9 9 9 8 9" />
            </svg>
          </div>
          <div>
            <h1 className="text-lg font-semibold">Document Intelligence</h1>
            <p className="text-xs text-muted-foreground">
              RAG-powered document Q&A
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {loading ? (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Checking...</span>
            </div>
          ) : status ? (
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1.5 text-sm">
                {status.openai_configured ? (
                  <>
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span className="text-muted-foreground">OpenAI</span>
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-4 h-4 text-yellow-500" />
                    <span className="text-muted-foreground">OpenAI Not Set</span>
                  </>
                )}
              </div>
              <div className="flex items-center gap-1.5 text-sm">
                {status.chroma_connected ? (
                  <>
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span className="text-muted-foreground">ChromaDB</span>
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-4 h-4 text-yellow-500" />
                    <span className="text-muted-foreground">ChromaDB</span>
                  </>
                )}
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 text-sm text-destructive">
              <AlertCircle className="w-4 h-4" />
              <span>API Offline</span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
