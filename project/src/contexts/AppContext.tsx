import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { Language, User, ChatMessage, DashboardData, ChatHistory } from '../types';
import { getTranslation } from '../utils/translations';

interface AppContextType {
  // Auth
  user: User | null;
  setUser: (user: User | null) => void;
  
  // Language
  language: Language;
  setLanguage: (language: Language) => void;
  
  // Chat
  messages: ChatMessage[];
  setMessages: (messages: ChatMessage[]) => void;
  addMessage: (message: ChatMessage) => void;
  
  // Dashboard
  dashboardData: DashboardData;
  setDashboardData: (data: DashboardData) => void;
  
  // Chat History
  chatHistories: ChatHistory[];
  setChatHistories: (histories: ChatHistory[]) => void;
  
  // UI State
  isSoundEnabled: boolean;
  setIsSoundEnabled: (enabled: boolean) => void;
  isMenuOpen: boolean;
  setIsMenuOpen: (open: boolean) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }
  return context;
};

interface AppProviderProps {
  children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [language, setLanguage] = useState<Language>('en');
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  // Initialize welcome message based on language
  useEffect(() => {
    const welcomeMessage: ChatMessage = {
      id: 'welcome-1',
      type: 'ai',
      content: getTranslation(language, 'botWelcome'),
      timestamp: new Date()
    };
    setMessages([welcomeMessage]);
  }, [language]);
  const [isSoundEnabled, setIsSoundEnabled] = useState(true);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [chatHistories, setChatHistories] = useState<ChatHistory[]>([]);
  
  const [dashboardData, setDashboardData] = useState<DashboardData>({
    yieldPrediction: 0,
    successRate: 0,
    waterRequirement: 0,
    irrigationPercentage: 0,
    fertilizerRecommendation: 'Chat with AI to get recommendations',
    pestManagementCost: 0
  });

  const addMessage = (message: ChatMessage) => {
    setMessages(prev => {
      const newMessages = [...prev, message];

      // If first user message, initialize a chat history entry
      if (message.type === 'user') {
        const chatTitle = message.content.length > 30
          ? message.content.substring(0, 30) + '...'
          : message.content;

        setChatHistories(prevHistories => {
          if (prevHistories.length > 0) return prevHistories; // keep existing behavior
          const newHistory: ChatHistory = {
            id: Date.now().toString(),
            title: chatTitle || 'New chat',
            messages: [message],
            createdAt: new Date()
          };
          return [newHistory, ...prevHistories];
        });
      }

      // Auto-save to chat history when AI responds (pair with previous user message)
      if (message.type === 'ai' && prev.length > 0) {
        const userMessage = prev[prev.length - 1];
        const chatTitle = userMessage.content.length > 30
          ? userMessage.content.substring(0, 30) + '...'
          : userMessage.content;

        setChatHistories(prevHistories => {
          if (prevHistories.length === 0) return prevHistories; // nothing to update
          const updated = [...prevHistories];
          updated[0] = {
            ...updated[0],
            title: updated[0].title || chatTitle,
            messages: [...updated[0].messages, message]
          };
          return updated;
        });
      }

      return newMessages;
    });
  };

  return (
    <AppContext.Provider value={{
      user,
      setUser,
      language,
      setLanguage,
      messages,
      setMessages,
      addMessage,
      dashboardData,
      setDashboardData,
      chatHistories,
      setChatHistories,
      isSoundEnabled,
      setIsSoundEnabled,
      isMenuOpen,
      setIsMenuOpen
    }}>
      {children}
    </AppContext.Provider>
  );
};