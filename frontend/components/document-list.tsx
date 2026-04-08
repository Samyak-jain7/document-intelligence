"use client";

import React, { useEffect, useState } from "react";
import {
  FileText,
  Trash2,
  RefreshCw,
  CheckCircle,
  Clock,
  AlertCircle,
  Loader2,
} from "lucide-react";
import { cn, formatFileSize, formatDate } from "@/lib/utils";
import { api, DocumentInfo } from "@/lib/api";
import { useStore } from "@/lib/store";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

const statusConfig = {
  pending: {
    icon: Clock,
    color: "text-muted-foreground",
    bg: "bg-muted",
    label: "Pending",
  },
  processing: {
    icon: Loader2,
    color: "text-blue-500",
    bg: "bg-blue-500/10",
    label: "Processing",
    animate: true,
  },
  completed: {
    icon: CheckCircle,
    color: "text-green-500",
    bg: "bg-green-500/10",
    label: "Ready",
  },
  failed: {
    icon: AlertCircle,
    color: "text-destructive",
    bg: "bg-destructive/10",
    label: "Failed",
  },
};

export function DocumentList() {
  const { documents, setDocuments, removeDocument, selectedDocumentId, setSelectedDocument } =
    useStore();
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchDocuments = async () => {
    try {
      const response = await api.listDocuments();
      setDocuments(response.documents);
    } catch (err) {
      console.error("Failed to fetch documents:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();

    // Poll for status updates
    const interval = setInterval(() => {
      const processingDocs = documents.filter((d) => d.status === "processing" || d.status === "pending");
      if (processingDocs.length > 0) {
        fetchDocuments();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleDelete = async (doc: DocumentInfo) => {
    if (deletingId) return;
    setDeletingId(doc.document_id);

    try {
      await api.deleteDocument(doc.document_id);
      removeDocument(doc.document_id);
    } catch (err) {
      console.error("Failed to delete document:", err);
    } finally {
      setDeletingId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-32">
        <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
        <p className="text-sm">No documents uploaded yet</p>
        <p className="text-xs mt-1">Upload a PDF to get started</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {documents.map((doc) => {
        const status = statusConfig[doc.status as keyof typeof statusConfig] || statusConfig.pending;
        const StatusIcon = status.icon;

        return (
          <div
            key={doc.document_id}
            onClick={() => setSelectedDocument(doc.document_id)}
            className={cn(
              "flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-all",
              selectedDocumentId === doc.document_id
                ? "border-primary bg-primary/5"
                : "border-transparent hover:bg-muted/50"
            )}
          >
            <div
              className={cn(
                "w-10 h-10 rounded-lg flex items-center justify-center shrink-0",
                status.bg
              )}
            >
              <FileText className={cn("w-5 h-5", status.color)} />
            </div>

            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{doc.filename}</p>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span>{formatFileSize(doc.file_size)}</span>
                <span>•</span>
                <span>{formatDate(doc.created_at)}</span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {doc.status === "completed" && doc.num_chunks > 0 && (
                <span className="text-xs text-muted-foreground">
                  {doc.num_chunks} chunks
                </span>
              )}

              <div
                className={cn(
                  "flex items-center gap-1 px-2 py-1 rounded-full text-xs",
                  status.bg,
                  status.color
                )}
              >
                <StatusIcon
                  className={cn("w-3 h-3", status.animate && "animate-spin")}
                />
                <span>{status.label}</span>
              </div>

              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete(doc);
                }}
                disabled={deletingId === doc.document_id}
              >
                {deletingId === doc.document_id ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Trash2 className="w-4 h-4 text-muted-foreground hover:text-destructive" />
                )}
              </Button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
