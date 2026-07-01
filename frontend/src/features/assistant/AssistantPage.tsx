import { useState } from 'react'
import { Bot, Send } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  INITIAL_TRANSCRIPT,
  SUGGESTED_PROMPTS,
  type ChatMessage,
} from '@/features/assistant/data'

export function AssistantPage() {
  const [messages, setMessages] = useState<ChatMessage[]>(INITIAL_TRANSCRIPT)
  const [draft, setDraft] = useState('')

  const send = (text: string) => {
    const trimmed = text.trim()
    if (!trimmed) return
    setMessages((prev) => [
      ...prev,
      { id: `u-${prev.length}`, role: 'user', text: trimmed, time: 'now' },
    ])
    setDraft('')
  }

  return (
    <div className="p-6">
      <Card className="flex h-[calc(100vh-7rem)] flex-col">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-base">
            <Bot className="h-5 w-5 text-blue-600" />
            AI Preparedness Assistant
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={() => setMessages(INITIAL_TRANSCRIPT)}>
            Clear Chat
          </Button>
        </CardHeader>

        <CardContent className="flex flex-1 flex-col gap-4 overflow-y-auto">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`max-w-[80%] rounded-lg p-3 text-sm ${
                m.role === 'user'
                  ? 'ml-auto bg-blue-600 text-white'
                  : 'bg-muted text-foreground'
              }`}
            >
              <div>{m.text}</div>
              {m.bullets ? (
                <ul className="mt-2 list-disc space-y-1 pl-4">
                  {m.bullets.map((b) => (
                    <li key={b}>{b}</li>
                  ))}
                </ul>
              ) : null}
              <div className="mt-1 text-[10px] opacity-70">{m.time}</div>
            </div>
          ))}
        </CardContent>

        <div className="border-t p-3">
          <div className="mb-2 flex flex-wrap gap-2">
            {SUGGESTED_PROMPTS.map((p) => (
              <button
                key={p}
                onClick={() => send(p)}
                className="rounded-full border px-3 py-1 text-xs hover:bg-muted"
              >
                {p}
              </button>
            ))}
          </div>
          <div className="flex gap-2">
            <Input
              placeholder="Ask a question…"
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && send(draft)}
            />
            <Button onClick={() => send(draft)} disabled={!draft.trim()}>
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default AssistantPage
