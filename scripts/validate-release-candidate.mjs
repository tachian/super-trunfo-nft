import { existsSync, readFileSync } from "node:fs";

const serviceCatalog = JSON.parse(
  readFileSync("apps/services/service-catalog.json", "utf8"),
);
const serviceNames = serviceCatalog.map((service) => service.name);
const releaseFiles = [
  "docs/operations/release-candidate.md",
  "docs/operations/rollback-runbook.md",
  "docs/security/owasp-mvp-checklist.md",
  "infra/k8s/base/observability.yaml",
  "infra/argocd/applications/staging.yaml",
  "infra/k8s/overlays/staging/kustomization.yaml",
];
const failures = [];

for (const file of releaseFiles) {
  if (!existsSync(file)) {
    failures.push(`Missing release candidate file: ${file}`);
  }
}

if (failures.length === 0) {
  validateArgoApplication();
  validateStagingOverlay();
  validateObservability();
  validateRunbooks();
}

if (failures.length > 0) {
  console.error("Release candidate validation failed:");

  for (const failure of failures) {
    console.error(`- ${failure}`);
  }

  process.exit(1);
}

console.log("Release candidate validation passed.");

function validateArgoApplication() {
  const stagingApplication = read("infra/argocd/applications/staging.yaml");

  requireFragment(
    stagingApplication,
    "name: super-trunfo-staging",
    "Staging ArgoCD application must be named super-trunfo-staging.",
  );
  requireFragment(
    stagingApplication,
    "targetRevision: main",
    "Staging ArgoCD application must track main.",
  );
  requireFragment(
    stagingApplication,
    "path: infra/k8s/overlays/staging",
    "Staging ArgoCD application must point to the staging overlay.",
  );
  requireFragment(
    stagingApplication,
    "selfHeal: true",
    "Staging ArgoCD application must self-heal drift.",
  );
}

function validateStagingOverlay() {
  const stagingOverlay = read("infra/k8s/overlays/staging/kustomization.yaml");
  const baseKustomization = read("infra/k8s/base/kustomization.yaml");

  requireFragment(
    stagingOverlay,
    "value: staging",
    "Staging overlay must set ENVIRONMENT=staging.",
  );
  requireFragment(
    baseKustomization,
    "observability.yaml",
    "Base kustomization must include observability manifests.",
  );

  for (const serviceName of [...serviceNames, "web"]) {
    requireFragment(
      stagingOverlay,
      `ghcr.io/tachian/super-trunfo-nft/${serviceName}`,
      `Staging overlay must publish image mapping for ${serviceName}.`,
    );
  }
}

function validateObservability() {
  const observability = read("infra/k8s/base/observability.yaml");
  const requiredFragments = [
    'grafana_dashboard: "1"',
    'prometheus_rule: "1"',
    "Super Trunfo MVP Release Candidate",
    "HTTP 5xx rate",
    "HTTP p95 latency",
    "Matchmaking queue depth",
    "Domain events published",
    "Economy credit balance",
    "SuperTrunfoHighErrorRate",
    "SuperTrunfoSlowApi",
    "SuperTrunfoMatchmakingBacklog",
  ];

  for (const fragment of requiredFragments) {
    requireFragment(
      observability,
      fragment,
      `Observability manifest must include ${fragment}.`,
    );
  }
}

function validateRunbooks() {
  const releaseRunbook = read("docs/operations/release-candidate.md");
  const rollbackRunbook = read("docs/operations/rollback-runbook.md");
  const requiredReleaseFragments = [
    "## Pre-flight",
    "## Staging Validation",
    "## Smoke Tests",
    "## Release Decision",
    "pnpm release:check",
    "gh workflow run CD",
  ];
  const requiredRollbackFragments = [
    "## Rollback Triggers",
    "## GitOps Rollback",
    "## Image Rollback",
    "## Data Safety",
    "rollout undo",
  ];

  for (const fragment of requiredReleaseFragments) {
    requireFragment(
      releaseRunbook,
      fragment,
      `Release candidate runbook must include ${fragment}.`,
    );
  }

  for (const fragment of requiredRollbackFragments) {
    requireFragment(
      rollbackRunbook,
      fragment,
      `Rollback runbook must include ${fragment}.`,
    );
  }
}

function requireFragment(content, fragment, message) {
  if (!content.includes(fragment)) {
    failures.push(message);
  }
}

function read(path) {
  return readFileSync(path, "utf8");
}
