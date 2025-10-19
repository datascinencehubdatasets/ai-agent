export type Language = 'ru' | 'en' | null;

export interface UsedDoc {
  source: string;
  chunk: number;
  score: number;
}

export interface IntentRequest {
  text: string;
  language: Language;
  session_id?: string;
}

export interface IntentResponse {
  intent: string;
  confidence: number;
  matched_reasons?: string[];
  llm?: string;
  fallback?: any;
}

export interface RouteRequest {
  text: string;
  language: Language;
  session_id?: string;
  context?: Record<string, any>;
}

export interface RouteResponse {
  intent: string;
  confidence: number;
  agent: string;
  answer: string;
  llm?: string;
  fallback?: any;
  extra?: {
    used_docs?: UsedDoc[];
  };
}

export type MessageRole = 'user' | 'assistant' | 'system';

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  status?: 'idle' | 'sending' | 'success' | 'error' | 'cancelled';
  meta?: Partial<RouteResponse> & { error?: string };
  createdAt?: number;
}

export const translations = {
  ru: {
    placeholder: 'Введите сообщение... (нажмите Enter или Отправить)',
    send: 'Отправить',
    classify: 'Определить интент',
    abort: 'Отмена',
    thinking: 'Assistant is thinking…',
    retry: 'Повторить',
    timeout: 'Время ожидания истекло. Повторить?'
  },
  en: {
    placeholder: 'Type a message... (press Enter or Send)',
    send: 'Send',
    classify: 'Classify intent',
    abort: 'Abort',
    thinking: 'Assistant is thinking…',
    retry: 'Retry',
    timeout: 'Request timed out. Retry?'
  }
} as const;