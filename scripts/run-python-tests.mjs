import {
  existsSync,
  mkdirSync,
  readdirSync,
  rmSync,
  unlinkSync,
} from "node:fs";
import { delimiter, join } from "node:path";
import { spawnSync } from "node:child_process";

const python = process.env.PYTHON ?? "python3";
const root = process.cwd();
const dependencyTarget = join(root, ".cache", "python-deps");
const coverageEnabled = process.env.PYTHON_COVERAGE === "1";
const coverageDirectory = join(root, ".coverage-reports", "python");
const coverageXml = join(coverageDirectory, "coverage.xml");
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

if (coverageEnabled) {
  rmSync(join(root, "coverage"), { force: true, recursive: true });
  rmSync(coverageDirectory, { force: true, recursive: true });
  mkdirSync(coverageDirectory, { recursive: true });
  removePreviousCoverageData();
}

for (const target of testTargets) {
  const pythonPathEntries = [
    ...(existsSync(dependencyTarget) ? [dependencyTarget] : []),
    ...target.pythonPath,
    ...(process.env.PYTHONPATH ? [process.env.PYTHONPATH] : []),
  ];

  console.log(`Running Python tests: ${target.name}`);

  const commandArguments = coverageEnabled
    ? [
        "-m",
        "coverage",
        "run",
        "--parallel-mode",
        "--source",
        "apps/services,packages/python",
        "-m",
        "pytest",
        target.path,
      ]
    : ["-m", "pytest", target.path];

  const result = spawnSync(python, commandArguments, {
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

if (coverageEnabled) {
  runCoverageCommand(["-m", "coverage", "combine"]);
  runCoverageCommand(["-m", "coverage", "xml", "-o", coverageXml]);
}

function runCoverageCommand(args) {
  const pythonPathEntries = [
    ...(existsSync(dependencyTarget) ? [dependencyTarget] : []),
    ...(process.env.PYTHONPATH ? [process.env.PYTHONPATH] : []),
  ];

  const result = spawnSync(python, args, {
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

function removePreviousCoverageData() {
  for (const filename of readdirSync(root)) {
    if (filename === ".coverage" || filename.startsWith(".coverage.")) {
      unlinkSync(join(root, filename));
    }
  }
}
