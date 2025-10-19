import React, { KeyboardEvent } from 'react';
import type { ChatMessage, Language } from '@/lib/types';
import { MessageBubble } from './MessageBubble';
import { translations } from '@/lib/types';
import { ExampleQueries } from './ExampleQueries';

interface Props {
  messages: ChatMessage[];
  inputValue: string;
  setInputValue: (v: string) => void;
  language: Language;
  setLanguage: (l: Language) => void;
  isSending: boolean;
  send: (text?: string) => Promise<void>;
  retry: (id: string) => Promise<void>;
  abort: () => void;
  classifyIntent: (text?: string) => Promise<any>;
}

export const ChatWindow = ({ messages, inputValue, setInputValue, language, setLanguage, isSending, send, retry, abort, classifyIntent }: Props) => {
  const t = translations[(language || 'ru') as keyof typeof translations];

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full relative">
      <div className="flex-1 overflow-y-auto p-6 pb-32">
        <div className="mx-auto w-full max-w-6xl">
          {messages.length === 0 && (
            <div className="mb-6">
              <ExampleQueries onQueryClick={(q) => send(q)} />
            </div>
          )}

          <div className="space-y-4">
            {messages.map(m => (
              <div key={m.id} className={m.role === 'user' ? 'flex justify-end' : 'flex justify-start'}>
                <div className="w-full max-w-6xl">
                  <MessageBubble role={m.role as any} content={m.content} />
                  {m.meta && m.role === 'assistant' && (
                    <div className="mt-1 text-xs text-gray-600">
                      <div>Intent: {m.meta.intent}</div>
                      <div>Agent: {m.meta.agent}</div>
                    </div>
                  )}
                  {m.status === 'error' && (
                    <div className="mt-2 text-sm text-red-700 bg-red-50 p-2 rounded">
                      <div>{m.meta?.error || 'Произошла ошибка'}</div>
                      <button className="text-sm mt-2 underline" onClick={() => retry(m.id)}>Повторить</button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="fixed bottom-0 left-0 right-0 bg-white border-t z-10">
        <div className="mx-auto w-full max-w-7xl px-6 py-4 flex items-center gap-4">
          <textarea
            aria-label="Сообщение"
            value={inputValue}
            onChange={e => setInputValue(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder={t.placeholder}
            className="flex-1 resize-none rounded-lg border px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 text-base"
            rows={2}
          />

          <div className="flex flex-col sm:flex-row gap-2">
            <button
              className="px-6 py-3 bg-blue-600 text-white rounded-lg disabled:opacity-50 font-medium hover:bg-blue-700 transition-colors"
              onClick={() => send()}
              disabled={isSending}
            >
              {t.send}
            </button>
            <button
              className="px-4 py-3 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              onClick={async () => {
                const res = await classifyIntent();
                if (res) alert(JSON.stringify(res, null, 2));
              }}
            >
              {t.classify}
            </button>
            <button
              className="px-4 py-3 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 transition-colors"
              onClick={() => abort()}
            >
              {t.abort}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};