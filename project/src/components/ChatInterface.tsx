import React, { useState, useRef, useEffect } from 'react';
import { Send, ImageIcon, Mic, Volume2, VolumeX, MessageCircle } from 'lucide-react';
import { useAppContext } from '../contexts/AppContext';
import { getTranslation } from '../utils/translations';
import { ChatMessage } from '../types';
import ChatHistoryModal from './ChatHistoryModal';
import { postJson, getJson, API_BASE } from '../utils/api';

const ChatInterface: React.FC = () => {
  const { 
    messages, 
    addMessage, 
    language, 
    isSoundEnabled, 
    setIsSoundEnabled
  } = useAppContext();
  
  const [inputText, setInputText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [showChatHistory, setShowChatHistory] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    console.log('[ChatInterface] Mounted. lang=', language, 'sound=', isSoundEnabled);
    console.log('[ChatInterface] API_BASE =', API_BASE);
    // Ping backend health to verify connectivity
    (async () => {
      try {
        const res = await getJson('/health');
        console.log('[ChatInterface] /health OK:', res);
      } catch (e) {
        console.error('[ChatInterface] /health FAILED:', e);
      }
    })();
    return () => console.log('[ChatInterface] Unmounted');
  }, []);

  useEffect(() => {
    console.log('[ChatInterface] messages updated. count=', messages.length);
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;
    console.log('[ChatInterface] Sending user message:', inputText);

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputText,
      timestamp: new Date()
    };

    addMessage(userMessage);
    console.log('[ChatInterface] Added user message. newCount=', messages.length + 1);

    try {
      const payload = { question: inputText, conversation_history: messages, language } as any;
      console.log('[ChatInterface] POST /followup payload:', {
        question: inputText,
        conversation_history_length: messages.length,
        language
      });

      const data = await postJson<{ answer: string }>(`/followup`, payload);
      console.log('[ChatInterface] Response from /followup:', data);

      const aiResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: data?.answer || 'Sorry, I could not generate a response right now.',
        timestamp: new Date()
      };

      addMessage(aiResponse);
      console.log('[ChatInterface] Added AI message.');

      // Text-to-speech for AI responses if enabled
      if (isSoundEnabled && 'speechSynthesis' in window) {
        console.log('[ChatInterface] Speaking AI response. lang=', language);
        const utterance = new SpeechSynthesisUtterance(aiResponse.content);
        utterance.lang = language === 'hi' ? 'hi-IN' : 'en-US';
        speechSynthesis.speak(utterance);
      }
    } catch (err: any) {
      console.error('[ChatInterface] Error calling backend /followup:', err);
      const aiResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `Error contacting backend: ${err?.message || 'unknown error'}`,
        timestamp: new Date()
      };
      addMessage(aiResponse);
    } finally {
      setInputText('');
      console.log('[ChatInterface] Cleared input.');
    }
  };

  const handleImageUpload = () => {
    console.log('[ChatInterface] Trigger image upload dialog.');
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    console.log('[ChatInterface] File selected:', file?.name, file?.type, file?.size);
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const imageUrl = e.target?.result as string;
        const userMessage: ChatMessage = {
          id: Date.now().toString(),
          type: 'user',
          content: 'Uploaded an image for analysis',
          imageUrl: imageUrl,
          timestamp: new Date()
        };
        addMessage(userMessage);
      };
      reader.readAsDataURL(file);
    }
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    console.log('[ChatInterface] Toggle recording ->', !isRecording);
    // Implement speech-to-text functionality here
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      console.log('[ChatInterface] Enter pressed. Sending message.');
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto">
      {/* Chat History Button */}
      <div className="flex justify-end mb-4">
        <button
          onClick={() => setShowChatHistory(true)}
          className="flex items-center space-x-2 bg-white/80 backdrop-blur-sm text-gray-700 px-4 py-2 rounded-xl hover:bg-white/90 transition-all duration-200 shadow-lg"
        >
          <MessageCircle className="w-4 h-4" />
          <span className="text-sm font-medium">{getTranslation(language, 'chatHistory')}</span>
        </button>
      </div>

      {/* Messages Area */}
      <div className="flex-1 bg-white/60 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6 mb-6 overflow-y-auto max-h-96">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 py-12">
            <MessageCircle className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p className="text-lg">Start a conversation with your AI agricultural assistant</p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${
                    message.type === 'user'
                      ? 'bg-gradient-to-br from-green-500 to-green-600 text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {message.imageUrl && (
                    <img
                      src={message.imageUrl}
                      alt="Uploaded"
                      className="w-full h-32 object-cover rounded-lg mb-2"
                    />
                  )}
                  <p className="text-sm">{message.content}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Sound Toggle */}
      <div className="flex justify-center mb-4">
        <button
          onClick={() => {
            console.log('[ChatInterface] Toggle sound ->', !isSoundEnabled);
            setIsSoundEnabled(!isSoundEnabled);
          }}
          className={`flex items-center space-x-2 px-4 py-2 rounded-xl transition-all duration-200 ${
            isSoundEnabled
              ? 'bg-green-100 text-green-700 hover:bg-green-200'
              : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
          }`}
        >
          {isSoundEnabled ? (
            <Volume2 className="w-4 h-4" />
          ) : (
            <VolumeX className="w-4 h-4" />
          )}
          <span className="text-sm font-medium">
            {isSoundEnabled ? getTranslation(language, 'soundOn') : getTranslation(language, 'soundOff')}
          </span>
        </button>
      </div>

      {/* Input Area */}
      <div className="flex items-center space-x-3">
        <div className="flex-1 relative">
          <div className="flex items-center bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-white/20 p-3">
            {/* Image Upload Button */}
            <button
              onClick={handleImageUpload}
              className="p-2 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
            >
              <ImageIcon className="w-5 h-5" />
            </button>

            {/* Text Input */}
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={getTranslation(language, 'typeMessage')}
              className="flex-1 px-3 py-2 bg-transparent border-none outline-none text-gray-800 placeholder-gray-500"
            />

            {/* Microphone Button */}
            <button
              onClick={toggleRecording}
              className={`p-2 rounded-lg transition-colors ${
                isRecording
                  ? 'text-red-600 bg-red-50 animate-pulse'
                  : 'text-gray-500 hover:text-blue-600 hover:bg-blue-50'
              }`}
            >
              <Mic className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Send Button */}
        <button
          onClick={handleSendMessage}
          disabled={!inputText.trim()}
          className="p-3 bg-gradient-to-br from-green-600 to-green-500 text-white rounded-2xl shadow-lg hover:from-green-700 hover:to-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105"
        >
          <Send className="w-5 h-5" />
        </button>

        {/* Hidden File Input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="hidden"
        />
      </div>

      {/* Chat History Modal */}
      <ChatHistoryModal 
        isOpen={showChatHistory}
        onClose={() => setShowChatHistory(false)}
      />
    </div>
  );
};

export default ChatInterface;