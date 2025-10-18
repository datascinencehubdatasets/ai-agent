'use client';

import { useState } from 'react';

interface VoiceInputProps {
  onSend: (message: string) => void;
}

export const VoiceInput = ({ onSend }: VoiceInputProps) => {
  const [message, setMessage] = useState('');
  const [isRecording, setIsRecording] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      onSend(message);
      setMessage('');
    }
  };

  const toggleRecording = () => {
    // Voice recording functionality to be implemented
    setIsRecording(!isRecording);
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <div className="flex-1 relative">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Message Zaman AI..."
          className="w-full h-[50px] pl-4 pr-[100px] bg-[#f2f2f2] rounded-xl text-[15px] text-gray-900 placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-300 transition-all"
        />
        <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
          <button
            type="button"
            onClick={toggleRecording}
            className={`w-[34px] h-[34px] flex items-center justify-center rounded-lg ${
              isRecording 
                ? 'bg-red-500 text-white' 
                : 'text-gray-700 hover:bg-gray-200'
            } transition-all`}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              className="w-5 h-5"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
              />
            </svg>
          </button>
          
          <button
            type="submit"
            disabled={!message.trim()}
            className="w-[34px] h-[34px] flex items-center justify-center rounded-lg bg-[#1a1a1a] text-white disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:bg-black"
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              viewBox="0 0 24 24" 
              fill="currentColor"
              className="w-5 h-5"
            >
              <path d="M3.478 2.404a.75.75 0 00-.926.941l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.404z" />
            </svg>
          </button>
        </div>
      </div>
    </form>
  );
};