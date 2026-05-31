import { readdirSync, readFileSync, statSync } from "node:fs";
import { extname, join, relative, sep } from "node:path";

const root = process.cwd();
const minLines = Number.parseInt(process.env.DUPLICATION_MIN_LINES ?? "8", 10);
const supportedExtensions = new Set([
  ".cjs",
  ".dart",
  ".js",
  ".jsx",
  ".mjs",
  ".py",
  ".sol",
  ".ts",
  ".tsx",
]);
const ignoredSegments = new Set([
  ".cache",
  ".dart_tool",
  ".git",
  ".next",
  ".pytest_cache",
  ".ruff_cache",
  ".terraform",
  "__pycache__",
  "build",
  "coverage",
  "dist",
  "node_modules",
  "test",
  "tests",
]);
const ignoredPrefixes = [
  "smart-contracts/artifacts/",
  "smart-contracts/cache/",
  "smart-contracts/typechain-types/",
];

function shouldIgnore(path) {
  const normalizedPath = path.split(sep).join("/");

  if (ignoredPrefixes.some((prefix) => normalizedPath.startsWith(prefix))) {
    return true;
  }

  const segments = path.split(sep);
  return segments.some((segment) => ignoredSegments.has(segment));
}

function collectFiles(directory) {
  const entries = readdirSync(directory);
  const files = [];

  for (const entry of entries) {
    const path = join(directory, entry);
    const relativePath = relative(root, path);

    if (shouldIgnore(relativePath)) {
      continue;
    }

    const stats = statSync(path);

    if (stats.isDirectory()) {
      files.push(...collectFiles(path));
      continue;
    }

    if (stats.isFile() && supportedExtensions.has(extname(path))) {
      files.push(path);
    }
  }

  return files;
}

function normalizedLines(path) {
  return readFileSync(path, "utf8")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith("#") && !line.startsWith("//"));
}

const occurrences = new Map();

for (const file of collectFiles(root)) {
  const lines = normalizedLines(file);

  for (let index = 0; index <= lines.length - minLines; index += 1) {
    const block = lines.slice(index, index + minLines).join("\n");
    const locations = occurrences.get(block) ?? [];

    locations.push({
      file: relative(root, file),
      line: index + 1,
    });
    occurrences.set(block, locations);
  }
}

const duplicatedBlocks = [...occurrences.entries()]
  .map(([block, locations]) => {
    const uniqueFiles = new Set(locations.map((location) => location.file));

    return {
      block,
      locations,
      uniqueFiles,
    };
  })
  .filter(({ uniqueFiles }) => uniqueFiles.size > 1);

if (duplicatedBlocks.length > 0) {
  console.error(
    `Found ${duplicatedBlocks.length} duplicated code block(s) with ${minLines}+ lines.`,
  );

  for (const { block, locations } of duplicatedBlocks.slice(0, 10)) {
    console.error("\nDuplicated block:");
    console.error(block);
    console.error("Locations:");

    for (const location of locations.slice(0, 8)) {
      console.error(`- ${location.file}:${location.line}`);
    }
  }

  process.exit(1);
}

console.log(`No duplicated code blocks with ${minLines}+ lines were found.`);
