/**
 * Memory store using simple in-memory vector database
 * TODO: Replace with AgentDB when integration is ready
 */

import { randomUUID } from 'crypto';
import { writeFile, readFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import { dirname } from 'path';
import { homedir } from 'os';
import { join } from 'path';
import { MemoryRecord, SearchResult, MemoryStoreConfig, PreferenceCategory } from './types.js';
import { EmbeddingService } from './embeddings.js';

const DEFAULT_PERSIST_PATH = join(homedir(), '.mcp-memory', 'memories.json');

/**
 * Simple in-memory vector store with persistence
 * Uses cosine similarity for semantic search
 */
export class MemoryStore {
  private memories: Map<string, MemoryRecord> = new Map();
  private persistPath: string;
  private embeddingService: EmbeddingService;
  private initPromise: Promise<void> | null = null;

  constructor(
    embeddingService: EmbeddingService,
    config: MemoryStoreConfig = {}
  ) {
    this.embeddingService = embeddingService;
    this.persistPath = config.persistPath || DEFAULT_PERSIST_PATH;
    // collectionName not used in simple in-memory store, but kept in config for future AgentDB integration
  }

  /**
   * Initialize the memory store (load persisted data)
   */
  async init(): Promise<void> {
    if (this.initPromise) {
      return this.initPromise;
    }

    this.initPromise = (async () => {
      try {
        // Ensure directory exists
        const dir = dirname(this.persistPath);
        if (!existsSync(dir)) {
          await mkdir(dir, { recursive: true });
        }

        // Load persisted memories if they exist
        if (existsSync(this.persistPath)) {
          const data = await readFile(this.persistPath, 'utf-8');
          const memories = JSON.parse(data) as MemoryRecord[];

          for (const memory of memories) {
            this.memories.set(memory.id, memory);
          }

          console.error(`Loaded ${memories.length} memories from ${this.persistPath}`);
        } else {
          console.error('No persisted memories found, starting fresh');
        }
      } catch (error) {
        console.error('Error initializing memory store:', error);
        // Don't throw - start with empty store if load fails
      }
    })();

    return this.initPromise;
  }

  /**
   * Store a new preference in memory
   */
  async store(
    content: string,
    category: PreferenceCategory = 'general',
    importance: number = 5
  ): Promise<MemoryRecord> {
    await this.init();

    // Validate inputs
    if (!content || content.trim().length === 0) {
      throw new Error('Content cannot be empty');
    }

    if (importance < 1 || importance > 10) {
      throw new Error('Importance must be between 1 and 10');
    }

    // Generate embedding
    const embedding = await this.embeddingService.generateEmbedding(content);

    // Create memory record
    const memory: MemoryRecord = {
      id: randomUUID(),
      content: content.trim(),
      category,
      importance,
      timestamp: new Date().toISOString(),
      embedding,
      metadata: {
        source: 'explicit',
      },
    };

    // Store in memory
    this.memories.set(memory.id, memory);

    // Persist to disk
    await this.persist();

    return memory;
  }

  /**
   * Search for similar memories using semantic search
   */
  async search(
    query: string,
    options: {
      category?: PreferenceCategory;
      limit?: number;
      minScore?: number;
    } = {}
  ): Promise<SearchResult[]> {
    await this.init();

    const limit = options.limit || 5;
    const minScore = options.minScore || 0.0;

    // Generate query embedding
    const queryEmbedding = await this.embeddingService.generateEmbedding(query);

    // Calculate similarities for all memories
    const results: SearchResult[] = [];

    for (const memory of this.memories.values()) {
      // Filter by category if specified
      if (options.category && memory.category !== options.category) {
        continue;
      }

      // Calculate cosine similarity
      const score = EmbeddingService.cosineSimilarity(queryEmbedding, memory.embedding);

      // Only include if above minimum score
      if (score >= minScore) {
        results.push({ memory, score });
      }
    }

    // Sort by score (descending) and importance (descending)
    results.sort((a, b) => {
      if (Math.abs(a.score - b.score) > 0.01) {
        return b.score - a.score;
      }
      return b.memory.importance - a.memory.importance;
    });

    // Return top k results
    return results.slice(0, limit);
  }

  /**
   * List all memories with optional filtering
   */
  async list(options: {
    category?: PreferenceCategory;
    limit?: number;
    offset?: number;
  } = {}): Promise<{ memories: MemoryRecord[]; total: number }> {
    await this.init();

    const limit = options.limit || 10;
    const offset = options.offset || 0;

    // Filter by category if specified
    let filtered = Array.from(this.memories.values());

    if (options.category) {
      filtered = filtered.filter((m) => m.category === options.category);
    }

    // Sort by importance (descending) and timestamp (descending)
    filtered.sort((a, b) => {
      if (a.importance !== b.importance) {
        return b.importance - a.importance;
      }
      return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
    });

    const total = filtered.length;
    const memories = filtered.slice(offset, offset + limit);

    return { memories, total };
  }

  /**
   * Get a specific memory by ID
   */
  async get(id: string): Promise<MemoryRecord | null> {
    await this.init();
    return this.memories.get(id) || null;
  }

  /**
   * Delete a memory by ID
   */
  async delete(id: string): Promise<boolean> {
    await this.init();

    const deleted = this.memories.delete(id);

    if (deleted) {
      await this.persist();
    }

    return deleted;
  }

  /**
   * Get total count of memories
   */
  async count(category?: PreferenceCategory): Promise<number> {
    await this.init();

    if (!category) {
      return this.memories.size;
    }

    let count = 0;
    for (const memory of this.memories.values()) {
      if (memory.category === category) {
        count++;
      }
    }

    return count;
  }

  /**
   * Clear all memories
   */
  async clear(): Promise<void> {
    await this.init();
    this.memories.clear();
    await this.persist();
  }

  /**
   * Persist memories to disk
   */
  private async persist(): Promise<void> {
    try {
      const memories = Array.from(this.memories.values());
      await writeFile(this.persistPath, JSON.stringify(memories, null, 2), 'utf-8');
    } catch (error) {
      console.error('Error persisting memories:', error);
      // Don't throw - just log error
    }
  }
}
