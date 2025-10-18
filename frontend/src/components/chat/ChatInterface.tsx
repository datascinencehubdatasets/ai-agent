'use client';

import { useState } from 'react';
import { MessageBubble } from './MessageBubble';
import { VoiceInput } from './VoiceInput';
import { TypingIndicator } from './TypingIndicator';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (message: string) => {
    setIsLoading(true);
    // Add user message to chat
    setMessages([...messages, { role: 'user', content: message }]);
    
    try {
      // Send message to backend
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });
      
      const data = await response.json();
      
      // Add AI response to chat
      setMessages(prev => [...prev, { role: 'assistant', content: data.message }]);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <div className="flex items-center px-6 py-3 bg-white border-b">
        <div className="flex-1 flex items-center justify-between max-w-5xl mx-auto w-full">
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-semibold text-gray-900">Zaman AI Assistant</h1>
            <span className="text-sm px-2 py-0.5 bg-green-50 text-green-700 rounded-full border border-green-100">
              Online
            </span>
          </div>
          <div className="text-sm text-gray-600">
            Islamic Finance Expert
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto w-full h-full">
          <div className="p-4 space-y-6">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center py-20 px-4">
                <div className="max-w-md">
                  <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                    Welcome to Zaman AI Assistant
                  </h2>
                  <p className="text-gray-600">
                    Your personal Islamic finance expert. Ask me anything about Islamic finance principles, investment options, or financial planning.
                  </p>
                </div>
              </div>
            ) : (
              <>
                {messages.map((msg, idx) => (
                  <MessageBubble key={idx} role={msg.role} content={msg.content} />
                ))}
              </>
            )}
            {isLoading && <TypingIndicator />}
          </div>
        </div>
      </div>
      
      {/* Input Area */}
      <div className="border-t bg-white">
        <div className="max-w-5xl mx-auto w-full px-4 py-4">
          <VoiceInput onSend={handleSendMessage} />
        </div>
      </div>
    </div>
  );
};