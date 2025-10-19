import { useCallback, useRef, useState } from 'react';
import type { ChatMessage, Language, RouteResponse, IntentResponse } from '@/lib/types';
import * as api from '@/lib/api';

export function useChat(initialLang: Language = 'ru', sessionId: string = 'default') {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [language, setLanguage] = useState<Language>(initialLang);
  const [isSending, setIsSending] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const makeId = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 8);

  const send = useCallback(async (text?: string) => {
    const content = text ?? inputValue;
    if (!content) return;
    const id = makeId();
    const userMsg: ChatMessage = {
      id,
      role: 'user',
      content,
      status: 'sending',
      createdAt: Date.now(),
    };

    // add user message
    setMessages(prev => [...prev, userMsg]);
    setIsSending(true);

    try {
      // call /route
      const res = await api.route(content, language, sessionId) as RouteResponse;

      const assistantMsg: ChatMessage = {
        id: makeId(),
        role: 'assistant',
        content: res.answer,
        status: 'success',
        meta: res,
        createdAt: Date.now(),
      };

      // update user status to success and append assistant message
      setMessages(prev => {
        const updated = prev.map(m => m.id === id ? { ...m, status: 'success' as const } : m);
        return [...updated, assistantMsg];
      });
      setInputValue('');
    } catch (err: any) {
      console.error('route error', err);
      setMessages(prev => prev.map(m => m.id === id ? { ...m, status: 'error', meta: { error: err?.message || String(err) } } : m));
    } finally {
      setIsSending(false);
    }
  }, [inputValue, language]);

  const retry = useCallback(async (messageId: string) => {
    const msg = messages.find(m => m.id === messageId);
    if (!msg) return;
    await send(msg.content);
  }, [messages, send]);

  const abort = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsSending(false);
    }
  }, []);

  const classifyIntent = useCallback(async (text?: string) => {
    const content = text ?? inputValue;
    if (!content) return null as IntentResponse | null;
    try {
      const res = await api.classifyIntent(content, language, sessionId) as IntentResponse;
      return res;
    } catch (err) {
      console.error('classify error', err);
      return null;
    }
  }, [inputValue, language]);

  return {
    messages,
    inputValue,
    setInputValue,
    language,
    setLanguage,
    isSending,
    send,
    retry,
    abort,
    classifyIntent,
  };
}
