'use client';

import { useState, useCallback } from 'react';
import { ExampleQueries } from './ExampleQueries';
import { ChatWindow } from './ChatWindow';
import { TechPanel } from './TechPanel';
import { useChat } from '@/hooks/useChat';

export const ChatInterface = () => {
  // Генерируем простой session_id для демо. В реальном приложении его нужно получать из авторизации/контекста
  const sessionId = typeof window !== 'undefined' ?
    window.localStorage.getItem('chat_session_id') ||
    `user-${Date.now().toString(36)}` : 'default';

  if (typeof window !== 'undefined' && !window.localStorage.getItem('chat_session_id')) {
    window.localStorage.setItem('chat_session_id', sessionId);
  }

  const chat = useChat('ru', sessionId);

  // TechPanel state
  const [isTechPanelVisible, setIsTechPanelVisible] = useState(true);
  const [techPanelWidth, setTechPanelWidth] = useState(320);

  const handleTechPanelToggle = useCallback((visible: boolean) => {
    setIsTechPanelVisible(visible);
  }, []);

  const handleTechPanelWidthChange = useCallback((width: number) => {
    setTechPanelWidth(width);
  }, []);

  return (
    <div className="flex flex-col min-h-screen bg-white">
      {/* Header */}
      <div className="flex items-center px-6 py-3 bg-white border-b">
        <div className="flex-1 flex items-center justify-between max-w-5xl mx-auto w-full">
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-semibold text-gray-900">Zaman AI Assistant</h1>
            <span className="text-sm px-2 py-0.5 bg-green-50 text-green-700 rounded-full border border-green-100">
              Online
            </span>
          </div>
          <div className="text-sm text-gray-600">Islamic Finance Expert</div>
        </div>
      </div>

      <div className="flex-1 flex justify-center overflow-hidden">
        <main className={`flex-1 ${isTechPanelVisible ? '' : 'mr-0'}`}>
          <ChatWindow
            messages={chat.messages}
            inputValue={chat.inputValue}
            setInputValue={chat.setInputValue}
            language={chat.language}
            setLanguage={chat.setLanguage}
            isSending={chat.isSending}
            send={chat.send}
            retry={chat.retry}
            abort={chat.abort}
            classifyIntent={chat.classifyIntent}
          />
        </main>

        <TechPanel
          data={chat.messages.slice().reverse().find(m => m.role === 'assistant')?.meta as any}
          isVisible={isTechPanelVisible}
          width={techPanelWidth}
          onToggle={handleTechPanelToggle}
          onWidthChange={handleTechPanelWidthChange}
        />
      </div>
    </div>
  );
};