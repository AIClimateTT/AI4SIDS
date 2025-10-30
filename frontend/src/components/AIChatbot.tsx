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
    <section>
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


export const AIChatBotWithButton = () => {

  const [isOpen, setIsOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const handleToggle = () => {
    setIsOpen(!isOpen);
    if (isOpen) {
      // When closing, also collapse if expanded
      setIsExpanded(false);
    }
  };

  return (
    <>
      {/* Chat Interface - positioned bottom right when open */}
      {isOpen && (
        <div 
          className={`fixed ${
            isExpanded 
              ? 'inset-4' 
              : 'bottom-24 right-4'
          } z-50 transition-all duration-300 max-w-xl`}
        >
          <AIChatbot
            
          />
        </div>
      )}

      {/* Floating Action Button */}
      <button
        onClick={handleToggle}
        className={`fixed bottom-6 right-6 z-40 p-4 rounded-full shadow-lg transition-all duration-300 ${
          isOpen 
            ? 'bg-red-600 hover:bg-red-700' 
            : 'bg-blue-600 hover:bg-blue-700'
        } text-white focus:outline-none focus:ring-4 focus:ring-blue-300`}
        aria-label={isOpen ? 'Close chat' : 'Open chat'}
      >
        {isOpen ? (
          // Close Icon (X)
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            className="h-6 w-6" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor" 
            strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          // Chat Icon
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            className="h-6 w-6" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor" 
            strokeWidth={2}
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" 
            />
          </svg>
        )}
      </button>

      {/* Notification Badge (optional - for unread messages) */}
      {!isOpen && false && ( // Set to true to show badge
        <div className="fixed bottom-16 right-16 z-50 bg-red-500 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
          3
        </div>
      )}
    </>
  );
};