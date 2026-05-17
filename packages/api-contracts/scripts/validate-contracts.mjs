import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const requiredFiles = ["openapi/platform.yaml", "events/domain-events.yaml"];
const packageRoot = join(dirname(fileURLToPath(import.meta.url)), "..");

for (const file of requiredFiles) {
  if (!existsSync(join(packageRoot, file))) {
    throw new Error(`Missing contract file: ${file}`);
  }
}

console.log("API contracts present.");
