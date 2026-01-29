// frontend/src/services/api.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatAPI = {
  sendMessage: async (message, conversationId = null, conversationHistory = []) => {
    try {
      console.log('Sending to API:', {
        message,
        conversationId,
        historyLength: conversationHistory.length
      });

      const response = await api.post('/chat', {
        message,
        conversation_id: conversationId,
        conversation_history: conversationHistory,
      });

      console.log('Received from API:', response.data);
      return response.data;
    } catch (error) {
      console.error('Chat API error:', error);
      throw error;
    }
  },

  // NEW: Get list of available policies
  getPolicies: async () => {
    try {
      const response = await api.get('/policies');
      return response.data;
    } catch (error) {
      console.error('Get policies error:', error);
      throw error;
    }
  },

  // NEW: Get suggestions for a specific policy
  getPolicySuggestions: async (filename) => {
    try {
      const response = await api.get('/policies/suggestions', {
        params: { filename }
      });
      return response.data;
    } catch (error) {
      console.error('Get suggestions error:', error);
      throw error;
    }
  },

  healthCheck: async () => {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check error:', error);
      throw error;
    }
  },
};

export default chatAPI;