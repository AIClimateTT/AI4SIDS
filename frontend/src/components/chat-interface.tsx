// src/components/app/chat-interface.tsx
import React, { useState, useRef, useEffect } from 'react';
import { type ChatInterfaceProps, type Message } from '@/types';
import { chatService, getContextualQuestions } from '@/lib/api/chatService';

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  isExpanded = false,
  onToggleExpand,
  selectedLocation = null
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello! I can help you understand flood risks in Trinidad and Tobago. Ask me about specific locations or general flood information.',
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleQuestionClick = async (question: string) => {
    await sendMessage(question);
  };

  const handleSendMessage = async (e: React.MouseEvent | React.KeyboardEvent) => {
    e.preventDefault();
    if (!inputText.trim() || isLoading) return;

    const userInput = inputText;
    setInputText('');
    await sendMessage(userInput);
  };

  const sendMessage = async (messageText: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      text: messageText,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Add typing indicator
      const typingId = `typing-${Date.now()}`;
      const typingMessage: Message = {
        id: typingId,
        text: '...',
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, typingMessage]);

      // Get response from chat service
      const response = await chatService.sendMessage({
        message: messageText,
        context: {
          selectedLocation: selectedLocation,
        }
      });

      // Remove typing indicator and add actual response
      setMessages(prev => {
        const filtered = prev.filter(msg => msg.id !== typingId);
        const botResponse: Message = {
          id: (Date.now() + 1).toString(),
          text: response.message,
          sender: 'bot',
          timestamp: new Date()
        };
        return [...filtered, botResponse];
      });

    } catch (error) {
      console.error('Error getting chat response:', error);
      
      // Remove typing indicator and show error
      setMessages(prev => {
        const filtered = prev.filter(msg => !msg.id.startsWith('typing-'));
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: 'I apologize, but I encountered an error processing your request. Please try again.',
          sender: 'bot',
          timestamp: new Date()
        };
        return [...filtered, errorMessage];
      });
    } finally {
      setIsLoading(false);
      // Focus back on input
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  // Auto-suggest context-aware questions when location changes
  useEffect(() => {
    if (selectedLocation) {
      const contextMessage: Message = {
        id: `location-context-${Date.now()}`,
        text: `I see you've selected ${selectedLocation.name}. I can provide specific information about flood risks, evacuation routes, and current conditions for this area.`,
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, contextMessage]);
    }
  }, [selectedLocation?.name]); // Only trigger when location name changes

  const suggestedQuestions = getContextualQuestions(selectedLocation);

  return (
    <div className={`bg-white border border-gray-300 rounded-lg shadow-lg flex flex-col ${isExpanded
      ? 'fixed inset-4 z-50'
      : 'w-96 h-[500px]'
      } transition-all duration-300`}>

      {/* Header */}
      <div className="bg-blue-600 text-white px-4 py-3 rounded-t-lg flex justify-between items-center">
        <h3 className="font-medium">Flood Risk Assistant</h3>
        {onToggleExpand && (
          <button
            onClick={onToggleExpand}
            className="text-white hover:text-gray-200 transition-colors"
            aria-label={isExpanded ? 'Minimize' : 'Expand'}
          >
            {isExpanded ? (
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-minimize">
                <path d="M8 3v3a2 2 0 0 1-2 2H3" />
                <path d="M21 8h-3a2 2 0 0 1-2-2V3" />
                <path d="M3 16h3a2 2 0 0 1 2 2v3" />
                <path d="M16 21v-3a2 2 0 0 1 2-2h3" />
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-expand">
                <path d="m15 15 6 6" />
                <path d="m15 9 6-6" />
                <path d="M21 16v5h-5" />
                <path d="M21 8V3h-5" />
                <path d="M3 16v5h5" />
                <path d="m3 21 6-6" />
                <path d="M3 8V3h5" />
                <path d="M9 9 3 3" />
              </svg>
            )}
          </button>
        )}
      </div>

      {/* Suggested Questions */}
      <div className="px-4 py-2 bg-gray-50 border-b border-gray-200">
        <p className="text-xs text-gray-600 mb-2">
          {selectedLocation ? `Questions about ${selectedLocation.name}:` : 'Quick questions:'}
        </p>
        <div className="flex flex-wrap gap-1">
          {suggestedQuestions.slice(0, isExpanded ? 4 : 2).map((question, index) => (
            <button
              key={index}
              onClick={() => handleQuestionClick(question)}
              className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full hover:bg-blue-200 transition-colors"
            >
              {question.length > 25 ? `${question.substring(0, 25)}...` : question}
            </button>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div className={`flex-1 overflow-y-auto space-y-3 ${isExpanded ? 'px-64' : 'p-4'}`}>
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {message.text === '...' ? (
              // Typing indicator
              <div className="bg-gray-100 px-4 py-3 rounded-lg max-w-xs lg:max-w-md">
                <div className="flex space-x-2 items-center">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            ) : (
              <div
                className={`max-w-xs lg:max-w-md px-3 py-2 rounded-lg text-sm ${message.sender === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-800'
                  }`}
              >
                {message.text}
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 p-4">
        <div className="flex space-x-2">
          <input
            ref={inputRef}
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !isLoading) {
                e.preventDefault();
                handleSendMessage(e);
              }
            }}
            disabled={isLoading}
            placeholder={isLoading ? "Waiting for response..." : "Ask about flood risks..."}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !inputText.trim()}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              'Send'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

/**
 * ChatWithButton Component
 * Provides a floating action button that toggles the chat interface
 * Use this component instead of ChatInterface directly for the hidden chat behavior
 */
export const ChatWithButton: React.FC<Omit<ChatInterfaceProps, 'isExpanded' | 'onToggleExpand'>> = ({
  selectedLocation = null
}) => {
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
          } z-50 transition-all duration-300`}
        >
          <ChatInterface
            isExpanded={isExpanded}
            onToggleExpand={() => setIsExpanded(!isExpanded)}
            selectedLocation={selectedLocation}
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

export default ChatInterface;

