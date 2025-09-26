// src/components/app/chat-interface.tsx
import React, { useState, useRef, useEffect } from 'react';
import { type ChatInterfaceProps, type Message } from '@/types';

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  isExpanded = false,
  onToggleExpand,
  selectedLocation = null // Add this prop
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
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Context-aware suggested questions
  const getContextualQuestions = () => {
    if (selectedLocation) {
      return [
        `What's the flood risk in ${selectedLocation.name}?`,
        `Show me evacuation routes from ${selectedLocation.name}`,
        `What are the current conditions in ${selectedLocation.name}?`,
        `Safety tips for ${selectedLocation.flood_risk} risk areas`
      ];
    } else {
      return [
        "What areas have the highest flood risk?",
        "How do I prepare for flood season?",
        "Where are the emergency shelters?",
        "What should I do during a flood warning?",
        "Show me current weather conditions"
      ];
    }
  };

  const handleQuestionClick = (question: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text: question,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, newMessage]);
    generateResponse(question);
  };

  const handleSendMessage = (e: React.MouseEvent | React.KeyboardEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, newMessage]);
    const userInput = inputText;
    setInputText('');
    generateResponse(userInput);
  };

  const generateResponse = (inputText: string) => {
    setTimeout(() => {
      let response = 'I can provide information about flood risks in Trinidad and Tobago.';

      // Location-specific responses
      if (inputText.toLowerCase().includes('port of spain')) {
        response = 'Port of Spain has HIGH flood risk due to its coastal location and urban drainage issues. Heavy rainfall often causes flooding in downtown areas, particularly around Independence Square and South Quay.';
      } else if (inputText.toLowerCase().includes('san fernando')) {
        response = 'San Fernando has CRITICAL flood risk, especially during the rainy season. The Guaracara River and coastal proximity contribute to frequent flooding. Main affected areas include High Street and Coffee Street.';
      } else if (inputText.toLowerCase().includes('arima')) {
        response = 'Arima has MEDIUM flood risk. While inland, the area can experience flash floods during heavy rainfall due to topography. The Arima River can overflow during intense storms.';
      } else if (inputText.toLowerCase().includes('chaguanas')) {
        response = 'Chaguanas has MEDIUM flood risk, particularly in low-lying areas like Longdenville and Edinburgh. Urban development has impacted natural drainage, leading to occasional flooding.';
      } else if (inputText.toLowerCase().includes('point fortin')) {
        response = 'Point Fortin has LOW flood risk, but localized flooding can occur during intense rain events. The area is generally well-drained due to its elevation.';
      }
      // Context-aware responses for selected location
      else if (selectedLocation && inputText.toLowerCase().includes(`flood risk in ${selectedLocation.name.toLowerCase()}`)) {
        response = `${selectedLocation.name} currently has ${selectedLocation.riskLevel.toUpperCase()} flood risk. `;
        if (selectedLocation.riskLevel === 'critical') {
          response += 'Immediate precautions recommended. Avoid unnecessary travel and stay informed about evacuation orders.';
        } else if (selectedLocation.riskLevel === 'high') {
          response += 'Monitor conditions closely. Prepare emergency supplies and know your evacuation routes.';
        } else if (selectedLocation.riskLevel === 'medium') {
          response += 'Stay alert to changing conditions. Review your flood preparedness plan.';
        } else {
          response += 'Current conditions are stable, but always stay prepared during rainy season.';
        }
      }
      // Evacuation routes
      else if (inputText.toLowerCase().includes('evacuation routes')) {
        if (selectedLocation) {
          response = `Evacuation routes from ${selectedLocation.name}: Primary route via Highway, Secondary route via local roads to higher ground. Nearest shelter: Community Center (2.3km away). Current route status: PASSABLE.`;
        } else {
          response = 'Main evacuation routes: Use major highways to move to higher ground. Avoid low-lying areas and bridges during heavy rain. Emergency shelters are located at community centers and schools.';
        }
      }
      // Current conditions
      else if (inputText.toLowerCase().includes('current conditions')) {
        if (selectedLocation) {
          response = `Current conditions in ${selectedLocation.name}: Weather - Light rain, River levels - Normal, Road access - Clear, Emergency services - Standby. Risk level: ${selectedLocation.riskLevel.toUpperCase()}.`;
        } else {
          response = 'Current conditions across Trinidad: Mixed weather patterns, some areas experiencing light rain. River levels are within normal ranges. All major roads are passable.';
        }
      }
      // Generic responses for preset questions
      else if (inputText.toLowerCase().includes('highest flood risk')) {
        response = 'Areas with highest flood risk: San Fernando (CRITICAL), Port of Spain (HIGH), followed by low-lying coastal areas. These areas are most vulnerable due to sea level, river proximity, and drainage issues.';
      } else if (inputText.toLowerCase().includes('prepare for flood season')) {
        response = 'Flood season preparation: 1) Create emergency kit with water, food, flashlight, radio 2) Know evacuation routes 3) Waterproof important documents 4) Have emergency contacts ready 5) Monitor weather alerts regularly.';
      } else if (inputText.toLowerCase().includes('emergency shelters')) {
        response = 'Emergency shelters are located at: Schools, Community centers, Religious buildings, Government buildings. Major shelters: Arima Community Center, San Fernando Town Hall, Chaguanas Secondary School. Check with local authorities for current availability.';
      } else if (inputText.toLowerCase().includes('during a flood warning')) {
        response = 'During flood warning: 1) Stay indoors if possible 2) Move to higher ground immediately 3) Avoid walking/driving through floodwater 4) Listen to emergency broadcasts 5) Have emergency supplies ready 6) Contact authorities if in immediate danger.';
      } else if (inputText.toLowerCase().includes('weather conditions')) {
        response = 'Current weather: Partly cloudy with scattered showers expected. Temperature: 28°C. Rainfall in last 24hrs: Moderate in central areas. Next 48hrs: Increased rainfall expected, monitor for flood advisories.';
      } else if (inputText.toLowerCase().includes('safety tips')) {
        const riskLevel = selectedLocation?.riskLevel || 'general';
        if (riskLevel === 'critical') {
          response = 'CRITICAL risk safety tips: Evacuate immediately if ordered, avoid all unnecessary travel, move valuables to high areas, stay tuned to emergency broadcasts, never attempt to cross flooded roads.';
        } else if (riskLevel === 'high') {
          response = 'HIGH risk safety tips: Prepare to evacuate, avoid low-lying areas, secure outdoor items, charge devices, keep emergency supplies accessible, monitor water levels closely.';
        } else if (riskLevel === 'medium') {
          response = 'MEDIUM risk safety tips: Stay alert, avoid unnecessary travel to flood-prone areas, keep emergency kit updated, monitor weather updates, know nearest evacuation routes.';
        } else {
          response = 'General safety tips: Never drive through flooded roads, stay informed during heavy rain, keep emergency supplies ready, know your evacuation routes, report flooding to authorities.';
        }
      }

      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: response,
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botResponse]);
    }, 1000);
  };

  // Auto-suggest context-aware questions when location changes
  useEffect(() => {
    if (selectedLocation) {
      const contextMessage: Message = {
        id: (Date.now() + 2).toString(),
        text: `I see you've selected ${selectedLocation.name}. I can provide specific information about flood risks, evacuation routes, and current conditions for this area.`,
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, contextMessage]);
    }
  }, [selectedLocation]);

  const suggestedQuestions = getContextualQuestions();

  return (
    <div className={`bg-white border border-gray-300 rounded-lg shadow-lg flex flex-col ${isExpanded
      ? 'fixed inset-4 z-50'
      : 'w-sm h-[500px]'
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
            <div
              className={`max-w-xs lg:max-w-md px-3 py-2 rounded-lg text-sm ${message.sender === 'user'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-800'
                }`}
            >
              {message.text}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 p-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                handleSendMessage(e);
              }
            }}
            placeholder="Ask about flood risks..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            onClick={handleSendMessage}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;


// export default function App() {
//   const [isExpanded, setIsExpanded] = useState(false);
//   const [scriptsLoaded, setScriptsLoaded] = useState(false);

//   useEffect(() => {
//     // Check if Leaflet is already loaded
//     if ((window as any).L) {
//       setScriptsLoaded(true);
//       return;
//     }

//     // Load Leaflet CSS
//     const link = document.createElement('link');
//     link.rel = 'stylesheet';
//     link.href = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css';
//     document.head.appendChild(link);

//     // Load Leaflet JS
//     const script = document.createElement('script');
//     script.src = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js';
//     script.onload = () => {
//       if ((window as any).L) {
//         setScriptsLoaded(true);
//       }
//     };
//     script.onerror = () => {
//       console.error('Failed to load Leaflet');
//     };
//     document.head.appendChild(script);

//     return () => {
//       // Only remove if we added them
//       try {
//         if (document.head.contains(link)) {
//           document.head.removeChild(link);
//         }
//         if (document.head.contains(script)) {
//           document.head.removeChild(script);
//         }
//       } catch (e) {
//         // Elements may already be removed
//       }
//     };
//   }, []);

//   return (
//     <div className="h-screen flex flex-col">
//       {/* Navbar */}
//       <nav className="bg-blue-800 text-white px-6 py-4 shadow-md">
//         <div className="flex items-center justify-between">
//           <h1 className="text-xl font-bold">Trinidad & Tobago Flood Risk Map</h1>
//           <div className="flex items-center space-x-4">
//             <div className="flex items-center space-x-2 text-sm">
//               <div className="flex items-center space-x-1">
//                 <div className="w-3 h-3 rounded-full bg-green-500"></div>
//                 <span>Low</span>
//               </div>
//               <div className="flex items-center space-x-1">
//                 <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
//                 <span>Medium</span>
//               </div>
//               <div className="flex items-center space-x-1">
//                 <div className="w-3 h-3 rounded-full bg-orange-500"></div>
//                 <span>High</span>
//               </div>
//               <div className="flex items-center space-x-1">
//                 <div className="w-3 h-3 rounded-full bg-red-500"></div>
//                 <span>Critical</span>
//               </div>
//             </div>
//           </div>
//         </div>
//       </nav>

//       {/* Main content */}
//       <div className="flex-1 relative">
//         {/* Map background */}
//         <div className="absolute inset-0">
//           {scriptsLoaded ? (
//             <MapComponent />
//           ) : (
//             <div className="flex items-center justify-center w-full h-full bg-gray-100">
//               <div className="text-gray-600">Loading map resources...</div>
//             </div>
//           )}
//         </div>

//         {/* Chat positioned on the right */}
//         <div className="absolute top-4 right-4 z-10">
//           <ChatInterface 
//             isExpanded={isExpanded}
//             onToggleExpand={() => setIsExpanded(!isExpanded)}
//           />
//         </div>
//       </div>
//     </div>
//   );
// }