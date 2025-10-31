/**
 * Embedding generation service using transformers.js
 * Generates 384-dimensional embeddings using all-MiniLM-L6-v2 model
 */

import { pipeline } from '@xenova/transformers';
import type { FeatureExtractionPipeline } from '@xenova/transformers';
import { EmbeddingConfig } from './types.js';

const DEFAULT_MODEL = 'Xenova/all-MiniLM-L6-v2';
const DEFAULT_DIMENSIONS = 384;

/**
 * Embedding service for generating semantic vectors
 */
export class EmbeddingService {
  private model: FeatureExtractionPipeline | null = null;
  private readonly modelName: string;
  private readonly dimensions: number;
  private initPromise: Promise<void> | null = null;

  constructor(config: EmbeddingConfig = {}) {
    this.modelName = config.modelName || DEFAULT_MODEL;
    this.dimensions = config.dimensions || DEFAULT_DIMENSIONS;
  }

  /**
   * Initialize the embedding model (lazy loading)
   */
  private async init(): Promise<void> {
    if (this.model) {
      return;
    }

    if (!this.initPromise) {
      this.initPromise = (async () => {
        try {
          console.error(`Loading embedding model: ${this.modelName}...`);
          this.model = await pipeline('feature-extraction', this.modelName);
          console.error('Embedding model loaded successfully');
        } catch (error) {
          console.error('Failed to load embedding model:', error);
          throw new Error(`Failed to initialize embedding model: ${error}`);
        }
      })();
    }

    await this.initPromise;
  }

  /**
   * Generate embedding for a single text
   * @param text - Input text to embed
   * @returns 384-dimensional embedding vector
   */
  async generateEmbedding(text: string): Promise<number[]> {
    if (!text || text.trim().length === 0) {
      throw new Error('Cannot generate embedding for empty text');
    }

    await this.init();

    if (!this.model) {
      throw new Error('Embedding model not initialized');
    }

    try {
      const output = await this.model(text.trim(), {
        pooling: 'mean',
        normalize: true,
      });

      // Extract the embedding array from the tensor
      const embedding = Array.from(output.data as Float32Array);

      // Validate dimensions
      if (embedding.length !== this.dimensions) {
        throw new Error(
          `Unexpected embedding dimensions: got ${embedding.length}, expected ${this.dimensions}`
        );
      }

      return embedding;
    } catch (error) {
      console.error('Error generating embedding:', error);
      throw new Error(`Failed to generate embedding: ${error}`);
    }
  }

  /**
   * Generate embeddings for multiple texts in batch
   * @param texts - Array of input texts
   * @returns Array of 384-dimensional embedding vectors
   */
  async generateEmbeddings(texts: string[]): Promise<number[][]> {
    if (texts.length === 0) {
      return [];
    }

    // Process in parallel for better performance
    const embeddings = await Promise.all(texts.map((text) => this.generateEmbedding(text)));

    return embeddings;
  }

  /**
   * Calculate cosine similarity between two embedding vectors
   * @param a - First embedding vector
   * @param b - Second embedding vector
   * @returns Similarity score between 0 and 1
   */
  static cosineSimilarity(a: number[], b: number[]): number {
    if (a.length !== b.length) {
      throw new Error('Vectors must have same dimensions');
    }

    let dotProduct = 0;
    let magnitudeA = 0;
    let magnitudeB = 0;

    for (let i = 0; i < a.length; i++) {
      dotProduct += a[i] * b[i];
      magnitudeA += a[i] * a[i];
      magnitudeB += b[i] * b[i];
    }

    magnitudeA = Math.sqrt(magnitudeA);
    magnitudeB = Math.sqrt(magnitudeB);

    if (magnitudeA === 0 || magnitudeB === 0) {
      return 0;
    }

    return dotProduct / (magnitudeA * magnitudeB);
  }

  /**
   * Get expected embedding dimensions
   */
  getDimensions(): number {
    return this.dimensions;
  }

  /**
   * Get model name
   */
  getModelName(): string {
    return this.modelName;
  }
}
