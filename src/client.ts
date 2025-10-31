/**
 * Simple client library for using memory store directly (non-MCP)
 * Perfect for Claude Code or any Node.js/TypeScript project
 */

import { EmbeddingService } from './embeddings.js';
import { MemoryStore } from './memory-store.js';
import type { PreferenceCategory, MemoryRecord, SearchResult } from './types.js';

/**
 * Simple memory client for direct usage
 *
 * @example
 * ```typescript
 * import { SimpleMemoryClient } from 'mcp-standards';
 *
 * const memory = new SimpleMemoryClient();
 * await memory.init();
 *
 * // Store a preference
 * await memory.remember("Use uv instead of pip", "python", 8);
 *
 * // Recall preferences
 * const results = await memory.recall("python package manager");
 * console.log(results[0].content);
 * ```
 */
export class SimpleMemoryClient {
  private embeddingService: EmbeddingService;
  private memoryStore: MemoryStore;
  private initialized = false;

  constructor(persistPath?: string) {
    this.embeddingService = new EmbeddingService();
    this.memoryStore = new MemoryStore(this.embeddingService, { persistPath });
  }

  /**
   * Initialize the memory client (must be called before use)
   */
  async init(): Promise<void> {
    if (this.initialized) {
      return;
    }
    await this.memoryStore.init();
    this.initialized = true;
  }

  /**
   * Store a new preference
   *
   * @param content - The preference text to remember
   * @param category - Domain classification (python, git, docker, general)
   * @param importance - Priority score from 1-10 (default: 5)
   * @returns The stored memory record with ID
   *
   * @example
   * ```typescript
   * const memory = await client.remember("Always create feature branches", "git", 8);
   * console.log(`Stored with ID: ${memory.id}`);
   * ```
   */
  async remember(
    content: string,
    category: PreferenceCategory = 'general',
    importance: number = 5
  ): Promise<MemoryRecord> {
    this.ensureInitialized();
    return await this.memoryStore.store(content, category, importance);
  }

  /**
   * Search for preferences using semantic search
   *
   * @param query - Search query
   * @param options - Search options (category filter, limit, min score)
   * @returns Array of matching memories with similarity scores
   *
   * @example
   * ```typescript
   * const results = await client.recall("git workflow", { category: "git", limit: 3 });
   * results.forEach(r => {
   *   console.log(`${r.memory.content} (score: ${r.score.toFixed(2)})`);
   * });
   * ```
   */
  async recall(
    query: string,
    options: {
      category?: PreferenceCategory;
      limit?: number;
      minScore?: number;
    } = {}
  ): Promise<SearchResult[]> {
    this.ensureInitialized();
    return await this.memoryStore.search(query, options);
  }

  /**
   * List all stored memories
   *
   * @param options - Filtering and pagination options
   * @returns Memories array and total count
   *
   * @example
   * ```typescript
   * const { memories, total } = await client.list({ category: "python", limit: 10 });
   * console.log(`Found ${total} Python preferences`);
   * ```
   */
  async list(options: {
    category?: PreferenceCategory;
    limit?: number;
    offset?: number;
  } = {}): Promise<{ memories: MemoryRecord[]; total: number }> {
    this.ensureInitialized();
    return await this.memoryStore.list(options);
  }

  /**
   * Get a specific memory by ID
   *
   * @param id - Memory UUID
   * @returns Memory record or null if not found
   */
  async get(id: string): Promise<MemoryRecord | null> {
    this.ensureInitialized();
    return await this.memoryStore.get(id);
  }

  /**
   * Delete a memory by ID
   *
   * @param id - Memory UUID
   * @returns true if deleted, false if not found
   */
  async delete(id: string): Promise<boolean> {
    this.ensureInitialized();
    return await this.memoryStore.delete(id);
  }

  /**
   * Count memories (optionally by category)
   *
   * @param category - Optional category filter
   * @returns Count of memories
   */
  async count(category?: PreferenceCategory): Promise<number> {
    this.ensureInitialized();
    return await this.memoryStore.count(category);
  }

  /**
   * Clear all memories
   */
  async clear(): Promise<void> {
    this.ensureInitialized();
    return await this.memoryStore.clear();
  }

  private ensureInitialized(): void {
    if (!this.initialized) {
      throw new Error(
        'Memory client not initialized. Call await client.init() first.'
      );
    }
  }
}

/**
 * Quick helper function for one-off memory operations
 * Automatically initializes and returns results
 *
 * @example
 * ```typescript
 * import { quickRecall } from 'mcp-standards';
 *
 * const results = await quickRecall("python package manager");
 * console.log(results[0]?.memory.content);
 * ```
 */
export async function quickRecall(
  query: string,
  options?: { category?: PreferenceCategory; limit?: number }
): Promise<SearchResult[]> {
  const client = new SimpleMemoryClient();
  await client.init();
  return await client.recall(query, options);
}

/**
 * Quick helper to store a preference
 *
 * @example
 * ```typescript
 * import { quickRemember } from 'mcp-standards';
 *
 * await quickRemember("Use conventional commits", "git", 8);
 * ```
 */
export async function quickRemember(
  content: string,
  category: PreferenceCategory = 'general',
  importance: number = 5
): Promise<MemoryRecord> {
  const client = new SimpleMemoryClient();
  await client.init();
  return await client.remember(content, category, importance);
}
