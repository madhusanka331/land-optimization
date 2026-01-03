import axios from 'axios';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 seconds (optimization can take time)
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    // Handle errors
    const errorMessage = error.response?.data?.detail || error.message || 'An error occurred';
    return Promise.reject(new Error(errorMessage));
  }
);

// API methods
export const optimizationAPI = {
  /**
   * Calculate buildable area from land dimensions
   * @param {Object} landInput - Land input parameters
   * @returns {Promise<Object>} Buildable area calculation results
   */
  calculateBuildableArea: async (landInput) => {
    return apiClient.post('/optimization/calculate-buildable-area', landInput);
  },

  /**
   * Run full optimization and generate floor plan
   * @param {Object} landInput - Land input parameters
   * @param {boolean} saveToDb - Whether to save to database
   * @returns {Promise<Object>} Optimization results with visualization URLs
   */
  runOptimization: async (landInput, saveToDb = false) => {
    return apiClient.post(`/optimization/optimize?save_to_db=${saveToDb}`, { land_input: landInput });
  },

  /**
   * Validate land input parameters
   * @param {Object} landInput - Land input parameters
   * @returns {Promise<Object>} Validation results
   */
  validateLandInput: async (landInput) => {
    return apiClient.post('/optimization/validate', landInput);
  },

  /**
   * Get visualization image URL
   * @param {string} filename - Visualization filename
   * @returns {string} Full URL to visualization
   */
  getVisualizationUrl: (filename) => {
    return `/api/v1/optimization/visualization/${filename}`;
  },

  /**
   * Get optimization history
   * @param {number} limit - Maximum number of records
   * @param {number} projectId - Optional project ID filter
   * @returns {Promise<Array>} List of optimizations
   */
  getHistory: async (limit = 50, projectId = null) => {
    const params = { limit };
    if (projectId) params.project_id = projectId;
    return apiClient.get('/optimization/history', { params });
  },

  /**
   * Get optimization by ID
   * @param {number} id - Optimization ID
   * @returns {Promise<Object>} Optimization details
   */
  getOptimizationById: async (id) => {
    return apiClient.get(`/optimization/history/${id}`);
  },

  /**
   * Get best optimizations
   * @param {number} limit - Maximum number of records
   * @param {number} minFitness - Minimum fitness score
   * @returns {Promise<Array>} List of best optimizations
   */
  getBestOptimizations: async (limit = 20, minFitness = 70.0) => {
    return apiClient.get('/optimization/best', {
      params: { limit, min_fitness: minFitness }
    });
  },

  /**
   * Delete optimization
   * @param {number} id - Optimization ID
   * @returns {Promise<Object>} Success response
   */
  deleteOptimization: async (id) => {
    return apiClient.delete(`/optimization/history/${id}`);
  },

  /**
   * Search optimizations with filters
   * @param {Object} filters - Search filters
   * @returns {Promise<Array>} Filtered optimizations
   */
  searchOptimizations: async (filters = {}) => {
    const params = {};
    if (filters.bedrooms) params.bedrooms = filters.bedrooms;
    if (filters.minArea) params.min_area = filters.minArea;
    if (filters.maxArea) params.max_area = filters.maxArea;
    if (filters.minFitness) params.min_fitness = filters.minFitness;
    if (filters.limit) params.limit = filters.limit;

    return apiClient.get('/optimization/search', { params });
  },
};

export default apiClient;
