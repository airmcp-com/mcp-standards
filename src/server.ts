/**
 * Simple Personal Memory MCP Server
 * Provides semantic memory for Claude with high auto-discovery rates
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { EmbeddingService } from './embeddings.js';
import { MemoryStore } from './memory-store.js';
import {
  RememberInput,
  RememberOutput,
  RecallInput,
  RecallOutput,
  ListMemoriesInput,
  ListMemoriesOutput,
} from './types.js';

/**
 * Create and configure the MCP server
 */
export async function createServer(): Promise<Server> {
  // Initialize services
  const embeddingService = new EmbeddingService();
  const memoryStore = new MemoryStore(embeddingService);

  // Initialize memory store
  await memoryStore.init();

  // Create MCP server
  const server = new Server(
    {
      name: 'mcp-standards',
      version: '1.0.0',
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  // Register tool handlers
  server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: [
      {
        name: 'remember',
        description: `Store user preferences, corrections, and workflow rules in semantic memory. Use when user explicitly shares preferences or corrects your suggestions.

**Trigger phrases**: 'remember', 'I prefer', 'always use', 'never use', 'my workflow', 'instead of', 'not X, use Y', 'actually use X'.

**Examples**: 'Remember: use uv not pip', 'I prefer conventional commits', 'Always create feature branches', 'Never commit to main directly'.

**Categories**: python (pip/uv/poetry/conda), git (commit/branch/merge), docker (compose/build), general (any other preferences).`,
        inputSchema: {
          type: 'object',
          properties: {
            content: {
              type: 'string',
              description: 'The preference text to remember',
            },
            category: {
              type: 'string',
              enum: ['python', 'git', 'docker', 'general'],
              description: 'Domain classification',
              default: 'general',
            },
            importance: {
              type: 'number',
              description: 'Priority score from 1-10',
              minimum: 1,
              maximum: 10,
              default: 5,
            },
          },
          required: ['content'],
        },
      },
      {
        name: 'recall',
        description: `Search user's stored preferences using semantic search.

**IMPORTANT: Use this BEFORE making any tool/command recommendations.**

Check if user has preferences for: Python package managers (pip/uv/poetry/conda), Git workflows (commit styles, branch naming, merge vs rebase), Docker usage (compose/CLI), build tools (npm/yarn/pnpm), testing frameworks.

**Always use when**: suggesting commands, recommending tools, before running npm/pip/git commands, when user asks 'how do I...' questions.

**Examples**: 'python package manager', 'git commit style', 'preferred testing framework', 'docker workflow'.`,
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Search query for preferences',
            },
            category: {
              type: 'string',
              enum: ['python', 'git', 'docker', 'general'],
              description: 'Optional filter by domain',
            },
            limit: {
              type: 'number',
              description: 'Maximum results to return',
              minimum: 1,
              maximum: 20,
              default: 5,
            },
          },
          required: ['query'],
        },
      },
      {
        name: 'list_memories',
        description: `List all stored preferences with optional filtering and pagination.

Use when user wants to see what preferences are stored, review their settings, or manage their memory.

**Examples**: 'show my preferences', 'list all memories', 'what do you remember about git?'`,
        inputSchema: {
          type: 'object',
          properties: {
            category: {
              type: 'string',
              enum: ['python', 'git', 'docker', 'general'],
              description: 'Optional filter by domain',
            },
            limit: {
              type: 'number',
              description: 'Number of results per page',
              minimum: 1,
              maximum: 50,
              default: 10,
            },
            offset: {
              type: 'number',
              description: 'Pagination offset',
              minimum: 0,
              default: 0,
            },
          },
        },
      },
    ],
  }));

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    try {
      switch (name) {
        case 'remember': {
          const input = args as unknown as RememberInput;
          const memory = await memoryStore.store(
            input.content,
            input.category || 'general',
            input.importance || 5
          );

          const output: RememberOutput = {
            id: memory.id,
            message: `Stored preference: "${memory.content}"`,
            content: memory.content,
            category: memory.category,
            importance: memory.importance,
          };

          return {
            content: [{ type: 'text', text: JSON.stringify(output, null, 2) }],
          };
        }

        case 'recall': {
          const input = args as unknown as RecallInput;
          const results = await memoryStore.search(input.query, {
            category: input.category,
            limit: input.limit || 5,
            minScore: 0.3, // Minimum similarity threshold
          });

          const output: RecallOutput = {
            results: results.map((r) => ({
              content: r.memory.content,
              category: r.memory.category,
              importance: r.memory.importance,
              score: r.score,
              timestamp: r.memory.timestamp,
            })),
            count: results.length,
          };

          return {
            content: [{ type: 'text', text: JSON.stringify(output, null, 2) }],
          };
        }

        case 'list_memories': {
          const input = args as unknown as ListMemoriesInput;
          const { memories, total } = await memoryStore.list({
            category: input.category,
            limit: input.limit || 10,
            offset: input.offset || 0,
          });

          const output: ListMemoriesOutput = {
            memories: memories.map((m) => ({
              id: m.id,
              content: m.content,
              category: m.category,
              importance: m.importance,
              timestamp: m.timestamp,
            })),
            total,
            limit: input.limit || 10,
            offset: input.offset || 0,
          };

          return {
            content: [{ type: 'text', text: JSON.stringify(output, null, 2) }],
          };
        }

        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      return {
        content: [{ type: 'text', text: `Error: ${errorMessage}` }],
        isError: true,
      };
    }
  });

  return server;
}

/**
 * Run the MCP server
 */
export async function runServer(): Promise<void> {
  const server = await createServer();
  const transport = new StdioServerTransport();

  await server.connect(transport);

  console.error('Simple Personal Memory MCP Server running on stdio');
}
