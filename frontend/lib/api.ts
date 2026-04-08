const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface UploadResponse {
  document_id: string;
  filename: string;
  status: string;
  message: string;
  file_size: number;
}

export interface DocumentInfo {
  document_id: string;
  filename: string;
  status: string;
  file_size: number;
  num_chunks: number;
  created_at: string;
  error_message?: string;
}

export interface ProcessingStatus {
  document_id: string;
  status: string;
  progress: number;
  message: string;
  num_chunks: number;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

export interface Source {
  chunk_id: string;
  content: string;
  document_id: string;
  filename: string;
  page_number?: number;
  score?: number;
}

export interface ChatRequest {
  query: string;
  document_ids?: string[];
  top_k?: number;
  conversation_history?: ChatMessage[];
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
  conversation_id: string;
}

export interface SearchResult {
  chunk_id: string;
  content: string;
  document_id: string;
  filename: string;
  score: number;
}

export interface SearchResponse {
  results: SearchResult[];
  query: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const config: RequestInit = {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    };

    const response = await fetch(url, config);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Request failed" }));
      throw new Error(error.detail || `HTTP error ${response.status}`);
    }

    return response.json();
  }

  // Health check
  async healthCheck() {
    return this.request<{
      status: string;
      version: string;
      chroma_connected: boolean;
      openai_configured: boolean;
    }>("/health");
  }

  // Document endpoints
  async uploadDocument(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${this.baseUrl}/documents/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Upload failed" }));
      throw new Error(error.detail || "Upload failed");
    }

    return response.json();
  }

  async getDocumentStatus(documentId: string): Promise<ProcessingStatus> {
    return this.request<ProcessingStatus>(`/documents/status/${documentId}`);
  }

  async listDocuments(): Promise<{ documents: DocumentInfo[]; total: number }> {
    return this.request("/documents/");
  }

  async getDocument(documentId: string): Promise<DocumentInfo> {
    return this.request<DocumentInfo>(`/documents/${documentId}`);
  }

  async deleteDocument(documentId: string): Promise<void> {
    await this.request(`/documents/${documentId}`, { method: "DELETE" });
  }

  // Chat endpoints
  async chat(request: ChatRequest): Promise<ChatResponse> {
    return this.request<ChatResponse>("/chat/", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  async search(query: string, documentIds?: string[], topK?: number): Promise<SearchResponse> {
    return this.request<SearchResponse>("/chat/search", {
      method: "POST",
      body: JSON.stringify({ query, document_ids: documentIds, top_k: topK }),
    });
  }
}

export const api = new ApiClient();
