import axios, { AxiosResponse } from 'axios';
import CacheService from './cacheService';

/**
 * Enhanced API service with caching and error handling
 */
class ApiService {
  private static instance: ApiService;
  private baseURL = 'http://127.0.0.1:8001';
  private cache: CacheService;

  static getInstance(): ApiService {
    if (!ApiService.instance) {
      ApiService.instance = new ApiService();
    }
    return ApiService.instance;
  }

  private constructor() {
    this.cache = CacheService.getInstance();
    
    // Setup axios interceptors
    axios.interceptors.request.use((config: any) => {
      // Add request timestamp for performance monitoring
      config.metadata = { startTime: Date.now() };
      return config;
    });

    axios.interceptors.response.use(
      (response: any) => {
        // Log performance metrics
        const duration = Date.now() - (response.config.metadata?.startTime || Date.now());
        console.log(`API Call: ${response.config.method?.toUpperCase()} ${response.config.url} - ${duration}ms`);
        return response;
      },
      (error: any) => {
        const duration = Date.now() - (error.config?.metadata?.startTime || Date.now());
        console.error(`API Error: ${error.config?.method?.toUpperCase()} ${error.config?.url} - ${duration}ms`, error.response?.status);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Generic GET with caching
   */
  async get<T>(endpoint: string, cacheKey?: string, ttl?: number): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const key = cacheKey || `get:${endpoint}`;

    return this.cache.getOrSet<T>(
      key,
      async () => {
        const response: AxiosResponse<T> = await axios.get(url);
        return response.data;
      },
      ttl
    );
  }

  /**
   * POST without caching (for mutations)
   */
  async post<T>(endpoint: string, data: any): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const response: AxiosResponse<T> = await axios.post(url, data);
    
    // Invalidate related cache entries
    this.invalidateRelatedCache(endpoint);
    
    return response.data;
  }

  /**
   * Search person by IIN with caching
   */
  async searchByIIN(iin: string): Promise<any> {
    const cacheKey = CacheService.KEYS.PERSON_SEARCH(iin);
    return this.get(`/api/persons/search/${iin}`, cacheKey, 10 * 60 * 1000); // 10 minutes cache
  }

  /**
   * Calculate risk with caching
   */
  async calculateRisk(data: any): Promise<any> {
    // For manual calculations, don't cache since data varies
    return this.post('/api/persons/calculate-risk', data);
  }

  /**
   * Get persons list with caching
   */
  async getPersonsList(params: any): Promise<any> {
    const queryString = new URLSearchParams(params).toString();
    const cacheKey = CacheService.KEYS.PERSON_LIST(queryString);
    return this.get(`/api/persons?${queryString}`, cacheKey, 2 * 60 * 1000); // 2 minutes cache
  }

  /**
   * Get statistics with caching
   */
  async getStatistics(): Promise<any> {
    const cacheKey = 'stats:main';
    return this.get('/api/statistics/summary', cacheKey, 5 * 60 * 1000); // 5 minutes cache
  }

  /**
   * Get forecasting data with caching
   */
  async getForecastingData(timeWindow: string): Promise<any> {
    const cacheKey = CacheService.KEYS.FORECASTING_DATA(timeWindow);
    return this.get(`/api/forecasts?timeWindow=${timeWindow}`, cacheKey, 15 * 60 * 1000); // 15 minutes cache
  }

  /**
   * Get timeline data with caching
   */
  async getTimelineData(timeRange: string): Promise<any> {
    const cacheKey = CacheService.KEYS.TIMELINE_DATA(timeRange);
    return this.get(`/api/timeline?timeRange=${timeRange}`, cacheKey, 15 * 60 * 1000); // 15 minutes cache
  }

  /**
   * Get regional statistics with caching
   */
  async getRegionalStats(): Promise<any> {
    const cacheKey = CacheService.KEYS.REGION_STATS();
    return this.get('/api/regions/stats', cacheKey, 10 * 60 * 1000); // 10 minutes cache
  }

  /**
   * Invalidate cache entries related to an endpoint
   */
  private invalidateRelatedCache(endpoint: string): void {
    const stats = this.cache.getStats();
    
    // Invalidate related keys based on endpoint
    if (endpoint.includes('/persons')) {
      stats.keys.forEach(key => {
        if (key.includes('person:') || key.includes('stats:')) {
          this.cache.delete(key);
        }
      });
    }
  }

  /**
   * Preload commonly used data
   */
  async preloadCommonData(): Promise<void> {
    try {
      // Preload statistics
      await this.getStatistics();
      
      // Preload regional data
      await this.getRegionalStats();
      
      console.log('Common data preloaded successfully');
    } catch (error) {
      console.error('Failed to preload common data:', error);
    }
  }

  /**
   * Clear all API cache
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * Get cache statistics for debugging
   */
  getCacheStats(): any {
    return this.cache.getStats();
  }
}

export default ApiService;