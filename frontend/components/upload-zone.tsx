"use client";

import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, X, CheckCircle, AlertCircle } from "lucide-react";
import { cn, formatFileSize } from "@/lib/utils";
import { Progress } from "@/components/ui/progress";
import { api, UploadResponse } from "@/lib/api";
import { useStore } from "@/lib/store";

interface UploadZoneProps {
  onUploadComplete?: (response: UploadResponse) => void;
}

export function UploadZone({ onUploadComplete }: UploadZoneProps) {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const { addDocument } = useStore();

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (!file) return;

      setUploading(true);
      setError(null);
      setUploadProgress(0);

      try {
        // Simulate progress
        const progressInterval = setInterval(() => {
          setUploadProgress((prev) => Math.min(prev + 10, 90));
        }, 200);

        const response = await api.uploadDocument(file);

        clearInterval(progressInterval);
        setUploadProgress(100);

        addDocument({
          document_id: response.document_id,
          filename: response.filename,
          status: response.status,
          file_size: response.file_size,
          num_chunks: 0,
          created_at: new Date().toISOString(),
        });

        onUploadComplete?.(response);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Upload failed");
      } finally {
        setUploading(false);
      }
    },
    [addDocument, onUploadComplete]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } =
    useDropzone({
      onDrop,
      accept: {
        "application/pdf": [".pdf"],
      },
      maxFiles: 1,
      disabled: uploading,
    });

  return (
    <div
      {...getRootProps()}
      className={cn(
        "relative border-2 border-dashed rounded-lg p-8 transition-colors",
        isDragActive && !isDragReject && "border-primary bg-primary/5",
        isDragReject && "border-destructive bg-destructive/5",
        !isDragActive && "border-muted-foreground/25 hover:border-muted-foreground/50",
        uploading && "pointer-events-none opacity-60"
      )}
    >
      <input {...getInputProps()} />

      <div className="flex flex-col items-center justify-center text-center">
        {uploading ? (
          <>
            <div className="w-16 h-16 mb-4 rounded-full bg-primary/10 flex items-center justify-center">
              <FileText className="w-8 h-8 text-primary animate-pulse" />
            </div>
            <p className="text-sm font-medium mb-2">Uploading...</p>
            <Progress value={uploadProgress} className="w-full max-w-xs" />
          </>
        ) : error ? (
          <>
            <div className="w-16 h-16 mb-4 rounded-full bg-destructive/10 flex items-center justify-center">
              <AlertCircle className="w-8 h-8 text-destructive" />
            </div>
            <p className="text-sm text-destructive font-medium mb-1">{error}</p>
            <p className="text-xs text-muted-foreground">
              Click or drag to try again
            </p>
          </>
        ) : (
          <>
            <div
              className={cn(
                "w-16 h-16 mb-4 rounded-full flex items-center justify-center",
                isDragActive ? "bg-primary/10" : "bg-muted"
              )}
            >
              <Upload
                className={cn(
                  "w-8 h-8",
                  isDragActive ? "text-primary" : "text-muted-foreground"
                )}
              />
            </div>
            <p className="text-sm font-medium mb-1">
              {isDragActive
                ? "Drop your PDF here"
                : "Drag & drop a PDF file, or click to select"}
            </p>
            <p className="text-xs text-muted-foreground">
              Maximum file size: 50MB
            </p>
          </>
        )}
      </div>
    </div>
  );
}
