/**
 * Direct test runner using Node.js test runner + tsx.
 * Bypasses esbuild's config file scanning issue.
 */
const { version } = require("esbuild");
console.log("esbuild version:", version);

// Quick test to verify imports work
try {
  const path = require("path");
  const fs = require("fs");
  
  // Verify the config file exists
  const configPath = path.resolve(__dirname, "vitest.config.ts");
  console.log("Config file exists:", fs.existsSync(configPath));
  
  // Verify our test files exist
  const testDir = path.resolve(__dirname, "src/__tests__");
  console.log("Test directory exists:", fs.existsSync(testDir));
  
  if (fs.existsSync(testDir)) {
    const files = fs.readdirSync(testDir, { recursive: true });
    console.log("Test files:", files.filter(f => f.endsWith(".ts") || f.endsWith(".tsx")));
  }
} catch (e) {
  console.error("Error:", e.message);
}
