import { existsSync } from "node:fs";
import { delimiter, join } from "node:path";
import { spawnSync } from "node:child_process";

const python = process.env.PYTHON ?? "python3";
const root = process.cwd();
const dependencyTarget = join(root, ".cache", "python-deps");
const sharedSource = join(
  root,
  "packages",
  "python",
  "super-trunfo-shared",
  "src",
);

const serviceNames = [
  "auth-service",
  "card-service",
  "matchmaking-service",
  "gameplay-service",
  "economy-service",
  "ranking-service",
  "nft-service",
  "social-service",
  "notification-service",
];

const testTargets = [
  {
    name: "shared-kernel",
    path: "packages/python/super-trunfo-shared/tests",
    pythonPath: [sharedSource],
  },
  ...serviceNames.map((serviceName) => ({
    name: serviceName,
    path: `apps/services/${serviceName}/tests`,
    pythonPath: [
      sharedSource,
      join(root, "apps", "services", serviceName, "src"),
    ],
  })),
];

for (const target of testTargets) {
  const pythonPathEntries = [
    ...(existsSync(dependencyTarget) ? [dependencyTarget] : []),
    ...target.pythonPath,
    ...(process.env.PYTHONPATH ? [process.env.PYTHONPATH] : []),
  ];

  console.log(`Running Python tests: ${target.name}`);

  const result = spawnSync(python, ["-m", "pytest", target.path], {
    cwd: root,
    env: {
      ...process.env,
      PYTHONPATH: pythonPathEntries.join(delimiter),
    },
    stdio: "inherit",
  });

  if (result.status !== 0) {
    process.exit(result.status ?? 1);
  }
}
