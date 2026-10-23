import axios from 'axios';

// Empty baseURL = same origin, so requests go through the Vite dev proxy
// (see vite.config.js) and never hit CORS. Set VITE_API_URL to point at a
// deployed backend instead.
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

const SESSION_KEY = 'taskflow-session';

// Session = { token, user: { id, name, email } }, persisted across reloads
export const sessionStore = {
  load() {
    try {
      const raw = localStorage.getItem(SESSION_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },
  save(session) {
    try {
      localStorage.setItem(SESSION_KEY, JSON.stringify(session));
    } catch {
      // Storage unavailable; the session still works until the page reloads
    }
  },
  clear() {
    try {
      localStorage.removeItem(SESSION_KEY);
    } catch {
      // ignore
    }
  }
};

let authToken = sessionStore.load()?.token || null;
let onUnauthorized = null;

export const setAuthToken = (token) => {
  authToken = token;
};

// Called when the backend rejects the session (expired or invalid token)
export const setUnauthorizedHandler = (handler) => {
  onUnauthorized = handler;
};

// Turn axios errors into one readable message for the UI
export const getErrorMessage = (error) => {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (error.code === 'ECONNABORTED') {
    return 'The server took too long to respond. Please try again.';
  }
  if (!error.response) {
    return 'Cannot reach the server. Make sure the backend is running.';
  }
  return 'Something went wrong. Please try again.';
};

apiClient.interceptors.request.use((config) => {
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const isAuthRoute = error.config?.url?.startsWith('/api/auth/sign');
    if (error.response?.status === 401 && !isAuthRoute && onUnauthorized) {
      onUnauthorized(getErrorMessage(error));
    }
    return Promise.reject(error);
  }
);

// Specific API functions
const api = {
  // Auth
  signUp: async (name, email, password) => {
    const response = await apiClient.post('/api/auth/signup', { name, email, password });
    return response.data;
  },

  signIn: async (email, password) => {
    const response = await apiClient.post('/api/auth/signin', { email, password });
    return response.data;
  },

  me: async () => {
    const response = await apiClient.get('/api/auth/me');
    return response.data;
  },

  // Send a message to the chat endpoint
  sendMessage: async (userId, message) => {
    const response = await apiClient.post(`/api/${userId}/chat`, {
      message: message,
      timestamp: new Date().toISOString()
    });
    return response.data;
  },

  // Health check endpoint
  healthCheck: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // List endpoints: each list is { id, title, task_count, completed_count, tasks: [...] }
  getLists: async (userId) => {
    const response = await apiClient.get(`/api/${userId}/lists`);
    return response.data;
  },

  createList: async (userId, title) => {
    const response = await apiClient.post(`/api/${userId}/lists`, { title });
    return response.data;
  },

  renameList: async (userId, listId, title) => {
    const response = await apiClient.patch(`/api/${userId}/lists/${listId}`, { title });
    return response.data;
  },

  deleteList: async (userId, listId) => {
    const response = await apiClient.delete(`/api/${userId}/lists/${listId}`);
    return response.data;
  },

  // Task endpoints
  getTasks: async (userId) => {
    const response = await apiClient.get(`/api/${userId}/tasks`);
    return response.data;
  },

  // parentId makes the new task a sub-item of that task
  addTask: async (userId, description, listId, parentId) => {
    const response = await apiClient.post(`/api/${userId}/tasks`, { description, list_id: listId, parent_id: parentId });
    return response.data;
  },

  // changes: { description?, status?: 'completed' | 'incomplete' }
  updateTask: async (userId, taskId, changes) => {
    const response = await apiClient.patch(`/api/${userId}/tasks/${taskId}`, changes);
    return response.data;
  },

  deleteTask: async (userId, taskId) => {
    const response = await apiClient.delete(`/api/${userId}/tasks/${taskId}`);
    return response.data;
  }
};

export default api;
