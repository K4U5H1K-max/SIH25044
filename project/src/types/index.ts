export type Language = 'en' | 'hi' | 'ta' | 'te' | 'kn' | 'od';

export interface User {
  id: string;
  username: string;
  email: string;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  imageUrl?: string;
}

export interface DashboardData {
  yieldPrediction: number;
  successRate: number;
  waterRequirement: number;
  irrigationPercentage: number;
  fertilizerRecommendation: string;
  pestManagementCost: number;
}

export interface ChatHistory {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: Date;
}