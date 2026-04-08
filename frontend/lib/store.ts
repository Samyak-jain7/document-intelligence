import { create } from "zustand";
import { ChatMessage, DocumentInfo } from "./api";

interface AppState {
  // Documents
  documents: DocumentInfo[];
  selectedDocumentId: string | null;
  setDocuments: (docs: DocumentInfo[]) => void;
  addDocument: (doc: DocumentInfo) => void;
  updateDocument: (docId: string, updates: Partial<DocumentInfo>) => void;
  removeDocument: (docId: string) => void;
  setSelectedDocument: (docId: string | null) => void;

  // Chat
  messages: ChatMessage[];
  isLoading: boolean;
  conversationId: string | null;
  addMessage: (msg: ChatMessage) => void;
  setLoading: (loading: boolean) => void;
  clearMessages: () => void;
  setConversationId: (id: string) => void;
}

export const useStore = create<AppState>((set) => ({
  // Documents
  documents: [],
  selectedDocumentId: null,

  setDocuments: (docs) => set({ documents: docs }),

  addDocument: (doc) =>
    set((state) => ({
      documents: [doc, ...state.documents],
    })),

  updateDocument: (docId, updates) =>
    set((state) => ({
      documents: state.documents.map((d) =>
        d.document_id === docId ? { ...d, ...updates } : d
      ),
    })),

  removeDocument: (docId) =>
    set((state) => ({
      documents: state.documents.filter((d) => d.document_id !== docId),
      selectedDocumentId:
        state.selectedDocumentId === docId ? null : state.selectedDocumentId,
    })),

  setSelectedDocument: (docId) =>
    set({ selectedDocumentId: docId }),

  // Chat
  messages: [],
  isLoading: false,
  conversationId: null,

  addMessage: (msg) =>
    set((state) => ({
      messages: [...state.messages, msg],
    })),

  setLoading: (loading) => set({ isLoading: loading }),

  clearMessages: () => set({ messages: [], conversationId: null }),

  setConversationId: (id) => set({ conversationId: id }),
}));
