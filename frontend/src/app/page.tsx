import { ChatInterface } from '@/components/chat/ChatInterface'

export default function Home() {
  return (
    <main className="flex min-h-screen bg-[#f5f5f5]">
      <div className="flex-1 flex flex-col">
        <ChatInterface />
      </div>
    </main>
  )
}