import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const appDirectory = dirname(fileURLToPath(import.meta.url));

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  outputFileTracingRoot: join(appDirectory, "../.."),
  reactStrictMode: true,
};

export default nextConfig;
