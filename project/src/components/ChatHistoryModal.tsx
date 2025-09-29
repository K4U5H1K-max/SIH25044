import React from 'react';
import { X, MessageCircle, Clock, Trash2 } from 'lucide-react';
import { useAppContext } from '../contexts/AppContext';
import { ChatHistory } from '../types';

interface ChatHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const ChatHistoryModal: React.FC<ChatHistoryModalProps> = ({ isOpen, onClose }) => {
  const { chatHistories, setChatHistories, setMessages, language } = useAppContext();

  if (!isOpen) return null;

  const loadChatHistory = (history: ChatHistory) => {
    setMessages(history.messages);
    onClose();
  };

  const deleteChatHistory = (historyId: string) => {
    setChatHistories(chatHistories.filter(h => h.id !== historyId));
  };

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat(language === 'hi' ? 'hi-IN' : 'en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm" 
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative bg-white/95 backdrop-blur-md rounded-2xl shadow-2xl border border-white/20 w-full max-w-2xl max-h-[80vh] m-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200/50">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <MessageCircle className="w-6 h-6 text-green-600" />
            </div>
            <h2 className="text-xl font-semibold text-gray-800">Chat History</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl hover:bg-gray-100/80 transition-colors"
          >
            <X className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-96">
          {chatHistories.length === 0 ? (
            <div className="text-center py-12">
              <MessageCircle className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-gray-500 text-lg">No chat history yet</p>
              <p className="text-gray-400 text-sm mt-2">Start a conversation to see your chat history here</p>
            </div>
          ) : (
            <div className="space-y-3">
              {chatHistories.map((history) => (
                <div
                  key={history.id}
                  className="bg-white/60 rounded-xl p-4 border border-white/40 hover:shadow-lg transition-all duration-200 group"
                >
                  <div className="flex items-start justify-between">
                    <div 
                      className="flex-1 cursor-pointer"
                      onClick={() => loadChatHistory(history)}
                    >
                      <h3 className="font-medium text-gray-800 group-hover:text-green-600 transition-colors">
                        {history.title}
                      </h3>
                      <div className="flex items-center space-x-2 mt-1">
                        <Clock className="w-4 h-4 text-gray-400" />
                        <span className="text-sm text-gray-500">
                          {formatDate(history.createdAt)}
                        </span>
                        <span className="text-sm text-gray-400">
                          • {history.messages.length} messages
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                        {history.messages[0]?.content || 'No messages'}
                      </p>
                    </div>
                    <button
                      onClick={() => deleteChatHistory(history.id)}
                      className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatHistoryModal;