"use client";

import React, { useState } from "react";
import { UploadZone } from "@/components/upload-zone";
import { DocumentList } from "@/components/document-list";
import { ChatInterface } from "@/components/chat-interface";
import { Header } from "@/components/header";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FileText, MessageSquare, Upload } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 container py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-8rem)]">
          {/* Left Sidebar - Documents */}
          <div className="lg:col-span-1 space-y-4">
            <Card className="h-full flex flex-col">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Upload className="w-4 h-4" />
                  Upload Document
                </CardTitle>
                <CardDescription>
                  Upload a PDF to start chatting
                </CardDescription>
              </CardHeader>
              <CardContent className="flex-1 overflow-auto">
                <UploadZone />
              </CardContent>
            </Card>

            <Card className="h-full flex flex-col">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  Documents
                </CardTitle>
                <CardDescription>
                  Your uploaded documents
                </CardDescription>
              </CardHeader>
              <CardContent className="flex-1 overflow-auto">
                <DocumentList />
              </CardContent>
            </Card>
          </div>

          {/* Main Content - Chat */}
          <div className="lg:col-span-2">
            <Card className="h-full flex flex-col">
              <CardHeader className="flex-row items-center justify-between space-y-0">
                <div>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <MessageSquare className="w-4 h-4" />
                    Chat with Documents
                  </CardTitle>
                  <CardDescription>
                    Ask questions and get AI-powered answers
                  </CardDescription>
                </div>
              </CardHeader>
              <CardContent className="flex-1 p-0">
                <div className="h-full">
                  <ChatInterface />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
