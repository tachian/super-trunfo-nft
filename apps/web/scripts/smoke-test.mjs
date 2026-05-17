import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const requiredFiles = ["app/page.tsx", "app/layout.tsx", "public/card-back.svg"];
const appRoot = join(dirname(fileURLToPath(import.meta.url)), "..");

for (const file of requiredFiles) {
  if (!existsSync(join(appRoot, file))) {
    throw new Error(`Missing web app file: ${file}`);
  }
}

console.log("Web smoke test passed.");
