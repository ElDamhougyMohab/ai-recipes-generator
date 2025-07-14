import axios from 'axios';

// Use relative URLs in production, localhost in development
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '' // Use relative URLs in production (same domain as frontend)
  : process.env.REACT_APP_API_URL || 'http://localhost:8000';

console.log('🔧 API Configuration:');
console.log('  NODE_ENV:', process.env.NODE_ENV);
console.log('  REACT_APP_API_URL:', process.env.REACT_APP_API_URL);
console.log('  Final API_BASE_URL:', API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Retry configuration
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

// Retry helper function
const retryRequest = async (requestFn, retries = MAX_RETRIES) => {
  try {
    return await requestFn();
  } catch (error) {
    if (retries > 0 && (error.code === 'ECONNABORTED' || error.response?.status >= 500)) {
      console.log(`Retrying request in ${RETRY_DELAY}ms... (${MAX_RETRIES - retries + 1}/${MAX_RETRIES})`);
      await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
      return retryRequest(requestFn, retries - 1);
    }
    throw error;
  }
}

// Connection health check
const checkBackendHealth = async () => {
  try {
    console.log('Health check - API_BASE_URL:', API_BASE_URL);
    const healthUrl = API_BASE_URL ? `${API_BASE_URL}/health` : '/health';
    console.log('Health check - URL:', healthUrl);
    
    const response = await api.get('/health', { timeout: 5000 });
    console.log('Health check - Response:', response.status, response.data);
    return response.status === 200;
  } catch (error) {
    console.warn('Backend health check failed:', error.message);
    console.warn('Error details:', error.response?.status, error.response?.data);
    return false;
  }
};

// Auto-reconnect functionality
const ensureConnection = async () => {
  const isHealthy = await checkBackendHealth();
  if (!isHealthy) {
    throw new Error('Backend is not available. Please check your connection.');
  }
};

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    
    // Enhanced error handling with user-friendly messages
    if (error.response) {
      const { status, data } = error.response;
      let userMessage = 'An error occurred. Please try again.';
      
      switch (status) {
        case 400:
          userMessage = data.detail || 'Invalid request. Please check your input.';
          break;
        case 422:
          // Handle validation errors with detailed field information
          if (data.detail && Array.isArray(data.detail)) {
            const validationErrors = data.detail.map(err => {
              const field = err.loc ? err.loc.slice(-1)[0] : 'unknown field';
              return `${field}: ${err.msg}`;
            });
            userMessage = `Validation errors: ${validationErrors.join('; ')}`;
          } else {
            userMessage = data.detail || 'Invalid data format. Please check your input.';
          }
          break;
        case 500:
          userMessage = 'Server error. Please try again later.';
          break;
        case 503:
          userMessage = 'Service temporarily unavailable. Please try again later.';
          break;
        default:
          userMessage = data.detail || `Error ${status}: ${error.message}`;
      }
      
      error.userMessage = userMessage;
    } else if (error.request) {
      error.userMessage = 'Network error. Please check your connection and try again.';
    } else {
      error.userMessage = 'An unexpected error occurred. Please try again.';
    }
    
    return Promise.reject(error);
  }
);

export const recipeAPI = {
  // Generate recipes using AI
  generateRecipes: async (requestData) => {
    console.log('📡 API: Starting recipe generation request');
    return retryRequest(async () => {
      console.log('📡 API: Sending POST to /api/recipes/generate');
      const response = await api.post('/api/recipes/generate', requestData);
      console.log('📡 API: Received response:', response.status, response.data);
      return response.data;
    });
  },

  // Get recipes with pagination
  getRecipes: async (page = 1, pageSize = 10) => {
    return retryRequest(async () => {
      const response = await api.get('/api/recipes', {
        params: { page, page_size: pageSize }
      });
      return response.data; // Returns PaginatedResponse with items, total, page, pages, etc.
    });
  },

  // Search recipes with pagination
  searchRecipes: async (query = '', page = 1, pageSize = 10, filters = {}) => {
    return retryRequest(async () => {
      const params = { 
        page, 
        page_size: pageSize,
        ...(query && { q: query }),
        ...filters // difficulty, min_rating, max_prep_time, max_cook_time
      };
      const response = await api.get('/api/recipes/search', { params });
      return response.data; // Returns PaginatedResponse
    });
  },

  // Get specific recipe
  getRecipe: async (recipeId) => {
    const response = await api.get(`/api/recipes/${recipeId}`);
    return response.data;
  },

  // Create new recipe manually
  createRecipe: async (recipeData) => {
    return retryRequest(async () => {
      const cleanedData = cleanRecipeData(recipeData);
      console.log('Sending recipe data to API:', cleanedData); // Debug log
      const response = await api.post('/api/recipes', cleanedData);
      return response.data;
    });
  },

  // Delete recipe
  deleteRecipe: async (recipeId) => {
    await api.delete(`/api/recipes/${recipeId}`);
  },

  // Rate recipe
  rateRecipe: async (recipeId, rating) => {
    const response = await api.put(`/api/recipes/${recipeId}/rating`, null, {
      params: { rating }
    });
    return response.data;
  },

  // Get application statistics
  getStats: async () => {
    const response = await api.get('/api/stats');
    return response.data;
  }
};

export const mealPlanAPI = {
  // Create meal plan
  createMealPlan: async (mealPlanData) => {
    return retryRequest(async () => {
      const response = await api.post('/api/meal-plans', mealPlanData);
      return response.data;
    });
  },

  // Get meal plans with pagination
  getMealPlans: async (page = 1, pageSize = 10) => {
    const response = await api.get('/api/meal-plans', {
      params: { page, page_size: pageSize }
    });
    return response.data; // Returns PaginatedMealPlansResponse
  },

  // Get specific meal plan
  getMealPlan: async (mealPlanId) => {
    const response = await api.get(`/api/meal-plans/${mealPlanId}`);
    return response.data;
  },

  // Delete meal plan
  deleteMealPlan: async (mealPlanId) => {
    await api.delete(`/api/meal-plans/${mealPlanId}`);
  }
};

// Helper function to clean and validate recipe data before sending to API
const cleanRecipeData = (recipe) => {
  const cleanedRecipe = {
    title: typeof recipe.title === 'string' ? recipe.title.trim() : '',
    description: typeof recipe.description === 'string' ? recipe.description.trim() : null,
    instructions: recipe.instructions || [],
    ingredients: [],
    prep_time: recipe.prep_time || null,
    cook_time: recipe.cook_time || null,
    servings: recipe.servings || null,
    difficulty: (() => {
      const diff = recipe.difficulty || 'Medium';
      // Ensure proper capitalization
      const validDifficulties = ['Easy', 'Medium', 'Hard', 'Expert'];
      const normalized = diff.charAt(0).toUpperCase() + diff.slice(1).toLowerCase();
      return validDifficulties.includes(normalized) ? normalized : 'Medium';
    })()
  };

  // Clean ingredients array
  if (Array.isArray(recipe.ingredients)) {
    cleanedRecipe.ingredients = recipe.ingredients
      .map(ing => {
        // Handle string ingredients (fallback)
        if (typeof ing === 'string') {
          return {
            name: ing.trim(),
            amount: null,
            unit: null,
            notes: null
          };
        }
        // Handle object ingredients (proper format)
        if (ing && typeof ing === 'object') {
          return {
            name: typeof ing.name === 'string' ? ing.name.trim() : '',
            amount: ing.amount || null,
            unit: typeof ing.unit === 'string' ? ing.unit.trim() : null,
            notes: typeof ing.notes === 'string' ? ing.notes.trim() : null
          };
        }
        return null;
      })
      .filter(ing => ing && ing.name && ing.name.length > 0); // Remove invalid ingredients
  }

  // Convert instructions to array if it's a string
  if (typeof cleanedRecipe.instructions === 'string') {
    cleanedRecipe.instructions = cleanedRecipe.instructions
      .split('\n')
      .map(step => step.trim())
      .filter(step => step.length > 0);
  }

  return cleanedRecipe;
};

// Export utilities for use in components
export const apiUtils = {
  checkBackendHealth,
  ensureConnection,
  retryRequest,
  cleanRecipeData
};

export default api;
