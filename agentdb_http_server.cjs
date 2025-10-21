#!/usr/bin/env node
/**
 * AgentDB HTTP Server
 *
 * Simple HTTP wrapper around AgentDB for Python integration
 */

const express = require('express');
const { SQLiteVectorDB } = require('agentdb');

const app = express();
app.use(express.json());

// Initialize AgentDB
const dbPath = '.agentdb/v2_patterns.db';
const db = new SQLiteVectorDB(dbPath);

console.log(`🚀 AgentDB HTTP Server starting...`);
console.log(`📁 Database: ${dbPath}`);

// CORS headers for development
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    if (req.method === 'OPTIONS') {
        res.sendStatus(200);
    } else {
        next();
    }
});

// Health check endpoint
app.get('/health', async (req, res) => {
    try {
        const stats = await db.stats();
        res.json({
            status: 'healthy',
            database: dbPath,
            stats: stats
        });
    } catch (error) {
        res.status(500).json({
            status: 'error',
            error: error.message
        });
    }
});

// Insert vector endpoint
app.post('/vectors', async (req, res) => {
    try {
        const { embedding, metadata } = req.body;

        if (!embedding || !Array.isArray(embedding)) {
            return res.status(400).json({
                error: 'embedding must be an array of numbers'
            });
        }

        const result = await db.insert({
            embedding: embedding,
            metadata: metadata || {}
        });

        res.json({
            success: true,
            id: result,
            metadata: metadata
        });
    } catch (error) {
        res.status(500).json({
            error: error.message
        });
    }
});

// Search vectors endpoint
app.post('/search', async (req, res) => {
    try {
        const {
            query_vector,
            top_k = 10,
            similarity_metric = 'cosine',
            threshold = 0.0
        } = req.body;

        if (!query_vector || !Array.isArray(query_vector)) {
            return res.status(400).json({
                error: 'query_vector must be an array of numbers'
            });
        }

        const results = await db.search(
            query_vector,
            top_k,
            similarity_metric,
            threshold
        );

        res.json({
            success: true,
            results: results.map(result => ({
                id: result.id,
                metadata: result.metadata,
                similarity: result.similarity || result.score
            })),
            count: results.length
        });
    } catch (error) {
        res.status(500).json({
            error: error.message
        });
    }
});

// Delete vector endpoint
app.delete('/vectors/:id', async (req, res) => {
    try {
        const { id } = req.params;

        // AgentDB delete functionality (if available)
        try {
            await db.delete(id);
            res.json({
                success: true,
                message: `Vector ${id} deleted`
            });
        } catch (e) {
            res.status(404).json({
                error: `Vector ${id} not found or delete not supported`
            });
        }
    } catch (error) {
        res.status(500).json({
            error: error.message
        });
    }
});

// Get database stats
app.get('/stats', async (req, res) => {
    try {
        const stats = await db.stats();
        res.json({
            success: true,
            stats: stats
        });
    } catch (error) {
        res.status(500).json({
            error: error.message
        });
    }
});

// Query by metadata (if supported)
app.post('/query', async (req, res) => {
    try {
        const { metadata_filter, limit = 100 } = req.body;

        // This is a simplified implementation
        // Real implementation would depend on AgentDB's query capabilities
        res.json({
            success: true,
            message: 'Metadata querying not yet implemented',
            filter: metadata_filter
        });
    } catch (error) {
        res.status(500).json({
            error: error.message
        });
    }
});

// Error handling middleware
app.use((error, req, res, next) => {
    console.error('❌ Server error:', error);
    res.status(500).json({
        error: 'Internal server error',
        message: error.message
    });
});

// Start server
const PORT = process.env.PORT || 3002;
app.listen(PORT, () => {
    console.log(`✅ AgentDB HTTP Server running on port ${PORT}`);
    console.log(`📊 Health check: http://localhost:${PORT}/health`);
    console.log(`🔍 Search endpoint: POST http://localhost:${PORT}/search`);
    console.log(`📥 Insert endpoint: POST http://localhost:${PORT}/vectors`);
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down AgentDB HTTP Server...');
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n🛑 Shutting down AgentDB HTTP Server...');
    process.exit(0);
});