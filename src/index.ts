/**
 * Simple Personal Memory MCP Server
 * Entry point for the MCP server
 */

import { runServer } from './server.js';

// Handle errors gracefully
process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason) => {
  console.error('Unhandled rejection:', reason);
  process.exit(1);
});

// Run the server
runServer().catch((error) => {
  console.error('Failed to start server:', error);
  process.exit(1);
});
