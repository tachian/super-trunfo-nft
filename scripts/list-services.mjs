import { readFileSync } from "node:fs";

const catalog = JSON.parse(readFileSync("apps/services/service-catalog.json", "utf8"));

for (const service of catalog) {
  console.log(`${service.name}\t${service.context}\t:${service.port}`);
}

