'use client';

export const TypingIndicator = () => {
  return (
    <div className="flex justify-start">
      <div className="bg-[#f2f2f2] rounded-2xl px-4 py-3">
        <div className="flex space-x-2">
          <div className="h-2 w-2 rounded-full bg-gray-400 animate-pulse"></div>
          <div className="h-2 w-2 rounded-full bg-gray-400 animate-pulse [animation-delay:0.2s]"></div>
          <div className="h-2 w-2 rounded-full bg-gray-400 animate-pulse [animation-delay:0.4s]"></div>
        </div>
      </div>
    </div>
  );
};