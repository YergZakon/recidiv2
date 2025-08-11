/**
 * Simple cache service for API responses and computed data
 * Helps reduce redundant API calls and improve performance
 */

interface CacheItem<T> {
  data: T;
  timestamp: number;
  expiresAt: number;
}

class CacheService {
  private static instance: CacheService;
  private cache: Map<string, CacheItem<any>> = new Map();
  private defaultTTL = 5 * 60 * 1000; // 5 minutes default TTL

  static getInstance(): CacheService {
    if (!CacheService.instance) {
      CacheService.instance = new CacheService();
    }
    return CacheService.instance;
  }

  private constructor() {
    // Clean expired items every 5 minutes
    setInterval(() => {
      this.cleanExpired();
    }, 5 * 60 * 1000);
  }

  /**
   * Store data in cache with optional TTL
   */
  set<T>(key: string, data: T, ttl?: number): void {
    const now = Date.now();
    const expiration = now + (ttl || this.defaultTTL);
    
    this.cache.set(key, {
      data,
      timestamp: now,
      expiresAt: expiration
    });
  }

  /**
   * Retrieve data from cache
   */
  get<T>(key: string): T | null {
    const item = this.cache.get(key);
    
    if (!item) {
      return null;
    }

    // Check if expired
    if (Date.now() > item.expiresAt) {
      this.cache.delete(key);
      return null;
    }

    return item.data as T;
  }

  /**
   * Check if key exists and is not expired
   */
  has(key: string): boolean {
    const item = this.cache.get(key);
    
    if (!item) {
      return false;
    }

    if (Date.now() > item.expiresAt) {
      this.cache.delete(key);
      return false;
    }

    return true;
  }

  /**
   * Remove specific key from cache
   */
  delete(key: string): void {
    this.cache.delete(key);
  }

  /**
   * Clear all cache
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * Get or set with async factory function
   */
  async getOrSet<T>(
    key: string, 
    factory: () => Promise<T>, 
    ttl?: number
  ): Promise<T> {
    const cached = this.get<T>(key);
    
    if (cached !== null) {
      return cached;
    }

    const data = await factory();
    this.set(key, data, ttl);
    return data;
  }

  /**
   * Clean expired items
   */
  private cleanExpired(): void {
    const now = Date.now();
    
    this.cache.forEach((item, key) => {
      if (now > item.expiresAt) {
        this.cache.delete(key);
      }
    });
  }

  /**
   * Get cache statistics
   */
  getStats(): { size: number; keys: string[] } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys())
    };
  }

  /**
   * Cache keys for common operations
   */
  static KEYS = {
    PERSON_SEARCH: (iin: string) => `person:search:${iin}`,
    PERSON_LIST: (params: string) => `person:list:${params}`,
    RISK_CALCULATION: (iin: string) => `risk:calc:${iin}`,
    REGION_STATS: () => 'region:stats',
    FORECASTING_DATA: (timeWindow: string) => `forecast:${timeWindow}`,
    TIMELINE_DATA: (timeRange: string) => `timeline:${timeRange}`
  } as const;
}

export default CacheService;