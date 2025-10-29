import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Send, Bot, User } from 'lucide-react'
import { useState, useRef, useEffect } from 'react'
import { chatService, getContextualQuestions } from '@/lib/api/chatService'

interface Message {
  id: string
  text: string
  sender: 'user' | 'bot'
  timestamp: Date
}

const AIChatbot = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hello! I'm your AI flood preparedness assistant. I can help you with evacuation planning, safety tips, and answer questions about flood risks in your area. How can I assist you today?",
      sender: 'bot',
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({
      behavior: 'smooth',
      block: 'nearest',
      inline: 'nearest',
    })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleQuestionClick = async (question: string) => {
    setInput(question)
    // Auto-send after a brief delay to show the question was selected
    setTimeout(() => handleSend(), 100)
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userInput = input
    setInput('')

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      text: userInput,
      sender: 'user',
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Add typing indicator
      const typingId = `typing-${Date.now()}`
      const typingMessage: Message = {
        id: typingId,
        text: '...',
        sender: 'bot',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, typingMessage])

      // Get response from chat service
      const response = await chatService.sendMessage({
        message: userInput,
        context: {
          selectedLocation: null, // Can be extended to accept location prop
        },
      })

      // Remove typing indicator and add actual response
      setMessages((prev) => {
        const filtered = prev.filter((msg) => msg.id !== typingId)
        const botResponse: Message = {
          id: (Date.now() + 1).toString(),
          text: response.message,
          sender: 'bot',
          timestamp: new Date(),
        }
        return [...filtered, botResponse]
      })
    } catch (error) {
      console.error('Error getting chat response:', error)

      // Remove typing indicator and show error
      setMessages((prev) => {
        const filtered = prev.filter((msg) => !msg.id.startsWith('typing-'))
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: 'I apologize, but I encountered an error processing your request. Please try again.',
          sender: 'bot',
          timestamp: new Date(),
        }
        return [...filtered, errorMessage]
      })
    } finally {
      setIsLoading(false)
      // Focus back on input
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }

  const suggestedQuestions = getContextualQuestions(null)

  return (
    <section className="py-16 px-6 bg-muted/30">
      <div className="container mx-auto ">
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-6 w-6 text-primary" />
              AI Preparedness Assistant
            </CardTitle>
            <CardDescription>
              Get personalized guidance on flood preparedness, evacuation
              planning, and safety measures
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Chat Messages */}
            <div className="space-y-4 mb-4 h-[400px] overflow-y-auto p-4 bg-background rounded-lg border">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${
                    message.sender === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.sender === 'bot' && (
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                        <Bot className="h-5 w-5 text-primary" />
                      </div>
                    </div>
                  )}

                  {message.text === '...' ? (
                    // Typing indicator
                    <div className="bg-muted px-4 py-3 rounded-lg">
                      <div className="flex space-x-2 items-center">
                        <div
                          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                          style={{ animationDelay: '0ms' }}
                        ></div>
                        <div
                          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                          style={{ animationDelay: '150ms' }}
                        ></div>
                        <div
                          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                          style={{ animationDelay: '300ms' }}
                        ></div>
                      </div>
                    </div>
                  ) : (
                    <div
                      className={`max-w-[80%] rounded-lg p-3 ${
                        message.sender === 'user'
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted'
                      }`}
                    >
                      <p className="text-sm">{message.text}</p>
                    </div>
                  )}

                  {message.sender === 'user' && (
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 rounded-full bg-accent/10 flex items-center justify-center">
                        <User className="h-5 w-5 text-accent" />
                      </div>
                    </div>
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Quick Actions */}
            <div className="flex flex-wrap gap-2 mb-4">
              {suggestedQuestions.slice(0, 4).map((question, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => handleQuestionClick(question)}
                  disabled={isLoading}
                >
                  {question.length > 30
                    ? `${question.substring(0, 30)}...`
                    : question}
                </Button>
              ))}
            </div>

            {/* Input Area */}
            <div className="flex gap-2">
              <Input
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !isLoading) {
                    e.preventDefault()
                    e.stopPropagation()
                    handleSend()
                  }
                }}
                disabled={isLoading}
                placeholder={
                  isLoading
                    ? 'Waiting for response...'
                    : 'Ask me anything about flood preparedness...'
                }
                className="flex-1"
              />
              <Button
                onClick={(e) => {
                  e.preventDefault()
                  handleSend()
                }}
                disabled={isLoading || !input.trim()}
                className="bg-primary"
              >
                {isLoading ? (
                  <svg
                    className="animate-spin h-4 w-4"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>

            {/* Info Note */}
            <p className="text-xs text-muted-foreground mt-4 text-center">
              This AI assistant provides guidance based on official disaster
              management protocols. Always follow instructions from local
              authorities.
            </p>
          </CardContent>
        </Card>
      </div>
    </section>
  )
}

export default AIChatbot
