#!/usr/bin/env node
/**
 * Test Direct AgentDB Integration
 *
 * Test the AgentDB library directly to understand its API
 */

const fs = require('fs');
const path = require('path');

async function testAgentDB() {
    console.log('🔍 Testing AgentDB Direct Integration');
    console.log('=' * 50);

    try {
        // Try to import AgentDB
        console.log('📦 Importing AgentDB...');

        // First, let's see what's available
        const agentdbPackagePath = path.join(__dirname, 'node_modules/agentdb');

        if (fs.existsSync(agentdbPackagePath)) {
            const packageJson = JSON.parse(fs.readFileSync(path.join(agentdbPackagePath, 'package.json'), 'utf8'));
            console.log(`   Package: ${packageJson.name}@${packageJson.version}`);
            console.log(`   Main: ${packageJson.main}`);
            console.log(`   Exports:`, packageJson.exports);
        }

        // Try different import methods
        let AgentDB;
        try {
            AgentDB = require('agentdb');
            console.log('✅ AgentDB imported successfully');
            console.log('   Available exports:', Object.keys(AgentDB));
        } catch (e) {
            console.log('❌ Direct import failed:', e.message);

            // Try specific imports
            try {
                const { SQLiteVectorDB } = require('agentdb');
                console.log('✅ SQLiteVectorDB imported successfully');
                AgentDB = { SQLiteVectorDB };
            } catch (e2) {
                console.log('❌ SQLiteVectorDB import failed:', e2.message);
            }
        }

        if (AgentDB && AgentDB.SQLiteVectorDB) {
            console.log('\n🧪 Testing SQLiteVectorDB...');

            // Test database connection
            const dbPath = '.agentdb/v2_patterns.db';
            console.log(`   Connecting to: ${dbPath}`);

            const db = new AgentDB.SQLiteVectorDB(dbPath);
            console.log('✅ Database connected');

            // Test basic operations
            console.log('\n🔬 Testing basic operations...');

            // Create a test vector
            const testVector = Array.from({length: 1536}, (_, i) => Math.random());
            const testMetadata = {
                pattern_type: 'test',
                description: 'test pattern',
                category: 'testing'
            };

            console.log('   Inserting test vector...');
            const insertResult = await db.insert({
                embedding: testVector,
                metadata: testMetadata
            });
            console.log('✅ Test vector inserted:', insertResult);

            // Test search
            console.log('   Testing search...');
            const searchResults = await db.search(testVector, 5, 'cosine', 0.0);
            console.log('✅ Search completed:', searchResults.length, 'results');

            // Test query functionality
            console.log('\n📊 Database statistics...');
            try {
                const stats = await db.stats();
                console.log('   Stats:', stats);
            } catch (e) {
                console.log('   Stats not available:', e.message);
            }

        } else {
            console.log('❌ No usable AgentDB exports found');
        }

    } catch (error) {
        console.log('❌ Error testing AgentDB:', error.message);
        console.log('   Stack:', error.stack);
    }
}

testAgentDB().catch(console.error);