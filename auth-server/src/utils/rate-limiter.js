/**
 * Redis-based rate limiter for auth server endpoints.
 * Provides persistent rate limiting across server restarts.
 */

import { createClient } from 'redis';
import dotenv from 'dotenv';

dotenv.config();

class RedisRateLimiter {
  constructor() {
    this.client = null;
    this.isEnabled = !!process.env.REDIS_URL;
    this.windowMs = parseInt(process.env.RATE_LIMIT_WINDOW_MS || '60000'); // 1 minute default
    this.maxRequests = parseInt(process.env.RATE_LIMIT_MAX || '10'); // 10 requests default
  }

  async initialize() {
    if (!this.isEnabled) {
      console.log('Redis not configured, using in-memory fallback');
      this.useInMemory = true;
      this.rateLimitMap = new Map();
      return;
    }

    try {
      this.client = createClient({
        url: process.env.REDIS_URL,
      });

      this.client.on('error', (err) => {
        console.error('Redis Client Error:', err);
        // Fallback to in-memory if Redis fails
        this.useInMemory = true;
        this.rateLimitMap = new Map();
      });

      await this.client.connect();
      console.log('Connected to Redis for rate limiting');
    } catch (error) {
      console.error('Failed to connect to Redis, falling back to in-memory:', error);
      this.useInMemory = true;
      this.rateLimitMap = new Map();
    }
  }

  async checkLimit(key, max = this.maxRequests, windowMs = this.windowMs) {
    if (this.useInMemory) {
      return this._checkInMemoryLimit(key, max, windowMs);
    }

    const now = Date.now();
    const windowStart = now - windowMs;
    const currentKey = `rate_limit:${key}`;

    try {
      // Use Redis ZSET to track requests with timestamps
      // Remove old entries outside the window
      await this.client.zRemRangeByScore(currentKey, 0, windowStart);

      // Count current entries in window
      const count = await this.client.zCard(currentKey);

      if (count >= max) {
        // Rate limit exceeded
        const oldestEntry = await this.client.zRange(currentKey, 0, 0, {
          WITHSCORES: true
        });

        if (oldestEntry && oldestEntry.length > 1) {
          const resetTime = parseInt(oldestEntry[1]) + windowMs;
          return {
            allowed: false,
            resetTime: new Date(resetTime).toISOString(),
            retryAfter: Math.ceil((resetTime - now) / 1000)
          };
        }
      }

      // Add current request
      await this.client.zAdd(currentKey, { score: now, value: now.toString() });

      // Set expiration to avoid memory leaks
      await this.client.expire(currentKey, Math.ceil(windowMs / 1000) + 1);

      return {
        allowed: true,
        resetTime: new Date(now + windowMs).toISOString(),
        remaining: max - count - 1
      };
    } catch (error) {
      console.error('Redis rate limit error, falling back to allow:', error);
      return { allowed: true, fallback: true };
    }
  }

  async _checkInMemoryLimit(key, max = this.maxRequests, windowMs = this.windowMs) {
    const now = Date.now();
    const entry = this.rateLimitMap.get(key);

    if (!entry || now - entry.windowStart > windowMs) {
      this.rateLimitMap.set(key, { windowStart: now, count: 1 });
      return {
        allowed: true,
        resetTime: new Date(now + windowMs).toISOString(),
        remaining: max - 1
      };
    }

    if (entry.count >= max) {
      const resetTime = entry.windowStart + windowMs;
      return {
        allowed: false,
        resetTime: new Date(resetTime).toISOString(),
        retryAfter: Math.ceil((resetTime - now) / 1000)
      };
    }

    entry.count++;
    return {
      allowed: true,
      resetTime: new Date(now + windowMs).toISOString(),
      remaining: max - entry.count
    };
  }

  async healthCheck() {
    if (this.useInMemory) {
      return { status: 'healthy', method: 'in-memory' };
    }

    if (!this.client) {
      return { status: 'unhealthy', error: 'No client initialized' };
    }

    try {
      await this.client.ping();
      return { status: 'healthy', method: 'redis' };
    } catch (error) {
      return { status: 'unhealthy', error: error.message };
    }
  }
}

// Global instance
const rateLimiter = new RedisRateLimiter();

export default rateLimiter;