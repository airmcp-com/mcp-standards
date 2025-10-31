/**
 * Core type definitions for Simple Personal Memory MCP Server
 */

/**
 * Category of user preference
 */
export type PreferenceCategory = 'python' | 'git' | 'docker' | 'general';

/**
 * Source of the memory (how it was created)
 */
export type MemorySource = 'user_correction' | 'explicit' | 'implicit';

/**
 * Memory record stored in vector database
 */
export interface MemoryRecord {
  /** Unique identifier (UUID) */
  id: string;

  /** User preference text content */
  content: string;

  /** Category classification */
  category: PreferenceCategory;

  /** Importance/priority score (1-10) */
  importance: number;

  /** Creation timestamp (ISO 8601) */
  timestamp: string;

  /** 384-dimensional embedding vector (all-MiniLM-L6-v2) */
  embedding: number[];

  /** Additional metadata */
  metadata: {
    /** How the memory was created */
    source: MemorySource;

    /** Optional context information */
    context?: string;
  };
}

/**
 * Result from semantic search query
 */
export interface SearchResult {
  /** The memory record */
  memory: MemoryRecord;

  /** Cosine similarity score (0-1) */
  score: number;
}

/**
 * Configuration for memory store
 */
export interface MemoryStoreConfig {
  /** Path to store database file */
  persistPath?: string;

  /** Name of the collection */
  collectionName?: string;

  /** Embedding model dimensions */
  embeddingDimensions?: number;
}

/**
 * Configuration for embedding service
 */
export interface EmbeddingConfig {
  /** Model name to use */
  modelName?: string;

  /** Expected output dimensions */
  dimensions?: number;
}

/**
 * Tool input schema for 'remember' tool
 */
export interface RememberInput {
  content: string;
  category?: PreferenceCategory;
  importance?: number;
}

/**
 * Tool output schema for 'remember' tool
 */
export interface RememberOutput {
  id: string;
  message: string;
  content: string;
  category: PreferenceCategory;
  importance: number;
}

/**
 * Tool input schema for 'recall' tool
 */
export interface RecallInput {
  query: string;
  category?: PreferenceCategory;
  limit?: number;
}

/**
 * Tool output schema for 'recall' tool
 */
export interface RecallOutput {
  results: Array<{
    content: string;
    category: PreferenceCategory;
    importance: number;
    score: number;
    timestamp: string;
  }>;
  count: number;
}

/**
 * Tool input schema for 'list_memories' tool
 */
export interface ListMemoriesInput {
  category?: PreferenceCategory;
  limit?: number;
  offset?: number;
}

/**
 * Tool output schema for 'list_memories' tool
 */
export interface ListMemoriesOutput {
  memories: Array<{
    id: string;
    content: string;
    category: PreferenceCategory;
    importance: number;
    timestamp: string;
  }>;
  total: number;
  limit: number;
  offset: number;
}
