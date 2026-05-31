import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";

const composePath = "infra/docker/compose.yaml";
const serviceCatalog = JSON.parse(
  readFileSync("apps/services/service-catalog.json", "utf8"),
);
const requiredInfrastructure = ["postgres", "redis", "rabbitmq", "opensearch"];
const requiredApps = ["web", ...serviceCatalog.map((service) => service.name)];
const requiredServices = [...requiredInfrastructure, ...requiredApps];
const expectedServicePorts = new Map(
  serviceCatalog.map((service) => [service.name, String(service.port)]),
);
expectedServicePorts.set("web", "3000");

const result = spawnSync(
  "docker",
  ["compose", "-f", composePath, "config", "--format", "json"],
  {
    encoding: "utf8",
  },
);

if (result.status !== 0) {
  process.stderr.write(result.stderr);
  process.exit(result.status ?? 1);
}

const compose = JSON.parse(result.stdout);
const services = compose.services ?? {};
const failures = [];

for (const serviceName of requiredServices) {
  if (!services[serviceName]) {
    failures.push(`Missing service: ${serviceName}`);
  }
}

for (const serviceName of requiredInfrastructure) {
  if (!services[serviceName]?.healthcheck) {
    failures.push(`Missing healthcheck for infrastructure: ${serviceName}`);
  }
}

for (const serviceName of requiredApps) {
  const service = services[serviceName];

  if (!service?.build) {
    failures.push(`Missing build definition for app service: ${serviceName}`);
  }

  if (!service?.healthcheck) {
    failures.push(`Missing healthcheck for app service: ${serviceName}`);
  }

  const expectedPort = expectedServicePorts.get(serviceName);
  const publishedPorts = (service?.ports ?? []).map((port) =>
    String(port.published),
  );

  if (expectedPort && !publishedPorts.includes(expectedPort)) {
    failures.push(
      `Missing published port ${expectedPort} for app service: ${serviceName}`,
    );
  }
}

for (const [serviceName, service] of Object.entries(services)) {
  const dependencies = Object.entries(service.depends_on ?? {});

  for (const [dependencyName, dependency] of dependencies) {
    if (dependency.condition !== "service_healthy") {
      failures.push(
        `${serviceName} depends on ${dependencyName} without service_healthy`,
      );
    }
  }
}

if (failures.length > 0) {
  console.error("Local Compose validation failed:");

  for (const failure of failures) {
    console.error(`- ${failure}`);
  }

  process.exit(1);
}

console.log(
  `Local Compose validation passed for ${requiredServices.length} services.`,
);
