/**
 * Main library entry point
 * Exports everything needed for using mcp-standards as a library
 */

// Client API
export { SimpleMemoryClient, quickRecall, quickRemember } from './client.js';

// Core classes (for advanced usage)
export { EmbeddingService } from './embeddings.js';
export { MemoryStore } from './memory-store.js';

// Types
export type {
  PreferenceCategory,
  MemorySource,
  MemoryRecord,
  SearchResult,
  MemoryStoreConfig,
  EmbeddingConfig,
} from './types.js';
