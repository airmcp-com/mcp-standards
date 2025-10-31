import { defineConfig } from 'tsup';

export default defineConfig({
  entry: {
    index: 'src/index.ts',      // MCP server entry point
    lib: 'src/lib.ts',           // Library entry point
  },
  format: ['esm'],
  dts: true,                     // Generate .d.ts files for library
  sourcemap: true,
  clean: true,
  splitting: false,              // Disabled for simpler library imports
  treeshake: true,
  minify: false,
  target: 'node18',
  outDir: 'dist',
  shims: true,
  bundle: true
});
