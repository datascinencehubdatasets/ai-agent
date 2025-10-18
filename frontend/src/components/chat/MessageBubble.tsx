'use client';

interface MessageBubbleProps {
  role: 'user' | 'assistant';
  content: string;
}

export const MessageBubble = ({ role, content }: MessageBubbleProps) => {
  const isUser = role === 'user';
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`relative max-w-[85%] md:max-w-[75%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-[#1a1a1a] text-white'
            : 'bg-[#f2f2f2] text-gray-900'
        }`}
      >
        <p className="text-[15px] leading-relaxed">{content}</p>
      </div>
    </div>
  );
};