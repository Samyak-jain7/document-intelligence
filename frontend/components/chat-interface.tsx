"use client";

import React, { useState, useRef, useEffect } from "react";
import { Send, Loader2, FileText, ChevronDown, ChevronUp } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { api, ChatMessage, Source } from "@/lib/api";
import { useStore } from "@/lib/store";

export function ChatInterface() {
  const [input, setInput] = useState("");
  const [showSources, setShowSources] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const { messages, isLoading, addMessage, setLoading, clearMessages, documents, selectedDocumentId } =
    useStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: input.trim(),
    };

    addMessage(userMessage);
    setInput("");
    setLoading(true);

    try {
      const completedDocs = documents.filter((d) => d.status === "completed");
      const docIds = selectedDocumentId
        ? [selectedDocumentId]
        : completedDocs.map((d) => d.document_id);

      const response = await api.chat({
        query: userMessage.content,
        document_ids: docIds.length > 0 ? docIds : undefined,
        top_k: 5,
        conversation_history: messages.slice(-10),
      });

      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: response.answer,
        sources: response.sources,
      };

      addMessage(assistantMessage);
    } catch (err) {
      const errorMessage: ChatMessage = {
        role: "assistant",
        content: `Sorry, I encountered an error: ${
          err instanceof Error ? err.message : "Unknown error"
        }`,
      };
      addMessage(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const lastMessage = messages[messages.length - 1];
  const hasSources = lastMessage?.sources && lastMessage.sources.length > 0;

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
            <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
              <FileText className="w-8 h-8" />
            </div>
            <p className="text-sm font-medium">Start a conversation</p>
            <p className="text-xs mt-1 max-w-xs">
              Ask questions about your uploaded documents and get
              AI-powered answers with citations
            </p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              className={cn(
                "flex animate-message",
                msg.role === "user" ? "justify-end" : "justify-start"
              )}
            >
              <div
                className={cn(
                  "max-w-[80%] rounded-lg px-4 py-3",
                  msg.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted"
                )}
              >
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>

                {msg.role === "assistant" && msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-border/50">
                    <button
                      onClick={() => setShowSources(!showSources)}
                      className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
                    >
                      {showSources ? (
                        <ChevronUp className="w-3 h-3" />
                      ) : (
                        <ChevronDown className="w-3 h-3" />
                      )}
                      {msg.sources.length} source{msg.sources.length > 1 ? "s" : ""}
                    </button>

                    {showSources && (
                      <div className="mt-2 space-y-2">
                        {msg.sources.map((source, idx) => (
                          <div
                            key={idx}
                            className="text-xs bg-background/50 rounded p-2"
                          >
                            <div className="flex items-center justify-between mb-1">
                              <span className="font-medium truncate max-w-[200px]">
                                {source.filename}
                              </span>
                              {source.page_number && (
                                <span className="text-muted-foreground ml-2">
                                  Page {source.page_number}
                                </span>
                              )}
                            </div>
                            <p className="text-muted-foreground line-clamp-2">
                              {source.content}
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex justify-start animate-message">
            <div className="bg-muted rounded-lg px-4 py-3">
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-muted-foreground typing-dot" />
                <div className="w-2 h-2 rounded-full bg-muted-foreground typing-dot" />
                <div className="w-2 h-2 rounded-full bg-muted-foreground typing-dot" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t p-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your documents..."
            className="flex-1 resize-none rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            rows={1}
            disabled={isLoading}
          />
          <Button
            type="submit"
            size="icon"
            disabled={!input.trim() || isLoading}
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </form>
        <div className="flex items-center justify-between mt-2">
          <p className="text-xs text-muted-foreground">
            Press Enter to send, Shift+Enter for new line
          </p>
          {messages.length > 0 && (
            <button
              onClick={clearMessages}
              className="text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
              Clear chat
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
